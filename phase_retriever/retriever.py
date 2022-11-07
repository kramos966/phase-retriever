import numpy as np
from scipy.fft import fft2, ifft2, fftshift, ifftshift
import multiprocessing as mp
import imageio

from .algorithm import multi
from .misc.radial import get_function_radius
from .misc.file_selector import get_polarimetric_names
from .misc.central_region import find_rect_region
from .misc.stokes import get_stokes_parameters

class SinglePhaseRetriever():
    # TODO: Crea una classe que encapsuli completament el mètode de recuperació de fase
    options = {
            "pixel_size":None,  # MUST BE SCALED ACCORDING TO THE WAVELENGTH
            "dim"       :256,
            "rect"      :None,
            "n_max"     :200,
            "eps"       :0.01,
            "bandwidth" :None,
            "origin"    :None,
            "lamb"      :None,
            "path"      :None
            }
    irradiance = None
    images = {}
    cropped = {}
    cropped_irradiance = None
    a_ft = None
    def __init__(self, n_max=200):
        self.options["n_max"] = n_max          # Maximum number of iterations

    def load_dataset(self, path):
        self.irradiance = None
        self.images = {}
        self.options["path"] = path
        
        self.polarimetric_sets = get_polarimetric_names(path)
        if not self.polarimetric_sets:
            raise ValueError(f"Cannot load polarimetric images from {path}")

        # Load all images into memory
        for z in self.polarimetric_sets:
            self.images[z] = {}
            for polarization in self.polarimetric_sets[z]:
                if type(polarization) != int:
                    continue
                path = self.polarimetric_sets[z][polarization]
                image = imageio.imread(path)
                self.images[z][polarization] = image.astype(np.float64)

        # Compute irradiance
        self._compute_irradiance()

    def _compute_irradiance(self):
        # Compute only the irradiance in the initial plane
        self.irradiance = 0
        if not self.images:
            raise ValueError("Dataset not yet specified/loaded.")
        # We only use one of the planes to compute the irradiance
        zetes = list(self.images.keys())
        z = zetes[0]    # We don't care which one...
        images = self.images[z]
        for polarization in images:
            if type(polarization) != int:
                continue
            self.irradiance += images[polarization]

        self.irradiance /= 3

    def _crop_images(self, top, bottom):
        if not self.images:
            raise ValueError("Images not yet loaded")

        y0, x0 = top
        y1, x1 = bottom
        first = True
        for z in self.images:
            self.cropped[z] = {}
            if first:
                self.cropped_irradiance = 0
            for polarization in self.images[z]:
                if type(polarization) != int:
                    continue
                image = self.images[z][polarization]
                cropped = image[y0:y1, x0:x1]
                self.cropped[z][polarization] = cropped
                if first:
                    # We also compute the cropped irradiance
                    self.cropped_irradiance += cropped
            first = False
        # And that's THA'

    def center_window(self):
        """Center the window of size dim X dim on the region with the most energy content."""
        # We do it based on the total irradiance.
        if not self.images:
            self.load_dataset()
        try:
            _ = self.irradiance.shape
        except:
            # Irradiance not yet computed
            self._compute_irradiance()
        top, bottom = find_rect_region(self.irradiance, self.options["dim"])

        # Now, we crop all images to the region specified by the top, bottom pair of coords.
        self.options["rect"] = top, bottom
        self._crop_images(top, bottom)
        return top, bottom

    def select_phase_origin(self):
        """Automatically select the point of highest intensity as the phase origin of the
        phase retrieval process."""
        if not self.cropped:
            self.center_window()

        # Find the location of the maximum intensity
        yloc, xloc = np.where(self.cropped_irradiance == self.cropped_irradiance.max())
        loc = yloc[0], xloc[0]
        self.options["origin"] = loc

    def compute_bandwidth(self, tol=1e-4):
        if not self.cropped:
            self._compute_irradiance()
        # Compute the Fourier Transform of the cropped irradiance to get its bandwidth
        ft = fftshift(fft2(ifftshift(self.cropped_irradiance)))
        self.a_ft = a_ft = np.real(np.conj(ft)*ft)
        r = get_function_radius(a_ft, tol=tol)/2
        if not r:
            raise ValueError("Could not estimate the Bandwidth of the beam")
        self.options["bandwidth"] = r
        return a_ft

    def retrieve(self):
        """Phase retrieval process. Using the configured parameters, begin the phase retrieval process."""
        if not self.options["pixel_size"]:
            raise ValueError("Pixel size not specified")
        if not self.options["bandwidth"]:
            self.compute_bandwidth()
        if not self.options["origin"]:
            self.select_phase_origin()
        p_size = self.options["pixel_size"]
        lamb = self.options["lamb"]
        p_size /= lamb
        # First, we construct the field amplitudes
        A_x = []
        A_y = []
        for z in self.cropped:
            I_x = self.cropped[z][2]
            I_y = self.cropped[z][0]
            A_x.append(np.sqrt(I_x))
            A_y.append(np.sqrt(I_y))
        # Then, we need to compute the free space transfer function H
        n = self.options["dim"]
        ny, nx = np.mgrid[-n//2:n//2, -n//2:n//2]
        umax = .5/p_size
        x = nx/nx.max()*umax
        y = ny/ny.max()*umax
        rho2 = x*x+y*y
        gamma = np.emath.sqrt(1-rho2)
        zetes = list(self.images.keys())
        dz = (zetes[1]-zetes[0])/lamb
        print(dz*lamb)
        H = np.sqrt(2j*np.pi*gamma)
        # Get the bandwidth of the beam we are computing and remove all values of H lying outside this region.
        bw = self.options["bandwidth"]
        bandwidth_mask = (ny*ny+nx*nx < bw*bw)
        H[:] = fftshift(H*bandwidth_mask)
        # Finally, we create an initial guess for the phase of both components
        phi_0 = np.zeros((n, n))

        # We set up the multiprocessing environment. Just two processes, as we have two phases to recover
        self.queues = [mp.Queue(), mp.Queue()]
        p1, c1 = mp.Pipe()
        p2, c2 = mp.Pipe()
        # As queues only work with base types, we need to separate real and imaginary parts of the result
        self.reals = [mp.Array("d", range(0, int(n**2))), mp.Array("d", range(0, int(n**2)))]
        self.imags = [mp.Array("d", range(0, int(n**2))), mp.Array("d", range(0, int(n**2)))]
        # List with each of the processes, to keep track of them
        self.processes = \
                [mp.Process(target=multi, args=(H, self.options["n_max"], phi_0, *A_x),
                    kwargs={"queue":self.queues[0], "real":self.reals[0], "imag":self.imags[0]}),
                 mp.Process(target=multi, args=(H, self.options["n_max"], phi_0, *A_y),
                    kwargs={"queue":self.queues[1], "real":self.reals[1], "imag":self.imags[1]})]
        # Begin monitoring
        self.monitor_process()
        return A_x, A_y

    def monitor_process(self):
        # TODO: Aconsegueix-ne les fases ajustades
        for p in self.processes:
            p.start()
        for p in self.processes:
            p.join()
    
    def get_phases(self):
        """Convert the multiprocessing arrays into the 2D phase distributions."""
        dim = self.options["dim"]
        exphi_x = (np.asarray(self.reals[0])+1j*np.asarray(self.imags[0])).reshape((dim, dim))
        exphi_y = (np.asarray(self.reals[1])+1j*np.asarray(self.imags[1])).reshape((dim, dim))
        # Now, impose the phase difference as obtained experimentally through the Stokes parameters
        irradiances = [self.cropped[0][pol] for pol in range(6)]
        stokes = get_stokes_parameters(irradiances)
        delta = np.arctan2(stokes[3], stokes[2])
        # The phase origin will correspond to the value of the phase where the maximum of irradiance lies
        origin = self.options["origin"]
        delta_0 = delta[origin[0], origin[1]]
        e_delta_0 = np.exp(1j*delta_0)

        exphi_x /= exphi_x[origin[0], origin[1]]
        exphi_y /= exphi_y[origin[0], origin[1]]
        exphi_x *= e_delta_0
        return exphi_x, exphi_y

    def config(self, **options):
        #def config(self, pixel_size=None, dim=256, n_max=200, eps=0.01, radius=None, origin=None):
        for option in options:
            # If the option is in the list, we change it...
            if option in self.options:
                self.options[option] = options[option]
            # Else, we raise an exception
            else:
                raise KeyError(f"Option {option} does not exist.")

class PhaseRetriever(SinglePhaseRetriever):
    # TODO: Deriva un recuperador de fase que utilitzi multiprocessing per a recuperar dues
    # fases a la vegada.
    def __init__(sef, *args, **kwargs):
        super().__init__(*args, **kwargs)
