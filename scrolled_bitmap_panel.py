from __future__ import division

import wx
import wx.lib.scrolledpanel

class ScrolledBitmapPanel(wx.lib.scrolledpanel.ScrolledPanel):

    def __init__(self, parent, background_tile, size, innerbitmap=None):

        def tiled_bitmap(tile):
            screen_width, screen_height = wx.DisplaySize()
            bitmap = wx.EmptyBitmap(screen_width, screen_height)

            dc = wx.MemoryDC()
            dc.SelectObject(bitmap)

            tile_width, tile_height = tile.Size
            for rownum in range(int(screen_height / tile_height)):
                for colnum in range(int(screen_width / tile_width)):
                    dc.DrawBitmap(tile, colnum * tile_width, rownum * tile_height, True)

            return bitmap

        self.background_tile = background_tile
        self.InnerSize = size
        self.innerbitmap = innerbitmap
        self._Buffer = None
        self.virtual_x = 0
        self.virtual_y = 0

        self.background = tiled_bitmap(background_tile)

        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, size=size)

        self.SetupScrolling()
        self.SetScrollRate(1, 1)

        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.Bind(wx.EVT_SIZE, self.onResize)

    def setInnerBitmap(self, bitmap):
        self.innerbitmap = bitmap

    def getVirtualPosition(self, (x, y)):
        scrolled_x, scrolled_y = self.CalcScrolledPosition((self.virtual_x, self.virtual_y))
        return x - scrolled_x, y - scrolled_y

    def updateDrawing(self):

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

    def onPaint(self, e):
        dc = wx.PaintDC(self)
        x, y = self.CalcScrolledPosition((0, 0))
        dc.DrawBitmap(self._Buffer, x, y)

    def onResize(self, e):
        width, height = e.GetSize()
        inner_width, inner_height = self.InnerSize
        self.SetSize((width, height))
        self.SetVirtualSize((inner_width, inner_height))
        self._Buffer = wx.EmptyBitmap(max(width, inner_width), max(height, inner_height))
        self.updateDrawing()

# ==============================================================================================
# tests
# ==============================================================================================

if __name__ == "__main__":

    class MainFrame(wx.Frame):

        def __init__(self, parent, title):

            background_tile = wx.Bitmap("logo_background_repeating.png")
            self.foreground = wx.Bitmap("rubberducky.png")

            displays = (wx.Display(i) for i in range(wx.Display.GetCount()))
            sizes = [display.GetGeometry().GetSize() for display in displays]
            size_x, size_y = sizes[0]

            wx.Frame.__init__(self, parent, title=title, size=(size_x * 0.75, size_y * 0.75))

            self.sbmpanel = ScrolledBitmapPanel(self, background_tile, size=self.foreground.Size, innerbitmap=self.foreground)
            self.sbmpanel.setInnerBitmap(self.foreground)

    app = wx.App()
    mainframe = MainFrame(None, "Scrolled Bitmap Panel Demo")
    mainframe.Show()

    app.MainLoop()


