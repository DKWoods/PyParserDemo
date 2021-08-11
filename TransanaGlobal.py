# Copyright (C) 2003 - 2021  Spurgeon Woods LLC
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of version 2 of the GNU General Public License as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#

"""This module contains Transana's global variables."""

__author__ = 'David Woods <dwoods@transana.com>'

# Import wxPython
import wx
# import Python's os and sys modules
import os
import sys

# We need to know what directory the program is running from.  We use this in several
# places in the program to be able to find things like images and help files.
# This has emerged as the "preferred" cross-platform method on the wxPython-users list.
programDir = os.path.abspath(sys.path[0])
# Okay, that doesn't work with wxversion, which adds to the path.  Here's the fix, I hope.
# This should over-ride the programDir with the first value that contains Transana in the path.
for path in sys.path:
    if 'transana' in path.lower():
        programDir = path
        break
if os.path.isfile(programDir):
    programDir = os.path.dirname(programDir)

# If we've done a build on the Mac, we need to adjust the path!!
if hasattr(sys, "frozen") and ('wxMac' in wx.PlatformInfo):
    # Split the path into it's element directories
    pathElements = programDir.split(os.sep)
    # Initialize the Program Directory
    programDir = ''
    # Iterate through the path elements, skipping the blank firt one and the last two, which get added in the
    # build process
    for element in pathElements[1:-2]:
        # Add a path separator and the path element
        programDir += os.sep + element


# We want enough colors for TEXT, but not too many.  This list seems about right to me.  I doubt my color names are standard.
# But then, I'm often perplexed by the colors that are included and excluded by most programs.  (Excel for example.)
# Each entry is made up of a color name and a tuple of the RGB values for the color.
transana_textColorList = [('Black',             (  0,   0,   0)),
                          ('Dark Blue',         (  0,   0, 128)),
                          ('Blue',              (  0,   0, 255)),
                          ('Light Blue',        (  0, 128, 255)),
                          ('Lavender',          (128, 128, 255)),
                          ('Cyan',              (  0, 255, 255)),
                          ('Light Aqua',        (128, 255, 255)),
                          ('Blue Green',        (  0, 128, 128)),
                          ('Dark Slate Gray',   ( 47,  79,  79)),
                          ('Dark Green',        (  0, 128,   0)),
                          ('Green Blue',        (  0, 255, 128)),
                          ('Green',             (  0, 255,   0)),
                          ('Chartreuse',        (128, 255,   0)),
                          ('Light Green',       (128, 255, 128)),
                          ('Olive',             (128, 128,   0)),
                          ('Sienna',            (142, 107,  35)),
                          ('Gray',              (128, 128, 128)),
                          ('Light Gray',        (192, 192, 192)),
                          ('Purple',            (128,   0, 255)),
                          ('Light Purple',      (176,  0, 255)),
                          ('Dark Purple',       (128,   0, 128)),
                          ('Maroon',            (128,   0,   0)),
                          ('Indian Red',        ( 79,  47,  47)),
                          ('Violet Red',        (204,  50, 153)),
                          ('Magenta',           (255,   0, 255)),
                          ('Light Fuchsia',     (255, 128, 255)),
                          ('Rose',              (255,   0, 128)),
                          ('Red',               (255,   0,   0)),
                          ('Red Orange',        (204,  50,  50)),
                          ('Salmon',            (255, 128, 128)),
                          ('Orange',            (255, 128,   0)),
                          ('Yellow',            (255, 255,   0)),  
                          ('Light Yellow',      (255, 255, 128)),  
                          ('Goldenrod',         (219, 219, 112)),
                          ('White',             (255, 255, 255))]

def CenterOnPrimary(win):
    """ a wxWindow is passed in as the win parameter.
        This window should be centered on the primary monitor used by Transana on a multi-monitor system
        rather than on the default monitor. """

    # Get the Size and Position for the PRIMARY screen
    (x1, y1, w1, h1) = wx.Display(1).GetClientArea()
    # Get the original Size and Position for the window
    (x2, y2, w2, h2) = win.GetRect()

    # I'm seeing some WEIRD values here with wxPython 2.9.??.  Let's try to correct for that.
    # If the left value is wider than the whole screen ...
    if (w2 > w1) or (w2 < 0):
        # ... set it to 50% of the screen width.
        w2 = int(w1 * 0.50)

    # If the height value is taller than the whole screen ...
    if (h2 > h1) or (h2 < 0):
        # ... set it to 50% of the screen height.
        h2 = int(h1 * 0.50)

    # Position the Window on the center of the Primary Screen
    win.SetPosition((x1 + ((w1 - w2) / 2), y1 + ((h1 - h2) / 2)))


def GetImage(imagename):
    if configData.LayoutDirection == wx.Layout_RightToLeft:
        img = imagename.GetImage().Mirror()
        return img.ConvertToBitmap()
    else:
        return imagename.GetBitmap()
