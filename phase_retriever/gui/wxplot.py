import wx
import wx.lib.agw.aui as aui
import wx.lib.mixins.inspection as wit

import numpy as np
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

    def set_rectangle(self, position, w, h, color="green"):
        """Draw a rectangle at a given position with width w and height h."""
        if not "rectangle" in self.patches:
            rect = self.patches["rectangle"] = Rectangle((0, 0), 1, 1, color=color, fill=True,
                    alpha=0.2)
            self.figure.axes[0].add_patch(rect)
        else:
            rect = self.patches["rectangle"]
        # We transform the coordinates of the rectangle, as position is assumed to be its center,
        # while matplotlib requires its position from the lower left corner.
        x_llc, y_llc = position[0], position[1]
        # Set its new coordinates, width and height
        rect.set(width=w, height=h, x=x_llc, y=y_llc)
        self.canvas.draw()
        self.canvas.flush_events()

class PlotsNotebook(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY):
        super().__init__(parent, id=id)
        self.nb = aui.AuiNotebook(self, agwStyle=aui.AUI_NB_TOP | aui.AUI_NB_TAB_SPLIT | aui.AUI_NB_TAB_MOVE | aui.AUI_NB_SCROLL_BUTTONS)
        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.pages = {}
        
    def add(self, name):
        if name in self.pages:
            raise NameError(f"Page with name {name} already exists!")
        page = Plot(self.nb)
        self.nb.AddPage(page, name)
        self.pages[name] = len(self.pages)
        return page.figure

    def set_imshow(self, name, image, cmap="viridis"):
        if name not in self.pages:
            fig = self.add(name)
            ax = fig.add_subplot()
            ax.imshow(np.zeros((16, 16)), cmap=cmap, vmin=0, vmax=1)
        idx = self.pages[name]
        plot = self.nb.GetPage(idx)
        canvas = plot.canvas
        figure = plot.figure
        ax = figure.axes[0]

        ny, nx = image.shape

        ax_img = ax.get_images()[0]
        ax_img.set_extent([0, nx, ny, 0])
        ax_img.set_data(image)
        ax_img.set_clim(image.min(), image.max())
        canvas.flush_events()
        canvas.draw()

    def set_rectangle(self, name, position, w, h, color="green"):
        if name not in self.pages:
            raise NameError(f"Notebook page with name {name} does not exist")
        idx = self.pages[name]
        plot = self.nb.GetPage(idx)
        plot.set_rectangle(position, w, h, color=color)

    def set_circle(self, name, position, r, color="green"):
        if name not in self.pages:
            raise NameError(f"Notebook page with name {name} does not exist")
        idx = self.pages[name]
        plot = self.nb.GetPage(idx)
        plot.draw_circle(position, r, color=color)

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
