import wx
import wx.propgrid

class TextedEntry(wx.Panel):
    def __init__(self, parent, text):
        super().__init__(parent)

        self.init(text)

    def init(self, text):
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, label=text)

        entry = wx.TextCtrl(self)

        sizer.Add(entry, 0, wx.LEFT | wx.EXPAND)
        sizer.Add(label, 0, wx.LEFT | wx.EXPAND)

        self.SetSizer(sizer)

class DirectorySelector(wx.Panel):
    def __init__(self, parent, text):
        super().__init__(parent)

        self.init(text)

    def init(self, text):
        sizer = wx.BoxSizer(wx.VERTICAL)

        button = wx.Button(self, label="Load directory")

        info = TextedEntry(self, text)

        sizer.Add(info, 0, wx.LEFT | wx.EXPAND)
        sizer.Add(button, 0, wx.LEFT | wx.EXPAND)

        self.SetSizer(sizer)

class wxEntryPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.init()

    def init(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Name and directory of the polarimetric images
        polEntry = DirectorySelector(self, "Working directory")

        # To hold all the data entries, we creat a grid (wokrsheet-like)
        pgrid = wx.propgrid.PropertyGrid(self, name="EntryPanel")

        pgrid.Append(wx.propgrid.PropertyCategory("Measurement properties"))
        pgrid.Append(wx.propgrid.FloatProperty("Wavelength (um)", value=0.52))
        pgrid.Append(wx.propgrid.FloatProperty("Pixel size (um)", value=3.75))
        pgrid.Append(wx.propgrid.PropertyCategory("Retrieving configuration"))
        pgrid.Append(wx.propgrid.IntProperty("Number of iterations", value=120))
        pgrid.Append(wx.propgrid.IntProperty("Window centre Y", value=0))
        pgrid.Append(wx.propgrid.IntProperty("Window centre X", value=0))
        pgrid.Append(wx.propgrid.IntProperty("Phase origin Y", value=0))
        pgrid.Append(wx.propgrid.IntProperty("Phase origin X", value=0))
        pgrid.Append(wx.propgrid.FloatProperty("Bandwidth (pixels)", value=20))


        sizer.Add(polEntry, 1, wx.EXPAND | wx.LEFT)
        sizer.Add(pgrid, 1, wx.EXPAND | wx.LEFT)
        self.SetSizer(sizer)
