from __future__ import division

import wx
import os
from wx.lib.scrolledpanel import ScrolledPanel
#import math
#import numpy as np
#import terrain
#import units
#import colors
#import maps
#import time
#import hexlib
#import aux_functions
#from battleresult import BattleResultPanel
#from mappanel import MapPanel
#import wx.animate
#import battle


class MainFrame(wx.Frame):

    def __init__(self, parent, title):

        wx.Frame.__init__(self, parent, title=title, size=(800, 680))

        if os.path.isfile("icon.ico"):
            self.icon = wx.Icon("icon.ico", wx.BITMAP_TYPE_ICO)
            self.SetIcon(self.icon)

        self.mappanel = ScrolledPanel(self, -1, style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER, name="mappanel")
        self.mappanel.SetAutoLayout(1)
        self.mappanel.SetupScrolling()

        leftpanel = wx.Panel(self, -1, size=(340, -1))
        leftpanel.SetBackgroundColour("RED")

        toppanel = wx.Panel(self, -1, size=(-1, 40))
        toppanel.SetBackgroundColour("GREEN")

        self.box = wx.BoxSizer(wx.HORIZONTAL)
        self.box.Add(leftpanel, 0, wx.EXPAND)
        self.box.Add(self.mappanel, 2, wx.EXPAND)

        self.box2 = wx.BoxSizer(wx.VERTICAL)
        self.box2.Add(toppanel, 0, wx.EXPAND)
        self.box2.Add(self.box, 2, wx.EXPAND)

        #self.SetAutoLayout(True)
        self.SetSizer(self.box2)
        #self.Layout()

        width_px, height_px = 500, 500
        #width_px, height_px = self.mappanel.currentmap.width * 32 + 16, self.mappanel.currentmap.height * 26 + 8
        self.mappanel.Size = width_px, height_px

        self.Bind(wx.EVT_SIZE, self.OnResize)

        if os.path.isfile("upper_bar.png"):
            toppanel.Bind(wx.EVT_ERASE_BACKGROUND, lambda evt, temp="upper_bar.png": self.createBackgroundImage(evt, temp))

        if os.path.isfile("left_bar.png"):
            leftpanel.Bind(wx.EVT_ERASE_BACKGROUND, lambda evt, temp="left_bar.png": self.createBackgroundImage(evt, temp))

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

app = wx.App()
mainframe = MainFrame(None, "Weewar")
mainframe.Show()

app.MainLoop()


