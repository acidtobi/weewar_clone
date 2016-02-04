from __future__ import division

import wx
import wx.lib.scrolledpanel

class MapPanel(wx.lib.scrolledpanel.ScrolledPanel):

    def __init__(self, parent, background_tile, size, innerbitmap=None):

        self.background_tile = background_tile
        self.InnerSize = size
        self.innerbitmap = innerbitmap

        screen_width, screen_height = wx.DisplaySize()
        self.background = wx.EmptyBitmap(screen_width, screen_height)

        dc = wx.MemoryDC()
        dc.SelectObject(self.background)
        #dc.Clear()

        tile_width, tile_height = self.background_tile.Size
        for rownum in range(int(screen_height / tile_height)):
            for colnum in range(int(screen_width / tile_width)):
                dc.DrawBitmap(self.background_tile, colnum * tile_width, rownum * tile_height, True)

        width_px, height_px = size
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, size=(width_px, height_px))

        #self.SetBackgroundColour("#F0F0F0")
        self.SetupScrolling()
        self.SetScrollRate(1, 1)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnResize)

    def setInnerBitmap(self, bitmap):
        self.innerbitmap = bitmap

    def OnPaint(self, e):

        dc = wx.PaintDC(self)
        dc.Clear()

        self_width, self_height = self.InnerSize
        sizer_width, sizer_height = self.GetSize()

        posx = max(0, (sizer_width - self_width) / 2)
        posy = max(0, (sizer_height - self_height) / 2)

        x, y = self.CalcScrolledPosition((posx, posy))

        tile_width, tile_height = self.background_tile.Size
        offset_x, offset_y = x % tile_width, y % tile_height

        dc.DrawBitmap(self.background, offset_x - tile_width, offset_y - tile_height)
        if self.innerbitmap:
            print self.innerbitmap.GetMask()
            dc.DrawBitmap(self.innerbitmap, x, y, True)

    def OnResize(self, e):
        self.SetSize(e.GetSize())
        self.SetVirtualSize(self.InnerSize)
        self.OnPaint(e)

# ==============================================================================================
# tests
# ==============================================================================================

if __name__ == "__main__":

    class MainFrame(wx.Frame):

        def __init__(self, parent, title):

            background = wx.Bitmap("tiles_background.jpg")
            background_tile = wx.Bitmap("logo_background_repeating.png")
            self.foreground = wx.Bitmap("rubberducky.png")
            wx.Frame.__init__(self, parent, title=title, size=background.Size)

            self.mappanel = MapPanel(self, background_tile, size=self.foreground.Size, innerbitmap=self.foreground)

            leftpanel = wx.Panel(self, -1, size=(100, -1))

            self.box = wx.BoxSizer(wx.HORIZONTAL)
            self.box.Add(leftpanel, 0, wx.EXPAND)
            self.box.Add(self.mappanel, 2, wx.EXPAND)

            self.SetAutoLayout(True)
            self.SetSizer(self.box)
            self.Layout()

            self.Bind(wx.EVT_PAINT, self.OnPaint)

        def OnPaint(self, e):
            self.mappanel.setInnerBitmap(self.foreground)


    app = wx.App()
    mainframe = MainFrame(None, "Map Panel")
    mainframe.Show()

    app.MainLoop()


