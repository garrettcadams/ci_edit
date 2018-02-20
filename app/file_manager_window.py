# Copyright 2018 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import app.color
import app.config
#import app.cu_editor
import app.log
import app.text_buffer
import app.window


# todo remove or use this.
class PathRow(app.window.ViewWindow):
  def __init__(self, host):
    if app.config.strict_debug:
      assert(host)
    app.window.ViewWindow.__init__(self, host)
    self.host = host
    self.path = ''

  def mouseClick(self, paneRow, paneCol, shift, ctrl, alt):
    row = self.scrollRow + paneRow
    col = self.scrollCol + paneCol
    line = self.path
    col = self.scrollCol + paneCol
    self.host.controller.shownDirectory = None
    if col >= len(line):
      return
    slash = line[col:].find('/')
    self.path = line[:col + slash + 1]

  def render(self):
    app.log.debug()
    offset = 0
    color = app.color.get('message_line')
    #self.addStr(0, 0, self.path, color)
    self.writeLineRow = 0
    self.writeLine(self.path, color)


class DirectoryList(app.window.Window):
  """This <tbd>."""
  def __init__(self, host, inputWindow):
    if app.config.strict_debug:
      assert host
      assert self is not host
    app.window.Window.__init__(self, host)
    self.host = host
    self.inputWindow = inputWindow
    self.controller = app.cu_editor.DirectoryList(self)
    self.setTextBuffer(app.text_buffer.TextBuffer())
    self.optionsRow = app.window.OptionsRow(self)
    self.opt = {
      'Name': True,
      'Size': None,
      'Modified': None,
    }
    self.optionsRow.beginGroup()
    for key, size in [('Name', -40), ('Size', 15), ('Modified', 24)]:
      self.optionsRow.addSortHeader(key, self.opt, size)
    self.optionsRow.setParent(self, 0)

  def reshape(self, rows, cols, top, left):
    """Change self and sub-windows to fit within the given rectangle."""
    app.log.detail('reshape', rows, cols, top, left)
    self.optionsRow.reshape(1, cols, top, left)
    top += 1
    rows -= 1
    app.window.Window.reshape(self, rows, cols, top, left)

  def mouseClick(self, paneRow, paneCol, shift, ctrl, alt):
    row = self.scrollRow + paneRow
    if row >= len(self.textBuffer.lines):
      return
    self.controller.openFileOrDir(row)

  def mouseDoubleClick(self, paneRow, paneCol, shift, ctrl, alt):
    self.changeFocusTo(self.host)

  def mouseMoved(self, paneRow, paneCol, shift, ctrl, alt):
    self.changeFocusTo(self.host)

  def mouseRelease(self, paneRow, paneCol, shift, ctrl, alt):
    self.changeFocusTo(self.host)

  def mouseTripleClick(self, paneRow, paneCol, shift, ctrl, alt):
    self.changeFocusTo(self.host)

  def mouseWheelDown(self, shift, ctrl, alt):
    self.textBuffer.mouseWheelDown(shift, ctrl, alt)
    self.changeFocusTo(self.host)

  def mouseWheelUp(self, shift, ctrl, alt):
    self.textBuffer.mouseWheelUp(shift, ctrl, alt)
    self.changeFocusTo(self.host)

  def setTextBuffer(self, textBuffer):
    if app.config.strict_debug:
      assert textBuffer is not self.host.textBuffer
    textBuffer.lineLimitIndicator = 0
    textBuffer.highlightCursorLine = True
    textBuffer.highlightTrailingWhitespace = False
    app.window.Window.setTextBuffer(self, textBuffer)
    self.controller.setTextBuffer(textBuffer)


class FileManagerWindow(app.window.Window):
  def __init__(self, host, inputWindow):
    if app.config.strict_debug:
      assert host
      assert issubclass(host.__class__, ActiveWindow), host
    app.window.Window.__init__(self, host)
    self.host = host
    self.inputWindow = inputWindow
    self.inputWindow.fileManagerWindow = self
    self.showTips = False
    self.controller = app.cu_editor.FileOpener(self)
    self.setTextBuffer(app.text_buffer.TextBuffer())
    #self.textBuffer.setMessage('asdf', 0)
    self.opt = {
      'dotFiles': True,
      'sizes': True,
      'modified': True,
    }
    self.titleRow = app.window.OptionsRow(self)
    self.titleRow.addLabel(' ci    Open File')
    self.titleRow.setParent(self, 0)
    self.optionsRow = app.window.OptionsRow(self)
    self.optionsRow.addLabel(' Show: ')
    for key in ['dotFiles', 'sizes', 'modified']:
      self.optionsRow.addToggle(key, self.opt)
    self.optionsRow.setParent(self, 0)
    self.directoryList = DirectoryList(self, inputWindow)
    self.directoryList.setParent(self, 0)
    #self.statusLine = StatusLine(self)
    #self.statusLine.setParent(self, 0)

  def getPath(self):
    return self.textBuffer.lines[0]

  def mouseClick(self, paneRow, paneCol, shift, ctrl, alt):
    row = self.scrollRow + paneRow
    col = self.scrollCol + paneCol
    line = self.textBuffer.lines[0]
    col = self.scrollCol + paneCol
    self.directoryList.controller.shownDirectory = None
    if col >= len(line):
      return
    slash = line[col:].find('/')
    self.setPath(line[:col + slash + 1])

  def quitNow(self):
    app.log.debug()
    self.host.quitNow()

  def reshape(self, rows, cols, top, left):
    """Change self and sub-windows to fit within the given rectangle."""
    app.log.detail('reshape', rows, cols, top, left)
    originalRows = rows
    self.titleRow.reshape(1, cols, top, left)
    top += 1
    rows -= 1
    app.window.Window.reshape(self, 1, cols, top, left)
    top += 1
    rows -= 1
    self.optionsRow.reshape(1, cols, originalRows - 2, left)
    rows -= 2
    #self.statusLine.reshape(1, cols, originalRows - 2, left)
    #rows -= 2
    self.directoryList.reshape(rows, cols, top, left)

  def setTextBuffer(self, textBuffer):
    textBuffer.lineLimitIndicator = 0
    textBuffer.highlightTrailingWhitespace = False
    app.window.Window.setTextBuffer(self, textBuffer)
    self.controller.setTextBuffer(textBuffer)

  def setPath(self, path):
    self.textBuffer.replaceLines((path,))
