from __future__ import division

import wx
import random
import wx.lib.scrolledpanel
import re
import math
import numpy as np
import sys
import terrain
import units
import colors
import maps
import time
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

UNSELECTED, MOVING, ATTACKING = range(3)

moves = np.array([[(-1, -1,), (0, -1), (-1, 0), (1, 0), (-1, 1), (0, 1)], [(0, -1,), (1, -1), (-1, 0), (1, 0), (0, 1), (1, 1)]])
total_calls = 0


class MapPanel(wx.lib.scrolledpanel.ScrolledPanel):

    def __init__(self, parent, currentmap):

        self.currentmap = currentmap
        self.mode = UNSELECTED
        self.overlays = np.empty_like(self.currentmap.terrain)
        self.selectedTile = None

        width_px, height_px = self.currentmap.width * 32 + 16, self.currentmap.height * 26 + 8
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, size=(width_px, height_px))
        self.SetupScrolling()

        Size = self.ClientSize
        self._Buffer = wx.EmptyBitmap(*Size)
        self.UpdateDrawingBuffered()

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)

    def OnPaint(self, e):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self._Buffer, 0, 0)

    def UpdateDrawingBuffered(self):

        dc = wx.MemoryDC()
        dc.SelectObject(self._Buffer)
        dc.Clear()

        for (rownum, colnum), value in np.ndenumerate(self.currentmap.tiles):
            if self.currentmap.terrain[rownum, colnum] > 0:
                self.putImage(dc, "%s.png" % terrain.type[self.currentmap.terrain[rownum, colnum]].picture, rownum, colnum)

            if self.overlays[rownum, colnum] == 1:
                self.putImage(dc, "selected_border_pink.png", rownum, colnum)

        for rownum, row in enumerate(self.currentmap.board.swapaxes(0, 1).swapaxes(1, 2)):
            for colnum, (unit_id, unit_color, unit_health) in enumerate(row):
                if unit_id > 0:
                    self.putImage(dc, "%s_%s.png" % (colors.type[unit_color].name, units.type[unit_id].picture), rownum, colnum)
                    self.putImage(dc, "counter_%s.png" % unit_health, rownum, colnum)

                if self.overlays[rownum, colnum] == 2:
                    self.putImage(dc, "selected_overlay.png", rownum, colnum)

        del dc
        self.Refresh(eraseBackground=False)
        self.Update()

#    def onMouseMove(self, event):
#        self.panel.SetFocus()
#        print event

    def OnLeftUp(self, e):

        row, col = getTileCoordinatesFromCursor(e.GetPosition())

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

            shortestpath = np.ones(self.currentmap.terrain.shape, dtype=np.int64) * -1

            t = time.time()
            reachable = find_paths(shortestpath, zoc, movecost, row, col, units.type[unit_type].movementpoints)
            print (time.time() - t) * 1000.0

            self.overlays[((reachable == -1) & (self.currentmap.terrain > 0)) | (self.currentmap.board[0] > 0)] = 2
            self.overlays[row, col] = 0

            self.mode = MOVING
            self.selectedTile = (row, col)
            ## flip value
            #overlays[row, col] ^= 1

        elif self.mode == MOVING:

            row, col = getTileCoordinatesFromCursor(e.GetPosition())

            ## unselect
            if (row, col) == self.selectedTile or self.overlays[row, col] != 0:
                self.selectedTile = None
                self.mode = UNSELECTED
                self.overlays[:] = 0
            else:
                # move unit
                source_row, source_col = self.selectedTile
                self.currentmap.board[:, row, col] = self.currentmap.board[:, source_row, source_col]
                self.currentmap.board[:, source_row, source_col] = 0
                self.selectedTile = row, col
                #self.moveUnit((source_row, source_col), (row, col))

                #self.selectedTile = None
                #self.mode = UNSELECTED
                #self.overlays[:] = 0

        self.UpdateDrawingBuffered()

    def getDistance(self,(source_row, source_col), (target_row, target_col)):
        #function offset_distance(a, b):
        #    var ac = offset_to_cube(a)
        #    var bc = offset_to_cube(b)
        #    return cube_distance(ac, bc)
        pass

    def putImage(self, dc, img, row, col):
        png = wx.Bitmap(img)
        return dc.DrawBitmap(png, col * 32 + (row % 2) * 16, row * 26, True)

    def onExit(self, e):
        self.Close(True)

    def moveUnit(self, (source_row, source_col), (target_row, target_col)):
        for color in self.currentmap.units:
            for u in self.currentmap.units[color]:
                if (u.row, u.col) == (source_row, source_col):
                    u.row, u.col = target_row, target_col

class MainFrame(wx.Frame):

    def __init__(self, parent, title):

        #First retrieve the screen size of the device
        #screenSize = wx.DisplaySize()
        #screenWidth = screenSize[0]
        #screenHeight = screenSize[1]

        wx.Frame.__init__(self, parent, title=title, size=(600, 600))
        self.panel = MapPanel(self, maps.maps[0]) # , pos=(200, 200)


#@profile
def find_paths(shortestpath, zoc, movecost, start_row, start_col, points_left):

    global total_calls
    total_calls += 1

    shortestpath[start_row, start_col] = points_left
    if points_left == 0:
        return shortestpath

    max_col, max_row = movecost.shape

    moves = (((-1, -1,), (0, -1), (-1, 0), (1, 0), (-1, 1), (0, 1)), ((0, -1,), (1, -1), (-1, 0), (1, 0), (0, 1), (1, 1)))
    possible_moves = moves[start_row % 2]

    for x, y in possible_moves:
        target_col, target_row = start_col + x, start_row + y
        if 0 <= target_row < max_row and 0 <= target_col < max_col:

            p = points_left - movecost[target_row, target_col]
            if p > 0 and zoc[target_row, target_col] == 1:
                p = 0

            ## been there with more points left using other path
            if shortestpath[target_row, target_col] >= p:
                continue

            if p >= 0:
                find_paths(shortestpath, zoc, movecost, target_row, target_col, p)
    return shortestpath


def getTileCoordinatesFromCursor(coords):

    x, y = coords
    row = int(y / 26)
    ymod = y % 26

    ## "between rows"
    if ymod <= 8:
        xmod = (x - (row % 2) * 16) % 32
        if (2 * (8 - ymod)) > (16 - abs(xmod - 16)):
            row -= 1

    col = int((x - (row % 2) * 16) / 32)
    return row, col

app = wx.App()
mainframe = MainFrame(None, "Weewar")
mainframe.Show()

app.MainLoop()


