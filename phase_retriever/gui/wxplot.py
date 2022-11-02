import wx
import wx.lib.agw.aui as aui
import wx.lib.mixins.inspection as wit

from matplotlib.figure import Figure
from matplotlib.patches import Rectangle, Circle
from matplotlib.backends.backend_wxagg import (
        FigureCanvasWxAgg as FigureCanvas,
        NavigationToolbar2WxAgg as NavigationToolbar)

# TODO: Reproduce the same functionality as in its Tk counterpart.
class Plot(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY, dpi=None, **kwargs):
        super().__init__(parent, id=id, **kwargs)
        self.figure = Figure(dpi=dpi, figsize=(2, 2))
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Realize()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)
        sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        self.SetSizer(sizer)

        # Dict to contain and access all the drawn patches in the current figure.
        self.patches = {}

    def draw_circle(self, position, r, color="green"):
        """Draw a circle with centre at the given coordinates with radius r."""
        ax = self.figure.axes[0]
        if "circle" not in self.patches:
            circle = self.patches["circle"] = Circle((position), radius=r, fill=True, color=color,
                    alpha=.2)
            ax.add_patch(circle)
        else:
            circle = self.patches["circle"]
            circle.set_radius(self.r)
            circle.x = position[0]
            circle.y = position[1]
        self.canvas.draw()
        self.canvas.flush_events()
    def draw_rectangle(self, position, w, h):
        pass

class PlotsNotebook(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY):
        super().__init__(parent, id=id)
        self.nb = aui.AuiNotebook(self, agwStyle=aui.AUI_NB_TOP | aui.AUI_NB_TAB_SPLIT | aui.AUI_NB_TAB_MOVE | aui.AUI_NB_SCROLL_BUTTONS)
        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.EXPAND)
        self.SetSizer(sizer)
        
    def add(self, name="plot"):
        page = Plot(self.nb)
        self.nb.AddPage(page, name)
        return page.figure

class LabelPlotsNotebook(PlotsNotebook, wx.Panel):
    def __init__(self, parent, text):
        #super(wx.Panel, self).__init__(parent)
        #super(PlotsNotebook, self).__init__(self)
        wx.Panel.__init__(self, parent)
        PlotsNotebook.__init__(self, self)

        self.init(text)

    def init(self, text):
        tctrl = wx.StaticText(self, label=text)
        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(tctrl, 1, wx.EXPAND | wx.LEFT)
        self.SetSizer(sizer)
