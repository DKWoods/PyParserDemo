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

"""This module contains miscellaneous general-purpose dialog classes.  These
are mostly intended to be sub-classed for specific uses."""

__author__ = 'David Woods <dwoods@transana.com>'

import wx
import os
import copy
import string
# Import Transana Globals
import TransanaGlobal
# Import Transana's Images
import TransanaImages

class ErrorDialog(wx.Dialog):
    """Error message dialog to the user."""

    def __init__(self, parent, errmsg, dlgCaption=_("Transana Error"), includeSkipCheck=False):
        # This should be easy, right?  Just use the OS MessageDialog like so:
        # wx.MessageDialog.__init__(self, parent, errmsg, _("Transana Error"), wx.OK | wx.CENTRE | wx.ICON_ERROR)
        # That's all there is to it, right?
        #
        # Yeah, right.  Unfortunately, on Windows, this dialog isn't TRULY modal.  It's modal to the parent window
        # it's called from, but you can still select one of the other Transana Windows and do stuff.  This message
        # can even get hidden behind other windows, and cause all kinds of problems.  According to Robin Dunn,
        # writing my own class to do this is the only solution.  Here goes.

        # Remember if we're supposed to include the checkbox to skip additional messages
        self.includeSkipCheck = includeSkipCheck

        # Create a Dialog box
        wx.Dialog.__init__(self, parent, -1, dlgCaption, size=(350, 150), style=wx.CAPTION | wx.CLOSE_BOX | wx.STAY_ON_TOP)
        # Set "Window Variant" to small only for Mac to make fonts match better
        if "__WXMAC__" in wx.PlatformInfo:
            self.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)

        # Create Vertical and Horizontal Sizers
        box = wx.BoxSizer(wx.VERTICAL)
        box2 = wx.BoxSizer(wx.HORIZONTAL)

        # Display the Error graphic in the dialog box
        graphic = wx.StaticBitmap(self, -1, TransanaImages.ArtProv_ERROR.GetBitmap())
        # Add the graphic to the Sizers
        box2.Add(graphic, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 10)

        # Display the error message in the dialog box
        message = wx.StaticText(self, -1, errmsg)
        # Add the error message to the Sizers
        box2.Add(message, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        box.Add(box2, 0, wx.EXPAND)

        # If we should add the "Skip Further messages" checkbox ...
        if self.includeSkipCheck:
            # ... then add the checkbox to the dialog
            self.skipCheck = wx.CheckBox(self, -1, _('Do not show this message again'))
            # ... and add the checkbox to the Sizers
            box.Add(self.skipCheck, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        # Add an OK button
        btnOK = wx.Button(self, wx.ID_OK, _("OK"))
        # Add the OK button to the Sizers
        box.Add(btnOK, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        # Make the OK button the default
        self.SetDefaultItem(btnOK)

        # Turn on Auto Layout
        self.SetAutoLayout(True)
        # Set the form sizer
        self.SetSizer(box)
        # Set the form size
        self.Fit()
        # Perform the Layout
        self.Layout()
        # Center the dialog on the screen
#        self.CentreOnScreen()
        # That's not working.  Let's try this ...
        TransanaGlobal.CenterOnPrimary(self)

    def GetSkipCheck(self):
        """ Provide the value of the Skip Checkbox """
        # If the checkbox is displayed ...
        if self.includeSkipCheck:
            # ... return the value of the checkbox
            return self.skipCheck.GetValue()
        # If the checkbox is NOT displayed ...
        else:
            # ... then indicate that it is NOT checked
            return False


class InfoDialog(wx.MessageDialog):
    """ Information message dialog to the user. """

    def __init__(self, parent, msg, dlgTitle = _("Transana Information")):
        # This should be easy, right?  Just use the OS MessageDialog like so:
        # wx.MessageDialog.__init__(self, parent, msg, _("Transana Information"), \
        #                     wx.OK | wx.CENTRE | wx.ICON_INFORMATION)
        # That's all there is to it, right?
        #
        # Yeah, right.  Unfortunately, on Windows, this dialog isn't TRULY modal.  It's modal to the parent window
        # it's called from, but you can still select one of the other Transana Windows and do stuff.  This message
        # can even get hidden behind other windows, and cause all kinds of problems.  According to Robin Dunn,
        # writing my own class to do this is the only solution.  Here goes.

        # Create a wxDialog
        wx.Dialog.__init__(self, parent, -1, dlgTitle, size=(350, 150), style=wx.CAPTION | wx.CLOSE_BOX | wx.STAY_ON_TOP)

        # Create Vertical and Horizontal Sizers
        box = wx.BoxSizer(wx.VERTICAL)
        box2 = wx.BoxSizer(wx.HORIZONTAL)

        # Display the Information graphic in the dialog box
        graphic = wx.StaticBitmap(self, -1, TransanaImages.ArtProv_INFORMATION.GetBitmap())
        # Add the graphic to the Sizers
        box2.Add(graphic, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 10)
        
        # Display the error message in the dialog box
        message = wx.StaticText(self, -1, msg)

        # Add the information message to the Sizers
        box2.Add(message, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        box.Add(box2, 0, wx.EXPAND)

        # Add an OK button
        btnOK = wx.Button(self, wx.ID_OK, _("OK"))
        # Add the OK button to the Sizers
        box.Add(btnOK, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        # Make the OK button the default
        self.SetDefaultItem(btnOK)

        # Turn on Auto Layout
        self.SetAutoLayout(True)
        # Set the form sizer
        self.SetSizer(box)
        # Set the form size
        self.Fit()
        # Perform the Layout
        self.Layout()
        # Center the dialog on the screen
#        self.CentreOnScreen()
        # That's not working.  Let's try this ...
        TransanaGlobal.CenterOnPrimary(self)


class PopupDialog(wx.Dialog):
    """ A popup dialog for temporary user messages """

    def __init__(self, parent, title, msg):
        # Create a dialog
        wx.Dialog.__init__(self, parent, -1, title, size=(350, 150), style=wx.CAPTION | wx.STAY_ON_TOP)
        # Add sizers
        box = wx.BoxSizer(wx.VERTICAL)
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        # Add an Info graphic
        graphic = wx.StaticBitmap(self, -1, TransanaImages.ArtProv_INFORMATION.GetBitmap())
        box2.Add(graphic, 0, wx.EXPAND | wx.ALL, 10)
        # Add the message
        message = wx.StaticText(self, -1, msg)
        box2.Add(message, 0, wx.EXPAND | wx.ALL, 10)
        box.Add(box2, 0, wx.EXPAND)
        # Handle layout
        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Fit()
        self.Layout()
#        self.CentreOnScreen()
        TransanaGlobal.CenterOnPrimary(self)
        # Display the Dialog
        self.Show()
        # Make sure the screen gets fully drawn before continuing.  (Needed for SAVE)
        try:
            wx.Yield()
        except:
            pass

