from __future__ import division

import wx
import wx.lib.scrolledpanel

class MapPanel(wx.lib.scrolledpanel.ScrolledPanel):

    def __init__(self, parent, background_tile, size, innerbitmap=None):

        self.background_tile = background_tile
        self.InnerSize = size
        self.innerbitmap = innerbitmap
        self._Buffer = None
        self.virtual_x = 0
        self.virtual_y = 0

        screen_width, screen_height = wx.DisplaySize()
        self.background = wx.EmptyBitmap(screen_width, screen_height)

        dc = wx.MemoryDC()
        dc.SelectObject(self.background)

        tile_width, tile_height = self.background_tile.Size
        for rownum in range(int(screen_height / tile_height)):
            for colnum in range(int(screen_width / tile_width)):
                dc.DrawBitmap(self.background_tile, colnum * tile_width, rownum * tile_height, True)

        width_px, height_px = size
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, size=(width_px, height_px))

        self.SetupScrolling()
        self.SetScrollRate(1, 1)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnResize)

        #self.OnResize(None)

    def setInnerBitmap(self, bitmap):
        self.innerbitmap = bitmap

    def GetVirtualPosition(self, (x, y)):
        scrolled_x, scrolled_y = self.CalcScrolledPosition((self.virtual_x, self.virtual_y))
        return x - scrolled_x, y - scrolled_y

    def UpdateDrawing(self):

        dc = wx.MemoryDC()
        dc.SelectObject(self._Buffer)

        self_width, self_height = self.InnerSize
        sizer_width, sizer_height = self.GetSize()

        self.virtual_x = max(0, (sizer_width - self_width) / 2)
        self.virtual_y = max(0, (sizer_height - self_height) / 2)

        tile_width, tile_height = self.background_tile.Size
        offset_x, offset_y = self.virtual_x % tile_width, self.virtual_y % tile_height

        dc.DrawBitmap(self.background, offset_x - tile_width, offset_y - tile_height)
        if self.innerbitmap:
            dc.DrawBitmap(self.innerbitmap, self.virtual_x, self.virtual_y, True)

        del dc
        self.Refresh(eraseBackground=False)
        self.Update()

    def OnPaint(self, e):
        dc = wx.PaintDC(self)
        x, y = self.CalcScrolledPosition((0, 0))
        dc.DrawBitmap(self._Buffer, x, y)

    def OnResize(self, e):
        width, height = e.GetSize()
        inner_width, inner_height = self.InnerSize
        self.SetSize((width, height))
        self.SetVirtualSize((inner_width, inner_height))
        self._Buffer = wx.EmptyBitmap(max(width, inner_width), max(height, inner_height))
        self.UpdateDrawing()

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

            #self.Bind(wx.EVT_PAINT, self.OnPaint)
            self.mappanel.setInnerBitmap(self.foreground)


    app = wx.App()
    mainframe = MainFrame(None, "Map Panel")
    mainframe.Show()

    app.MainLoop()


