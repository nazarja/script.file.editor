import os
import xbmc
import xbmcgui
import xbmcaddon
import shutil

#=====================#

dialog = xbmcgui.Dialog()
addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo('path')
icon_path = os.path.join(addon_path, 'resources', 'images', 'icon.png')

#=====================#

class Editor(xbmcgui.WindowXML):

    def __init__(self, *args, **kwargs):
        self.dir_path = kwargs.get('dir_path')
        self.file_path = kwargs.get('file_path')
        self.file_name = kwargs.get('file_name')
        self.choice = kwargs['choice']
        self.file_lines = []
        self.list_items = []

    #=====================#

    def onInit(self):
        self.clearList()
        self.setFocusId(50)
        self.control = self.getControl(50)
        self.getControl(8002).setLabel(self.file_name)
        if self.choice == 0: self.openNewFile()
        elif self.choice == 2: self.openExistingFile()
        else: self.doExit()

    #=====================#

    def openNewFile(self):
        try:
            list_item = xbmcgui.ListItem('', '0')
            self.file_lines.append('')
            self.control.addItem(list_item)
        except:
            self.doExit()

    #=====================#

    def openExistingFile(self):
        try:
            with open(self.file_path) as file:
                for i, line in enumerate(file.readlines()):
                    line = line.replace(chr(9), '        ').rstrip()
                    list_item = xbmcgui.ListItem(line, str(i))
                    self.file_lines.append(line)
                    self.list_items.append(list_item)
            self.control.addItems(self.list_items)
        except:
            self.doExit()

    #=====================#

    def onClick(self, controlId):
        if controlId == 50: self.editLine()
        elif controlId == 9001: self.editLine()
        elif controlId == 9002: self.addLine()
        elif controlId == 9003: self.indentLine(9003)
        elif controlId == 9004: self.indentLine(9004)
        elif controlId == 9005: self.indentLine(9005)
        elif controlId == 9006: self.copyLine()
        elif controlId == 9007: self.removeLine()
        elif controlId == 9008: self.saveFile()
        elif controlId == 9009: self.exitEditor()

    #=====================#

    def getSelectedItem(self):
        selected = self.control.getSelectedItem()
        label = selected.getLabel()
        label2 = selected.getLabel2()
        return (selected, label, int(label2))

    #=====================#

    def editLine(self):
        try:
            item = self.getSelectedItem()
            kb = xbmc.Keyboard(item[1], 'Edit Line')
            kb.doModal()
            if kb.isConfirmed():
                label = kb.getText()
                item[0].setLabel(label)
                self.file_lines[item[2]] = label
        except:
            self.doExit()

    #=====================#

    def addLine(self, spaces=''):
        try:
            item = self.getSelectedItem()
            self.file_lines.insert(item[2] + 1, spaces + '')
            self.control.reset()

            list_items = []
            for i, line in enumerate(self.file_lines):
                list_item = xbmcgui.ListItem(line, str(i))
                list_items.append(list_item)
                
            self.control.addItems(list_items)
            xbmc.executebuiltin('SetFocus(50,{})'.format(item[2] + 1))

        except:
            self.doExit()

    #=====================#

    def indentLine(self, controlId):
        item = self.getSelectedItem()
        spaces = 0
        for c in item[1]:
            if c == ' ': spaces += 1
            else: break


        if controlId == 9003: # keep indent 
            spaces = ' ' * spaces
            return self.addLine(spaces)
        elif controlId == 9004: # indent right
            spaces = ' ' * 4 + ' ' * spaces
            return self.addLine(spaces)
        elif controlId == 9005: # indent left
            if spaces - 4 < 0: return self.addLine(item, '')
            else: return self.addLine(' ' * (spaces - 4))

    #=====================#
    
    def copyLine(self):
        try:
            item = self.getSelectedItem()
            self.file_lines.insert(item[2] + 1, item[1])
            self.control.reset()

            list_items = []
            for i, line in enumerate(self.file_lines):
                list_item = xbmcgui.ListItem(line, str(i))
                list_items.append(list_item)
                
            self.control.addItems(list_items)
            xbmc.executebuiltin('SetFocus(50,{})'.format(item[2] + 1))

        except:
            self.doExit()

    #=====================#

    def removeLine(self):
        try:
            item = self.getSelectedItem()
            del self.file_lines[item[2]]
            self.control.reset()

            list_items = []
            for i, line in enumerate(self.file_lines):
                list_item = xbmcgui.ListItem(line, str(i))
                list_items.append(list_item)

            self.control.addItems(list_items)
            xbmc.executebuiltin('SetFocus(50,{})'.format(item[2] - 1))

            if len(self.file_lines) == 0:
                return self.openNewFile()   

        except:
            self.doExit()
 

    #=====================#

    def saveFile(self):
        try:
            if self.choice == 0:
                self.file_path = os.path.join(self.dir_path, self.file_name)
                self.writeFile()

            elif self.choice == 2:
                self.dir_name = os.path.split(self.file_path)[0]
                
                backup_name = self.file_name.split('.')
                backup_name.insert(-1, 'backup')
                backup_name = '.'.join(backup_name)
                self.backup_path = os.path.join(self.dir_name, backup_name)
                shutil.copyfile(self.file_path, self.backup_path)
            
                self.writeFile()
                os.unlink(self.backup_path)

        except:
            try:
                if self.choice == 2:
                    os.unlink(self.file_path)
                    os.rename(self.backup_path, self.file_path)
            except:
                self.doExit()

            dialog.notification('Maintenance Helper', 'Unable To Save File.')
            self.doExit()
    

    #=====================#

    def writeFile(self):
        if dialog.yesno('File Editor', 'Are You Sure You Want To Save This File'):
            with open(self.file_path, 'w') as file:
                for line in self.file_lines:
                    line = str(line) + '\n'
                    file.writelines(line)
            
            dialog.notification('File Editor', 'File Saved Successfully', icon_path, 3000)
            

    #=====================#

    def exitEditor(self):
        if dialog.yesno('Are You Sure You Want To Quit?', 'All Unsaved Work Will Be Lost.'):
            self.close()

    #=====================#

    def doExit(self):
        dialog.notification('File Editor', 'There Was A Problem', icon_path, 3000)
        self.close()

    #=====================#
