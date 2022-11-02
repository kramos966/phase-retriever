import wx
import numpy as np

from .gui.wxplot import PlotsNotebook, LabelPlotsNotebook
from .gui.wxentries import wxEntryPanel

class wxGUI(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(800, 600))

        self.init()
        self.Centre()

    def init(self):
        # Initializing the plotter
        plotter = PlotsNotebook(self)
        ax1 = plotter.add("Region of interest").add_subplot()
        ax1.imshow(np.random.rand(256, 256), interpolation="nearest")
        plotter.nb.GetPage(0).draw_circle((128, 128), 32, color="red")

        ax2 = plotter.add("Bandwidth").add_subplot()
        ax2.imshow(np.random.normal(size=(256, 256)), interpolation="nearest")

        # FIXME: Notebook
        notebook = wx.Notebook(self)

        # Separators for each of the panels we'll have
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        entries = wxEntryPanel(notebook)

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

    def OnQuit(self, event):
        self.Close()

        pass

if __name__ == "__main__":
    app = wx.App()
    gui = wxGUI(None, "Phase retriever")
    gui.Show()

    app.MainLoop()
