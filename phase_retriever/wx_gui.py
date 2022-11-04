import wx
import numpy as np

from .gui.wxplot import PlotsNotebook, LabelPlotsNotebook
from .gui.wxentries import wxEntryPanel
from .retriever import PhaseRetriever

class wxGUI(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(800, 600))

        # Initializing a dict containing the names of the plots that we will have on our
        # GUI with their pointers
        self.plots = {
                "irradiance": None,
                "mse"       : None,
                "phi"       : None,
                "bandwidth" : None,
                }

        self.init()
        self.Centre()

    def init(self):
        # Initializing the plotter
        self.plotter = plotter = PlotsNotebook(self)
        # TODO: Just left as a reference for future code, delete after it's not needed
        #ax1 = plotter.add("Region of interest").add_subplot()
        #ax1.imshow(np.random.rand(256, 256), interpolation="nearest")
        #plotter.nb.GetPage(0).draw_circle((128, 128), 32, color="red")
        #
        #ax2 = plotter.add("Bandwidth").add_subplot()
        #ax2.imshow(np.random.normal(size=(256, 256)), interpolation="nearest")

        # FIXME: Notebook
        notebook = wx.Notebook(self)

        # Separators for each of the panels we'll have
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.entries = entries = wxEntryPanel(notebook)
        self.entries.GetButton("search").Bind(wx.EVT_BUTTON, self.OnLoadClick)
        self.entries.GetButton("autoadjust").Bind(wx.EVT_BUTTON, self.OnAutoadjust)

        # FIXME: Notebook
        notebook.AddPage(entries, "Config")
        notebook.AddPage(wx.Panel(notebook), "Exploration")

        # Adding it, from left to right, to the sizer
        sizer.Add(notebook, 1, wx.LEFT | wx.EXPAND)
        sizer.Add(plotter, 2, wx.RIGHT | wx.EXPAND)
        self.SetSizer(sizer)

        # Creating a menu
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        fileItem = fileMenu.Append(wx.ID_EXIT, "Quit", "Quit application")
        menubar.Append(fileMenu, "&File")
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnQuit, fileItem)

        # TODO: Initialize the phase retriever
        self.retriever = PhaseRetriever()

    def OnAutoadjust(self, event):
        # TODO
        # We center the window with the size given by the entries.
        configs = self.entries.GetValues()
        window_size = configs["window_size"]
        self.retriever.config(dim=window_size)
        top, bottom = self.retriever.center_window()
        rect_llc = top[0], bottom[1]
        # Adjust the phase origin
        self.retriever.select_phase_origin()
        phase_origin = self.retriever.options["origin"]
        # ... and its bandwidth
        a_ft = self.retriever.compute_bandwidth(tol=1e-5)
        a_ft_log = np.log10(a_ft)

        # Plot the relevant information...
        self.plotter.set_imshow("Cropped irradiance", self.retriever.cropped_irradiance, cmap="gray")
        self.plotter.set_imshow("Autocorrelation spectrum", a_ft_log, cmap="viridis")

        # Draw and change the configurations as required by the autoconfiguration
    def OnStartProcessing(self, event):
        # Check if pixel_size is properly set, needed to do any assignment
        p_size = self.retriever.options["pixel_size"]
        if ((not p_size) or (p_size <= 0)):
            error_dialog = wx.MessageDialog(self, 
                            "Pixel size must be selected before proceeding!",
                            style=wx.ICON_ERROR | wx.OK)
            error_dialog.ShowModal()

    def OnLoadClick(self, event):
        dialog = wx.DirDialog(self, "Choose input directory", "", wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)

        # Run the window and check if it successfully finishes
        res = dialog.ShowModal()
        if res == wx.ID_OK:
            # Retain a reference of the user selected path
            dirname = dialog.GetPath()
        dialog.Destroy()
        if res != wx.ID_OK:
            return

        # We now update the entry to contain the selected path
        info = self.entries.GetTextEntry()
        info.ChangeValue(dirname)

        # Finally, we load all images into the phase retriever
        try:
            self.retriever.load_dataset(dirname)
        except:
            error_dialog = wx.MessageDialog(self, 
                            "Selected directory does not contain polarimetric images.",
                            style=wx.ICON_ERROR | wx.OK)
            error_dialog.ShowModal()

        # We show the important images through the plots
        self.ShowDataset()

    def ShowDataset(self):
        # FIXME: This process could better be encapsulated inside the plotter class...
        self.plotter.set_imshow("Irradiance", self.retriever.irradiance, cmap="gray")

    def OnQuit(self, event):
        self.Close()

if __name__ == "__main__":
    app = wx.App()
    gui = wxGUI(None, "Phase retriever")
    gui.Show()

    app.MainLoop()
