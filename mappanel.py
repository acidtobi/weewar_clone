from __future__ import division

import wx
import wx.lib.scrolledpanel

class MainFrame(wx.Frame):

    def __init__(self, parent, title):

        background = wx.Bitmap("tiles_background.jpg")
        foreground = wx.Bitmap("rubberducky.png")

        wx.Frame.__init__(self, parent, title=title, size=background.Size)

        self.mappanel = MapPanel(self, background, foreground)
        self.SetAutoLayout(True)
        self.Layout()

        self.Bind(wx.EVT_SIZE, self.mappanel.OnResize)


class MapPanel(wx.lib.scrolledpanel.ScrolledPanel):

    def __init__(self, parent, background, foreground):

        self.background = background
        self.foreground = foreground

        width_px, height_px = foreground.Size
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, size=(width_px, height_px))

        self.SetBackgroundColour("#F0F0F0")
        self.SetupScrolling()
        self.SetScrollRate(1, 1)

        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, e):

        dc = wx.PaintDC(self)
        dc.Clear()

        self_width, self_height = self.foreground.Size
        sizer_width, sizer_height = self.GetParent().GetVirtualSize()
        posx = max(0, (sizer_width - self_width) / 2)
        posy = max(0, (sizer_height - self_height) / 2)

        x, y = self.CalcScrolledPosition((posx, posy))
        dc.DrawBitmap(self.background, x - 200, y - 200)
        dc.DrawBitmap(self.foreground, x, y)

    def OnResize(self, e):

        self_width, self_height = self.foreground.Size
        sizer_width, sizer_height = self.GetParent().GetVirtualSize()
        self.SetSize(self.GetParent().GetVirtualSize())

        posx = max(0, (sizer_width - self_width) / 2)
        posy = max(0, (sizer_height - self_height) / 2)

        self_width = min(self_width, sizer_width)
        self_height = min(self_height, sizer_height)

        self_vwidth = max(self_width, sizer_width)
        self_vheight = max(self_height, sizer_height)

        #self.SetVirtualSize((self_vwidth, self_vheight))
        #self.SetVirtualSize(self.foreground.Size)

        print self_width, self_height, sizer_width, sizer_height, posx, posy

        self.OnPaint(e)

    def onExit(self, e):
        self.Close(True)

app = wx.App()
mainframe = MainFrame(None, "Map Panel")
mainframe.Show()

app.MainLoop()


