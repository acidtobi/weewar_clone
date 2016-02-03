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

        #First retrieve the screen size of the device
        #screenSize = wx.DisplaySize()
        #screenWidth = screenSize[0]
        #screenHeight = screenSize[1]

        wx.Frame.__init__(self, parent, title=title, size=(800, 650))

        self._mappanel = wx.Panel(self, -1)
        self.mappanel = MapPanel(self, maps.maps[0]) # , pos=(200, 200)

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

        self.battle_result_panel = BattleResultPanel(self.mappanel)
        self.battle_result_panel.SetBackgroundColour("WHITE")
        self.battle_result_panel.Hide()

        self.SetAutoLayout(True)
#        self.SetSizer(self.box)
        self.SetSizer(self.box2)
        self.Layout()

        width_px, height_px = self.mappanel.currentmap.width * 32 + 16, self.mappanel.currentmap.height * 26 + 8
        self._mappanel.Size = width_px, height_px
        self.mappanel.Size = width_px, height_px

        self.Bind(wx.EVT_SIZE, self.printSize)
        toppanel.Bind(wx.EVT_ERASE_BACKGROUND, lambda evt, temp="upper_bar.png": self.createBackgroundImage(evt, temp))
        leftpanel.Bind(wx.EVT_ERASE_BACKGROUND, lambda evt, temp="left_bar.png": self.createBackgroundImage(evt, temp))
        #btn_stayhere.Bind(wx.EVT_LEFT_UP, self.battle_result_panel._showBattleResult)

    def createBackgroundImage(self, evt, img):

        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)

        dc.Clear()
        bmp = wx.Bitmap(img)
        dc.DrawBitmap(bmp, 0, 0)

    def printSize(self, e):
        e.Skip()
        self.battle_result_panel.CentreOnParent()
        self.mappanel.OnResize(e)
        print [(x, x.GetSize()) for x in self.box.Children]


class MapPanel(wx.lib.scrolledpanel.ScrolledPanel):

    def __init__(self, parent, currentmap):

        self.currentmap = currentmap
        self.mode = UNSELECTED
        self.overlays = np.zeros_like(self.currentmap.terrain)
        self.selectedTile = None
        self.sourceTile = None
        self.original_board = None
        self.arrows = []

        width_px, height_px = self.currentmap.width * 32 + 16, self.currentmap.height * 26 + 8
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, size=(width_px, height_px))
        self.SetBackgroundColour("#F0F0F0")
        self.SetupScrolling()
        self.SetScrollRate(1,1)

        #size = self.ClientSize
        self._Buffer = wx.EmptyBitmap(width_px+500, height_px+500)
        self.UpdateDrawingBuffered()

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMove)

    def OnPaint(self, e):

        dc = wx.PaintDC(self)
        #dc.Clear()

        x, y = self.CalcScrolledPosition((0, 0))
        dc.DrawBitmap(self._Buffer, x, y)

    def OnResize(self, e):

        self_width, self_height = self._Buffer.Size
        sizer_width, sizer_height = self.GetParent().Size

        posx = max(0, (sizer_width - self_width) / 2)
        posy = max(0, (sizer_height - self_height) / 2)

        self_width = min(self_width, sizer_width)
        self_height = min(self_height, sizer_height)
        #self.SetSize((self_width, self_height))

        self.SetVirtualSize((600, 400))

        self.SetPosition((posx, posy))

    def UpdateDrawingBuffered(self):

        dc = wx.MemoryDC()
        dc.SelectObject(self._Buffer)
        dc.Clear()

        dc.SetBrush(wx.Brush("#F0F0F0", wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        width, height = self.Size
        dc.DrawRectangle(0, 0, width, height)

        for rownum in range(-15, 25):
            for colnum in range(-15, 25):
                self.putImage(dc, "logo_background.png", rownum, colnum)

        for (rownum, colnum), value in np.ndenumerate(self.currentmap.tiles):
            if self.currentmap.terrain[rownum, colnum] > 0:
                self.putImage(dc, "%s.png" % terrain.type[self.currentmap.terrain[rownum, colnum]].picture, rownum, colnum)

            if self.overlays[rownum, colnum] & BLUE_RING:
                self.putImage(dc, "selected_border_blue.png", rownum, colnum)

            if self.overlays[rownum, colnum] & RED_RING:
                self.putImage(dc, "selected_border_red.png", rownum, colnum)

        for (rownum, colnum), value in np.ndenumerate(self.currentmap.tiles):
            print (rownum, colnum), value
            unit_id, unit_color, unit_health = self.currentmap.board[:, rownum, colnum]
            if unit_id > 0:
                self.putImage(dc, "%s_%s.png" % (colors.type[unit_color].name, units.type[unit_id].picture), rownum, colnum)
                self.putImage(dc, "counter_%s.png" % unit_health, rownum, colnum)

            if self.overlays[rownum, colnum] & SHADED:
                self.putImage(dc, "selected_overlay.png", rownum, colnum)

        gc = wx.GraphicsContext.Create(dc)
        gc.SetAntialiasMode(True)
        for x in self.arrows:
            print x
            coords1, coords2, width, color = x
            self.drawArrow(gc, coords1, coords2, width, color)

        #self.showBattleResult(gc, 1, 2, 0, 10, 2, 5, 5, 3)

        del dc
        self.Refresh(eraseBackground=False)
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

        font = wx.Font(24, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        gc.SetFont(font, wx.BLACK)

#    def onMouseMove(self, event):
#        self.panel.SetFocus()
#        print event

    def OnMove(self, e):

        row, col = hexlib.pixel_to_hexcoords(e.GetPosition(), self.currentmap.width, self.currentmap.height)
        print row, col

    def OnLeftUp(self, e):

        row, col = hexlib.pixel_to_hexcoords(e.GetPosition(), self.currentmap.width, self.currentmap.height)

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

            row, col = hexlib.pixel_to_hexcoords(e.GetPosition(), self.currentmap.width, self.currentmap.height)

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

            row, col = hexlib.pixel_to_hexcoords(e.GetPosition(), self.currentmap.width, self.currentmap.height)

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

            defending_row, defending_col = hexlib.pixel_to_hexcoords(e.GetPosition(), self.currentmap.width, self.currentmap.height)
            attacking_row, attacking_col = self.selectedTile

            defending_type, defending_color, defending_health = self.currentmap.board[:, defending_row, defending_col]
            attacking_type, attacking_color, attacking_health = self.currentmap.board[:, attacking_row, attacking_col]

            print attacking_type, attacking_color, attacking_health
            print defending_type, defending_color, defending_health

            defending_left = defending_health - 1
            attacking_left = attacking_health - 1

            self.GetParent().battle_result_panel.showBattleResult(attacking_color, attacking_type, 1, attacking_left, defending_color, defending_type, 1, defending_left)

        self.UpdateDrawingBuffered()

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


