import wx
import units
import colors

class BattleResultPanel(wx.Panel):

    def __init__(self, parent):

        width_px = 250
        height_px = 190

        self.attacking_color = None
        self.attacking_type = None
        self.attacking_lost = None
        self.attacking_left = None
        self.defending_color = None
        self.defending_type = None
        self.defending_lost = None
        self.defending_left = None

        wx.Panel.__init__(self, parent, style=wx.RAISED_BORDER, size=(width_px, height_px))

        self.btn_continue = wx.Button(self, -1, "Continue game", (70, 145))
        self.btn_continue.SetBackgroundColour('#cce5ff')

        self._Buffer = wx.EmptyBitmap(width_px, height_px)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_UP, self.onClick)
        self.btn_continue.Bind(wx.EVT_LEFT_UP, self.onClick)

    def onClick(self, e):
        self.Hide()

    def OnPaint(self, e):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self._Buffer, 0, 0)

    def UpdateDrawingBuffered(self):

        width, height = self.GetVirtualSize()

        border = 20
        image_width, image_height = 32, 34

        dc = wx.MemoryDC()
        dc.SelectObject(self._Buffer)
        dc.Clear()

        dc.SetPen(wx.Pen("#C0C0C0", style=wx.SOLID))
        dc.DrawLine(border, 30, width - border, 30)

        rect_y_pos = 45
        rect_size = 90
        dc.DrawRectangle(border, rect_y_pos, rect_size, rect_size)
        dc.DrawRectangle(width - border - rect_size, rect_y_pos, rect_size, rect_size)

        self.putUnitTypeImage(self.attacking_type, self.attacking_color, border + 10, rect_y_pos + 27)
        self.putUnitTypeImage(self.defending_type, self.defending_color, width - border - rect_size + 10, rect_y_pos + 27)

        gc = wx.GraphicsContext.Create(dc)
        gc.SetAntialiasMode(True)

        self.putCenteredText(gc, "Battle", 10, "#808080", wx.BOLD, width / 2, 15)
        self.putCenteredText(gc, "Player", 10, wx.BLACK, wx.BOLD, border + (rect_size / 2), rect_y_pos + 15)
        self.putCenteredText(gc, "AI", 10, wx.BLACK, wx.BOLD, width - border - (rect_size / 2), rect_y_pos + 15)

        self.putCenteredText(gc, "%d" % -self.attacking_lost, 14, wx.RED, wx.BOLD, border + rect_size - 30, rect_y_pos + (rect_size / 2))
        self.putCenteredText(gc, "%d" % -self.defending_lost, 14, wx.RED, wx.BOLD, width - border - 30, rect_y_pos + (rect_size / 2))

        self.putCenteredText(gc, "%d units left" % self.attacking_left, 8, wx.BLACK, wx.NORMAL, border + (rect_size / 2), rect_y_pos + rect_size - 15)
        self.putCenteredText(gc, "%d units left" % self.defending_left, 8, wx.BLACK, wx.NORMAL, width - border - (rect_size / 2), rect_y_pos + rect_size - 15)

        button_width, button_height = self.btn_continue.GetVirtualSize()
        self.btn_continue.SetPosition(((width - button_width) / 2, 135 + (55 - button_height) / 2))

        del dc
        self.Refresh(eraseBackground=False)
        self.Update()

    def _showBattleResult(self):
        if self.IsShown():
            self.Hide()
        else:
            self.showBattleResult(1, 2, 0, 10, 2, 5, 5, 3)
            self.Show()

    def showBattleResult(self, attacking_color, attacking_type, attacking_lost, attacking_left, defending_color, defending_type, defending_lost, defending_left):

        if not self.IsShown():
            self.Show()

        self.attacking_color = attacking_color
        self.attacking_type = attacking_type
        self.attacking_lost = attacking_lost
        self.attacking_left = attacking_left
        self.defending_color = defending_color
        self.defending_type = defending_type
        self.defending_lost = defending_lost
        self.defending_left = defending_left
        self.UpdateDrawingBuffered()

    def putUnitTypeImage(self, type, color, x, y):
        image = wx.Image("%s_%s.png" % (colors.type[color].name, units.type[type].picture), wx.BITMAP_TYPE_ANY)
        wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(image), pos=(x, y))

    def putCenteredText(self, gc, str, fontsize, color, style, x, y):

        font = wx.Font(fontsize, wx.DEFAULT, wx.NORMAL, style)
        gc.SetFont(font, color)
        txtWidth, txtWeight, txtDescent, txtExternalLeading = gc.GetFullTextExtent(str)
        gc.DrawText(str, x - (txtWidth / 2), y - (txtWeight / 2))
