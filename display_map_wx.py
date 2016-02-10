from __future__ import division

import wx
import wx.lib.scrolledpanel
import math
import numpy as np
import terrain
import units
import colors
import maps
import time
import hexlib
import aux_functions
from battleresult import BattleResultPanel
import os
from mappanel import MapPanel
import wx.animate
import battle

from pprint import pprint

# - To move: Click a unit, wait for the movement grid to show up, click a spot, wait for the confirm grid to show up, click the spot again.
#   You'll know said grids when you see them.
# - To attack with artillery: Click a unit, wait for the movement grid to show up, find an enemy unit with a red hexagon around them,
#   click that spot. Wait for the confirm grid to show up and click the spot again.
# - To attack with anything else: Move a unit next to an enemy, and click an enemy unit with a red hexagon around it instead of clicking yourself to confirm.
# - To capture a base: Move any infantry onto a base the way I told you to move. Wait two turns. (You can kill infantry while it's capturing, which stops it)
# - To move infantry onto a base without capture: Instead of confirming by hitting the hex again, hit "do nothing" in the top right corner.
# - To build a unit: Click a base and pick a unit to build. Your economy is in the upper left.
# - To repair a unit: Don't move a unit and hit the repair button in the upper left.
# - To check things: Mouse over a unit to get its stats. That's attack power vs infantry, attack power vs vehicles, and defence power.
#   Mouse over terrain to get its stats. You get the bonuses of the terrain you are standing on. That's attack power for infantry, attack power
#   for vehicles, defence /for/ infantry, and defence /for/ vehicles. Check out the woods. A tank in the plains that attacks a tank in the woods
#   will pwn it. An infantry in the plains that attacks an infantry in the woods will get pwned.

UNSELECTED, MOVING, MOVING_CONFIRM, ATTACKING = range(4)
SHADED, RED_RING, BLUE_RING = 1, 2, 4

moves = np.array([[(-1, -1,), (0, -1), (-1, 0), (1, 0), (-1, 1), (0, 1)], [(0, -1,), (1, -1), (-1, 0), (1, 0), (0, 1), (1, 1)]])
total_calls = 0


class MainFrame(wx.Frame):

    def __init__(self, parent, title):

        wx.Frame.__init__(self, parent, title=title, size=(800, 680))

        self.icon = wx.Icon("icon.ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)

        self.mappanel = MapPanelWrapper(self, maps.maps[0]) # , pos=(200, 200)

        leftpanel = wx.Panel(self, -1, size=(340, -1))
        leftpanel.SetBackgroundColour("WHITE")

        toppanel = wx.Panel(self, -1, size=(-1, 40))
        toppanel.SetBackgroundColour("WHITE")

        #btn_stayhere = wx.Button(toppanel, -1, "stay here")

        self.box = wx.BoxSizer(wx.HORIZONTAL)
        self.box.Add(leftpanel, 0, wx.EXPAND)
        self.box.Add(self.mappanel, 2, wx.EXPAND)

        self.box2 = wx.BoxSizer(wx.VERTICAL)
        self.box2.Add(toppanel, 0, wx.EXPAND)
        self.box2.Add(self.box, 2, wx.EXPAND)

        gif_fname = "loading.gif"
        #gif_fname = "main_loading_black_60.gif"
        gif = wx.animate.GIFAnimationCtrl(leftpanel, -1, gif_fname, pos=(10, 550))
        gif.GetPlayer().UseBackgroundColour(True)

        self.gif = gif
        self.gif.Play()

        self.SetAutoLayout(True)
#        self.SetSizer(self.box)
        self.SetSizer(self.box2)
        self.Layout()

        width_px, height_px = self.mappanel.currentmap.width * 32 + 16, self.mappanel.currentmap.height * 26 + 8
        self.mappanel.Size = width_px, height_px

        self.Bind(wx.EVT_SIZE, self.OnResize)

        if os.path.isfile("upper_bar.png"):
            toppanel.Bind(wx.EVT_ERASE_BACKGROUND, lambda evt, temp="upper_bar.png": self.createBackgroundImage(evt, temp))

        if os.path.isfile("left_bar.png"):
            leftpanel.Bind(wx.EVT_ERASE_BACKGROUND, lambda evt, temp="left_bar.png": self.createBackgroundImage(evt, temp))
        #btn_stayhere.Bind(wx.EVT_LEFT_UP, self.battle_result_panel._showBattleResult)

    #def CallMeLater(self, play=True):
        #if play:
        #    self.gif.Play()
        #else:
        #    self.gif.Stop()

    def createBackgroundImage(self, evt, img):

        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)

        dc.Clear()
        bmp = wx.Bitmap(img)
        dc.DrawBitmap(bmp, 0, 0)

    def OnResize(self, e):
        ## skip this event handler so that SIZE event of superclass is processed too
        e.Skip()


class YesNoDialog(wx.Panel):

    def __init__(self, parent):

        width_px = 250
        height_px = 120

        wx.Panel.__init__(self, parent, style=wx.RAISED_BORDER, size=(width_px, height_px))

        self.SetBackgroundColour(wx.WHITE)

        self.dragging = False
        self.anchor = 0, 0

        self.btn_yes = wx.Button(self, -1, "Yes", (40, 85))
        self.btn_no = wx.Button(self, -1, "No", (150, 85))
        self.btn_yes.SetBackgroundColour('#CCE5FF')
        self.btn_no.SetBackgroundColour('#CCE5FF')

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMove)
        self.Bind(wx.EVT_SHOW, self.OnShow)
        self.btn_yes.Bind(wx.EVT_LEFT_UP, self.OnClick)
        self.btn_no.Bind(wx.EVT_LEFT_UP, self.OnClick)

        self.CentreOnParent()


    def OnPaint(self, e):
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        gc.SetAntialiasMode(True)
        self.putCenteredText(gc, "Stay here?", 10, "#808080", wx.BOLD, self.GetSize()[0] / 2, 30)

    def OnShow(self, e):
        print "OnShow"
        self.CentreOnParent()

    def OnClick(self, e):
        self.Hide()

    def OnLeftDown(self, e):
        self.dragging = True
        self.anchor = e.GetPosition()

    def OnLeftUp(self, e):
        self.dragging = False

    def OnMove(self, e):

        if self.dragging:
            pos = self.GetPosition()[0] - self.anchor[0] + e.GetPosition()[0], self.GetPosition()[1] - self.anchor[1] + e.GetPosition()[1]
            self.SetPosition(pos)

    def putCenteredText(self, gc, str, fontsize, color, style, x, y):
        font = wx.Font(fontsize, wx.DEFAULT, wx.NORMAL, style)
        gc.SetFont(font, color)
        txtWidth, txtWeight, txtDescent, txtExternalLeading = gc.GetFullTextExtent(str)
        gc.DrawText(str, x - (txtWidth / 2), y - (txtWeight / 2))

class MapPanelWrapper(MapPanel):

    def __init__(self, parent, currentmap):

        self.currentmap = currentmap
        self.mode = UNSELECTED

        self.overlays = np.zeros_like(self.currentmap.terrain)
        self.red_counters = np.ones_like(self.currentmap.terrain) * -1

        self.selectedTile = None
        self.sourceTile = None
        self.original_board = None
        self.arrows = []
        self.circles = []

        width_px, height_px = self.currentmap.width * 32 + 16, self.currentmap.height * 26 + 8

        MapPanel.__init__(self, parent, background_tile=wx.Bitmap("logo_background_repeating.png"), size=(width_px, height_px))

        ## create buffer with mask
        self.Buffer = wx.BitmapFromBufferRGBA(width_px, height_px, np.ones((width_px, height_px), np.int32) * int("0xff00ff", 0))

        self.battle_result_panel = BattleResultPanel(self)
        self.battle_result_panel.SetBackgroundColour("WHITE")
        self.battle_result_panel.Hide()

        self.RedrawMap()

        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMove)
        self.Bind(wx.EVT_SIZE, self.OnResize)

    def OnResize(self, e):
        self.battle_result_panel.CentreOnParent()
        super(MapPanelWrapper, self).OnResize(e)

    def RedrawMap(self):

        dc = wx.MemoryDC()
        dc.SelectObject(self.Buffer)

        for (rownum, colnum), value in np.ndenumerate(self.currentmap.tiles):
            if self.currentmap.terrain[rownum, colnum] > 0:
                self.putImage(dc, "%s.png" % terrain.type[self.currentmap.terrain[rownum, colnum]].picture, rownum, colnum)

            if self.overlays[rownum, colnum] & BLUE_RING:
                self.putImage(dc, "selected_border_blue.png", rownum, colnum)

            if self.overlays[rownum, colnum] & RED_RING:
                self.putImage(dc, "selected_border_red.png", rownum, colnum)

        for (rownum, colnum), value in np.ndenumerate(self.currentmap.tiles):
            unit_id, unit_color, unit_health = self.currentmap.board[:, rownum, colnum]
            if unit_id > 0:
                self.putImage(dc, "%s_%s.png" % (colors.type[unit_color].name, units.type[unit_id].picture), rownum, colnum)
                self.putImage(dc, "counter_%s.png" % unit_health, rownum, colnum)

            if self.red_counters[rownum, colnum] > -1:
                self.putImage(dc, "counter_%d_red.png" % self.red_counters[rownum, colnum], rownum, colnum)

            if self.overlays[rownum, colnum] & SHADED:
                self.putImage(dc, "selected_overlay.png", rownum, colnum)

        gc = wx.GraphicsContext.Create(dc)
        gc.SetAntialiasMode(True)
        for x in self.arrows:
            coords1, coords2, width, color = x
            self.drawArrow(gc, coords1, coords2, width, color)

        for coords, text in self.circles:

            x, y = coords

            gc.SetBrush(wx.Brush("#E60000", wx.SOLID))
            #gc.SetPen(wx.TRANSPARENT_PEN)
            gc.SetPen(wx.Pen(wx.BLACK, 1, wx.SOLID))
            gc.DrawRoundedRectangle(x, y, 12, 12, 3)
            font = wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            gc.SetFont(font, wx.WHITE)
            txtWidth, txtWeight, txtDescent, txtExternalLeading = gc.GetFullTextExtent(text)
            gc.DrawText(text, int(x + 6 - (txtWidth / 2)), int(y + 6 - (txtWeight / 2)))
            #gc.DrawText(text, x, y)

        b = dc.GetAsBitmap()
        del dc

        b.SetMaskColour("#FF00FF")
        self.setInnerBitmap(b)

        #self.Refresh(eraseBackground=False)
        self.Update()

    def drawArrow(self, gc, coords1, coords2, width, color):

        c1, c2 = np.array(coords1), np.array(coords2)
        c3 = c1 - c2
        l = math.sqrt(c3[0]**2 + c3[1]**2)

        ## stop 15 pixels short of target
        c2 = c2 + (c3 / l) * 12

        norm = c3 / l * width / 2
        ortho = np.array((c3[1], -c3[0])) / l * width / 2

        gc.SetBrush(wx.Brush(color, wx.SOLID))
        gc.SetPen(wx.Pen("#000000", 1, wx.SOLID))
        #gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawLines([c1 - ortho,
                      c1 + ortho,
                      c2 + ortho + (5 * norm),
                      c2 + 3 * ortho + (5 * norm),
                      c2,
                      c2 - 3 * ortho + (5 * norm),
                      c2 - ortho + (5 * norm),
                      c1 - ortho])


#    def onMouseMove(self, event):
#        self.panel.SetFocus()
#        print event

    def OnMove(self, e):
        row, col = hexlib.pixel_to_hexcoords(self.GetVirtualPosition(e.GetPosition()), self.currentmap.width, self.currentmap.height)
        #row, col = max(0, row), max(0, col)
        height, width = self.currentmap.terrain.shape

        if 0 <= row < height and 0 <= col < width:
            if self.currentmap.terrain[row, col] > 0:
                print "BOARD:", self.currentmap.terrain[row, col]

    def OnLeftUp(self, e):

        if self.battle_result_panel.IsShown():
            return

        row, col = hexlib.pixel_to_hexcoords(self.GetVirtualPosition(e.GetPosition()), self.currentmap.width, self.currentmap.height)

        if self.mode == UNSELECTED:
            unit_type, unit_color, unit_health = self.currentmap.board[:, row, col]

            if not unit_type:
                return

            unit_class = units.type[unit_type].unitclass

            movement_cost = units.unitclass2movementcost[unit_class]
            movecost = movement_cost[self.currentmap.terrain]

            ## do not move to blocked tiles
            movecost[(self.currentmap.board[1] != 0) & (self.currentmap.board[1] != unit_color)] = 888

            zoc = self.currentmap.zoc(unit_class, unit_color)
            #movecost *= - ((zoc * 2) - 1)
            print movecost

            visited = np.ones(self.currentmap.terrain.shape, dtype=np.int64) * -1

            can_move = units.type[unit_type].movementpoints[0]
            t = time.time()
            reachable = aux_functions.find_paths(visited, zoc, movecost, row, col, can_move)
            print (time.time() - t) * 1000.0

            self.overlays[((reachable == -1) & (self.currentmap.terrain > 0)) | (self.currentmap.board[0] > 0)] |= SHADED
            self.overlays[row, col] = BLUE_RING

            self.original_board = self.currentmap.board.copy()

            self.mode = MOVING
            self.selectedTile = (row, col)
            self.sourceTile = (row, col)
            ## flip value
            #overlays[row, col] ^= 1

        elif self.mode == MOVING:

            row, col = hexlib.pixel_to_hexcoords(self.GetVirtualPosition(e.GetPosition()), self.currentmap.width, self.currentmap.height)

            source_row, source_col = self.sourceTile
            print "DISTANCE:", getDistance(row, col, source_row, source_col)

            ## deselect
            if (row, col) == self.selectedTile or self.overlays[row, col] != 0:

                print "self.overlays[row, col] = ", self.overlays[row, col]

                self.selectedTile = None
                self.sourceTile = None
                self.mode = UNSELECTED
                self.arrows = []
                self.overlays[:] = 0
            else:
                # move unit
                source_row, source_col = self.selectedTile
                self.currentmap.board[:, row, col] = self.currentmap.board[:, source_row, source_col]
                self.currentmap.board[:, source_row, source_col] = 0

                self.selectedTile = row, col
                self.mode = MOVING_CONFIRM

                ## shade everything but target tile
                self.overlays[self.currentmap.terrain > 0] |= SHADED
                self.overlays[row, col] = 0

                source_coords = hexlib.hexcoords_to_pixel(self.sourceTile, self.currentmap.width, self.currentmap.height)
                target_coords = hexlib.hexcoords_to_pixel((row, col), self.currentmap.width, self.currentmap.height)

                self.arrows = [(source_coords, target_coords, 5, "#80b3ff")]

        elif self.mode == MOVING_CONFIRM:

            row, col = hexlib.pixel_to_hexcoords(self.GetVirtualPosition(e.GetPosition()), self.currentmap.width, self.currentmap.height)

            ## unselect
            if (row, col) != self.selectedTile:
                ## todo: moved units must be shaded
                self.overlays[:] = 0

                ## move unit back
                source_row, source_col = self.sourceTile
                target_row, target_col = self.selectedTile
                self.currentmap.board[:, source_row, source_col] = self.currentmap.board[:, target_row, target_col]
                self.currentmap.board[:, target_row, target_col] = 0

                self.selectedTile = None
                self.mode = UNSELECTED
                self.arrows = []

            else:
                # move unit
                source_row, source_col = self.sourceTile
                self.moveUnit((source_row, source_col), (row, col))

                self.mode = ATTACKING

                ## attack overlay
                self.overlays[self.currentmap.terrain > 0] |= SHADED

                unit_type, unit_color, unit_health = self.currentmap.board[:, row, col]
                min_range, max_range = units.type[unit_type].attackrange
                attackable = sum([hexlib.rings(self.currentmap.terrain.shape, row, col, x) for x in range(min_range, max_range + 1)])
                self.overlays[(attackable > 0) & (self.currentmap.board[1, :, :] > 0) & (self.currentmap.board[1, :, :] != unit_color)] = RED_RING

        elif self.mode == ATTACKING:

            if self.selectedTile == (row, col):
                dlg = YesNoDialog(self)
                dlg.Show()
                return

            defending_row, defending_col = hexlib.pixel_to_hexcoords(self.GetVirtualPosition(e.GetPosition()), self.currentmap.width, self.currentmap.height)
            attacking_row, attacking_col = self.selectedTile

            defending_type, defending_color, defending_health = self.currentmap.board[:, defending_row, defending_col]
            attacking_type, attacking_color, attacking_health = self.currentmap.board[:, attacking_row, attacking_col]

            attacking_terrain = self.currentmap.terrain[attacking_row, attacking_col]
            defending_terrain = self.currentmap.terrain[defending_row, defending_col]

            #print attacking_type, attacking_color, attacking_health
            #print defending_type, defending_color, defending_health

            attacking_left, defending_left = battle.evaluate(attacking_type, attacking_health, attacking_terrain, defending_type, defending_health, defending_terrain)

            self.red_counters[attacking_row, attacking_col] = attacking_health - attacking_left
            self.red_counters[defending_row, defending_col] = defending_health - defending_left

            #self.circles.append([hexlib.hexcoords_to_pixel((defending_row, defending_col), self.currentmap.width, self.currentmap.height), "-5"])
            #self.circles.append([hexlib.hexcoords_to_pixel((attacking_row, attacking_col), self.currentmap.width, self.currentmap.height), "X"])

            self.battle_result_panel.showBattleResult(attacking_color,
                                                                  attacking_type,
                                                                  attacking_health - attacking_left,
                                                                  attacking_left,
                                                                  defending_color,
                                                                  defending_type,
                                                                  defending_health - defending_left,
                                                                  defending_left)

        self.RedrawMap()
        self.UpdateDrawing()

    def putImage(self, dc, img, row, col):
        png = wx.Bitmap(img)
        target_row, target_col = hexlib.cube_to_oddr(col, 0, row)
        target_col -= math.ceil(self.currentmap.height / 2) - 1

        pixel_x, pixel_y = target_col * 32 + (target_row % 2) * 16, target_row * 26
        b = dc.DrawBitmap(png, pixel_x, pixel_y, True)
        #dc.DrawText("%d,%d" % (row, col), pixel_x, pixel_y)
        return b

    def onExit(self, e):
        self.Close(True)

    def moveUnit(self, (source_row, source_col), (target_row, target_col)):
        for color in self.currentmap.units:
            for u in self.currentmap.units[color]:
                if (u.row, u.col) == (source_row, source_col):
                    u.row, u.col = target_row, target_col

def offset_to_cube(row, col):
    # convert odd-r offset to cube
    x = col - (row - (row & 1)) / 2
    z = row
    y = -x - z

    return x, y, z

def cube_distance(a, b):
    (x1, y1, z1), (x2, y2, z2) = a,b
    return (abs(x1 - x2) + abs(y1 - y2) + abs(z1 - z2)) / 2


def getDistance(source_row, source_col, target_row, target_col):
    a = offset_to_cube(source_row, source_col)
    b = offset_to_cube(target_row, target_col)
    return cube_distance(a, b)

app = wx.App()
mainframe = MainFrame(None, "Weewar")
mainframe.Show()

app.MainLoop()


