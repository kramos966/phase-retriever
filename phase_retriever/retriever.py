import numpy as np
import multiprocessing as mp

from .algorithm import multi
from .misc.radial import get_function_radius
from .misc.file_selector import get_polarimetric_names

class SinglePhaseRetriever():
    # TODO: Crea una classe que encapsuli completament el mètode de recuperació de fase
    def __init__(self, n_max=200):
        self.n_max = n_max          # Maximum number of iterations

    def load_dataset(self, path):
        self.path = path
        
        self.polarimetric_sets = get_polarimetric_names(path)
        if not self.polarimetric_sets:
            raise ValueError(f"Cannot load polarimetric images from {path}")

    def seek_central_region(self):
        """Seek the region where the greatest amount of energy is contained."""
        pass
    
    def config(self,):
        pass

class PhaseRetriever(SinglePhaseRetriever):
    # TODO: Deriva un recuperador de fase que utilitzi multiprocessing per a recuperar dues
    # fases a la vegada.
    def __init__(sef, *args, **kwargs):
        super().__init__(*args, **kwargs)
