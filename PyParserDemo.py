# -*- coding: utf8 -*-
# Copyright (C) 2009-2021  Spurgeon Woods LLC
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

""" A demonstration application for a wxPython RichTextCtrl-based Rich Format File Parser """

__author__ = 'David Woods <dwoods@transana.com>'

# Import wxPython, its HTML controls, its RichText controls, and embedded image handling
import wx

if __name__ == '__main__':
    # This module expects i18n.  Enable it here.
    __builtins__._ = wx.GetTranslation

import wx.html
import wx.richtext as richtext
from wx.lib.embeddedimage import PyEmbeddedImage

# If we're using wx 2.8 instead of wx 2.9 ...
if (wx.VERSION[0] == 2) and (wx.VERSION[1] < 9):
    # Add these variables to the wx module.  (These were moved from richtext to wx in 2.9)
    wx.TEXT_ATTR_LINE_SPACING_HALF = richtext.TEXT_ATTR_LINE_SPACING_HALF
    wx.TEXT_ATTR_LINE_SPACING_NORMAL = richtext.TEXT_ATTR_LINE_SPACING_NORMAL
    wx.TEXT_ATTR_LINE_SPACING_TWICE = richtext.TEXT_ATTR_LINE_SPACING_TWICE

# Import Python modules io, os, sys, and traceback
import io
import os, sys, traceback

# We have to fake the configuration data here so the Format Dialogs will work
import TransanaGlobal
class configData(object):
    formatUnits = 'in'
    def SaveConfiguration(self):
        pass

TransanaGlobal.configData = configData()

# import the PyRTFParser
import PyRTFParser
# import the PyDocxParser
import PyDocxParser
# Import the Format Dialog
import FormatDialog

# Some global configuration options:
# If you don't have Chinese character support on your computer, set this to False
INCLUDE_CHINESE = True
# This component was originally built for integration into Transana, which has a
# couple of special requirements.  This allows the Transana-specific code to be turned off.
INCLUDE_TIMECODES = PyRTFParser.IN_TRANSANA
TIMECODE_CHAR =  '\xa4'  # unicode('\xc2\xa4', 'utf-8')
# This allows support for bulleted and numbered lists to be enabled or disabled.
# Bulleted and numbered lists are not yet fully supported.
INCLUDE_LISTS = False

class MainWindow(wx.Frame):
    """ This window displays and manipulates a wxRichTextCtrl. """
    def __init__(self,parent,id,title):
        # Create the main Demo window
        wx.Frame.__init__(self,parent,-1, title, size = (800,800), style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE)
        self.SetBackgroundColour(wx.WHITE)
        self.CreateStatusBar()

        # Create a MenuBar
        menuBar = wx.MenuBar()
        # Build a Menu Object to go into the Menu Bar
        menu1 = wx.Menu()
        # Populate the File menu
        MENU_FILE_NEW = wx.NewIdRef()
        menu1.Append(MENU_FILE_NEW, "&New", "Clear the text control")
        menu1.AppendSeparator()
      
        MENU_FILE_LOAD_PROG = wx.NewIdRef()
        menu1.Append(MENU_FILE_LOAD_PROG, "Populate &Programmatically", "Populate the text control programmatically")
        menu1.AppendSeparator()

        MENU_FILE_LOAD_XML = wx.NewIdRef()
        menu1.Append(MENU_FILE_LOAD_XML, "Load from XML", "Populate the text control from a previously saved XML file")
        MENU_FILE_LOAD_RTF = wx.NewIdRef()
        menu1.Append(MENU_FILE_LOAD_RTF, "Load from RTF", "Populate the text control from a previously saved RTF file")
        MENU_FILE_LOAD_DOCX = wx.NewIdRef()
        menu1.Append(MENU_FILE_LOAD_DOCX, "Load from DOCX", "Populate the text control from a previously saved DOCx file")
        menu1.AppendSeparator()

        MENU_FILE_DISPLAY_HTML = wx.NewIdRef()
        menu1.Append(MENU_FILE_DISPLAY_HTML, "Display in HTML Window", "Display the text control contents in a pop-up HTML Window")
        menu1.AppendSeparator()

        MENU_FILE_SAVE_XML = wx.NewIdRef()
        menu1.Append(MENU_FILE_SAVE_XML, "Save to XML", "Save the text control contents to an XML file")
        MENU_FILE_SAVE_RTF = wx.NewIdRef()
        menu1.Append(MENU_FILE_SAVE_RTF, "Save to RTF", "Save the text control contents to an RTF file")
        MENU_FILE_SAVE_DOCX = wx.NewIdRef()
        menu1.Append(MENU_FILE_SAVE_DOCX, "Save to DOCX", "Save the text control contents to a DOCx file")
        MENU_FILE_SAVE_HTML = wx.NewIdRef()
        menu1.Append(MENU_FILE_SAVE_HTML, "Save to HTML", "Save the text control contents to an HTML file")
        MENU_FILE_SAVE_TXT = wx.NewIdRef()
        menu1.Append(MENU_FILE_SAVE_TXT, "Save to TXT", "Save the text control contents to a TXT (plain text) file")
        menu1.AppendSeparator()

        MENU_FILE_PRINTPREVIEW = wx.NewIdRef()
        menu1.Append(MENU_FILE_PRINTPREVIEW, "Print Preview", "Preview the printed contents of the control")
        MENU_FILE_PRINT = wx.NewIdRef()
        menu1.Append(MENU_FILE_PRINT, "Print", "Print the contents of the control")
        menu1.AppendSeparator()

        MENU_FILE_EXIT = wx.NewIdRef()
        menu1.Append(MENU_FILE_EXIT, "E&xit", "Quit Application")
        # Place the File Menu in the Menu Bar
        menuBar.Append(menu1, "&File")

        # Create and populate the Edit menu
        menu2 = wx.Menu()
        MENU_EDIT_CUT = wx.NewIdRef()
        menu2.Append(MENU_EDIT_CUT, "Cu&t", "Cut RTF Formatted Text")
        MENU_EDIT_COPY = wx.NewIdRef()
        menu2.Append(MENU_EDIT_COPY, "&Copy", "Copy RTF Formatted Text")
        MENU_EDIT_PASTE = wx.NewIdRef()
        menu2.Append(MENU_EDIT_PASTE, "&Paste", "Paste RTF Formatted Text")
        menu2.AppendSeparator()
        self.MENU_EDIT_FORMAT_FONT = wx.NewIdRef()
        menu2.Append(self.MENU_EDIT_FORMAT_FONT, "Format &Font", "Format Font Properties")
        self.MENU_EDIT_FORMAT_PARAGRAPH = wx.NewIdRef()
        menu2.Append(self.MENU_EDIT_FORMAT_PARAGRAPH, "Format P&aragraph", "Format Paragraph Properties")
        self.MENU_EDIT_FORMAT_TABS = wx.NewIdRef()
        menu2.Append(self.MENU_EDIT_FORMAT_TABS, "Format Tab&s", "Format Tabs")
        # Place the Edit Menu in the Menu Bar
        menuBar.Append(menu2, "&Edit")
        # Set the window's menu
        self.SetMenuBar(menuBar)
      
        #Define Events for the File Menu
        self.Bind(wx.EVT_MENU, self.OnClear, id=MENU_FILE_NEW)
        self.Bind(wx.EVT_MENU, self.OnLoadProg, id=MENU_FILE_LOAD_PROG)
        self.Bind(wx.EVT_MENU, self.OnLoadXML, id=MENU_FILE_LOAD_XML)
        self.Bind(wx.EVT_MENU, self.OnLoadRTF, id=MENU_FILE_LOAD_RTF)
        self.Bind(wx.EVT_MENU, self.OnLoadDocx, id=MENU_FILE_LOAD_DOCX)
        self.Bind(wx.EVT_MENU, self.OnDisplayHTML, id=MENU_FILE_DISPLAY_HTML)
        self.Bind(wx.EVT_MENU, self.OnSaveXML, id=MENU_FILE_SAVE_XML)
        self.Bind(wx.EVT_MENU, self.OnSaveRTF, id=MENU_FILE_SAVE_RTF)
        self.Bind(wx.EVT_MENU, self.OnSaveDocx, id=MENU_FILE_SAVE_DOCX)
        self.Bind(wx.EVT_MENU, self.OnSaveHTML, id=MENU_FILE_SAVE_HTML)
        self.Bind(wx.EVT_MENU, self.OnSaveTXT, id=MENU_FILE_SAVE_TXT)
        self.Bind(wx.EVT_MENU, self.OnPrintPreview, id=MENU_FILE_PRINTPREVIEW)
        self.Bind(wx.EVT_MENU, self.OnPrint, id=MENU_FILE_PRINT)
        self.Bind(wx.EVT_MENU, self.OnClose, id=MENU_FILE_EXIT)

        # Define Events for the Edit menu
        self.Bind(wx.EVT_MENU, self.OnCutCopy, id=MENU_EDIT_CUT)
        self.Bind(wx.EVT_MENU, self.OnCutCopy, id=MENU_EDIT_COPY)
        self.Bind(wx.EVT_MENU, self.OnPaste, id=MENU_EDIT_PASTE)
        self.Bind(wx.EVT_MENU, self.OnFormat, id=self.MENU_EDIT_FORMAT_FONT)
        self.Bind(wx.EVT_MENU, self.OnFormat, id=self.MENU_EDIT_FORMAT_PARAGRAPH)
        self.Bind(wx.EVT_MENU, self.OnFormat, id=self.MENU_EDIT_FORMAT_TABS)

        # Define the main Sizer
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        # Define the RichTextCtrl
        self.txtCtrl = richtext.RichTextCtrl(self, -1, style=wx.VSCROLL|wx.HSCROLL)
        mainSizer.Add(self.txtCtrl, 5, wx.EXPAND | wx.ALL, 5)
        # If we're including Transana Time Codes, we need custom methods for handling key presses and
        # the left mouse up event
        if INCLUDE_TIMECODES:
            self.txtCtrl.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
            self.txtCtrl.Bind(wx.EVT_CHAR, self.OnKey)
            self.txtCtrl.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
            self.txtCtrl.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        # Bind a hyperlink event handler
        self.txtCtrl.Bind(wx.EVT_TEXT_URL, self.OnURL)

        # Override the RichTextCtrl's Cut, Copy, and Paste methods so that we can support formatted text copy/paste
        self.txtCtrl.Bind(wx.EVT_MENU, self.OnCutCopy, id=wx.ID_CUT)
        self.txtCtrl.Bind(wx.EVT_MENU, self.OnCutCopy, id=wx.ID_COPY)
        self.txtCtrl.Bind(wx.EVT_MENU, self.OnPaste, id=wx.ID_PASTE)
        
        # Set the focus to the RichTextCtrl
        wx.CallAfter(self.txtCtrl.SetFocus)
        # Clear the control AND the default text attributes
        self.OnClear(None)

        # Prepare the RichTextCtrl for initial text
        self.txtCtrl.Freeze()
        self.txtCtrl.BeginSuppressUndo()

        # Initialize the RichTextCtrl with a few usage notes
        self.txtCtrl.WriteText("This program shows off the wxPython RichTextCtrl and demonstrates the RTF and DOCx parsers I've written.")
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()
        self.txtCtrl.WriteText('To start, you may wish to generate display contents programmatically using the option in the File menu.  ')
        self.txtCtrl.WriteText('The features displayed in the programmatically generated document are the ones supported by the RTF and DOCx parsers.')
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()
        self.txtCtrl.WriteText('This program can load many RTF and DOCx documents.  It can only load XML files created by itself or Transana.  ')
        self.txtCtrl.WriteText('Please note that hyperlinks in DOCx files are not yet supported.')
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()
        self.txtCtrl.WriteText('This program can show the display contents in an HTML window.  ')
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()
        self.txtCtrl.WriteText('This program can save the display contents in XML, RTF, DOCx, HTML, or TXT format files.  ')
        self.txtCtrl.WriteText('Please note that hyperlinks do not yet function correctly in DOCx files.')
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()
        self.txtCtrl.WriteText("Background Colors and images in RTF files do not load in TextEdit on OS X.  That's not my fault.")
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()
        self.txtCtrl.WriteText("Text background colors are not supported by HTML display or save.  Unicode characters are encoded with UTF-8, so you may need to adjust your browser to match.")
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()
        self.txtCtrl.WriteText("TXT files are plain text files.  They will not include unicode characters, images or any formatting, just the text of the display contents.")
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()
        self.txtCtrl.WriteText("The copy and paste for RTF formatted text works with Word on Windows and both Word and TextEdit on OS X.  I haven't tested it on Linux or with Open Office.")
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()
        self.txtCtrl.WriteText("The python-docx module from the python-openxml project is unfortunately not adequate for DOCx support.  You will need my ")
        self.txtCtrl.WriteText("custom python-docx fork for image reading capability.  I was able to get several features into the main python-docx ")
        self.txtCtrl.WriteText("repository, but the maintainer was not willing to work with me on the issue of reading images.  I'm not quite sure why.")

        # Finalize initial text addition
        self.txtCtrl.EndSuppressUndo()
        self.txtCtrl.Thaw()

##        self.formatPanel = wx.Panel(self, -1)
##        mainSizer.Add(self.formatPanel, 1, wx.EXPAND | wx.ALL, 5)
##
##        lblFont = wx.StaticText(self.formatPanel, -1, "Font:", pos=(3, 3))
##        self.lblFontFace = wx.StaticText(self.formatPanel, -1,      "Face:       Courier New", pos=(8, 15))
##        self.lblFontSize = wx.StaticText(self.formatPanel, -1,      "Size:       12", pos=(8, 27))
##        self.lblFontBold = wx.StaticText(self.formatPanel, -1,      "Bold:       0", pos=(8, 39))
##        self.lblFontItalic = wx.StaticText(self.formatPanel, -1,    "Italic:     0", pos=(8, 51))
##        self.lblFontUnderline = wx.StaticText(self.formatPanel, -1, "Underline:  0", pos=(8, 63))
##        self.lblFontColor = wx.StaticText(self.formatPanel, -1,     "Color:      (255, 255, 255)", pos=(8, 75))
##        self.lblFontBgColor = wx.StaticText(self.formatPanel, -1,   "BgColor:    (  0,   0,   0)", pos=(8, 87))
##
##        lblParagraph = wx.StaticText(self.formatPanel, -1, "Paragraph:", pos=(273, 3))
##        self.lblParagraphAlign = wx.StaticText(self.formatPanel, -1,      "Align:        0", pos=(278, 15))
##        self.lblParagraphLeftIndent = wx.StaticText(self.formatPanel, -1, "Left Indent:  0", pos=(278, 27))
##        self.lblParagraphLeftSubIndent = wx.StaticText(self.formatPanel, -1, "Left Sub:     0", pos=(278, 39))
##        self.lblParagraphRightIndent = wx.StaticText(self.formatPanel, -1,   "Right Indent: 0", pos=(278, 51))
##        self.lblParagraphLineSpacing = wx.StaticText(self.formatPanel, -1,   "Line Spacing:  0", pos=(278, 63))
##        self.lblParagraphSpacingBefore = wx.StaticText(self.formatPanel, -1, "Before:       0", pos=(278, 75))
##        self.lblParagraphSpacingAfter = wx.StaticText(self.formatPanel, -1,      "After:       0", pos=(278, 87))


        # Finish up creating the main Demo form
        self.SetSizer(mainSizer)
        self.SetAutoLayout(True)
        self.Layout()
        self.CenterOnScreen()
        self.Show(True)

    def SetTxtStyle(self, fontColor = None, fontBgColor = None, fontFace = None, fontSize = None,
                          fontBold = None, fontItalic = None, fontUnderline = None,
                          parAlign = None, parLeftIndent = None, parRightIndent = None,
                          parTabs = None, parLineSpacing = None, parSpacingBefore = None, parSpacingAfter = None):
        """ I find some of the RichTextCtrl method names to be misleading.  Some character styles are stacked in the RichTextCtrl,
            and they are removed in the reverse order from how they are added, regardless of the method called.

            For example, starting with plain text, BeginBold() makes it bold, and BeginItalic() makes it bold-italic. EndBold()
            should make it italic but instead makes it bold. EndItalic() takes us back to plain text by removing the bold.

            According to Julian, this functions "as expected" because of the way the RichTextCtrl is written.

            The SetTxtStyle() method handles overlapping styles in a way that avoids this problem.  """

        # If we are formatting ANY paragraph characteristic ...
        if parAlign or (parLeftIndent != None) or (parRightIndent != None) or parTabs or \
           (parLineSpacing != None) or (parSpacingBefore != None) or (parSpacingAfter != None):
            # ... note that we are doing paragraph formatting
            formattingParagraph = True
        # If we're NOT doing paragraph formatting ...
        else:
            # ... note that we're NOT doing paragraph formatting
            formattingParagraph = False

        # If the font face (font name) is specified, set the font face
        if fontFace:
            self.txtAttr.SetFontFaceName(fontFace)
        # If the font size is specified, set the font size
        if fontSize:
            self.txtAttr.SetFontSize(fontSize)
        # If a color is specified, set text color
        if fontColor:
            self.txtAttr.SetTextColour(fontColor)
        # If a background color is specified, set the background color
        if fontBgColor:
            self.txtAttr.SetBackgroundColour(fontBgColor)
        # If bold is specified, set or remove bold as requested
        if fontBold != None:
            if fontBold:
                self.txtAttr.SetFontWeight(wx.FONTWEIGHT_BOLD)
            else:
                self.txtAttr.SetFontWeight(wx.FONTWEIGHT_NORMAL)
        # If italics is specified, set or remove bold as requested
        if fontItalic != None:
            if fontItalic:
                self.txtAttr.SetFontStyle(wx.FONTSTYLE_ITALIC)
            else:
                self.txtAttr.SetFontStyle(wx.FONTSTYLE_NORMAL)
        # If underline is specified, set or remove bold as requested
        if fontUnderline != None:
            if fontUnderline:
                self.txtAttr.SetFontUnderlined(True)
            else:
                self.txtAttr.SetFontUnderlined(False)

        # Apply the modified font to the document
        self.txtCtrl.SetDefaultStyle(self.txtAttr)

        # If there's no SELECTION in the text, paragraph formatting changes get lost.  They don't happen.
        # This code corrects for that.
        
        # If we have paragraph formatting ...
        if formattingParagraph:
            # Get the current selection
            sel = self.txtCtrl.GetSelection()
            # If there is no current selection ...
            if sel == (-2, -2):
                # ... remember the current insertion point
                ip = self.txtCtrl.GetInsertionPoint()
                # If the document is empty, that's a problem, as initial paragraph formatting doesn't register.
                # See if we're in an empty document.
                if self.txtCtrl.GetLastPosition() == 0:
                    # If so, add a space and an newline().  BOTH are necessary to resolve the problem.
                    self.txtCtrl.WriteText(' ')
                    self.txtCtrl.Newline()
                    # Then move back to the beginning of the document.
                    self.txtCtrl.SetInsertionPoint(0)
                # If we're NOT at the end of the document ...
                if ip < self.txtCtrl.GetLastPosition() - 1:
                    # ... select the character to the right of the cursor
                    self.txtCtrl.SetSelection(ip, ip + 1)
                # If we ARE at the end of the document ...
                else:
                    # ... select the character to the LEFT of the cursor
                    self.txtCtrl.SetSelection(ip - 1, ip)

            # If Paragraph Alignment is specified, set the alignment
            if parAlign != None:
                self.txtAttr.SetAlignment(parAlign)
            # If Left Indent is specified, set the left indent
            if parLeftIndent != None:
                # Left Indent can be an integer for left margin only, or a 2-element tuple for left indent and left subindent.
                if type(parLeftIndent) == int:
                    self.txtAttr.SetLeftIndent(parLeftIndent)
                elif (type(parLeftIndent) == tuple) and (len(parLeftIndent) > 1):
                    self.txtAttr.SetLeftIndent(parLeftIndent[0], parLeftIndent[1])
            # If Right Indent is specified, set the right indent
            if parRightIndent != None:
                self.txtAttr.SetRightIndent(parRightIndent)
            # If Tabs are specified, set the tabs
            if parTabs != None:
                self.txtAttr.SetTabs(parTabs)
            # If Line Spacing is specified, set Line Spacing
            if parLineSpacing != None:
                self.txtAttr.SetLineSpacing(parLineSpacing)
            # If Paragraph Spacing Before is set, set spacing before
            if parSpacingBefore != None:
                self.txtAttr.SetParagraphSpacingBefore(parSpacingBefore)
            # If Paragraph Spacing After is set, set spacing after
            if parSpacingAfter != None:
                self.txtAttr.SetParagraphSpacingAfter(parSpacingAfter)

            # Get the current range
            tmpRange = self.txtCtrl.GetSelectionRange()
            # Apply the paragraph formatting change
            self.txtCtrl.SetStyle(tmpRange, self.txtAttr)

            # Apply the modified paragraph formatting to the document
            self.txtCtrl.SetDefaultStyle(self.txtAttr)

            # if there was no initial selection ...
            if sel == (-2, -2):
                # ... remove the selectoin made above and return to the correct cursor position
                self.txtCtrl.SetInsertionPoint(ip)
      
    def OnKeyDown(self, event):
        """ Handler for EVT_KEY_DOWN events for use with Transana.
            This handles deletion of time codes. """
        # Assume that event.Skip() should be called unless proven otherwise
        shouldSkip = True
        # Create some variables to make this code a little simpler to read
        ctrl = event.GetEventObject()
        ip = ctrl.GetInsertionPoint()
        sel = ctrl.GetSelection().GetRange()

        # Capture the current text style
        tmpStyle = richtext.RichTextAttr()
        ctrl.GetStyle(ctrl.GetInsertionPoint(), tmpStyle)

        # If the Delete key is pressed ...
        if event.GetKeyCode() == wx.WXK_DELETE:
            # See if we have an insertion point rather than a selection.
            if sel[0] == sel[1]:
                # If so, look at the character to the right, the one to be deleted
                ctrl.SetSelection(ip, ip+1)
                # If that character is a time code ...
                if ctrl.GetStringSelection() == u'\xa4':
                    # ... batch the undo
                    self.undoString = ''
                    ctrl.BeginBatchUndo(self.undoString)

                # Delete the character to be deleted
                ctrl.DeleteSelection()
                # Update the current text style for the next character
                tmpStyle = richtext.RichTextAttr()
                ctrl.GetStyle(ip, tmpStyle)
                # if the style shows a point size of 1, that signals "hidden" text which needs to be removed
                while tmpStyle.GetFont().GetPointSize() == 1:
                    # As long as the style is "hidden", keep deleting characters
                    ctrl.SetSelection(ip, ip+1)
                    ctrl.DeleteSelection()
                    tmpStyle = richtext.RichTextAttr()
                    ctrl.GetStyle(ip, tmpStyle)
                # We are handling the delete manually, so event.Skip() should be skipped!
                shouldSkip = False

        # If the backspace key is pressed ...
        elif event.GetKeyCode() == wx.WXK_BACK:
            # See if we have an insertion point rather than a selection.
            if sel[0] == sel[1]:
                # Capture the current text style of the character BEFORE the insertion point
                tmpStyle = richtext.RichTextAttr()
                ctrl.GetStyle(ip-1, tmpStyle)
                # if the style shows a point size of 1, that signals "hidden" text which needs to be removed
                if tmpStyle.GetFont().GetPointSize() == 1:
                    # ... batch the undo
                    self.undoString = ''
                    ctrl.BeginBatchUndo(self.undoString)
                # Go ahead and call Skip to implement the backspace
                event.Skip()
                # Get the new insertion point and current text style
                ip = ctrl.GetInsertionPoint()
                tmpStyle = richtext.RichTextAttr()
                ctrl.GetStyle(ip-1, tmpStyle)
                # if the style shows a point size of 1, that signals "hidden" text which needs to be removed
                while tmpStyle.GetFont().GetPointSize() == 1:
                    # As long as the style is "hidden", keep deleting characters
                    ip -= 1
                    ctrl.SetSelection(ip, ip+1)
                    ctrl.DeleteSelection()
                    ctrl.SetInsertionPoint(ip)
                    tmpStyle = richtext.RichTextAttr()
                    ctrl.GetStyle(ip-1, tmpStyle)
                # We have already called event.Skip(), so the next event.Skip() should be skipped!
                shouldSkip = False

        # If F1 is pressed ...
        elif event.GetKeyCode() == wx.WXK_F1:
            # Iterate through 30 characters
            for x in range(0, 30):
                # Move the insertion point
                ctrl.SetInsertionPoint(ip + x)
                # Select the next character
                ctrl.SetSelection(ip + x, ip + x + 1)
                # Get that character's style
                tmpStyle = richtext.RichTextAttr()
                ctrl.GetStyle(ctrl.GetInsertionPoint(), tmpStyle)
##                # If it's NOT a time code ...
##                if ctrl.GetStringSelection() != u'\xa4':
##                    # print basic formatting information
##                    print(ip + x, ctrl.GetStringSelection(), tmpStyle.GetFont().GetPointSize(), tmpStyle.GetFont().GetWeight(), tmpStyle.GetFont().GetStyle(), tmpStyle.GetFont().GetUnderlined())
##                # Otherwise
##                else:
##                    # don't print the character, as that raises an exception
##                    print(ip + x, 'TC', tmpStyle.GetFont().GetPointSize(), tmpStyle.GetFont().GetWeight(), tmpStyle.GetFont().GetStyle(), tmpStyle.GetFont().GetUnderlined())
            # Reset the insertion point back to where we were
            ctrl.SetInsertionPoint(ip)

        # If we should call event.Skip()...
        if shouldSkip:
            # ... then call event.Skip()!
            event.Skip()

    def OnKey(self, event):
        """ Handler for EVT_CHAR events for use with Transana """
        # At the moment, there's nothing special to do.
        event.Skip()

    def OnKeyUp(self, event):
        """ Handler for EVT_KEY_DOWN events for use with Transana.
            This handles deletion of time codes. """
        # Create some variables to make this code a little simpler to read
        ctrl = event.GetEventObject()
        ip = ctrl.GetInsertionPoint()
        sel = ctrl.GetSelection().GetRange()

        # Capture the current text style.  (NOTE that the cursor has already moved!)
        tmpStyle = richtext.RichTextAttr()
        ctrl.GetStyle(ctrl.GetInsertionPoint(), tmpStyle)

        # if Cursor Left is pressed ...
        if event.GetKeyCode() == wx.WXK_LEFT:
            # If the style shows a point size of 1, that signals "hidden" text which needs to be skipped ...
            if tmpStyle.GetFont().GetPointSize() == 1:
                # ... so move a word to the left
                ctrl.WordLeft()
        # if Cursor Right is pressed ...
        elif event.GetKeyCode() == wx.WXK_RIGHT:
            # If the style shows a point size of 1, that signals "hidden" text which needs to be skipped ...
            if tmpStyle.GetFont().GetPointSize() == 1:
                # ... so move a word to the right
                ctrl.WordRight()
        # Call event.Skip()
        event.Skip()

        # if either Backspace or Delete was pressed ...
        if event.GetKeyCode() in [wx.WXK_BACK, wx.WXK_DELETE]:
            # ... and if we are in the midst of a batch undo specification ...
            if ctrl.BatchingUndo():
                # ... then signal that the undo batch is complete.
                 ctrl.EndBatchUndo()

    def OnLeftUp(self, event):
        """ Handler for EVT_LEFT_UP mouse events for use with Transana.
            This prevents the cursor from being placed between a time code and its hidden data. """
        # Create some variables to make this code a little simpler to read
        ctrl = event.GetEventObject()
        ip = ctrl.GetInsertionPoint()
        sel = ctrl.GetSelection().GetRange()

        # Capture the current text style.  (NOTE that the cursor has already moved!)
        tmpStyle = richtext.RichTextAttr()
        ctrl.GetStyle(ctrl.GetInsertionPoint(), tmpStyle)

        # If the style shows a point size of 1, that signals "hidden" text which needs to be skipped ...
        if (tmpStyle.GetFont().GetPointSize() == 1):
            # ... so move a word to the right
            wx.CallAfter(ctrl.WordRight)
        # Call event.Skip()
        event.Skip()

    def OnURL(self, event):
        """ Handle EVT_TEXT_URL events """
        # We don't need to do anything special here, as not all hyperlinks will be URLs!
        wx.MessageBox(event.GetString(), "Hyperlink clicked")
      
    def OnClear(self, event):
        """ Clear the wxRichTextCtrl """
        # Create default font specifications
        fontColor = wx.Colour(0, 0, 0)
        fontBgColor = wx.Colour(255, 255, 255)
        fontFace = 'Courier New'
        fontSize = 12

        # Create a default font object
        self.txtAttr = richtext.RichTextAttr()
        # Populate the Default Font object with the default font specifications
        self.SetTxtStyle(fontColor = fontColor, fontBgColor = fontBgColor, fontFace = fontFace, fontSize = fontSize,
                         fontBold = False, fontItalic = False, fontUnderline = False)

        # Prepare the control for massive change
        self.txtCtrl.Freeze()
        self.txtCtrl.BeginSuppressUndo()
        # Clear the control
        self.txtCtrl.Clear()
        # Finish up change handling
        self.txtCtrl.EndSuppressUndo()
        self.txtCtrl.Thaw()
      
    def OnLoadProg(self, event):
        """ Populate the wxRichTextCtrl programmatically with sample text """
        self.txtCtrl.Freeze()
        self.txtCtrl.BeginSuppressUndo()
        # Clear the Control AND the default text attributes
        self.OnClear(None)
      
        self.SetTxtStyle(fontSize = 16, fontBold = True, parAlign = wx.TEXT_ALIGNMENT_CENTER)
        self.txtCtrl.WriteText('This is the RichTextCtrl from')
        self.txtCtrl.Newline()
        self.txtCtrl.WriteText('%s.' % wx.version())
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()
      
        self.SetTxtStyle(fontSize = 14, fontBold = True, parAlign = wx.TEXT_ALIGNMENT_LEFT)
        self.txtCtrl.WriteText('Character Formatting:')
        self.txtCtrl.Newline()
        self.SetTxtStyle(fontSize = 12, fontBold = False)

        self.txtCtrl.WriteText('Default font face is %s ' % 'Courier New')
        self.SetTxtStyle(fontFace = 'Comic Sans MS')
        self.txtCtrl.WriteText('Comic Sans MS ')
        self.SetTxtStyle(fontFace = 'Times New Roman')
        self.txtCtrl.WriteText('Times New Roman ')
        self.SetTxtStyle(fontFace = 'Courier New')
        self.txtCtrl.WriteText('back to %s.' % 'Courier New')
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()
      
        self.txtCtrl.WriteText('"Default font size is %d ' % 12)
        self.SetTxtStyle(fontSize = 6)
        self.txtCtrl.WriteText('6 point font ')
        self.SetTxtStyle(fontSize = 18)
        self.txtCtrl.WriteText('18 point font ')
        self.SetTxtStyle(fontSize = 24)
        self.txtCtrl.WriteText('24 point font ')
        self.SetTxtStyle(fontSize = 12)
        self.txtCtrl.WriteText('%d point font.  ' % 12)
        self.txtCtrl.WriteText('(Note that there are some issues with quotation marks getting dropped, so we have added a bunch ')
        self.txtCtrl.WriteText('here and in the next few lines to make sure everything works right!)"')
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()

        self.txtCtrl.WriteText('1:  "Plain" text ')
        self.SetTxtStyle(fontBold = True)
        self.txtCtrl.WriteText('Bold ')
        self.SetTxtStyle(fontItalic = True)
        self.txtCtrl.WriteText('Bold-Italic ')
        self.SetTxtStyle(fontItalic = False)
        self.txtCtrl.WriteText('Bold ')
        self.SetTxtStyle(fontBold = False)
        self.txtCtrl.WriteText('Plain text ')
        self.txtCtrl.Newline()

        self.txtCtrl.WriteText('" 2:  Plain text ')
        self.SetTxtStyle(fontBold = True)
        self.txtCtrl.WriteText('Bold ')
        self.SetTxtStyle(fontItalic = True)
        self.txtCtrl.WriteText('Bold-Italic ')
        self.SetTxtStyle(fontBold = False)
        self.txtCtrl.WriteText('Italic ')
        self.SetTxtStyle(fontItalic = False)
        self.txtCtrl.WriteText('Plain text "')
        self.txtCtrl.Newline()

        self.txtCtrl.WriteText('3:  Plain text ')
        self.SetTxtStyle(fontItalic = True)
        self.txtCtrl.WriteText('Italic ')
        self.SetTxtStyle(fontUnderline = True)
        self.txtCtrl.WriteText('Italic-Underline ')
        self.SetTxtStyle(fontItalic = False)
        self.txtCtrl.WriteText('Underline ')
        self.SetTxtStyle(fontUnderline = False)
        self.txtCtrl.WriteText('Plain text ')
        self.txtCtrl.Newline()

        self.txtCtrl.WriteText('4:  Plain text ')
        self.SetTxtStyle(fontItalic = True)
        self.txtCtrl.WriteText('Italic ')
        self.SetTxtStyle(fontBold = True)
        self.txtCtrl.WriteText('Italic-Bold ')
        self.SetTxtStyle(fontItalic = False)
        self.txtCtrl.WriteText('Bold ')
        self.SetTxtStyle(fontBold = False)
        self.txtCtrl.WriteText('Plain text ')
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()

        self.txtCtrl.WriteText('Black ')
        self.SetTxtStyle(fontColor = wx.Colour(255, 0, 0))
        self.txtCtrl.WriteText('Red ')
        self.SetTxtStyle(fontBgColor = wx.Colour(0, 255, 0))
        self.txtCtrl.WriteText('Red on Green ')
        self.SetTxtStyle(fontColor = wx.Colour(0, 0, 255))
        self.txtCtrl.WriteText('Blue on Green ')
        self.SetTxtStyle(fontBgColor = wx.Colour(255, 0, 0))
        self.txtCtrl.WriteText('Blue on Red ')
        self.SetTxtStyle(fontColor = wx.Colour(51, 192, 51), fontBgColor = wx.Colour(211, 211, 211))
        self.txtCtrl.WriteText('Novel Color ')
        self.SetTxtStyle(fontColor = wx.Colour(0, 0, 0), fontBgColor = wx.Colour(255, 255, 255))
        self.txtCtrl.WriteText('Black on white ')
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()

        self.SetTxtStyle(fontSize = 14, fontBold = True)
        self.txtCtrl.WriteText('Paragraph Formatting:')
        self.txtCtrl.Newline()

        self.SetTxtStyle(fontSize = 12, fontBold = False, parAlign = wx.TEXT_ALIGNMENT_CENTER)
        self.txtCtrl.WriteText('Center Alignment')
        self.txtCtrl.Newline()

        self.SetTxtStyle(parAlign = wx.TEXT_ALIGNMENT_LEFT)
        self.txtCtrl.WriteText('Left Alignment')
        self.txtCtrl.Newline()

        self.SetTxtStyle(parAlign = wx.TEXT_ALIGNMENT_RIGHT)
        self.txtCtrl.WriteText('Right Alignment')
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()

        self.SetTxtStyle(parAlign = wx.TEXT_ALIGNMENT_LEFT)
        self.txtCtrl.WriteText("    There should be 4 leading spaces on this line.  Leading spaces must not disappear on load ")
        self.txtCtrl.WriteText("and save operations.  It's a pretty long line so we should ")
        self.txtCtrl.WriteText("see some word wrap in this line.  Really, we should see word wrap by now.")
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()

        self.SetTxtStyle(parLeftIndent = (100, -100))
        self.txtCtrl.WriteText("This line shows a left indent of 100 and a second-and-later line indent of -100.  ")
        self.txtCtrl.WriteText("(100 10ths of a mm.)  It's a pretty long line so we should ")
        self.txtCtrl.WriteText("see some word wrap in this line.  Really, we should see word wrap by now.")
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()

        self.SetTxtStyle(parLeftIndent = (200, -100))
        self.txtCtrl.WriteText("This line shows a left indent of 200 and a second-and-later line indent of -100, which produces a left indent.  ")
        self.txtCtrl.WriteText("(100 10ths of a mm.)  NO TABS are set or used.  It's a pretty long line so we should ")
        self.txtCtrl.WriteText("see some word wrap in this line.  Really, we should see word wrap by now.")
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()

        self.SetTxtStyle(parLeftIndent = (0, 100))
        self.txtCtrl.WriteText("This line shows a left indent of 0 and a second-and-later line indent of 100, which produces a left hang.  ")
        self.txtCtrl.WriteText("(100 10ths of a mm.)  NO TABS are set or used.  It's a pretty long line so we should ")
        self.txtCtrl.WriteText("see some word wrap in this line.  Really, we should see word wrap by now.")
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()

        self.SetTxtStyle(parLeftIndent = (100, 100))
        self.txtCtrl.WriteText("X\tThis line shows left indent of 100 and a second-and-later line indent of 100, producing a left hang.  ")
        self.txtCtrl.WriteText("(100 10ths of a mm.)  NO TABS are set, but a tab separates the marker.  ")
        self.txtCtrl.WriteText("This is NOT a bulleted list item.  It's a pretty long line so we should ")
        self.txtCtrl.WriteText("see some word wrap in this line.  Really, we should see word wrap by now.")
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()


        self.SetTxtStyle(parLeftIndent = (127, 127), parTabs = [127, 254, 381])
        self.txtCtrl.WriteText("X\tThis line shows a left indent of 127 with a second-and-later line indent of 127.  ")
        self.txtCtrl.WriteText("(127 10ths of a mm = 1/2 inch.)  1/2 inch TABS are set and a tab separates the marker.  ")
        self.txtCtrl.WriteText("This is NOT a bulleted list item.  It's a pretty long line so we should ")
        self.txtCtrl.WriteText("see some word wrap in this line.  Really, we should see word wrap by now.")
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()

        # Apply the modified indents to the document
        self.SetTxtStyle(parLeftIndent = 254, parRightIndent = 254, parTabs = [])
        self.txtCtrl.WriteText("This line shows a Left Indent of 254 and a Right Indent of 254.  (254 10ths of a mm, so 1 inch!  ")
        self.txtCtrl.WriteText("Not that my screen representation is correct here, though it looks good printed out.)  It's a pretty ")
        self.txtCtrl.WriteText("long line so we should see some word wrap in this line.  Really, we should see word wrap by now.")
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()

        self.SetTxtStyle(parLeftIndent = (0, 0), parRightIndent = 0, parSpacingBefore = 0, parSpacingAfter = 0)
        self.txtCtrl.WriteText("This is a preceding paragraph.")
        self.txtCtrl.Newline()
        self.txtCtrl.WriteText("This paragraph has no Space Before or space after.")
        self.txtCtrl.Newline()
        self.txtCtrl.WriteText("This is a following paragraph.")
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()

        self.txtCtrl.WriteText("This is a preceding paragraph.")
        self.txtCtrl.Newline()
        self.SetTxtStyle(parSpacingBefore = 51)
        self.txtCtrl.WriteText("This paragraph has Space Before set to 51.")
        self.txtCtrl.Newline()
        self.SetTxtStyle(parSpacingBefore = 0)
        self.txtCtrl.WriteText("This is a following paragraph.")
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()

        self.txtCtrl.WriteText("This is a preceding paragraph.")
        self.txtCtrl.Newline()
        self.SetTxtStyle(parSpacingAfter = 51)
        self.txtCtrl.WriteText("This paragraph has Space After set to 51.")
        self.txtCtrl.Newline()
        self.SetTxtStyle(parSpacingAfter = 0)
        self.txtCtrl.WriteText("This is a following paragraph.")
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()

        self.SetTxtStyle(parSpacingBefore = 0, parSpacingAfter = 0)
        self.txtCtrl.WriteText("This is a preceding paragraph.")
        self.txtCtrl.Newline()
        self.txtCtrl.WriteText("This paragraph has no Space Before or space after.")
        self.txtCtrl.Newline()
        self.txtCtrl.WriteText("This is a following paragraph.")
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()

        self.txtCtrl.WriteText("Let's explore tabs.")
        self.txtCtrl.Newline()
        self.txtCtrl.WriteText("Here's the default tab system.  (10mm in wxRichTextCtrl, 1/2 inch in Word)")
        self.txtCtrl.Newline()
        self.txtCtrl.WriteText("\tA\tB\tC\tD\tE\tF")
        self.txtCtrl.Newline()

        self.txtCtrl.WriteText("Here's the 10 mm system.")
        self.txtCtrl.Newline()
        self.txtCtrl.WriteText("\tA\tB\tC\tD\tE\tF")

        tabStops = []
        for x in range(100, 2160, 100):
            tabStops.append(x)
        self.SetTxtStyle(parTabs = tabStops)

        self.txtCtrl.Newline()

        self.txtCtrl.WriteText("Here's the 1/2 inch system.")
        self.txtCtrl.Newline()
        self.txtCtrl.WriteText("\tA\tB\tC\tD\tE\tF")

        tabStops = []
        for x in range(127, 2160, 127):
            tabStops.append(x)
        self.SetTxtStyle(parTabs = tabStops)

        self.txtCtrl.Newline()

        self.txtCtrl.WriteText("Here's the 1 inch system.")
        self.txtCtrl.Newline()
        self.txtCtrl.WriteText("\tA\tB\tC\tD\tE\tF")

        tabStops = []
        for x in range(254, 2160, 254):
            tabStops.append(x)
        self.SetTxtStyle(parTabs = tabStops)

        self.txtCtrl.Newline()

        self.txtCtrl.WriteText("Back to the default tab system.")
        self.txtCtrl.Newline()
        self.txtCtrl.WriteText("\tA\tB\tC\tD\tE\tF")

        tabStops = []
        self.SetTxtStyle(parTabs = tabStops, parLineSpacing = wx.TEXT_ATTR_LINE_SPACING_HALF)

        self.txtCtrl.Newline()
        self.txtCtrl.Newline()

        self.txtCtrl.WriteText('1.5 line spacing, 1.5 line spacing, 1.5 line spacing, 1.5 line spacing, 1.5 line spacing, 1.5 line spacing, 1.5 line spacing, 1.5 line spacing, 1.5 line spacing, 1.5 line spacing, 1.5 line spacing, 1.5 line spacing, ')
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()

        self.SetTxtStyle(parLineSpacing = wx.TEXT_ATTR_LINE_SPACING_NORMAL)
        self.txtCtrl.WriteText('1.0 line spacing, 1.0 line spacing, 1.0 line spacing, 1.0 line spacing, 1.0 line spacing, 1.0 line spacing, 1.0 line spacing, 1.0 line spacing, 1.0 line spacing, 1.0 line spacing, 1.0 line spacing, 1.0 line spacing, ')
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()

        self.SetTxtStyle(parLineSpacing = wx.TEXT_ATTR_LINE_SPACING_TWICE)
        self.txtCtrl.WriteText('2.0 line spacing, 2.0 line spacing, 2.0 line spacing, 2.0 line spacing, 2.0 line spacing, 2.0 line spacing, 2.0 line spacing, 2.0 line spacing, 2.0 line spacing, 2.0 line spacing, 2.0 line spacing, 2.0 line spacing, ')
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()

        self.SetTxtStyle(fontSize = 14, fontBold = True, parLineSpacing = wx.TEXT_ATTR_LINE_SPACING_NORMAL)
        self.txtCtrl.WriteText('Unicode Character support:')
        self.txtCtrl.Newline()
        self.SetTxtStyle(fontSize = 12, fontBold = False)

        self.txtCtrl.WriteText(u'Here are some Unicode characters:  ')
        self.txtCtrl.WriteText(u'ä ë ï ö ü  ')
        if INCLUDE_CHINESE:
            self.txtCtrl.WriteText('焼 知 ')  # Python 2.7: (u'\u713c \u77e5 ')
            self.txtCtrl.WriteText('保.  ')   # Python 2.7: unicode('\xe4\xbf\x9d', 'utf8')
        self.txtCtrl.WriteText(u'This is a tëst.  ')
        if INCLUDE_CHINESE:
            self.txtCtrl.WriteText(u'This is a t知st.')
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()

        self.SetTxtStyle(fontSize = 14, fontBold = True)
        self.txtCtrl.WriteText('Embedded Images and Hyperlinks:')
        self.txtCtrl.Newline()
        self.SetTxtStyle(fontSize = 12, fontBold = False)

        img = getKeyImage()      # wx.Image('Keyword16.xpm', wx.BITMAP_TYPE_XPM)
        self.txtCtrl.WriteImage(img)
        self.txtCtrl.Newline()

        self.txtCtrl.WriteText('The small image is above this, and embedded ')
        self.txtCtrl.WriteImage(img)
        self.txtCtrl.WriteText(' in this.')
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()

        img = getSplash2Image()   # wx.Image('splash.gif', wx.BITMAP_TYPE_GIF)
        self.txtCtrl.WriteImage(img)
        self.txtCtrl.Newline()

        self.txtCtrl.WriteText('The large image is above this!  This image was taken from ')
        # Make a style suitable for showing a URL
        urlStyle = richtext.RichTextAttr()
        urlStyle.SetFontFaceName('Courier New')
        urlStyle.SetFontSize(12)
        urlStyle.SetTextColour(wx.BLUE)
        urlStyle.SetFontUnderlined(True)
        self.txtCtrl.BeginStyle(urlStyle)
        self.txtCtrl.BeginURL("http://www.transana.org/")
        self.txtCtrl.WriteText("the Transana web site")
        self.txtCtrl.EndURL();
        self.txtCtrl.EndStyle();
        self.txtCtrl.WriteText(".  Such links are clickable in the wxRichTextCtrl.")
        self.txtCtrl.Newline()
        self.txtCtrl.Newline()

        if INCLUDE_TIMECODES:
            self.SetTxtStyle(fontSize = 14, fontBold = True)
            self.txtCtrl.WriteText('Transana Time Codes (Hidden Text):')
            self.txtCtrl.Newline()
            self.SetTxtStyle(fontSize = 12, fontBold = False)

            self.txtCtrl.Newline()
            self.txtTimeCodeAttr = richtext.RichTextAttr()
            self.txtTimeCodeAttr.SetTextColour(wx.Colour(255,0,0))
            self.txtTimeCodeAttr.SetBackgroundColour(wx.Colour(255, 255, 255))
            self.txtTimeCodeAttr.SetFontFaceName('Courier New')
            self.txtTimeCodeAttr.SetFontSize(12)
            self.txtTimeCodeAttr.SetFontWeight(wx.FONTWEIGHT_NORMAL)
            self.txtTimeCodeAttr.SetFontStyle(wx.FONTSTYLE_NORMAL)
            self.txtTimeCodeAttr.SetFontUnderlined(False)

            self.txtHiddenAttr = richtext.RichTextAttr()
            self.txtHiddenAttr.SetTextColour(wx.Colour(255, 255, 255))
            self.txtHiddenAttr.SetBackgroundColour(wx.Colour(255, 255, 255))
            self.txtHiddenAttr.SetFontFaceName('Times New Roman')
            self.txtHiddenAttr.SetFontSize(1)
            self.txtHiddenAttr.SetFontWeight(wx.FONTWEIGHT_NORMAL)
            self.txtHiddenAttr.SetFontStyle(wx.FONTSTYLE_NORMAL)
            self.txtHiddenAttr.SetFontUnderlined(False)

            self.txtCtrl.WriteText('This section tests Transana time codes. ')

            self.txtCtrl.SetDefaultStyle(self.txtTimeCodeAttr)
            self.txtCtrl.WriteText(TIMECODE_CHAR)
            self.txtCtrl.SetDefaultStyle(self.txtHiddenAttr)
            self.txtCtrl.WriteText('<102495> ')
            self.txtCtrl.SetDefaultStyle(self.txtAttr)

            self.txtCtrl.WriteText("Transana time codes require hidden text, which I'm trying to fake here.  ")
            self.txtCtrl.WriteText("The hidden text looks like a space following the time code symbol, but you can't ")
            self.txtCtrl.WriteText("put the cursor between the time code symbol and the space.")
            self.txtCtrl.Newline()
            self.txtCtrl.Newline()

        if INCLUDE_LISTS:

            self.SetTxtStyle(fontSize = 14, fontBold = True, parTabs = [127, 254, 381])
            self.txtCtrl.WriteText('Bulleted and Numbered Lists:')
            self.txtCtrl.Newline()
            self.SetTxtStyle(fontSize = 12, fontBold = False, parSpacingAfter = 42)

            self.txtCtrl.WriteText("Now let's explore bulleted lists.  ")
            self.txtCtrl.Newline()
            self.txtCtrl.WriteText("Currently, lists almost save and re-load in the wxRichTextCtrl, but do not load properly ")
            self.txtCtrl.WriteText("in Word.  Lists created in Word seem to load okay.  Assistance with this would be most welcome.")
            self.txtCtrl.Newline()
            self.txtCtrl.WriteText("(NOTE:  We're also implementing spacing after paragraphs here.)")
            self.txtCtrl.Newline()

            self.txtCtrl.BeginSymbolBullet('*', 127, 127)

            self.txtCtrl.WriteText('This is a symbol bullet using ("*", 127, 127) and the default bullet style.')
            self.txtCtrl.Newline()

            self.txtCtrl.WriteText('This is a second symbol bullet.')
            self.txtCtrl.Newline()

            self.txtCtrl.EndSymbolBullet()

            self.txtCtrl.WriteText("Okay, we're done with that now.  ")
            self.txtCtrl.Newline()

            self.txtCtrl.BeginSymbolBullet('-', 127, 127)

            self.txtCtrl.WriteText('This is a symbol bullet using ("-", 127, 127) and the default bullet style.')
            self.txtCtrl.Newline()

            self.txtCtrl.WriteText('This is a second symbol bullet.')
            self.txtCtrl.Newline()

            self.txtCtrl.EndSymbolBullet()

            self.txtCtrl.WriteText("Okay, we're done with that now.  ")
            self.txtCtrl.Newline()

            self.txtCtrl.BeginSymbolBullet('*', 127, 127, wx.TEXT_ATTR_BULLET_STYLE_STANDARD)

            self.txtCtrl.WriteText('This is a symbol bullet using ("*", 127, 127) and bulletStyle wx.TEXT_ATTR_BULLET_STYLE_STANDARD.')
            self.txtCtrl.Newline()

            self.txtCtrl.WriteText('This is a second symbol bullet.')
            self.txtCtrl.Newline()

            self.txtCtrl.EndSymbolBullet()

            self.txtCtrl.WriteText("Okay, we're done with that now.  ")
            self.txtCtrl.Newline()

            self.txtCtrl.WriteText("Now let's explore numbered lists.  There are lots of options here.  ")
            self.txtCtrl.Newline()

            self.txtCtrl.BeginNumberedBullet(1, 127, 127)
            self.txtCtrl.WriteText('This is a numbered bullet using (1, 127, 127) and the default style.')
            self.txtCtrl.Newline()
            self.txtCtrl.EndNumberedBullet()

            self.txtCtrl.BeginNumberedBullet(2, 127, 127)
            self.txtCtrl.WriteText('This is a second numbered bullet using (2, 127, 127) and the default style.')
            self.txtCtrl.Newline()
            self.txtCtrl.EndNumberedBullet()

            self.SetTxtStyle(parTabs = [64, 127, 192, 254, 381])

            self.txtCtrl.BeginNumberedBullet(3, 64, 127, wx.TEXT_ATTR_BULLET_STYLE_LETTERS_UPPER | wx.TEXT_ATTR_BULLET_STYLE_PARENTHESES)
            self.txtCtrl.WriteText('This is a third numbered bullet using (3, 64, 127) and bulletStyle wx.TEXT_ATTR_BULLET_STYLE_LETTERS_UPPER | wx.TEXT_ATTR_BULLET_STYLE_PARENTHESES.')
            self.txtCtrl.Newline()
            self.txtCtrl.EndNumberedBullet()

            self.txtCtrl.BeginNumberedBullet(4, 64, 127, wx.TEXT_ATTR_BULLET_STYLE_LETTERS_LOWER | wx.TEXT_ATTR_BULLET_STYLE_PERIOD)
            self.txtCtrl.WriteText('This is a fourth numbered bullet using (4, 64, 127) and bulletStyle wx.TEXT_ATTR_BULLET_STYLE_LETTERS_LOWER | wx.TEXT_ATTR_BULLET_STYLE_PERIOD.')
            self.txtCtrl.Newline()
            self.txtCtrl.EndNumberedBullet()

            self.txtCtrl.BeginNumberedBullet(5, 127, 64, wx.TEXT_ATTR_BULLET_STYLE_ROMAN_UPPER | wx.TEXT_ATTR_BULLET_STYLE_STANDARD)
            self.txtCtrl.WriteText('This is a fifth numbered bullet using (5, 127, 64) and bulletStyle wx.TEXT_ATTR_BULLET_STYLE_ROMAN_UPPER | wx.TEXT_ATTR_BULLET_STYLE_STANDARD.')
            self.txtCtrl.Newline()
            self.txtCtrl.EndNumberedBullet()

            self.SetTxtStyle(parTabs = [381, 508])

            self.txtCtrl.BeginNumberedBullet(6, 127, 254, wx.TEXT_ATTR_BULLET_STYLE_ROMAN_UPPER | wx.TEXT_ATTR_BULLET_STYLE_RIGHT_PARENTHESIS)
            self.txtCtrl.WriteText('This is a sixth numbered bullet using (6, 127, 254) and bulletStyle wx.TEXT_ATTR_BULLET_STYLE_ROMAN_UPPER | wx.TEXT_ATTR_BULLET_STYLE_RIGHT_PARENTHESIS.')
            self.txtCtrl.Newline()
            self.txtCtrl.EndNumberedBullet()

            self.txtCtrl.BeginNumberedBullet(7, 127, 254, wx.TEXT_ATTR_BULLET_STYLE_ROMAN_LOWER | wx.TEXT_ATTR_BULLET_STYLE_RIGHT_PARENTHESIS)
            self.txtCtrl.WriteText('This is a seventh numbered bullet using (7, 127, 254) and bulletStyle wx.TEXT_ATTR_BULLET_STYLE_ROMAN_LOWER | wx.TEXT_ATTR_BULLET_STYLE_RIGHT_PARENTHESIS.')
            self.txtCtrl.Newline()
            self.txtCtrl.EndNumberedBullet()

            self.SetTxtStyle(parSpacingAfter = 0)

        # Playing with Tables

        self.SetTxtStyle(fontSize = 14, fontBold = True)
        self.txtCtrl.WriteText('Tables:')
        self.txtCtrl.Newline()
        self.SetTxtStyle(fontSize = 12, fontBold = False)

        self.txtCtrl.Newline()

        rows = 2
        cols = 3
        table = self.txtCtrl.WriteTable(rows, cols)
        for col in range(cols):
            for row in range(rows):
                cell = table.GetCell(row, col)
                self.SetTxtStyle(fontSize = 10, fontItalic = True, parLeftIndent = 10, parRightIndent = 10, parSpacingAfter = 25)
                cell.SetDefaultStyle(self.txtAttr)
                cell.AddParagraph("This is the cell at Row {0}, Column {1}\n".format(row, col))

##        print('Tables:')
##        for x in dir(table):
##            print(' ', x)
##        print()
##        print('Cells:')
##        for x in dir(cell):
##            print(' ', x)
##        print()


        self.txtCtrl.EndSuppressUndo()
        self.txtCtrl.Thaw()

    def OnLoadXML(self, event):
        """ Handle the Load from XML menu item """
        # Display a File Open Dialog for XML files
        dlg = wx.FileDialog(self, "Choose a filename",
                          wildcard=u'XML files (*.xml)|*.xml',
                          style=wx.FD_OPEN)
        # if a file is selected ...
        if dlg.ShowModal() == wx.ID_OK:
            # assign it to path
            path = dlg.GetPath()
        # Otherwise
        else:
            # signal no file by making path empty
            path = ''
        # Destroy the File Open dialog
        dlg.Destroy()
        # If an existing file is selected ...
        if (path != "") and (os.path.exists(path)):
            # Prepare the control for data
            self.txtCtrl.Freeze()
            self.txtCtrl.BeginSuppressUndo()
            # Clear the Control AND the default text attributes
            self.OnClear(None)
            # Create an XML Handler
            handler = richtext.RichTextXMLHandler()
            # Load the XML file via the XML Handler.
            # Note that for XML, the BUFFER is passed.
            handler.LoadFile(self.txtCtrl.GetBuffer(), path)
            # Signal the end of changing the control
            self.txtCtrl.EndSuppressUndo()
            self.txtCtrl.Thaw()

    def OnLoadRTF(self, event):
        """ Handle the Load from RTF menu item """
        # Display a File Open Dialog for RTF files
        dlg = wx.FileDialog(self, "Choose a filename",
                            wildcard=u'Rich Text Format files (*.rtf)|*.rtf',
                            style=wx.FD_OPEN)
        # if a file is selected ...
        if dlg.ShowModal() == wx.ID_OK:
            # assign it to path
            path = dlg.GetPath()
        # Otherwise
        else:
            # signal no file by making path empty
            path = ''
        # Destroy the File Open dialog
        dlg.Destroy()
        # If an existing file is selected ...
        if (path != "") and (os.path.exists(path)):
            # Prepare the control for data
            self.txtCtrl.Freeze()
            self.txtCtrl.BeginSuppressUndo()
            # Clear the Control AND the default text attributes
            self.OnClear(None)
            # Start exception handling
            try:
                # Use the custom RTF Handler
                handler = PyRTFParser.PyRichTextRTFHandler()
                # Load the RTF file via the XML Handler.
                # Note that for RTF, the wxRichTextCtrl CONTROL is passed.
                handler.LoadFile(self.txtCtrl, path)
            # exception handling
            except:
                print("Custom RTF Handler Load failed")
                print()
                print(sys.exc_info()[0], sys.exc_info()[1])
                print(traceback.print_exc())
                print()
                pass

            # Signal the end of changing the control
            self.txtCtrl.EndSuppressUndo()
            self.txtCtrl.Thaw()

    def OnLoadDocx(self, event):
        """ Handle the Load from Docx menu item """

        # Display a File Open Dialog for RTF files
        dlg = wx.FileDialog(self, "Choose a filename",
                            wildcard=u'Word Files files (*.docx)|*.docx',
                            style=wx.FD_OPEN)
        # if a file is selected ...
        if dlg.ShowModal() == wx.ID_OK:
            # assign it to path
            path = dlg.GetPath()
        # Otherwise
        else:
            # signal no file by making path empty
            path = ''
        # Destroy the File Open dialog
        dlg.Destroy()

        # If an existing file is selected ...
        if (path != "") and (os.path.exists(path)):
            # Prepare the control for data
            self.txtCtrl.Freeze()
            self.txtCtrl.BeginSuppressUndo()
            # Clear the Control AND the default text attributes
            self.OnClear(None)
            # Start exception handling
            try:
                # Use the custom Docx Handler
                handler = PyDocxParser.PyRichTextDocxHandler()
                # Load the Docx file via the XML Handler.
                # Note that for Docx, the wxRichTextCtrl CONTROL is passed.
                handler.LoadFile(self.txtCtrl, path)
            # exception handling
            except:
                print("Custom Docx Handler Load failed")
                print()
                print(sys.exc_info()[0], sys.exc_info()[1])
                print(traceback.print_exc())
                print()
                pass

            # Signal the end of changing the control
            self.txtCtrl.EndSuppressUndo()
            self.txtCtrl.Thaw()

    def OnDisplayHTML(self, event):
        """ Handle the Display as HTML menu command """
        # If there's text in the wxRichTextCtrl ...
        if len(self.txtCtrl.GetValue()) > 0:
            # This code is lifted from the wxPython wxRichTextCtrl Demo.
            # Needed to view as HTML with images in memory
            wx.FileSystem.AddHandler(wx.MemoryFSHandler())
            # Create an HTML Handler
            handler = richtext.RichTextHTMLHandler()
            # Tell the HTML Handler to do images in memory
            handler.SetFlags(richtext.RICHTEXT_HANDLER_SAVE_IMAGES_TO_MEMORY)
            # Tell the HTML Handler how to handle font sizes
            handler.SetFontSizeMapping([7, 9, 11, 12, 14, 22, 100])
            # Create a io object
            stream = io.BytesIO()
            # if the handler can save streams, do it.  If not, exit this method
            if not handler.SaveFile(self.txtCtrl.GetBuffer(), stream):
                return
            # Create a dialog for the HTML Window
            dlg = wx.Dialog(self, title="HTML", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
            # Create an HTML Window
            html = wx.html.HtmlWindow(dlg, size=(600, 500), style=wx.BORDER_SUNKEN)
            
            try:
                # Specify the stream as the HTML contents
                html.SetPage(stream.getvalue())  # .decode('utf8')
            except UnicodeDecodeError:
                # Specify the stream as the HTML contents
                html.SetPage("The page contained Unicode characters which could not be displayed.")

            # Add a button to the HTML Dialog
            btn = wx.Button(dlg, wx.ID_CANCEL)
            # Handle layout for the HTML Dialog
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(html, 1, wx.ALL|wx.EXPAND, 5)
            sizer.Add(btn, 0, wx.ALL|wx.CENTER, 10)
            dlg.SetSizer(sizer)
            sizer.Fit(dlg)
            # Center the HTML Dialog on screen
            dlg.CenterOnScreen()
            # Display the HTML Dialog
            dlg.ShowModal()
            # Delete the memory images created by the handler
            handler.DeleteTemporaryImages()
         
    def OnSaveXML(self, event):
        """ Handle the Save To XML menu item """
        # If there's text in the wxRichTextCtrl ...
        if len(self.txtCtrl.GetValue()) > 0:
            # Begin exception handling
            try:
                # Display a File Save Dialog for XML files
                dlg = wx.FileDialog(self, "Choose a filename",
                                    wildcard=u'XML files (*.xml)|*.xml',
                                    style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
                # if a file is selected ...
                if dlg.ShowModal() == wx.ID_OK:
                    # assign it to path
                    path = dlg.GetPath()
                # Otherwise
                else:
                    # signal no file by making path empty
                    path = ''
                # Destroy the File Save dialog
                dlg.Destroy()
                # If an existing file is selected ...
                if (path != ""):
                    # Get an XML Handler
                    handler = richtext.RichTextXMLHandler()
                    # Save the file using the XML Handler.
                    # Note that the XML Handler takes a wxRichTextBuffer argument.
                    handler.SaveFile(self.txtCtrl.GetBuffer(), path)
            # Exception Handling
            except:
                print("XML Save failed")
                pass

    def OnSaveRTF(self, event):
        """ Handle the Save To RTF menu item """
        # If there's text in the wxRichTextCtrl ...
        if len(self.txtCtrl.GetValue()) > 0:
            # Begin exception handling
            try:
                # Display a File Save Dialog for RTF files
                dlg = wx.FileDialog(self, "Choose a filename",
                                    wildcard=u'Rich Text Format files (*.rtf)|*.rtf',
                                    style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
                # if a file is selected ...
                if dlg.ShowModal() == wx.ID_OK:
                    # assign it to path
                    path = dlg.GetPath()
                # Otherwise
                else:
                    # signal no file by making path empty
                    path = ''
                # Destroy the File Save dialog
                dlg.Destroy()
                # If an existing file is selected ...
                if (path != ""):
                    # Use the custom RTF Handler
                    handler = PyRTFParser.PyRichTextRTFHandler()
                    # Save the file with the custom RTF Handler.
                    # The custom RTF Handler can take either a wxRichTextCtrl or a wxRichTextBuffer argument.
                    handler.SaveFile(self.txtCtrl.GetBuffer(), path)
            # Exception Handling
            except:
                print("Custom RTF Handler Save failed")
                print()
                print(sys.exc_info()[0], sys.exc_info()[1])
                print(traceback.print_exc())
                print()
                pass

    def OnSaveDocx(self, event):
        """ Handle the Save To Docx menu item """
        # If there's text in the wxRichTextCtrl ...
        if len(self.txtCtrl.GetValue()) > 0:
            # Begin exception handling
            try:
                # Display a File Save Dialog for Docx files
                dlg = wx.FileDialog(self, "Choose a filename",
                                    wildcard=u'Word Format files (*.docx)|*.docx',
                                    style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
                # if a file is selected ...
                if dlg.ShowModal() == wx.ID_OK:
                    # assign it to path
                    path = dlg.GetPath()
                # Otherwise
                else:
                    # signal no file by making path empty
                    path = ''
                # Destroy the File Save dialog
                dlg.Destroy()
                # If an existing file is selected ...
                if (path != ""):
                    # Use the custom Docx Handler
                    handler = PyDocxParser.PyRichTextDocxHandler()
                    # Save the file with the custom Docx Handler.
                    # The custom Docx Handler can take either a wxRichTextCtrl or a wxRichTextBuffer argument.
                    handler.SaveFile(self.txtCtrl.GetBuffer(), path)
            # Exception Handling
            except:
                print("Custom Docx Handler Save failed")
                print()
                print(sys.exc_info()[0], sys.exc_info()[1])
                print(traceback.print_exc())
                print()
                pass

    def OnSaveHTML(self, event):
        """ Handle the Save To HTML menu item """
        # If there's text in the wxRichTextCtrl ...
        if len(self.txtCtrl.GetValue()) > 0:
            # Begin exception handling
            try:
                # Display a File Save Dialog for HTML files
                dlg = wx.FileDialog(self, "Choose a filename",
                                    wildcard=u'HTML files (*.html, *.htm)|*.html;*.htm',
                                    style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
                # if a file is selected ...
                if dlg.ShowModal() == wx.ID_OK:
                    # assign it to path
                    path = dlg.GetPath()
                # Otherwise
                else:
                    # signal no file by making path empty
                    path = ''
                # Destroy the File Save dialog
                dlg.Destroy()
                # If an existing file is selected ...
                if (path != ""):
                    # Get an HTML Handler
                    handler = richtext.RichTextHTMLHandler()
                    # Set the handler's encoding
                    handler.SetEncoding('UTF-8')
                    # Use the HTML Handler to save the file.
                    # Note that the HTML Handler takes a wxRichTextBuffer argument
                    handler.SaveFile(self.txtCtrl.GetBuffer(), path)
            # Exception Handling
            except:
                print("HTML Save failed")
                pass

    def OnSaveTXT(self, event):
        """ Handle the Save To TXT menu item """
        # If there's text in the wxRichTextCtrl ...
        if len(self.txtCtrl.GetValue()) > 0:
            # Begin exception handling
            try:
                # Display a File Save Dialog for TXT files
                dlg = wx.FileDialog(self, "Choose a filename",
                                    wildcard=u'Plain Text files (*.txt)|*.txt',
                                    style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
                # if a file is selected ...
                if dlg.ShowModal() == wx.ID_OK:
                    # assign it to path
                    path = dlg.GetPath()
                # Otherwise
                else:
                    # signal no file by making path empty
                    path = ''
                # Destroy the File Save dialog
                dlg.Destroy()
                # If an existing file is selected ...
                if (path != ""):
                    # The wxRichTextCtrl can save plain text without a File Handler.
                    self.txtCtrl.SaveFile(path, richtext.RICHTEXT_TYPE_ANY)
            # Exception Handling
            except:
                print("TXT Save failed")
                pass

    def OnPrintPreview(self, event):
        if False:
            # Create a RichTextPrinting helper object
            rtp = richtext.RichTextPrinting("Print test")
            # Call the Page Setup Dialog
            rtp.PageSetup()
            # Calling Print Preview crashes and burns for me with wxPython 2.8.10.1 on Windows
            # and wxPython 2.8.9.2 on OS X.
            # rtp.PreviewBuffer(self.txtCtrl.GetBuffer())
            # Send the output to the printer
            rtp.PreviewBuffer(self.txtCtrl.GetBuffer())
        else:
            printout1 = richtext.RichTextPrintout()
            printout1.SetRichTextBuffer(self.txtCtrl.GetBuffer())
            printout2 = richtext.RichTextPrintout()
            printout2.SetRichTextBuffer(self.txtCtrl.GetBuffer())
            data = wx.PrintDialogData()
            data.SetCollate(True)
            datapr = wx.PrintData()
            datapr.SetPaperId(wx.PAPER_LETTER)
            data.SetPrintData(datapr)
            # Impression
            preview = wx.PrintPreview(printout1, printout2, data)
            if not preview.IsOk():
                print("Probleme dans le preview du richTextCtrl.")
                return
            pfrm = wx.PreviewFrame(preview, self, "Print Preview Test")
            pfrm.Initialize()
            pfrm.SetPosition(self.GetPosition())
            pfrm.SetSize(self.GetSize())
            pfrm.Show(True)

    def OnPrint(self, event):
        """ Handle the Print menu item """
        # Create a RichTextPrinting helper object
        rtp = richtext.RichTextPrinting("Print test")
        # Call the Page Setup Dialog
        rtp.PageSetup()
        # Calling Print Preview crashes and burns for me with wxPython 2.8.10.1 on Windows
        # and wxPython 2.8.9.2 on OS X.
        # rtp.PreviewBuffer(self.txtCtrl.GetBuffer())
        # Send the output to the printer
        rtp.PrintBuffer(self.txtCtrl.GetBuffer())

    def OnClose(self, event):
        """ Handle the Exit Menu item """
        # Close the demo window
        self.Close()

    def GetFormattedSelection(self, format):
        """ Return a string with the formatted contents of just the RichText control's current selection.
            format can either be 'XML' or 'RTF'. """
        # If a valid format is NOT passed ...
        if not format in ['XML', 'RTF']:
            # ... return a blank string
            return ''
        
        # NOTE:  The wx.RichTextCtrl doesn't provide an easy way to get a formatted selection that I can figure out.
        #        This is a hack, but it works.

        # Freeze the control so things will work faster
        self.txtCtrl.Freeze()
        # We'll need to undo everything from this point on.  Let's do it as ONE operation.
        self.txtCtrl.BeginBatchUndo('RTCBufferSelection')
        # Get the start and end of the current selection
        sel = self.txtCtrl.GetSelection().GetRange()
        # Delete everything AFTER the end of the current selection
        self.txtCtrl.Delete((sel[1], self.txtCtrl.GetLastPosition()))
        # Delete everything BEFORE the start of the current selection
        self.txtCtrl.Delete((0, sel[0]))
        # This leaves us with JUST the selection in the control!

        # If XML format is requested ...
        if format == 'XML':
            # Create a Stream
            stream = io.StringIO()
            # Get an XML Handler
            handler = richtext.RichTextXMLHandler()
            # Save the contents of the control to the stream
            handler.SaveStream(self.txtCtrl.GetBuffer(), stream)
            # Convert the stream to a usable string
            tmpBuffer = stream.getvalue()
        # If RTF format is requested ....
        elif format == 'RTF':
            # Get an RTF Handler
            handler = PyRTFParser.PyRichTextRTFHandler()
            # Get the string representation by leaving off the filename parameter
            tmpBuffer = handler.SaveFile(self.txtCtrl.GetBuffer())

        # End Undo batching
        self.txtCtrl.EndBatchUndo()
        # Undo the changes.  This restores ALL the text
        self.txtCtrl.Undo()
        # Now thaw the control so that updates will be displayed again
        self.txtCtrl.Thaw()
            
        # Return the buffer's XML string
        return tmpBuffer

    def OnCutCopy(self, event):
        """ Handle Cut and Copy events, over-riding the RichTextCtrl versions.
            This implementation supports Rich Text Formatted text, and at least on Windows can
            share formatted text with other programs. """
        # Create a Composite Data Object for the Clipboard
        compositeDataObject = wx.DataObjectComposite()

        # Get the current selection in RTF format
        rtfSelection = self.GetFormattedSelection('RTF')

        # Create a Custom Data Format for RTF
        if 'wxMac' in wx.PlatformInfo:
            rtfFormat = wx.DataFormat('public.rtf')
        else:
            # Create a Custom Data Format for RTF
            rtfFormat = wx.DataFormat('Rich Text Format')
        # Create a Custom Data Object for the RTF format
        rtfDataObject = wx.CustomDataObject(rtfFormat)
        # Save the RTF version of the control selection to the RTF Custom Data Object
        rtfDataObject.SetData(rtfSelection.encode('utf8'))
        # Add the RTF Custom Data Object to the Composite Data Object
        compositeDataObject.Add(rtfDataObject)

        # Get the current selection in Plain Text
        txtSelection = self.txtCtrl.GetStringSelection()
        # Create a Text Data Object
        txtDataObject = wx.TextDataObject()
        # Save the Plain Text version of the control selection to the Text Data Object
        txtDataObject.SetText(txtSelection)
        # Add the Plain Text Data Object to the Composite Data object
        compositeDataObject.Add(txtDataObject)

        # Open the Clipboard
        if wx.TheClipboard.Open():
            # Place the Composite Data Object (with RTF and Plain Text) on the Clipboard
            wx.TheClipboard.SetData(compositeDataObject)
            # Close the Clipboard
            wx.TheClipboard.Close()

        # If we are CUTting (rather than COPYing) ...
        if event.GetId() == wx.ID_CUT:
            # ... delete the selection from the Rich Text Ctrl.
            self.txtCtrl.DeleteSelection()

    def OnPaste(self, event):
        """ Handle Paste events, over-riding the RichTextCtrl version.
            This implementation supports Rich Text Formatted text, and at least on Windows can
            share formatted text with other programs. """
        # Open the Clipboard
        if wx.TheClipboard.Open():
            if 'wxMac' in wx.PlatformInfo:
                rtfFormat = wx.DataFormat('public.rtf')
            else:
                # Create a Custom Data Format for RTF
                rtfFormat = wx.DataFormat('Rich Text Format')
            # See if the RTF Format is supported by the current clipboard data object
            if wx.TheClipboard.IsSupported(rtfFormat):
                # Specify that the data object accepts data in RTF format
                customDataObject = wx.CustomDataObject(rtfFormat)
                # Try to get data from the Clipboard
                success = wx.TheClipboard.GetData(customDataObject)
                # If the data in the clipboard is in an appropriate format ...
                if success:
                    # ... get the data from the clipboard
                    formattedText = customDataObject.GetData().tobytes().decode('utf8')
                    # Prepare the control for data
                    self.txtCtrl.Freeze()
                    self.txtCtrl.BeginSuppressUndo()
                    # Start exception handling
                    try:
                        # Use the custom RTF Handler
                        handler = PyRTFParser.PyRichTextRTFHandler()
                        # Load the RTF data into the Rich Text Ctrl via the RTF Handler.
                        # Note that for RTF, the wxRichTextCtrl CONTROL is passed with the RTF string.
                        handler.LoadString(self.txtCtrl, formattedText)
                    # exception handling
                    except:
                        print("Custom RTF Handler Load failed")
                        print()
                        print(sys.exc_info()[0], sys.exc_info()[1])
                        print(traceback.print_exc())
                        print()
                        pass

                    # Signal the end of changing the control
                    self.txtCtrl.EndSuppressUndo()
                    self.txtCtrl.Thaw()
            # If there's not RTF data, see if there's Plain Text data
            elif wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_TEXT)):
                # Create a Text Data Object
                textDataObject = wx.TextDataObject()
                # Get the Data from the Clipboard
                wx.TheClipboard.GetData(textDataObject)
                # Write the plain text into the Rich Text Ctrl
                self.txtCtrl.WriteText(textDataObject.GetText())
            # Close the Clipboard
            wx.TheClipboard.Close()

    def OnFormat(self, event):
        if event.GetId() == self.MENU_EDIT_FORMAT_FONT:
            tabToShow = 0
        elif event.GetId() == self.MENU_EDIT_FORMAT_PARAGRAPH:
            tabToShow = 1
        elif event.GetId() == self.MENU_EDIT_FORMAT_TABS:
            tabToShow = 2

        # Set the Wait cursor
        self.SetCursor(wx.Cursor(wx.CURSOR_WAIT))
            
        # Create a RichTextAttr object to hold the style
        currentStyle = richtext.RichTextAttr()

        # If we don't have a text selection, we can just get the wxFontData and go.
        if self.txtCtrl.GetSelection().GetRange()[0] == self.txtCtrl.GetSelection().GetRange()[1]:
            if self.txtCtrl.GetCaretPosition() >= 0:
                pos = self.txtCtrl.GetCaretPosition()
            else:
                pos = self.txtCtrl.GetInsertionPoint()

            self.txtCtrl.GetStyle(pos, currentStyle)
        else:
            self.txtCtrl.GetStyleForRange(self.txtCtrl.GetSelectionRange(), currentStyle)
        # Get the font associated with that style
        currentFont = currentStyle.GetFont()

        # First, get the initial values for the Font Dialog.  This will match the
        # formatting of the LAST character in the selection.
        fontData = FormatDialog.FormatDef()
        fontData.fontFace = currentFont.GetFaceName()
        fontData.fontSize = currentFont.GetPointSize()
        if currentFont.GetWeight() == wx.FONTWEIGHT_BOLD:
            fontData.fontWeight = FormatDialog.fd_BOLD
        else:
            fontData.fontWeight = FormatDialog.fd_OFF
        if currentFont.GetStyle() == wx.FONTSTYLE_ITALIC:
            fontData.fontStyle = FormatDialog.fd_ITALIC
        else:
            fontData.fontStyle = FormatDialog.fd_OFF
        if currentFont.GetUnderlined():
            fontData.fontUnderline = FormatDialog.fd_UNDERLINE
        else:
            fontData.fontUnderline = FormatDialog.fd_OFF
        fontData.fontColorDef = currentStyle.GetTextColour()
        fontData.fontBackgroundColorDef = currentStyle.GetBackgroundColour()

#        print "TranscriptEditor.CallFormatDialog(): Paragraph Characteristics:"

#        print "Alignment:", currentStyle.GetAlignment(), wx.TEXT_ALIGNMENT_LEFT, wx.TEXT_ALIGNMENT_CENTRE, wx.TEXT_ALIGNMENT_RIGHT
#        print "Left Indent:", currentStyle.GetLeftIndent()
#        print "Left Sub-Indent:", currentStyle.GetLeftSubIndent()
#        print "   ... producing Left: %d, First Line: %d" % (currentStyle.GetLeftIndent() + currentStyle.GetLeftSubIndent(), 0 - currentStyle.GetLeftSubIndent())
#        print "Right Indent:", currentStyle.GetRightIndent()
#        print "Line Spacing:", currentStyle.GetLineSpacing()
#        print "Space Before:", currentStyle.GetParagraphSpacingBefore()
#        print "Space After:", currentStyle.GetParagraphSpacingAfter()
#        print "Tabs:", currentStyle.GetTabs()

        fontData.paragraphAlignment = currentStyle.GetAlignment()
        fontData.paragraphLeftIndent = currentStyle.GetLeftIndent()
        fontData.paragraphLeftSubIndent = currentStyle.GetLeftSubIndent()
        fontData.paragraphRightIndent = currentStyle.GetRightIndent()
        fontData.paragraphLineSpacing = currentStyle.GetLineSpacing()
        fontData.paragraphSpaceBefore = currentStyle.GetParagraphSpacingBefore()
        # There's a bug in RTC's ParagraphSpacingBefore specification.  It adds space AFTER too.  This compensates for that if possible.
        fontData.paragraphSpaceAfter = currentStyle.GetParagraphSpacingAfter() + currentStyle.GetParagraphSpacingBefore()
        fontData.tabs = currentStyle.GetTabs()

        # Now we need to iterate through the selection and look for any characters with different font values.
        for selPos in range(self.txtCtrl.GetSelection().GetRange()[0], self.txtCtrl.GetSelection().GetRange()[1] + 1):
                tmpStyle = richtext.RichTextAttr()
                # Get the Font Attributes of the current Character
                self.txtCtrl.GetStyle(selPos, tmpStyle)
                tmpFont = tmpStyle.GetFont()

                # Now look for specs that are different, and flag the TransanaFontDef object if one is found.
                # If the the Symbol Font is used, we ignore this.  (We don't want to change the Font Face of Special Characters.)
                if (fontData.fontFace != None) and (tmpFont.GetFaceName() != 'Symbol') and (tmpFont.GetFaceName() != fontData.fontFace):
                    del(fontData.fontFace)

#                print fontData.fontSize, tmpFont.GetPointSize()

                if (fontData.fontSize != None) and (tmpFont.GetPointSize() != fontData.fontSize):
                    del(fontData.fontSize)

                if (fontData.fontWeight != FormatDialog.fd_AMBIGUOUS) and \
                   ((tmpFont.GetWeight() == wx.FONTWEIGHT_BOLD) and (fontData.fontWeight == FormatDialog.fd_OFF)) or \
                   ((tmpFont.GetWeight() != wx.FONTWEIGHT_BOLD) and (fontData.fontWeight == FormatDialog.fd_BOLD)):
                    fontData.fontWeight = FormatDialog.fd_AMBIGUOUS

                if (fontData.fontStyle != FormatDialog.fd_AMBIGUOUS) and \
                   ((tmpFont.GetStyle() == wx.FONTSTYLE_ITALIC) and (fontData.fontStyle == FormatDialog.fd_OFF)) or \
                   ((tmpFont.GetStyle() != wx.FONTSTYLE_ITALIC) and (fontData.fontStyle == FormatDialog.fd_ITALIC)):
                    fontData.fontStyle = FormatDialog.fd_AMBIGUOUS

                if (fontData.fontUnderline != FormatDialog.fd_AMBIGUOUS) and \
                   ((tmpFont.GetUnderlined()) and (fontData.fontUnderline == FormatDialog.fd_OFF)) or \
                   ((not tmpFont.GetUnderlined()) and (fontData.fontUnderline == FormatDialog.fd_UNDERLINE)):
                    fontData.fontUnderline = FormatDialog.fd_AMBIGUOUS

                if (fontData.fontColorDef != None) and (fontData.fontColorDef != tmpStyle.GetTextColour()):
                    del(fontData.fontColorDef)
        
                if (fontData.fontBackgroundColorDef != None) and (fontData.fontBackgroundColorDef != tmpStyle.GetBackgroundColour()):
                    del(fontData.fontBackgroundColorDef)

                if (fontData.paragraphAlignment != None) and (fontData.paragraphAlignment != tmpStyle.GetAlignment()):
                    del(fontData.paragraphAlignment)

                if (fontData.paragraphLeftIndent != None) and (fontData.paragraphLeftIndent != tmpStyle.GetLeftIndent()):
                    del(fontData.paragraphLeftIndent)

                if (fontData.paragraphLeftSubIndent != None) and (fontData.paragraphLeftSubIndent != tmpStyle.GetLeftSubIndent()):
                    del(fontData.paragraphLeftSubIndent)

                if (fontData.paragraphRightIndent != None) and (fontData.paragraphRightIndent != tmpStyle.GetRightIndent()):
                    del(fontData.paragraphRightIndent)

                if (fontData.paragraphLineSpacing != None) and (fontData.paragraphLineSpacing != tmpStyle.GetLineSpacing()):
                    del(fontData.paragraphLineSpacing)

                if (fontData.paragraphSpaceBefore != None) and (fontData.paragraphSpaceBefore != tmpStyle.GetParagraphSpacingBefore()):
                    del(fontData.paragraphSpaceBefore)

                # There's a bug in RTC's ParagraphSpacingBefore specification.  It adds space AFTER too.  This compensates for that if possible.
                if (fontData.paragraphSpaceAfter != None) and (fontData.paragraphSpaceAfter != tmpStyle.GetParagraphSpacingAfter() + tmpStyle.GetParagraphSpacingBefore()):
                    del(fontData.paragraphSpaceAfter)

                if (fontData.tabs != None) and (fontData.tabs != tmpStyle.GetTabs()):
                    del(fontData.tabs)

        # Create the Format Dialog.
        # Note:  We used to use the wx.FontDialog, but this proved inadequate for a number of reasons.
        #        It offered very few font choices on the Mac, and it couldn't handle font ambiguity.
        formatDialog = FormatDialog.FormatDialog(self, fontData, tabToShow)
        # Display the FormatDialog and get the user feedback
        if formatDialog.ShowModal() == wx.ID_OK:
            # Begin an Undo Batch for formatting
            self.txtCtrl.BeginBatchUndo('FormatDialog')
            # If we don't have a text selection, we can just update the current font settings.
            if self.txtCtrl.GetSelection().GetRange()[0] == self.txtCtrl.GetSelection().GetRange()[1]:

                # Get the wxFontData from the Font Dialog
                newFontDef = formatDialog.GetFormatDef()

                # Set the current font
                self.SetTxtStyle(fontColor = newFontDef.fontColorDef,
                                 fontBgColor = newFontDef.fontBackgroundColorDef,
                                 fontFace = newFontDef.fontFace,
                                 fontSize = newFontDef.fontSize,
                                 fontBold = (newFontDef.fontWeight != 0),
                                 fontItalic = (newFontDef.fontStyle != 0),
                                 fontUnderline = newFontDef.fontUnderline,
                                 parAlign = newFontDef.paragraphAlignment,
                                 parLeftIndent = (newFontDef.paragraphLeftIndent, newFontDef.paragraphLeftSubIndent),
                                 parRightIndent = newFontDef.paragraphRightIndent,
                                 parLineSpacing = newFontDef.paragraphLineSpacing,
                                 parSpacingBefore = newFontDef.paragraphSpaceBefore,
                                 # There's a bug in RTC's ParagraphSpacingBefore specification.  It adds space AFTER too.
                                 # This compensates for that if possible.
                                 parSpacingAfter = newFontDef.paragraphSpaceAfter - newFontDef.paragraphSpaceBefore,
                                 parTabs = newFontDef.tabs)
            else:


                self.txtCtrl.Freeze()
                
                # NEW MODEL -- Only update those attributes not flagged as ambiguous.  This is necessary
                # when processing a selection
                # Get the TransanaFontDef data from the Font Dialog.
                newFontData = formatDialog.GetFormatDef()
                # Now we need to iterate through the selection and update the font information.
                # It doesn't work to try to apply formatting to the whole block, as ambiguous attributes
                # lose their values.

                tmpAttr = richtext.RichTextAttr()

                for selPos in range(self.txtCtrl.GetSelection().GetRange()[0], self.txtCtrl.GetSelection().GetRange()[1] + 1):
                        tmpStyle = richtext.RichTextAttr()
                        # Get the Font Attributes of the current Character
                        self.txtCtrl.GetStyle(selPos, tmpStyle)
                        tmpFont = tmpStyle.GetFont()

                        # Now alter those characteristics that are not ambiguous in the newFontData.
                        # Where the specification is ambiguous, use the old value from attrs.
                        
                        # We don't want to change the font of special symbols!  Therefore, we don't change
                        # the font name for anything in Symbol font.
                        if (newFontData.fontFace != None) and \
                           (tmpFont.GetFaceName() != 'Symbol'):
                            tmpAttr.SetFontFaceName(newFontData.fontFace)
                        else:
                            tmpAttr.SetFontFaceName(tmpFont.GetFaceName())

                        if newFontData.fontSize != None:
                            tmpAttr.SetFontSize(newFontData.fontSize)

                        else:
                            tmpAttr.SetFontSize(tmpFont.GetPointSize())

                        if newFontData.fontWeight == FormatDialog.fd_BOLD:
                            tmpAttr.SetFontWeight(wx.FONTWEIGHT_BOLD)
                        elif newFontData.fontWeight == FormatDialog.fd_OFF:
                            tmpAttr.SetFontWeight(wx.FONTWEIGHT_NORMAL)
                        else:
                            # if fontWeight is ambiguous, use the old value
                            tmpAttr.SetFontWeight(tmpFont.GetWeight())

                        if newFontData.fontStyle == FormatDialog.fd_ITALIC:
                            tmpAttr.SetFontStyle(wx.FONTSTYLE_ITALIC)
                        elif newFontData.fontStyle == FormatDialog.fd_OFF:
                            tmpAttr.SetFontStyle(wx.FONTSTYLE_NORMAL)
                        else:
                            # if fontUnderline is ambiguous, use the old value
                            tmpAttr.SetFontStyle(tmpFont.GetStyle())

                        if newFontData.fontUnderline == FormatDialog.fd_UNDERLINE:
                            tmpAttr.SetFontUnderlined(True)
                        elif newFontData.fontUnderline == FormatDialog.fd_OFF:
                            tmpAttr.SetFontUnderlined(False)
                        else:
                            # if fontUnderline is ambiguous, use the old value
                            tmpAttr.SetFontUnderlined(tmpFont.GetUnderlined())

                        if newFontData.fontColorDef != None:
                            color = newFontData.fontColorDef
                        else:
                            color = tmpStyle.GetTextColour()
                        # Now apply the font settings for the current character
                        tmpAttr.SetTextColour(color)

                        if newFontData.fontBackgroundColorDef != None:
                            color = newFontData.fontBackgroundColorDef
                        else:
                            color = tmpStyle.GetBackgroundColour()
                        # Now apply the font settings for the current character
                        tmpAttr.SetBackgroundColour(color)

                        if newFontData.paragraphAlignment != None:
                            tmpAttr.SetAlignment(newFontData.paragraphAlignment)
                        else:
                            tmpAttr.SetAlignment(tmpStyle.GetAlignment())

#                        print "TranscriptEditor_RTC:"

                        if newFontData.paragraphLeftSubIndent != None:
                            tmpLeftSubIndent = newFontData.paragraphLeftSubIndent

#                            print "Left Sub known:", tmpLeftSubIndent
                            
                        else:
                            tmpLeftSubIndent = tmpStyle.GetLeftSubIndent()

                        if newFontData.paragraphLeftIndent != None:
                            tmpLeftIndent = newFontData.paragraphLeftIndent

#                            print "Left is Known:", tmpLeftIndent
                            
                        else:
                            # Here's where it gets interesting.  The Left Indent is ambiguous.
                            # if the Left SubIndent / First Line Adjust is known ...
                            if newFontData.paragraphLeftSubIndent != None:
                                # Determine the original Left Indent by adjusting for SubIndent, then add the new SubIndent
                                tmpLeftIndent = tmpStyle.GetLeftIndent() - tmpStyle.GelLeftSubIndent() + tmpLeftSubIndent
                            # If the Left SubIndent is also ambiguous ...
                            else:
                                # just use the original value!
                                tmpLeftIndent = tmpStyle.GetLeftIndent()

#                        print "tmpAttr.SetLeftIndent(%s, %s)" % (tmpLeftIndent, tmpLeftSubIndent)
                        
                        tmpAttr.SetLeftIndent(tmpLeftIndent, tmpLeftSubIndent)

                        if newFontData.paragraphRightIndent != None:
                            tmpAttr.SetRightIndent(newFontData.paragraphRightIndent)
                        else:
                            tmpAttr.SetRightIndent(tmpStyle.GetRightIndent())

                        if newFontData.paragraphLineSpacing != None:
                            tmpAttr.SetLineSpacing(newFontData.paragraphLineSpacing)
                        else:
                            tmpAttr.SetLineSpacing(tmpStyle.GetLineSpacing())
                            
                        if newFontData.paragraphSpaceBefore != None:
                            tmpAttr.SetParagraphSpacingBefore(newFontData.paragraphSpaceBefore)

#                            print "Before:", newFontData.paragraphSpaceBefore
                            
                        else:
                            tmpAttr.SetParagraphSpaceBefore(tmpStyle.GetParagraphSpacingBefore())

                        if newFontData.paragraphSpaceAfter != None:
                            # There's a bug in RTC's ParagraphSpacingBefore specification.  It adds space AFTER too.
                            # This compensates for that if possible.
                            if newFontData.paragraphSpaceBefore != None:
                                tmpAttr.SetParagraphSpacingAfter(newFontData.paragraphSpaceAfter - newFontData.paragraphSpaceBefore)
                            else:
                                tmpAttr.SetParagraphSpacingAfter(newFontData.paragraphSpaceAfter - tmpStyle.GetParagraphSpacingBefore())

#                            print "After:", newFontData.paragraphSpaceAfter
                            
                        else:
                            # There's a bug in RTC's ParagraphSpacingBefore specification.  It adds space AFTER too.
                            # This compensates for that if possible.
                            if newFontData.paragraphSpaceBefore != None:
                                tmpAttr.SetParagraphSpacingAfter(tmpStyle.GetParagraphSpacingAfter() - newFontData.paragraphSpaceBefore)
                            else:
                                tmpAttr.SetParagraphSpacingAfter(tmpStyle.GetParagraphSpacingAfter() - tmpStyle.GetParagraphSpacingBefore())

                        if newFontData.tabs != None:
                            tmpAttr.SetTabs(newFontData.tabs)
                        else:
                            tmpAttr.SetRightIndent(tmpStyle.GetTabs())

#                        print
#                        print

                        self.txtCtrl.SetStyle((selPos, selPos + 1), tmpAttr)

                self.txtCtrl.Thaw()
                self.txtCtrl.MarkDirty()

            # End the Formatting Undo Batch
            self.txtCtrl.EndBatchUndo()

        # Destroy the Font Dialog Box, now that we're done with it.
        formatDialog.Destroy()

        # Set the cursor back to normal
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))



#----------------------------------------------------------------------

# Define embedded images 
Splash2 = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAUwAAACoCAIAAAAErkAoAAAAA3NCSVQICAjb4U/gAAAgAElE"
    "QVR4nOxdeVgTV9c/SQiQBMImiEZADKIWrFGoC4hVpOIWcS3YWlutr0trcWutvm3d2rrU1qpt"
    "be1rte76qa2Iu0itG6CgUUE2ASFEw5YEQkJCtu+Pi8M4MwkBccP8Hh6eyZ27npnfPeeeuwzN"
    "ZDKBDTbY0HZBf94VsMEGG54ubCS3wYY2DhvJbbChjcNGchtsaOOwkdwGG9o4bCS3wYY2DhvJ"
    "bbChjcNGchtsaOOwkdwGG9o4bCS3wYY2DhvJbbChjcNGchtsaOOwkdwGG9o4bCS3wYY2Drvn"
    "XQEbnhHOXUg99n8bL6fk5uUX4sM7eHv6+QcEBwfxOnUaOnRYt67+Thz286qkDU8DNNt+8jaP"
    "DFHWymVfJCYmYCFsDteB46pVKdSqGkJkPp//xhuhvUP7jRkzoYu/r71NC7z8sJG8jWPngcQF"
    "8+bKy0vYHG7/AQOSk864efmu+OkYABTcPLt57eLIqOjo4dGS0tLMzKzkpDNYQjaHG9i1y6Dh"
    "70yNHRncI8DBweH5NcKGJ4JtTN6WsfNA4kczpsjLS9y8fNdsvxg9PBoABvbrzeaw2BxW+f0M"
    "AAgOHerefVTPqFmxcXEAwOZw4+cvjIyKVqtqRCLR5rWLQ3sH9+/f/7sffswQZT3n9tjQItis"
    "sTaLDFHWRzOmIIP8vXcmsjmslPQ0APAPCkcRziSnAECfXt11AACQlXkHAMYIR/SMmhU2snbq"
    "hx/fuJWzee1iABCJRCKRiM3hDo0cMjpm7NsTxrq6uj6fVtnQfNg0eduEVquNnzsHG3J7Bg4F"
    "gEuXLgOAp28QAMhyTsjLSwQCgc65GwA429devJAMAL1D+6EkOuduQQGeAMDn8+OXfId0e2Ji"
    "wqwZ04KDg+ctWHTuQurzaJkNzYaN5G0TO/fsv3rlErpmc7hcDx5TmSuRSPh8vrdvAABkZeUB"
    "wKDBkShOdcltkUjE4/H8Xn/T2b4WAJzta48nHAWAUcKYsMihMxev/nP/sanTZgOARCLZvHHD"
    "sCEDhr41fOeBRIVC8VzaaIOVsJG8DUKr1f768yZC4I1bOQDwxhuh6Oftm6kAEBTcE/28ciUN"
    "AIYOE2LxNVUS5JDv028wCnH04Lm6sAFAIBAIhTEAkJx05oPJY0JDQ7/74ceH0vKn2CQbngA2"
    "krdBLF7yX5FIhP1Uq2pqqiTIzYascaP0KtLbdO8wZ/taV2Nh4omTABAe3k9Z74RS3Ui7AABC"
    "YYyjBw+FaKok2/63DQAmT5n67ifLtm7bgRR7QUHB558uDOr1xrwFi3LyS55lS22wBjaStzUc"
    "Tjy9eeMGABg2YTaP18DP/OuJ16+nA0B7XgAAZN2rAICIiIHO9rXKeqfCvGw0PnfxfR3Z6gBw"
    "IjEBAAa++SaW8420C2pVTWRUdJfAHu7Mencvb+G4GDcvXwBgc7jy8pLNGzeE9O45b8Eimx/+"
    "hYKN5G0KD6XlSxbMBQChMCaLE+7XuQsK37Xjt4KCAszNlpl+HgB6h/ZT1js529de/vdfABg0"
    "/B0sn+Lb/xYUFPD5/C6BPVAIQ1N+5NBBAIgeHm1w9AIAg6PXv6f+lJeXREZFb9m2J37+Qh6P"
    "p1bVbN64YdDAsPenz7FR/QWBjeRtB0YTzJo5E5E503WcvcnQMXg4PsLrvfsDAFOZixa9IK2u"
    "qZKcT/4HAPr06o7FRLQfJYxBfAaAS8nnJBIJUuMAYGIUa6ok23edAoDYuLgOPPWo8X03/roN"
    "GfBqVc2uHb8NGhhmM+BfBNhI3nawbfufyFXmGjIbAOoYzGJmd8xiB4CgoEAAKJPcA4DIqGg0"
    "2L5xKwcZ4fixN8HlRlDjbo75ck3X0wl71aoaoTCmcyCLZvADAK5rdX2dHAAEAgGm1cMGRsxb"
    "ut7mlnuOsJG8jSBDlLVg3jwAmDptdnG9Yx2D6ePk6G5HHzD6I0LMm+lpABAcOhQAnO1rkemO"
    "FsMhEFxuDE35pat3JBKJQCBAapxm8KsuuX3gwEEAGB0zlmbwMzGKAUB07cGBAwfZHO7yFZM3"
    "/rpt7pxYAJCXl2xeuzhiYNjvf/yp1WqfgShsIMBG8rYAhUIxY9oUpJDPG8Ixhju5tuvo3zMs"
    "PAJFS/j7b6YyF3ng0EKX6pLbyUln2BwuMt0BgKEpJ7vcThzaCgCTp0xFarxaqUBT6HFxsZ0D"
    "WSZGMc3gV6Nw2fzjDwAw45Mv2e5+XNdq4eRxf+4/FhkVDQAFBQWzZkzr37//4cTTz1IyNoCN"
    "5G0Dy1d+jabEjH7jAABjOM9RTmd5hgo/Q9GuXrn0+8/rkUfNxfd1wC1lxWz1wrxsgssNhSA1"
    "ztCU0wx+snIpsueHx7yLDHUTo/jIvj8lEklYeMSokb5YxTrw1Ph6ikSiSWNGTJ4cZ/PJPUvY"
    "SP7SA5szGzD6o3wdpyOXjWe4Bwc823nGz1+IIqNlcKOEMegnYSkrkFxuDE3577/+AgCTp0wF"
    "ABdnVxOjeOeO7QAwddrsDjw1MtTv59Uh6/39adPxdUvc/3dy0hkej7d1247Vq6aj+bYDBw4O"
    "Ghg2b+l621K5ZwMbyV9uFJSUzZ8zAwCGTZh9WduZzHCuM4vrzOoZNUv4iNgAwOvUSVnvhC1l"
    "xZQ23uXmzqxnaMrxip3rWg0AomsPrl65xOZwI4eNRGq8RuGCFtjNnRPbOZCFlSK69uDnXw8C"
    "QPyCRZ0DWSGDh23//eO4uFgAUKtqNq9dPGTIEJv1/gzwipJ83oJFbeD10hthwdxZyCUm7/AW"
    "wUpHDAcANoflbF/77ifLBAIBSrh/zy5XYyG2lBWbJ8O73GQ6exQTAEZNmsV1rZZrulYrFQl/"
    "/w0AM/4zA1Pjl5LPiUQiPp//5ogPsLqpZcVoiD53Tqygb0cUyHb3m/bRuHXfb+Dz+fDIen9/"
    "+hyb7/2p4lUk+c4DiZs3bpg0ZsR3P/z4vOvyRNjw44+JiQlsDhfNmSGG+7jZERju4cy2d/By"
    "cfKc//kqNocLACKR6NtlS8+fTQSA8PAGWx3vcmNoyt2Z9YV52Yi9EWE9aQY/N8f8wrzsq1cu"
    "8Xi8iMi3UKr7eXVosDBzzsdI1SP89HMyGqILJ48jVDswQIf/uWvHbxEDw3YeSHw6QrLh1SP5"
    "Q2n5F5/OQdeff7rw5VUj5y6krly+AgBGTvlcxfLEGA4ABIYDAItpYjsw/QPf2LJtD0ouEonQ"
    "pjR3L28UgrfMXZxdMaWN1DgA1ChckGKf8N48LOTggQMAEBfXqK4B4MRf15DT/rPPRuPrzLUX"
    "q2XFny76vaCgIDIqet33G5BxUVBQ8MHkMZMnxxWUlD1dqb2SeOVIvuS/yyUSCfZz147fRo6I"
    "fumcvQqFYvGCOWjOrJjZncxwdPYLnuEAwGYxg3qFrft+A5ZPQUHBr5s3VpfcZmjK8S43mc6+"
    "UWmH9UQz4Zeu3sEUO0qeLzqEzpOKjeuD5Ynp9uUrV7Dd/fDVlkqNK1fsR776T+ZGDhpoWLd5"
    "CZpOB4ADBw5GR4a3gWHUi4ZXi+SHE0/v2vEbIVAkEg0aGPb7H38+jxq1EPMWLkV8YwbPptTh"
    "AEBmOAofNX46nufJSWdmzZj27bKliYkJbl6+ffoNdnPMZ2jKkRqfMCmW61ptYhTXKFyO7N4E"
    "OLP8oYS9/uckAFiyeD5GZrWs+Ls13wDA1GmzMd3OtReji/Xrj6NqL18x2dubXlPvw7UXv/t+"
    "6NZtO9DKvIKCgkljRsxbsOglNa9eTLxCJFcoFGjzBkJcXCxy/wCAWlUza8a0l8V033kgEXVV"
    "vaOmAwBiuAenUYe3dzOYYzjL0Q4ARo2fHr/kO3yeaGsqm2kAgBqFi6xcevXKJTcv34jIt5AL"
    "Ha1dDwuPwFzxpxP2ot0peEP94IEbSFGPi/EnVPvn9ftRnt//MNPbmw448rPhslrHwGJu3rhh"
    "4sSJtpNnWguvEMmXr/y6oKAAXYeFRwydsip+9RH8xBIy3V/wdysnv2TBvLkAMHXabCXrtW7e"
    "DMRwgAaGA4C9gxeYZzjCzJkzCTwHAIlE8sHkMZeSz6GR9nvvTMTU+O59hwEgZtw4bCINTYyj"
    "4x8RMi6cRcta58ydh3Q7onFNvc+OLX8jH+Ha1SuRDsdSXbzMeG/GH/LykrlzYlevmo5cg1ev"
    "XBo7Ovpl94y+IGCsWLHiedfhWeDchdTFny7U6bQAwOZwpy3ayHDigb4ueMBIf1/fOzfT0C2p"
    "VHrk8CGmg2NoSB87uxfulEutVjth/Lj8nDth4RFuwVNoHE9XZ2cCwyl1OMvRjmlH7NBDQkLs"
    "WO5pl89hIXw+Xy6Xp6WmFBUWsDncGR8tdObqaAa/swm/Xfz3amRU9MR3BgFAjcJl3Tcr5XJ5"
    "/PyFfQd2Rmnv59UtWLACAFZ+9W7/ARytwQUA0P/E/X9v//Mgm8NdvnJF31AVADgwGg6f++ds"
    "9tKlawEgLi72P7ND/fme0dERuTmVUqlUp9MmnT2Tm5sTPnCQsxPnacn0FcAroclrVWrkpkI/"
    "Z3zyJdeDx2LUsTkstaqO33vY0vX70RJrAFCraj7/dOGkSbEv4B7JTT9vQQtR+G8uUNt7knW4"
    "hzObxTSRGW4uQ7I+j1/yHfJ4q1U1yWdP1ihcHkgrsC2lKE7i3wnIJh81vi+WEK2HiYuLDRk8"
    "DFPUXHvxib+uoSUxy1euGDTQAADY3X/OZv932XYAmDsndt78hnOpvL3pv2+JRmtmAODAgYMv"
    "o2f0hcIrock/W74x4fBudC0QCCInLUL0rpIWl+amunfgO7C53UPeCgzogqm1vLzco38dcnJx"
    "D+kjeH4VfwwPpeUTxk/Q6bRzPv5YxgkhMNzZvtaZ7cpimgDASoYDQJ1G36tXb5ZzO9RwuVyu"
    "ra3YtmOPI8sxLTXllihdUlKSdUeUl3tXKIwZNqY3ANzPq/t21VcAsPKbNa4eDQOBHVv+Tko6"
    "z+fzFy4azWS5AgDXXqw1uFw9n7Z6zRYAWL1q+uAhHigyUuP7DzxEt+LnL3xnSjd8rUw0dv/+"
    "HYvu04sKCwBAKpXu2bPHs32HF+dZvFxo+yTPEGV9Mvt9ZI0DwMfL/nBgc5n2TJ1Of3rvtwd2"
    "/eZqJ/fpEQEA7h344ZFCrUIsFpcAgFKpPH4soaikrH+/vi+CuXjmn0v7dm3n8/mBb84mWOnO"
    "9rX2Dl4tYDi66BoYzGWb0lJTAEAqlWZm3tmze2evvuFXL164m5WJmLZo8RJE6U3f/y4Wl0yd"
    "NntQVFeUXHTtwcYNGwBg7foNnp3aAQDXXlxT7yO69gCZ4vHzFwpj/GvqfTArff+Bh2iabe6c"
    "WALDAYBhrNx3sPrAvj1YiE6nPX4sQV6tjI6OptGeSIyvINq4uU44fjx+/kIXXk+kxgtunkUH"
    "pBw4cHDzfydoxMkAwPXgxcb/hLdg0XqsF2HytjAvGwBeey0YvyidzHA2i9kkw+s0eozh6jod"
    "AEx47zP8JpZJk2InCodfT7+BOSb/STpdo3A58de1q1cu8fl8zHmulhWjNTnx8xe+HlyJFXE/"
    "r+7zTxcCwNw5sZPjOgDOl753ZzpiePz8he++H4qvGMNYKZUav16Tg0X4++g6bDXu5o0bxsaM"
    "fSlmQF4otHFNvmHTTzv++B+65vP5Iz5YzXYAtaoOANZ/MU2n0w6bMLu9O+v2LVHS2TNeztAx"
    "IBQeqXSatgopMblcfmj/3ueu0v/v0OG01JT+4UM68QUA4ODApGQ4imxZh+v1RnSBGA4Aaq2u"
    "a1B/D2ca0ud5eblyLWfS2GGTJ8exnV2uXkm5efPGjWupFy9e1um0S774yiegYVy9etXewoL8"
    "yKjoabNHIzcb1158O7PdgnnzdDotcqfhdfjeneloiL561XTh49NsDGOlpNx95Yr9Fy/+y+Zw"
    "V3717lihM5dTJxwVIC1vl5eXiyp2/nzS4KEj23m4tIpUXwW0ZZLn5JdM+3CWRtWwoHrht3sc"
    "2Fw9g8t2gFM7vsjKvB0ZFV3gPqLWrU/frt4F2em3ROnSe6k9OnPtXPxVNLfe/YYGBnTJy8tF"
    "OdwSpZ8/n9SO1/m1bgHPpTkH/u/oLVF6r96hHr4Cgg5nOzCZdgwAYDIZ0JQOp2Q4ANTpaJ17"
    "DKBpHmRmZgFA2uVzwSH9X+sWEB42oG/YkOSk08XFxTqdNiw8Iu79oShh4v6/j/x1ksfjrVwZ"
    "5+GiRCSXVyg+/2yNrKoyMip67qeTHRg1lAwfMqwHoW75WSWz5x+4X5DL5/O3bl0g6NloZr4Z"
    "0c7BvtO19CwAkEqlR/861LNPGL9zpycW6iuBNktyvREmT47NvnMD/Zw6bXbQgFFMe6bexMy5"
    "emT39p/ZHG7HgfHVBrt6GqOayYsa8IZWUZydnY1Uumen1xwcmOAaGB4e4URXITUilUqfo0o/"
    "mnACkdw/aACB4SiCNVY6dk1mOADUa8t5QdGq8nxkwly9eGHyO1OcnTj8zp1iJr6bmXmnqLCg"
    "SqZwZrcP7METXXuwevUGAPhy+UqfAB+twYVrL5ZXKD5d9HtxcXFkVPQncyM9XJSolJp6n99+"
    "St7+JzXDGcbK5HPFcxds16iqI6Oiv/pqIs9LRqh8r16uGM+VSuWRw4c6dQkWBBPH8zaQ0WZJ"
    "vm37nz9t/AFd8/n8cbPWM+2ZAKCrU25evUCjqp48ZdptXec6BtNEo+npjIp6jsnnTUyll2Rd"
    "6BXo6ezRWUVzCwp5c0j/wKKCe3K5HABuidIPHNjv0bHrM37DEMl7dOd3Cx1GYDibxWxSh4MZ"
    "Kx0eMRwADAZVvcG+T1CX66kXlUqlUqmskNWOixkNAO4uTnGxk0oklenXrqSlpujrGIkJCWiq"
    "fFBUd+RLl1coVq7Yn52dLRAIFi8egxa9IDX+20/JaPHMuu83YG52AGAYK0009sZNdzf9tAcA"
    "5s6JXTS/O5dTR6587t3Kg3/dkUql6KdOpz16ZD/b2SU8bMATCPWVQNskeUFJ2bT34pTKBjWy"
    "5IuvmO1DmHR9nYGVcmhZetrVsPCIm67jDDS66ZGvVk9nmICGVLq9QYZUuqud3LtjZxXNTcfm"
    "9wkf3bOLCxqyKpXKo0f25+bmBPfq+8wGhxcu/JOWmuLl3SlsUASB4SiClb50cwyv15ajz6fU"
    "6jkhr3VIOnsGAG6J0sMHD0eGsZ2d3biY0Wxnl6SzZzIzs+RyORqKI186AGxY/3fK1St8Pn/1"
    "mg/QwlXE8NXfXv7rryNsDvebNWuGhJWZaGysVg/LHJcvTzx16iQArF41fdy4xrNl8di1+/7S"
    "ZbulUqlAIIj/aGTKtQI0XZJ09oyN502ibZL849kzUlJS0HVcXGxQ5CzE8Lr8wxs3bGBzuL6D"
    "F9UaGPWMx1iBqXRt+/59u3o/LMm7efOG6PrlQB93nk8Xbb2e4xUUOXw85pDLzMzad/AvGh2e"
    "zfK4O1l3k86eqddqosdOdmKxrWe45XE4+okxHHkla+wD/NxMt0TpACCRlL733hRs4io8bIB/"
    "95Czp0/odNoOHTr27dPeyYmmNbisW7UDnfS0cdNHiOEAIJUa16w9f+b0CTaHu3XTpN6hHniG"
    "38vMWfjZ3rtZmTweb8uPb/ft50mouZNDcdHDLstWnD/y10kAmDsn9sv/hr7eozJEILiWUY46"
    "8aSzZ2xTa5bRBkl+OPH08i+Woms3L9/3Fm7BDPUNK+cqlcohY6YV0jvXMZiUyTGVHtRrSEd2"
    "dX7OnbTL5+oVRf6Br+sdPOk0hn/w4J6vdat8WCiXyzWq6qSzZ5L/+de3S4+n7Qd6WFV9aP9e"
    "pVI5euRoJ1dvph3DSoZj1+bG4QaDCs9wANBp1B7eviU5aXK5vKiwYOAjZY4gCO7WN2zI8VPn"
    "8nPu5OZUhoYG/98B0dG/DrI53DXr1vO7NGRSU++zYf3faGP51k2TAoIbP94AAP+czZ67YLtS"
    "qQwLj/j22/f8O1Nw9OQZ3fyFWwsL8t28fJd9PuG9OH29wbXe4Nq5U0W/gWMvX8pGPE9LTVFU"
    "K0fgTpW2AY+2RvKH0vJ3YyegwTMArFy5HBnqAJCa+PPli/8IBIIHnSbW0xgm8z0/UukqPV3m"
    "/kZ0/9Bqae7tWzf/ObGvV2cWxysIADjufoKI8T27uNy5k6XTacXikiOHD5VXVAoEvZ+eQ45O"
    "t9+xfbtOp/Xt2rvX671bi+HKeqd6gz3gGF6jrAOAKg2rq68nWgmnkFVOnhyHz5nfuVPUW8PO"
    "J53Jzs4+eCDpligdvzQdAKRS4+pVey/+m8zj8dasW98jmI1Pvndn+pr1ewAgLi525Vc9yYPw"
    "6sqSLdvkm37ao9NphcKY71fyXwvuaG9XXW9wdXIoBoB2LtKg7q/9fewmip+WmiKvVr41LJpu"
    "0+cktDWSz43/9EJyw9JUoTBGMPxjZKgr8xJ++O5bAOg+akW1wY5gqFNCT2fQTaZynVOXbuE9"
    "OzHy8nLTUlPkJRmCQA+tUw+6sZ7jFRQxdBTyvet02rTUlAMH9utNtKdkvbu6uZw+dUosLtHW"
    "VoyImcJkMii3nWCwhuEaegejvh5IDAeAOh3QnP000gypVFoqeRg3Zbq7ixM+/47eXuGDhl5L"
    "u4qcYbNmjBWO6YBuSaXG9euPozMnfv4lPrCzGLPSpVLj5k1X9uw9AgDx8xfOmu4BJOTerZz7"
    "6fmUlBQ0Wz7tfb92bop6gysiub1dda3W7+QZ3Y8//4v15gCQlpqSn5czfsJEm91OQJsi+eHE"
    "019+vgBdszncmV/twgz1Les+lcvlwybMtmCok4FUutzAfMh6Lbp/KDbH1sFR5tUpEBgsYLDa"
    "Bw8fObCrWqUWi0uUSuXTs97pNLidX5l2+ZxUKh085E0vb59mMVyt1ekMRnjcl16nBaBieJUK"
    "AMBYV+HXqUPa5XM6nTYoOIi8dLyjt9dbI8ddvJAklUolDxWD3uzr5ETDGO7m5bv1t0+8vel4"
    "hmNrXbb/OiVysDO55sjHplQqBQLB5p8+GhgqRqwGAKTGJRLa+k0Pf916AHn+/vPBmzl5DePz"
    "zMwsm91ORtshuUKheHvCWKxrn7Po604Bweg6NfHnC8nnkKEOAHo6w2wuVDDRaCYaDT/HlpmZ"
    "Jbp+OcDPm+PuRzfWGxx9uvZ+Cxuoi8Ulu3f+UVRS5uvn39HbqxXb6NXOdc+ePTqdtqZa9taI"
    "CeZIjnek6/RGeKTAAafDFXU0SisdHjEcAEx6NTi2y7t9RaOqdvfogObSCHB3cYoZO/78+aT8"
    "/PyzyXk+PmE/b957/fo1gUDw4w/TMQ8cANzLzJn2n9/E4mLEXv/ONAO9Hd3U+PUFSbn7p58d"
    "PXb8PDzysXV0z6nV+tUbXAHAyaHY3q766An2gi//vXXzGlLyCz+y6x6oGzqo8/HzNWjNErLb"
    "bTzHo+2Q/POlX5w+dRJdR0ZFD327QaVLS+5t/HYhAAyM+eShjmu9GidAT2cwTUYZs5PgjeGY"
    "Q05blefqI+CwOYAN1F/rVlp0V6lU3hKl79mzp3UH6h29vdJS0/LycosKC0J79/D1Jy4aA/NT"
    "ZfCI4TU6hp2ptkmGG+sqJBo3pZ7Foxfl5eVyOKz3pk5jUPUqzk4cxPP7BblJZ8+giS50wBMW"
    "Z/+Bh0v+uwUNsBcsHInWuuAZnpRUMXPWeqlUijztQ6M6OjkUIwWO6C2R0P77rXzbH4c1quqw"
    "8IitP4b2DWloF5cLgqDuZ843zKvZeE4AzWQyPe86tALOXUgdOzoabURhc7hbtu2pYQtYjDq1"
    "qm7Hmg9EItGwCbOzOOEGeitsyGEZdPU0xgBWScrxLehMyKnTZnd9Qwj27g0x6mUVeee3/W8b"
    "qg+Px4tfsGjmh9NcXV2fvPRzF1KHDRkAAHw+/+DhBEeXxwYFlFZ6wy2cp60hQlMMB4BaRaVz"
    "3d3DW7/g8Xg5uXlOnMf8Z3gUlJRFR4ajs3d2b/sQ70vftDEdrYSZOyd26nudCQkl5e7b/7iK"
    "PuogFMbE/4ft0q7xQ0uI6klJFet/TpKXl7A53C8/nzh2lBpIyLjJWbL8NHZK57rvNyxetMBc"
    "bV8ptAVNrtVqYyeNE4uL0c85i77mdIliMeoAIOfi9oSjf/P5/Kou7+KXvjwJkEOuVO/StdsA"
    "5JC7JUrPE/3r59OBg84zZLA0nKBhw0f5eHHz8/NkVZVJZ88cPnzYkcPt1i3Q3r6FpgQCv3On"
    "3NwctBalprpq0FAhdssyw+u15SoT13odzq6v0DE49Rq1v7Mi7fI5g5G2YH68o6OjuYq5uziF"
    "Dxp64niCUqksKjGFhgaj8Tl+rcuYCb3w2hsAcu9WLvxsb3r6dczH5sh2cXIoRsNvpMBXrC1C"
    "CjwyKvqX9b0wBf4Y9CUm4Fy5psaWxCWdPdPRp7NtCzq0DZJv2PTTnl070XVYeET0u4vRnJm0"
    "5N7arz4BgKFvf/pQx7XGo24l0Cgdc8jZG2T5+flpl885mSp5XV6r0rA8OAAMFngIMKqXl0mP"
    "H0s4dfIknekYHNTjSdzvwb36Hv3rkFKpzMzM8vPx8vHvybSjm2N4nY6mN9LgkZvNSoYDANOg"
    "1jE40tpahqr8bkYy095h0cIFFkgOAB29vXr2CTty+JBYXJybU8mxZ65ctQ9b6xIyoAfDWImP"
    "j/nYwsIjfvhhxsBQMeJ2rdYP/T95RvfRgoS83LvYCJzLpS766KkOHy1IEIuL2RwudnZA8vl/"
    "+oYNse1jeenN9QxR1qCBYdiO8T/3H9M5Nywp37FmxtUrl4TCmBtuE1vFUKcEy6ADgAi71MP/"
    "tw9VI37+Qs/AoVU6d3SuQ5UKPJiy/OuJWASBQDB5ytQnMeB//+PPWTOmoeut23b0CWvQ5+bG"
    "4c2y0tn1FWp7z1pFJQDI9EY/Xc7hrV/w+XzRrdsWzHUMOw8kfjB5DPYT7VTx9qbjGZ57t/KH"
    "nzPQEbHIhsdG4ADg5FCccZOz40Ap2vAfGRW9NN6dx6N+UTNucn7dkYc+5Iis/YRTRrTXDQDc"
    "vHzPnTkZIghqstptGC+3Jq/XwwfvT83LvYt+xs9fyAkci9T4naSth24462MAACAASURBVA8d"
    "5PF4Tr0+lBntW8VQpwRaIVdk8n2912BsOr0kJ62rryey3tn2UKVhsbwFw4aP6tnVu1Rckp+f"
    "jwz4godafz+fFqx+D+kjkFcr0UL648cSAvy9/bv2Ik+GIx1OZniNsk5b36D5sdkyk16N6XD5"
    "I/7n1dR1N965JUrvHdL3Px9Os6ZuguBuaH07AKBdqDwvGd5K3/N/uiX/3SKVSvl8/ub144dG"
    "dQQAzIVeb3A9eUa3+MvDebl30UI3Cwp8yzbT0mW7xeISHo+39LNJn0wv4TpVvyGoKSnrgzYO"
    "alTV19Kuxowd/yKc7fO88HKT/Icff/zfb1vQtUAgGD1jLVr6wlZlfb3iS51OG/3OkmyNeysa"
    "6pTArPdSTvDwfiFaRXFBQUHa5XM0dal/4OvAYNXpwIMDVRoWzS1o0OConj0FlQ8LUZwd27fn"
    "3StxcmnXXKsycsjge/fy0d7vpLNnWM7tXgvqBRYXpet0DcQmMBwAMIYjNV6vUcv0xjqjycXe"
    "rjorUSwuEb49a0RUuJV1Cw8bgPogpVJJA48B/RoMFkm5++p1Kehcp7i42B/WhXXuVIHoDY8U"
    "+Pc/5W374zC20I16BA6QcZMza97VM2cvoaz++Nmve5cC7O5bg9RX0j3Q+Fwqlebl5Y8fP+4F"
    "PH732YBIcqMJmqXzmhu/FUE4E+LjZX84ubgDAJOu3/vrKnT24HW7AU+b4RiQsYCm0/t41RUV"
    "FtBpIAgbAYY6laqWY6etM7IQ1U127PAho3r2FDBMmsKC/Fui9N07/ziXlGww0Tp27GilzrGz"
    "sxMKhVdTr6PdMmmXz3HZps7d+wLVonQAQAwn63DAjcPZ9RXlahpiOACIazWv0+6d+XsHm8P9"
    "39ZfmmVxRA4ZjOqWmZnlYN+pVy/XpKSK+Qu3YgPsdyfzgKTA5y7YXlRY0KCWZwKlApdIaBu3"
    "mr5evVsulwsEgvXfjJocUwDGakK0/n0Dki/K0SKZvLzcmlr1Kzup1kByowlMADRaw39rgOjd"
    "ZHwsZ3Jac3laiIDP88Np79+6eQ2FxM9fyO89DF3fuZxwYNdvANAxYkGtgdHcpS9PCKbJCAA1"
    "d47K5fL3Zi3VsLurJOmbV0z38eJ28vGt0rAAgMbk1BlZNGe/1wUhPSPi/NsZC4vEhQX5x48l"
    "HDiw/1ZmvpNLu/ae7sgPjxcFQSx2dnYxY0ZfzxA18Dw1hWGs8+3WnWHHAQD8thPEcFkdg26s"
    "B4AqFTwy7R/zpWNWep3RJK7VdGcob538QalUzvn44/feeRuV3mS3jp4O085u2LBhR4/+LZfL"
    "r6VnZeXQ/9yVoNNpI6Oi1617H/nYUHykwL/5TvTnrgQAiIuLXbW0szkFfvQE+4uVyWiL4dw5"
    "sWtXenb0LAAAsPPF85zjmOXoaH/ttg+SDBKOf/cQyiMAyC162qrLSkm2VmVoJpPJ+MijYW5x"
    "v9FEvIVPQriLfpIDCfGxCOQLc0XjE+I9TwKB4ONvDmJJ7lxO2Lx2MQBERkUb/cYV1zvW0xhP"
    "z/FGAMug66pOPXvkt7DwiBHTvoN62Z8/xGNfbomLi/XqHOLpG1SlczfWVdBZngBgrKsAAJBe"
    "uHghGfmiUKMGDX9nauzIXq8HIQmYE85DafnEiROR5wkVMXb6YivdbACA1+EoXKY3ims1Ax3u"
    "o4UAAoHgn3/+4bq4kuuAHiv5aWLheLcomuKOimrcT4qcbbt230d+Mh6P9/GsaMo5cACQSGhr"
    "NsuQKy4sPGLOtMCQntkAAHa+oCeekJ9xp8eKNRcwsSPgnXCUL5u5cMr3n/zONxd4oQEQ33Mr"
    "62bNXZrBaMKeSguAryU5HCueHNNcoeRw8ttTVlb+Rmgf/LIHVteJaGIcQZZzYu13G+XlJW5e"
    "vkPHzUqp8wWAZ8BzlkHnZ6+5dmCxWlUTv/YYneVpfHhp89rFfD7fzz8AvaAAIBAIXu/d37Xb"
    "SE8uo6LG8BjVAcpFey9duoy1DmN7cI8ABwcHwpuBUFZG5PnQKauAiuHQlC8dABDDT+5Zp1bV"
    "hIVH7Np3yN+nPaGl5LeTcI0xH3O2szncvXu/6OZzE5shw/vY4+JiF8Z3RjvMyDh6gv3NusNq"
    "VU3jYhh9CZneHMesvOKRf+wzorU3AoFg0dyQ/0uoRCttUMily1fYbDaQ9BNlh2VlezHgM7Es"
    "MbyIKKtBgDmlSPhPWShj+fIVTzKHZgKgTG7C/VHGNFcoORxLiN2a8u676enXsQiV5WVdAoPR"
    "gLwBbr0GDxtbryjKvnPjbkbyYF+jE9dPpaebgPb03OwAYAJaB+X1nFtXIqOig/qOYoPs0LZv"
    "5HL50Lc/vesYJnhjeGCXTlAvz87OviVKT0vaL5fcdWHWObjwTHo1neVp0qsBgOP9+mv9RvcL"
    "7c1xpJeVVYjFxWmXz/2+dcvx48ezc/PVOpObC5fDeWzcznXmjBw5KiU1DZ0Yn5mZxTFWePP7"
    "o7t4HY6sdGNdRWmtg1LPApwvnZLhhw8f7tTxMYbTaY89WfRu4Z8yjfbYI+sV3E1RrUxLTdHp"
    "tLk5ldHDQwCg3uC6a/f9r9cliMXFaBZ98gSdvR1xXA0AGTc5y9bcR6a+UBizcXVQ314FYKxu"
    "ZDjOUD90YtBjxvxXdV39/g3gv4YNzqVSqUqtGTk8mvaIEjRS/YHqrUbtwpqGv8ZC8PzEIuBz"
    "IJSCjXZNuGrQaY3XBBKZcAlRWaZHxZmgMS25UJqhxUr8OYFOg3lL1yODHI/4Jd/1HBiDD0GH"
    "q6OYPB5vwOiPUup87U2GFi9ftwykxi/8MRsACGrcGPZVPY0BAPYmAwCEsCXaB9du3EjHq+vX"
    "e/d3bd8FXLvTWZ6YVgcAUORkpp+/eTtbXt6gtXg8XrcewcGhQ0dHR/jwOvr7tmfaOwCAWq2O"
    "GTsesxemTpsdMny2BSvdnA4/vPULABAKY3bt+hNZ6U8IXb125OgYVDGhMObtmHZ4Bf7hO3Qe"
    "z4TUOz6VRELDZrwbLXmkwAEIOlxS5ocZ82hePdDvJHb34vWJ7834A/t56Nip8aOHg3lzslmw"
    "nEmrFPGEWb18JEf46/jp+XNmYCRBEApjoqasRF8FQ6gzsKold07tXYtM2ac6SmcYjd0e7ElO"
    "OhMXF+s9YL4Hs2E0PnHWtxlqHtazMIxGe5OhnsboylS1s6vSPrh2924mNnrk8Xh9+oT6B4WD"
    "a8Pab3mN3o1rBwCgyCm/n5GTk4uN2wGAzeEGdu3SvXu33qH9ugT2cHF2nTNjCpZb/PyFnsGT"
    "gMqRDrhxOJnhcXGx/9u2HZm1rYIicdmbYSH458Xn81csHRzSWwUAZIZn3ORgg2qsI6A00QFg"
    "y58+23edajTmo3M4jlkqTRD2HwDW/zYcWyHD4/Gup99o3741Nwi+yGgkuQWXgzlXmYXIhEDy"
    "T3NjjyaBckBOncWfLcIUFwLaDeLefRQWgsalBSm70Ec53Lx8haNGXtL3B4BWpDpejX+95USV"
    "zp2gxskFMYxGwOn2mkpxeUEqnsBh4REBgUFIvcPjbAeAoqwrYnExPj4AoO/+Yuv/ACB+yXf0"
    "DhHo2rIOH0a7hD57PnXa7P/9/qud+UmJlvmZ/jp+etKYEVjTNq4Pw1aw4qNJJDTCoDqkt+ox"
    "BY7jecadHphRgJa7BfqdJNAbQaUJemeWGhNXXFzs3n0Hmt2GlxOM5ctX4CfDCIMBII0cABq9"
    "/4TpMfI4hzDHRnZpECbM8BfYUAcDuosyN5qgo7fXxAnjVUZX/Md30bENbg56Tz+BnsFl0vVM"
    "eybTnuncPig8UuhEV926ee2WKL0z/X6wv0+p3sXRqH/yOTaG0Wig0Z3z/0QfCQOvAR7MxtG4"
    "uWXzaAkNWjBXrnOSMTspvcNDQqMHCTpxOKxaLeTn3LklSk+7fK5f1GQAYDk0dBPyelcNzd2x"
    "vaB7yNB+UZP7hfbuF9qT48R14TobjXpZ1WPrw0uL7vboM8SkV6PlLmgcLlfW1WvUgGP468pL"
    "f+37DQDi5y/85ZfNmJzxMz3YRZNTaJQRegQGKLQc9LCMRsOISFcuF9BJL1gcihmyDrpGYtNd"
    "wFjdMAK3892ynYuOcEWj+qmTiju0u0rJcACwt6soLeuPjm0HgMzMrC7dQ3r37IbZsZTTty2b"
    "vrIwQ0xmGTlmk1N6zZqBAwCaztBCc53gD4TmOMytyZys8ymdh3QaHE48vWTBXMJ8CZ/Pnznn"
    "Y1bXiSaNDBnwSKVrxMm///oLioys93wd5wkH6iyDLoQtObz1CzaHu3T9fmvUOCUwS95Ap3dn"
    "KO0VorNHfhMIBIPiVgEAKHKO7N7UrUdwcHAQOHrj7XksB7yqv3h6H1JcYeERocLP8AvaMB0u"
    "rtX4ODm6PTx39shvABC/5LsfV39mzr1McOFaftzkmHTaY4NzgUDw+5ZoTI0TZshWft6p0T7H"
    "gFPg2K7SuXNiP/pAjChtjuEqTdCqH32QdYCBz+dfuny1fXsvSn81UFmdZN84odWEC0ImhFvk"
    "nMmpAChyozSHKZ8LumYsW76C9JisgonkhLTeYW5N5kDlkCRHM5rgtW4Bb8fGSSRitMYTQS6X"
    "J50948mq6xgQqtPpdTo9zdEd9HV2Lv79hsYGdmLfuZOVl3v3/s3jg32NLK6/3MBsmVZHalx7"
    "Y5tUKp3z8ccabqgHU3b64CapVNrc3W8Nip1GAwCVnu6hKy3ITh82Yqxju67yGj2r7m7SubNF"
    "hQVpqSlpl8+lJe0vzb6oLs+mK/MYqtx6I8PLsRo0laCplNMDNDT39l3fVD1IRyfV9AvuoHTs"
    "gS1oAxzDvYt3nTq6FwDWfb/hm68WkadF8PK3/nGTY5oA6Ay7AWGD9h38S6OqlkqlSlWnN8Np"
    "AHD0BPuDmbuLCgvQYrjF81gNa93oLgDQoMP1JQAgKfPb+D/u16sbzoda/82od2KO6fRe6A8A"
    "7O0q7O1wbkuAvQkTPlmcgVkHVXINOj5ILpdXyGrHxowmeLCByqENpAtK+RAuyLnhb1G+24RU"
    "lLmRK4Z3qpMl33JN/qKBToNt2/9ctfxLgjcOjdIdfSIBgObobtI0fH+nRlmXf2UnGoUCgFAY"
    "o/QagbR6s8bqmBrn8Xizv/i9xWocD4bRaKDTvUXrRSJR/JLvkNLOTPolOemMUBijte9QXpCq"
    "VCoJxgu+yZHv/wQAbsZ7aHLBzct39IyNhOUuPk6Ozjm/oyOTf9y0afq0D5pbz5Zh7/81blOb"
    "Oyf2xu0H+D1kjbvNMCv90SD86Jnu2Gz59KkjkAJXaYIAgOxpA4C84pEE6yDQ7yTB0372n5Qh"
    "g/o/m4Y/L7QdkiPcKyhZs2YNRl0MQmFM3xEzuR7ED3TUVEmyLu7CDLnmUh0Z2PSrXxcUFCAX"
    "lwdTduT3L0Qi0dRps88bWngWDcNo7MpUXfhjNpvDnfFVw2e6t309Ra2qGfzhb8X1jnUMJnL1"
    "tbOrAoCaSjEAONQ/rJLJRKJbalVN/JLv5PQAAKA9PIukERcXK/eOwwbheIZv2bbn3beFZmvz"
    "FPDhjDn4Z0Rc64a30h8p8OXrSrEpEjRDhugNOIZjGao0QUfPdP/vsu3waKXduzFHsLvTFvXH"
    "/LVh4RHJ588xmA5Pq6kvABhffrXisTG9sRmeBiwyuiCnNRrBZHosTpNZWVkTwl3sp7u7i3D0"
    "6F5v9M/PzsIOCQGAvLzcf07sC+zEdvfphc/Hgc316RERHils72zIzMzKy8u9f/N4T6fKbrz2"
    "5TonpsnINBktLKFxNOpD2JIr5w7z+fzwEe/XGVkqSXrC4d18Pr+Y1/KzaByN+gCHsrsZyRFv"
    "Dvbq0ldeo2fV5V3+57hAILjffogJaHSTyUCjy4z25TqnhzqujNlJau/3kPVanZugt59bQXa6"
    "fyd3hlswAIAzn67MlUqlhUViv5Bx2KJ0yPzfxX+T3bx8t+/a+fa4UZgYTU952TZCWP++aFk7"
    "ALA53IM73npssTpmpRurkYPtk0UHxOKShqMjZj5ADjYUF1PmmJV+8frET5eV7N1/CgDQ+pkh"
    "/Y7hS3+t++u792eia7G4xKczv3fvtnyADOOrZStMJsD+ABoeM/a8CReEyCgcpSKkxU6jsJwz"
    "uibkbDIBUoH47gP/ChLywYcAQLeuAePHj9cxve7cTMPOCQGAtNSUOymJ3l6e7h34eClgVPfx"
    "4pY8KM/PuXM3I9lDdSfAw8GZ005mtHc06slUZxiNDDAVn1mnVCrRXhQPDpzet1YqlQrHxt4z"
    "+bV4fs4ENK+Kc3l5ucIxMeDUmeVAVxRfuyVKfz18bI1dx3qGHfLMozE8+kM/mSajM6fd/ZvH"
    "5XKFv2Akyq07j4EWnPXu9Xq2it3NrlaR8dv169d4PN6e/YdGvDUYRTMaG58Xue+23INjIZTx"
    "ydcsFseHH3jiWKJOp9XptC6uQW/0oQHght/GagDIuNPj0y/voPNb4+Jiv1vZbUi/Y9jwm+OY"
    "ha45jlmI4SpN0KZtIXiX+5z3Tnq45hPE6+Gar6eNxTzt2VmZsbFx+EWE5IYQGktuEaU+M6fk"
    "KEWEccGy5MmZN6kgGV8tWwEk4PlJuKCMSac30BLPbQvxCRlSJsF3Dfg4eDITMkQVQGCzOcOj"
    "wkeOGvPwgQSdH4CgVCrTLp/DvkOOL1FFc+P3COnTb1DPrt5aTV12dnZBdjqm2Fk0u0qTA8ug"
    "Q4rURKM5GvVd1amitH8EAkHo8I/qdKAqufTkahwNAUqv7lEqlf3GNnzvKTPlqFhc0nvQuIc6"
    "rgXvoAloMqO9V+3t4uLiweEhGpo7AGiYvlWFl5VKZafOga4cD/GF9dnZ2Xw+/8jRE31D++C7"
    "bLzwUc+L/4/9YR0rwGPh6OngHxzlNZqf6x4YUFlZic69uJae1b9vv46eBQ1WurFaUua353DD"
    "DBk6W2JyTAHXqRrRG8HergIxHP28eH3i+3Myzic3ONh+WkPr6vevOUEJgh2OnjKita5yuVzH"
    "9IoeGg6P6IHXHJSNxa4x+WANx5IQlBymtAhvNYqMvbp4acOjtxrPZ+wnAlYcvqMhkJ+a5M0F"
    "gYdPFRZKIb+p7b283o6NI1vvUqk06eyZmodZAR0d7Vz8ZXUMFtPEYpoAQEVzY3n3Dg4dNnxQ"
    "EMvBsVTysLAg/25Gcnnexd4usp5uKjs7j1oDg2ky+tlrbpzbrlFVv/3BQo67Hxta6FQnwNGo"
    "97PX3Pl3P5/PDwwZjgJP/t+vOp3WS/B2hdHB8geeHI36AA+Hxyx2ADdGRV5eLtTLy3OSi4uL"
    "BQLB7n2HegZbOhSJsofF37KQyjIwqgwM63f48GFktN/Oqnkn9jWkw4+e6f71uoYDIebOif3x"
    "a0PH9o9N/uN1OADkFY9c/j1v7ff78S53go+dAHu7Ckcn4fl/Gr6ylJeXO27cBHd3F0KXZ6XS"
    "siaJhXB4XG7mpG3uWRDCCQ/OZGolkr/g6NY14J0pH3QJCMjOysR/WEcsLkFU7+lnj6c6i2lS"
    "GR1N9u3bBw9/c8hbPXsKOI700tLSvNy7t0Tp928e70y/7+sMprKU7Ds3IqOigwa9X6UCNBoX"
    "CARF7sMsf2vNMpgmo5cyvSA7PTp6GMf7dcKAHBkRlpOTLfYOzrVpqSlyuRzR4HDC6a58fwuZ"
    "PBuwWI68Lg1Gu1wupzGCOnZw+3ajPfo6Slh4xOrlb8VEPzaDQDDRVZqgQycGfbQgISvzNgCs"
    "XjV99ZKrfry7TRa9N2HCHzsbv7KkUVUrazXC0RRfj2gDeFUOxOGwHT94/wPhqJG79+7FFsMg"
    "XL1y6eqVS2HhEaERQvfew2qUdXo7J3eWAYBVo6wFe3fPgIghARFDxssqSrIy08/nZmeKRCJ4"
    "tEAyOOpjqJd5cNyPnN4HAAH9JmWoW76tlWE01jGYtdIsAPDqHAIAblw7RW4hAHjx+1cbdJSL"
    "drAVsvU0hp+9xrn8FABIJBI34z3kYy+XNkwrRkZF79m9y6PdC7FsW2+AMSOGT3z7HeRp//nX"
    "g9t3cdGa3NWrpo+NzgHIJiTBJswA4OL1iT/8nCESbYdGl/sRYhkk5BWP/GxZNkqFgc3hurbv"
    "YscAvaGV2vYigabVtakpNGtQVVlOpjoC2rzt6RukZ/sCgJ2+luvMktUx7PS1jZHqZRU1BnTG"
    "Q/fu3YKi5lepAJsb9xn8GZqBa4hLaxg/W7/oDU2eAUD82gafcHri+qtXLmEbXRiPxoiolHoa"
    "w95k8LPX+BpFpeIibHIoLi6W2SUWAHSFB9EcoVAYs/X3318QhmOoqiyPGBiGPYuGs1nbEzeW"
    "4+fJVJqgLX/64Deo4WfIzIFy3RsACIUxy1d9a3nw8lLjVSQ5AqL6/j27CHs8AIDN4Y4Rjgga"
    "NLXxoygAejunx6iOB+74F4FA4N6uvZ2LP7edT6Xeo7jeEQDQtPZjKWjUzjN7kwEtrUFrUVHg"
    "5iVj2Bxu+/GbUVbwaD9MO7uqmkqxQ/1D/D42Noc7NHKIf1A40uGKOzvRkQlh4RHHT57lsC0d"
    "nP68sP/wY8tjPpt9GpshwwNT4JRrWi1jb8IEtJAGHygQCL5YtWbMiOGt0IYXGI+RXG8E89/J"
    "bBrk5PgQC5lbGa3J4pqbAwCoaxUJpy/t+uOX1JQUwhsAaNV3hNDTNwjPdgrUy/KvJ97Lyyq+"
    "X0hYb4e2giLaAwC3nQ8AVOobvteLugACghV/JyYmTJ0227XbSHmNHq1a4/F4Qf2FAKCvLtLU"
    "qbPzi7Ht5QgNm8yDg+TsgSiE9vBs4omTKJpQGPPdD5u7+PuSi3tBMHH8WOz8lt3bPhz0xmE8"
    "zzEH2+b/qVE0tEFt0BuHm8z5kVX/WFeOfbuK7dQKG+ZfcDSQXG8EgAZuYNeEQDwPEVAcfExy"
    "NHI+lDHJpRDKIqSy0C8QqkSuCbnmAHDlauqeXTvPn00ksBRBKIzxDwq3hu0VNQZQ5CjKCkvF"
    "RcVF9x5KK8h9BwY3L19358fG2BqNBlUAW82qyD1JXsAHADwez9PTs3v3bl7ePHD0RnobANyM"
    "94qyruAPPMKUFdZkc0+KDIL88eHWdNnQVA+OFX0ns/E0uLDwiG0bGsY7mH2OrWmFRyP2JhU4"
    "/igoDGwOd+Lb7yxdupTQ5T2JhrPQZHIg/gJIYic/nRZUg5CcptI2z1zHE4N8C4DiroUklhM2"
    "F4TuxnIdyIXa0UH8oOz8uVMHDxygVOyYJYyxvUoFHoQDlOtl6Nsp6MMpAIBoDxqpolotr3xY"
    "JZOVSR9oNBoAkCuUhFLYHK4Dx9Wvo3vDzjMARe7JUnGRVztXe5abqwsbHL0borp2x/afuXHt"
    "UM9y5eI5zG4PC4+YOfezMSPfQiY64d0yJzoLsqKEhZeB0I3isyKXZUeHzz5bhPb8A8DqVdPf"
    "jTmCBuF5xSPJa1rNVugRKO3zyKjoJV+sCA/rT6mKCELAIlCqEELTyO8enm/mdBWhCALDyT2s"
    "BcVJzhnLrdkkf0WQfTfr/Pmz+/fsyssvpFTF6MCmoKDAenY3sHfHjl4BgAaGcwAfSIAHU1ZR"
    "04Qnl3AOFH5LKeB2lZbfz7h+PR1/tsyESbGjYyaFh71k+y6qZY0eODcv3yuJnQCgBQ42Svtc"
    "IBDMmTvvg/c/gNZQJy8XbCRvAojtZ06fwZ+yRgB2hIunb8MwskrXaNV7MGXYT3SNDmPG/jdZ"
    "B0TvBlYDIKV9Ly8LO54VAHg8XkTEwOEx7w4b3M/F/cXyn1uPPbsbT9qOjIqWVZZhR8EtW9C0"
    "gw0/aMfg5uX73vS5S+a9//KK5QlhI7m1KCkuuXgxOSvzzonEBAsjbTcv3x5d/QICgxpMa9fu"
    "6NxlTy4Dz3wL3CYf5AgAirJCeeVD/NmP8MirN2hwZJ9+g19qbmMw6tTR0cPxnZeVDjY0qYZO"
    "esOHx8XFfvr5V8E9AmgMh1dNgWOwkbzZMBhNeTl3MzKuZ2XeyczMys3OJA+tCUBOMvd27Tks"
    "Rw7HEQC8vHkP6jw6sqqw/+x6MQDU18nLKxWaOnWZ9AHldnE3L1+/ju6DBkcGBfcMCXkjsPtr"
    "jBact/aiwo4Ox041HgXH5/MT97VvUoFfvD6R/CkFbPj9tOr68sBG8idFtaz8gbQiI+O6QiHP"
    "ysq7l5dVJn0gU+q0KoVl5jcJzAnn4+Pnz+cHBff053fv0sXfy8urLRGbjLiJjdNp545NtuBm"
    "w/vkMPD5/MVLv5z87vttW0rWw0byVobBaNLXa8vKylUqZZFYrFLpyiT3AEBSqQeN1HJaXqdO"
    "AODq6ubA8ejo7enD6+ji7MjitrN/ktULLyGuXE0dOzoadZGRUdE7fkglx8EvesPA5nBn/GdG"
    "/ILFHbyJn3x5lWEjuQ0vIj58Pw6b30ZrY/B39yZM+GXrGcKKBjT87vFam12d2mIQVYTBaEIn"
    "saML7CchAj4Qi28uDj4COUNCWspwQhHWZEJZc8rGUjbTQhJzORBCyKmsb7jlhGThW7hocbua"
    "rJX14S1IOH3WfHSGPACcSGpcTXzx+sSY9/3/u2w7nuFh4RGHjp36Y+cBMsOt/HaIuRegxbk1"
    "N0nLCrIStJq6pn2OaGxjMJoY9GZ8cQUbEVlOYiFPfLmEfCzXBLtLTkiZHB/fXCnmri3nYLm9"
    "FvIBM2InFGRNcZQSMFcoPhWCBUGRK9akxLBo+MzJLWXQaYSROQCQp8fQwdv/+c8cB0dHQm6U"
    "mZNLwYdQyoryyeJjmntklNIDK3hkIS0WbuEnOcQqktvQlmB9T92sPt2aTCgzNNc/pqamDRsy"
    "AF3z+XzCtCV++N2sSj5ho6zvVS0oDEJgkyKypiYWMqEgub5eK1M0ftRCp9XCE0ClUgKATKEM"
    "7t7FydWzyfg22IBgMJpGDRtM8JwjCIUxnyxcEh7Wv3XN2rYKikMjysrKL15MduB4aFVVAKBQ"
    "yMlxrISktLRcKikRPxCJbu3cfzD6reiW19SGVwwMOu39adMJJA8Lj1jw+X/Ri2RjuJWgnptR"
    "KOR4hksq9QZ1ZrP/4xj+hDPGNryaEI4a6ebVsFeMz+ev+37DF4BTXgAAGzJJREFU8ZNnbaqi"
    "uaDQ5CqVUlJaalBnMtjBaHZXUa1WgD1AYbP+19fZGG7DE8HdzeW96XOP7N40YVJs/ILFXl4v"
    "/brd5wI7ysG6olqtqLYHyKuvk6tUmiqZzJHF1tSpm/VfVllG3sJlzmGI3SV4X4HkqyQ4Qilj"
    "kv2NlAU1GZPyLr4O5upmoZ7kQLJPmHJ2wFyT4XH/DaXH2HKLzNXBggSA6vFRVq/JB2EuKwCo"
    "N9l/s/zTb5Z/aiEHKwt6qslbMZOngUZNjtFPplDey8sCALVKqVQqMa8mNm/pwHHVqhQOnMeO"
    "1NCqFOjCgt4mOFEpx1TmbplLazkcA9nnSZ4yoXRsWqgkkN5OfB0o2Qg4QhIyJ/QO5HBCzpbj"
    "UGbFoNMoux5zQiNniDXZGocw5aOknN8ipLLQMxIERU5CrhJlz0upbCw4usnPi3yX0HBCq8lp"
    "zU0rUM7PUVaMLEzKfKhPay2+X0jedIH9RBctNsJb4C8x9xZanydlDpTvdAtq1awIzergCNy2"
    "kLMFfsKjx08WgoUmWO49WyxGayI3+bCaVQeyDCkpYTlPcleFz6S57ye+hyKzl7KXoawMZW+C"
    "5Y/dpSB5tVJBeQSSDS8vWtCxPmHCFx/W9HRPI62FHFpR6+CvX62dDzbY8ArCRnIbbGjjoMlV"
    "BoMRGDiyV1VW3Lx1kzJ24t8J6ORQ5IQjD8unTpstHBdDmbZ3r94e7RpWvKESCeVaA4MRAFqY"
    "1lyGrZKPDTa8sLBDtDHg1ra6unsOGTIMXWN0QhEK87Lh0WEGmDsdj6CgwKihDWnxeWI5GEgr"
    "5Qm8xbMOi4xCsJjkhIQ45HIJP/HhlPkQakguBZ8D4ZoyW3wdKO9SVpVQGSykuXUmRzN3i7Ji"
    "ABRCNtdqwoMgFEp4o8g/rckHqF4GcuvMtcucQMgP15z8CWgysrlrfIhlfUOunoXKE9DEt9AI"
    "zJRU6tkcrpurM4ABOK5kTS6p1OPjm8uHHIL/aS45+Zqcg4WEliNbmQ9lNPxrYa5EypCWtcty"
    "ZZoVjdzTUVaMkj8WGkIZ33LdLOdJIKeF+IQ4lO2yXLoFBUDIkJycstcmRybEodRq5PbicyP0"
    "tuY6TYTmffCQ186ugze2yUSj5XAJPOe1s6N8qG0eT6nVlvuIZ1AcIdzK0i1Es6YvNhfBmtJb"
    "lr/lyNY/BUomNykNa5SilZWhTNg8kru6ujk7O6Nr9HkAApAmf5ZQyCoKC4t8eB09O3RqWQ71"
    "eqiuKAUApoODq/uLu0+u4mEpuuC489gOT3FllUJWgW09fNpl2YSP4emJotmfLmZznAFArVJS"
    "3uW1a8m3kNVak0r22My86lH+MoWSksD1tZWZOYU3M1KysvJu30wdNPydZV8sam659+9lyxTK"
    "ooIcAFAo5JLSUgBAxxvbO7XDomEPmLJ6Xbr4N+uRNLexFQ9LxZIHWCUBwFw9nwT1tZUPpBV4"
    "aaBwtHkBnSHZJ7Rvq5SF8FIIn1BJwAl/YFjf1qIi4RG3uiholUqid90CjhzctXPHdgBQq5QV"
    "FRXkVXHxS75rAdkqHpZevJgMAGh/K2qnolqNPic2c87HH86ah49//152Zk6hVlWFDkVOTjqz"
    "7vsNH/xnXrP85DfSr1UrFSqVrqHESr2xOqNSDuWVCg7LcfmqbzsH9MBaja8bkLbQYn7KJ2ms"
    "vPKhqk4TGxc3IXYqiomMlAfSisd2BD6KXCWTAcCKb757Qu7V6+HB/ezMnEIAwBdkUGdK1d1B"
    "IzVqJTUat/o6uT3LTTguplmNNQeb8PGieCCtAICnJwo6NkzHrHkLf00CjckpBwmE/PHXKpUS"
    "VRprJ8bwgoICvDNPrTXdSL+GGK5QyMulkpu3swFAUqnHu77IdSZcIMnKyqXYkwaNtFIOKpVG"
    "VlkmFhcv/mxRxcNSfEPQwyZIFvVxZPlQlouuCY0FAOy9kVWWYTkoZBU3b93Ev2SS0lL0ktXX"
    "yVV1mjLpA5Ho1uIFcxSyCvxIDC9eMgiBClnFlUtni8RiraoK1SfrXgUqKKfIXlFWqKhWV8oB"
    "7VMqFRd9u2zpqq8+w0o0B3NFN0v4+LQWhG+hRDKenvCbJQoMSBSY8FtFFGTYgXUeAiuBH5Ob"
    "IxhlWchEQdrDWJ1RKlbkZmei1bWYM89ghJw71zGrRlyQdv16Ovp0ET4OAeTSb6RfwzIxqDNz"
    "iuzRS6yq02jq1Eplgwn065ZNy75ebzA22q4GdaZU5mpBspTeWnKrCY2VV2qqZDK0HQjFkZU1"
    "KBx49IY1vF6PKqlWNWwcEolEm3/dteyLRZR+Y8s8VyoqLl+9BljfWlpq1EqKSxsrg/wvaIDW"
    "kESpPHLoYPr167v2HXJ29bQwBYi/xvt+n4bwrXfLWSN8paLi/LlT1gt/5VeL6vUUEqAUBR63"
    "bjwtURDQkiG0BWBjcuv7CwYdZAqlolqtqM4DsK+vyyivbGQ44DoOvFAkpaU3bjd+Y8R6h59W"
    "ZyoqyMFZO6oScT72mVG1joHN/6dfv/7PP2cHvTkMHr0Zimp7eWWBWFxs7iuIeFBKgLKxxUX3"
    "UOmOjo4AoNIajx07gr2FlXIoET8okz4AnLMTP1C6eHqfYWmzh0iI4ZimysrKKxUX4cWOB/aJ"
    "ZfRlZYlEsmrFivUbf7HQa1OKQq1tfeE/4ZtGFv6RQ/uaJfz6R8Jvlo58Gu+huQq0Mslb4F1H"
    "NSsVF3FYjqo6jayyrKKiAv+qoY5DpTXezEhBIeKCtLv5CsLBQPZ2UG9F4Tl3rqMRAWikRQUF"
    "YnFx8QMZ+UuGBQU1AHBk35+D3hyWldW4r75M+sDyJ8db0Fj00rA5XAClQiE/tOuny//+q6rT"
    "yCpvEERBCZFIpFRUODfz/DykrJAOuX1XlZOTS/gMKB7y8hJ5+WMhu3b85tq+C2ZBWIkXX/jn"
    "ju15BsKHZyuKViZ5i6GpUyNDSKlUEiSLOo6M1CTsmJp7eQ/I5/tZw3AAuJmRgrrDcqnEnGQR"
    "CgoKNBrNrRvXkFdGVlmG313/JMA3FlML6H9WVt7h/9vX3CJu3rqJenorcevGNexgr/L7KvyX"
    "j63Htp++iZ8ztVnvt034jameoShan+RWalTrgTT5peRzyEdy924m5RtpTbmystJHBo+6vFKh"
    "VCopF+dikEgkxxMOicXFAKBUKimXBrQu0NaA5uLS1TtDhgyzXqnezEjBeswSMfHLimwOd+Lb"
    "77i276IoK7Tw0qtVNefPnRo7aaqVhdqEj+EZi8KO4CABMwv3zDkVyKirb0wOpHGCubXclnHx"
    "37OZmVnY16opgRhObg4+MDPnLjxyqMoqy2RKXZPd4bb/bXNzbfA8qXUMc9EwoeEvKJeUWwke"
    "jxe/YJGkUn/i0FZr1Gy93toV4OLCbOwNKxUXFd8vxOcjEAgOJ5zG9POyFStWrVhBfvv5fP7a"
    "H38OjxhGWQoB6O5TEr6BtJbb+ilhc2iu8JvrsX567yElHtPkFvwo1jcDaVRz8S14vzGwSatl"
    "LyWfS01JsSwIBp2oyck5F+ZlY7Mg5rpPoTBmdMxYADiecDQxMUGtqkFjNrQnh7IO5uYRWjxb"
    "MXXa7LUbfkHXXyxdNGPKeMKXQwjITD/PoC8iV4NcB4MRisRiRbUaANAbJlc8tq5p2449bK4n"
    "lpDN9UQ1wfNcKIz58eet+GiUyoCwnv8pCZ9QSpMbhJpEC4QPsAjf11goEd19eu8hpXJtfXO9"
    "dW11AJBU6k8kJpBbFRnVeDQvr52dNeVKSkuR60JTpwaqrbJCYczWXX81XE+Y6rbwY/RyP8sD"
    "Z9kc7uKv1mI/DUZYvupb9J5hx+w1OXtnAYV52dhUjVL52HKmyKjojp17kHNbtmLFlYvnCgoK"
    "2Bzuj5s2CSeYNdEtz5I+DeFbnrZsLsPZHO6yFSvwuVkvfGt6dsTDp/cePospNHgKY3K8yYQ+"
    "jjM6ZlKwoCUrjcqljS49yoHNmk078T8Xf7W2BZ6YJ8SM/8xwd3PGh3Ts3AN9JwgenaL5JPlL"
    "SkvLKxUAIKssIwgBvyAEDzbXc9SkWZnp5zf/fpBQN+vRpPB//Hkr/ufzEj6yUDC0rvABwGB8"
    "1u9h6x+Y0OqaHGO4QCC4dqdkyfL1LWN4pugaACANplYpyQMboTCG8Aa7uzlPfPsdwPXizwBB"
    "wT3JgX7+AQ4cVzdXZzbTQL6LFII1YNBBUa3W1Kkp+SwSiR7cz6ZMGD9n6p5DJ1vMcGuET2BX"
    "2xM+wrN/D1uf5E/o8zAHgUCw568LLX7JyCB3yf5B4eRo4eH90AU6gvoZvHD+/O7kwODQoe7O"
    "TEdHR0dHR8Jh2M2CwQj1dfIy6QOlUqlUUrxhM6ZNkckpdh8RGPiEeDWFTwlKUZBJ9CSioAOA"
    "3mDSGyjOhUThlLcsABsVNJm2WTl/sWoNl+tETk4uhVBt7OKBtEKl0gAAfs0gHhFhPfGZoIvw"
    "yHHI28FmGsw9YEJZ+PqYq6QFYHYKPtugAE9nZ+eGdaZU+sT6/HuH9pMpdeiP/IaJRKKZ7wkR"
    "z5v76C2gWcLHYI3wrYc1zaE0EpsUfrMqYI0oyEPrJxEFHf8m4d9IvcFkx6ABgB2D1iy2Ezoh"
    "LC3hj1CoZYSFR/QLewvVB58DVklyzli1UQQMqjqzc4w9ggfA49TSG0xcrpNA0As9WnMPGCuL"
    "XCV86dbLEEuL4uMzwfbzk+tASE54mtifq6ubvLwE/REyYXO4bA5XJLoVPzP2wf1sfEOwnIHE"
    "FspnSqgAumWl8LHk1gjfgkjxtSW/CdakIsCc8AkJCTng30kssmVRkEu3RhRAehYIRLOAUguZ"
    "y5ESWp1VPUKzsg2NEIIZkpjLh/zOYdt3wIy3g8t1omyyr09HZKqZqx7lS0++thJkRqELNscZ"
    "v1eEnIr8gCmLHjH2PUpHMQpEg8/ionvxc+fs/mMTpQ4AMy8TZQi6eHrCJ7TdghyseRDm2miN"
    "8FGnbMegYb0zZVdrjSjwmhXLpFnvIT5t6w+grewvmwVKW665yMq8g7pPdOIFwVdpYZDj5c0D"
    "AGdn56cxJHsumPHJl+TAho9hMQ3oNVKrlPv37Prys7lZeQ8sZGVlF/a8hN/cHvZJQLZcKGGN"
    "KChzaLEoWp/kT0OsyJZrFZjzhQoEvSjD9UZTUHBPy3baS4eZM2ea45Vc8diqyds3U5d+NGb/"
    "n5tbpVyb8DE8S1G8HJqc4HJ7lrCjPzYefhK/y4sDLtdp5/6D5HC0rArxHO8T2r9n18fTJpSL"
    "c55hHQHaqPBbhicRxcuhyZ8j9MaGIdnzrkgro1/YW+u+30B5i5Lnd+9mzpg2JfncyWdVwUa0"
    "PeG3GC0TRSPJ9Wa+rqY3mtAtcxHMgTJhczNpsghytuRrLMT6dQtYEqwHteR3edTS54vm1mHy"
    "B/GWeS5T6ioqKtCMOgBUVFQsmDe3xaZ7cxeN4GFO+CqVzkKqF+GhUOIZi4KOf0HxlCDQo1ny"
    "QnkiemD5WC7ImgwJMfE/7eg0LA6+XPxddN3g7TCzjwfPbXz1HFlsc3VTqXR2dBo+voWux8rG"
    "4lttZar/b+/qYuMqrvD4egkbr5y1IwsaLVaMAxbI1coPJg8ORoKqoikEWqkSIIUIRYD60ESJ"
    "mzQ8WDwUHjBJIxVUKqLUadNUWKrAgSSNGkgiUqBSY0OcOiJuMXHibDC2wWtHu147600fxpke"
    "zzkzd+7fetvcT5Z179wz53zzzd+9e3+G3RiPsDE5AvKNp57Z/ObefeT1eTYzNTF6iXd1cZU+"
    "k0nv2Nb21u9f0zQMKRwURC8+dmIrPlvYwFQ0zIHL5dGPKt1EClxxeilUsCR3TrufIUUBqfO4"
    "CIE7s1TBUt8Qu/zVK1vC0CF0y/VV3cDAYyI5uplADFjQswnIgtuOON9/bP3RUwNNTU2kz2xm"
    "aiaT5l1dtMgd29pOHT/Ks0ujG68XXGoT8eEfMxYfjuA4o4tacDq2avjjv4hVZisFyVycUerb"
    "IRk3gGtyrTQ+DhwuXPHhk3zMSI/YUu19WuPW46OZPhe5q+oDtbU1733Qs/mFV0nP/Ne4mUwa"
    "vuH4UvvWb8Ynyf6A+fMGWhzxTfiYw/cq45Z6KUgBeaKtFCSTAH5dtwJccMMvOPpxUnwlsyJW"
    "WYTvkywK8oXrW9q2Hjv5d82UDncHBwf/uL/TsK6llheKL6B8jI8auVxL4aCT582qxuNcHRwa"
    "Gxs0R/FH4wSKv/bTYuGuxuZ3jp3WTOlwd+/rL5vXdSi+QPGlcNDJI86+OVPqcPAeT24kFovq"
    "z5T+n7ClbWvXsV5bfbKZqVPHj7oLEYovUAQp+FtoxCzNU2C64UwOLaFnKVH4N3ErkZGykB5U"
    "xpprwn+cOUt6EL+UkG//6pmYULWFu1xe/KxuSh48/Ffb9vdpn/x4jD6EXnypyvh/c/Ftsbji"
    "SzBvhwKupbBw38NaG3ZFCFX3JvHttSUmDplipMBsYUqkfD6xvuFe/a8+k5fOSiLk59jw8Piy"
    "6MSSpdV6bmQZJQHzc0ZnQ5iDOfAACokJKTAxXJC6e5o7u0+Kfs5fUJPCXTj3MTle4yKYiI8L"
    "ayI+Q5qTJeLFt21p2JXhCSzWHIoA3bqQwrAdYjIc9Om6l9HLfF4V28tvmXXtH5ZHddbAEa+0"
    "eab/XP8/ceJo6ox1a4LdeDdQ8/UfzQCkIm8Lc3tyyJMOqQxmpzNkx1jdlHx2Uzvv3uQbEXzd"
    "P41nsWsuPqRqIr5qKiKnK5OWJo3IJlWAbcgU/mcihVSoSLlpO5Tqmu8G8xkXhzCZyb2j7p7m"
    "3A2QBm//mXic+9vREbHt4vYP4bAohTXH5MTkkXc6+05/gA/l59jTGzY23F3fcHf98spbvLyB"
    "978ofkAjsgsp8nNGUqgIlEQnLxpW1tXzixnykiaVSnX/6XWYMjUywO9bzE5P5Kaz3m/hlNqP"
    "l1MjA59+cih1+fKhbvqrw/HqeG3tyuU1t3t/P2TRxWcOzxmDQ5GluLk6+V0Njfz5LZXBnt/+"
    "ZvDCV3x7cmKyt/d0ajxfmEmNjqe/HrmC12N3Ci/XQf5idjozdL6nt/c0bz0T419JDYtj6HzP"
    "natW3VZTRT4y3XzffeYRF118VjKnUUWWwsEnmfOeFzZedDQ2NuzPTFXEluFLGn7ZWVlZufPF"
    "5x7+wfwX3eey/emvl1weTvNlLnzh4GIy8Vf5fIFlRwf4Gu88JT2ZzUzn3jqwv6qq+sFH1gvL"
    "a9dmLgyeZ9HvMEav+5e44w7zuKUgvgsE0eyLLIWDTh5xOOvnC3QWVbq/IKM89MMNbFubahTk"
    "p6O56exHH34Yi0UZY6Pj6dtqqgY+79cMuk7hYjLxUa7Z6czHJ7rFs1Op8Txfo5u/F/WHfZ3n"
    "vhh79OHWW5fVzUwNXRkZS6cnWG6EMZbNXMUiJFt+Yh66FMR3gSDaapGliEgDVcSa7x5kuiG4"
    "B30WEcVQRJIVW1gHwht0DjPGq+Pr1j2uWfXm6tWrY2NjfHkwflK0+YVXU13zP4So7htDVpAA"
    "JmYIyNlQeRyCDNr/xeDhdw/ypsMY4+vg8kepGWPRpRWjQ72H3x2BUzRflG9sTF5Gs2VN66o7"
    "V8AokDDWIRYPRHxcWD0lp/BxJhccAmqHyqA4iVEFc9TDbe2hjWELVllKiWKXDJEvsEcf/xEp"
    "7o0lbBecl1bElj29YeNrr/wCpugvhyQCKp62HlR+TEJrUpKNyb/UrDh0ZP7bD+J0sbqqMhqN"
    "VsQqM5loejLL2GWePjqSujR85eLQl3il7ud/tp2sFw3/IMQ3EdxRS3M0n5GhGdON0TxEoFJA"
    "DhHL4TJJ6fQEX9g5l8vZrs/uCMKtL7+vaNC6dn1T06/J1VFx3Gc3tcficY2BO7gorI/Kb9r+"
    "Ml5zhy+mx7llpnMT41HGGF8N+1///pJcrGv1A2udhi6a+Jpeais+zutCfP3Qky8UQwoRy/Fa"
    "aGSVe0R5bjQItyps2fHLZ556zNaMD5++R3ddWL8kisXjnd0nN/74QdzPBwfnU/QnLIlE4sWO"
    "37mLfpOLD1E0KejLlEKB3k6N5x0Vlect2J38ZDL26zM7DapB8/1rN29ps/Xzxt4DcPj0C+4K"
    "61R5PZKNSfjIKoa+h/9q33uulQnFFyiaFBYDXVH8iV0BaVcD7MeyFmRXbZv4lBKhB2EjwsFD"
    "kpPnf97x5JNPaCJ27NrdfP9aZjBk4FJgnubqSR4MR0nbcDgx2Zh8+/3+ljWtDlwz1rKm9eD7"
    "fd+9N4nZSpw1tM3Fdwqyhah2nXrzSAYftSz20+1+SiG19v8G0jcjF41M5YS56t7YFe69EkPV"
    "WCChfeeBl944kkgkpPSWNa1dx3ofeWITmcuWG8kTG+j9QGOnYytOweLwxNraFXu6TnTs2o1F"
    "wEgkEh27du/pOrG0Mq4iKSkgcRBHLYu17zzw5t59tuK7KDuMhYd7c1e4RIa5hL0UHdvwDX+l"
    "EHEFMctiZf3Di/aYQYmg56Oj4pXJloe+J01TNwn6Pz/7yYnjPX87dOZMnzg1TSQSK+vqm1vX"
    "BSdLKL5AcFKU9V28Ji1ROFdg5db84qTiEE90DeFT48RLCMO8HkMwg4WZcQiP0oUI4RERBhYb"
    "FhANGnZ4uC2BN2JsAHeFEw1IDwz0E3EImpVburhk0aBnXBZYfGhMMpQyQksVGUlYsqSYsEQD"
    "B9VExIlYWMmVhiTkoImF/zPFtIF1w8OinipDjUTTcpxCJYtqNFcVDRaQMUITQxqqWGQ4xmdy"
    "owghQoTwA5oZyEt2zWg73+sLzJ+vL/rixy8yIUKUILz0cE12Mp0nRgrsusXKGOhaFiuTtmEK"
    "hmTPXYmMTN1poY3IBR2qnMAUmB0TILPAFAGYRfKJjWE4jQ1TqIpZSSJI/HFeSQHSHitDEpAq"
    "C/Ihq17KIhnjXLhJqEpH+tHUAuQslZQh4ENSjWP+ZKXjQ2RQTUvDWbBDlcikPnpNGGNln10s"
    "idfoQ4QwhH7KgTb6gZV0pXJuEtTW3nayZAtHB3Madp4Nnl4gb9hiY9tbediPxzvwmih+mbmI"
    "q9IziMLehDDpbNyGtCyw6yIdG6icO72EVIXWZ7GN4o5eRPNUiXRXnSlaLTaDgEfJQNLDA8Le"
    "spR84CGYy1r4uyKmpyKjYqvPDvlIHHBoTEwTVxQECoIjwkQsFyaG2UrGkLkUXaM5dk7ak8Sg"
    "IKqSYimkjGRhGdW0IOBRXDRsQ1YuFAqSVEWUiiNBo6Teg95zWe+F8HQ9RElANSa68+OXN+yc"
    "aU/Kgotr61Y1ITl+Cy1EiIDgV98gzzr9guE1afHjSjYLznH8pxMiRIhSwoJOPle4PoeWsJMS"
    "+bZIIbPoD4l01VFpQ8ooZdcQUPmREvVFMLcxgSNjH/MW322I0sF/AJe0bEoPZZI5AAAAAElF"
    "TkSuQmCC")
getSplash2Data = Splash2.GetData
getSplash2Image = Splash2.GetImage
getSplash2Bitmap = Splash2.GetBitmap

#----------------------------------------------------------------------

Key = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAAAA3NCSVQICAjb4U/gAAACaklE"
    "QVQokSXSTWtcVRzA4d/5n/s2907mrZMMMZOh4K6mWEo3dVPdiCC4sGvxA/gh/AquRLeCFISu"
    "pUXEXaFiwW4KpRlKS2lsEjOZ+37PPee48PkMj1r7+grRKC9RmmHY4BwuxunKEuh3fT5Mx6kV"
    "TN8lUQPBhMS0JYMMC02L6lvtoyAm1KB20ysWaLu+s2Gi675T3no8eOym0FFKJDbBgDJd3IOB"
    "JEID4KBB2DbUjrNau5R/KjYmf/VK4XwY1OLwggdFZ8GBoPzlJaflz3fuLkmdVp88vM97wg4t"
    "2uJTIrzatsZ6tRPGgaD8y+NfPv9y/8xM28B15mQon/5xj9UMZxhkOE3riAaI4JW3Vr0Yz89s"
    "/XbgDg8O/LO3s+l8u5zc+OlH4oQ4wgtFzXCGKIpzVvuqQ53EHD75laZ6+dlX8m9dpkGbDhod"
    "1HFcJGFtmNr4dbXVHx19/cN3EooaZRHW4NVMJLNupQeLy+bqWf1BH3Hybu78/Lw8kqE+vcD2"
    "6uk8uWia67dvTiR+/eBRjCSrgzen57sqOxV/7c8HWHl8524VBB//fo/lRK4fP3p2dHV9nD9/"
    "+DwLlsP3b/09nV178vjpMFvv7TKfsBivl4s3+wuWh+hYVf7FoNa/ffGN+2u9Nxyr1eLD77/l"
    "YEEutC0z2Blx0pKNGAuRqHNfpBBttqJ3qAHLVCOeVnCCbUkzaoMOL8p8sjdTG++rvhwFA9fW"
    "YV4n00mlrUUiMHmR9VoNRzbEQghNYZTvPQ4cAFhiVdP3iIEYsl7oXZ6oi7JYpeN+0wj/D9sY"
    "Kkuge9AEQInpwJQFgXh0kiV4gjT5DwPEK8dCBKqeAAAAAElFTkSuQmCC")
getKeyData = Key.GetData
getKeyImage = Key.GetImage
getKeyBitmap = Key.GetBitmap

#----------------------------------------------------------------------


class MyApp(wx.App):
    """ Main class for the PyRTFParserDemo """
    def OnInit(self):
        """ Initialize the Application """
        # Create the Main Window frame
        frame = MainWindow(None, -1, "wxRichTextCtrl RTF Parser Test")
        # Set the Main Window as the Top Frame
        self.SetTopWindow(frame)
        # Excpect Success.
        return True

# Initialize the App
app = MyApp(0)
# Run the Main Loop
app.MainLoop()
