import os
import sys
import xbmc
import xbmcgui
import xbmcaddon
import shutil

#=====================#

from resources.lib.editor import Editor

#=====================#

dialog = xbmcgui.Dialog()
addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo('path')
home_path = xbmc.translatePath('special://home')
icon_path = os.path.join(addon_path, 'resources', 'images', 'icon.png')

#=====================#

class FileEditor:

    def __init__(self, *args, **kwargs):
        self.dir_path = None
        self.file_path = None

    #=====================#

    def startScript(self):
        self.options = [
            'Create File', 'Create Directory', 'Edit File',
            'Copy File', 'Copy Directory',
            'Rename File', 'Rename Directory',
            'Delete File', 'Delete Directory'
        ]
        self.choice = dialog.select('Choose Option', self.options)

        if self.choice is not -1:
            if self.choice is 0: self.createFile()
            elif self.choice is 1: self.createDirectory()
            elif self.choice is 2: self.editFile()
            elif self.choice is 3: self.copyFile()
            elif self.choice is 4: self.copyDirectory()
            elif self.choice is 5: self.renameFile()
            elif self.choice is 6: self.renameDirectory()
            elif self.choice is 7: self.deleteFile()
            elif self.choice is 8: self.deleteDirectory()

    #=====================#

    def createFile(self):
        self.dir_path = dialog.browse(0, 'Select Location', '', 'files', False, False, home_path)
        if self.dir_path == home_path:
            if not self.rootOrCancel():
                return

        kb = xbmc.Keyboard('', 'Enter New File Name And Extension')
        kb.doModal()
        if kb.isConfirmed():
            self.file_name = kb.getText()
            try:
                for c in self.file_name:
                    if not c.isalnum() and c not in '-._':
                        dialog.ok(
                            'Invalid File Name',
                            'Valid Characters:  letters, numbers, hypen, underscore, period.\n' +
                            'Valid Extensions:  .txt  .xml  .py  .js  .json'
                        )
                        self.doExit()

                text = self.file_name.split('.')
                if len(text) < 2 or text[-1] not in ['txt', 'xml', 'py', 'js', 'json']:
                    dialog.ok(
                        'Invalid File Name',
                        'Valid Characters:  letters, numbers, hypen, underscore, period.\n' +
                        'Valid Extensions:  .txt  .xml  .py  .js  .json'
                    )
                    self.doExit()

                if os.path.exists(os.path.join(self.dir_path, self.file_name)):
                    dialog.ok(
                        'Invalid File Name',
                        'A File With That Name Already Exists.\n' +
                        'Please Choose Another File Name.'
                    )
                    self.doExit()
                else:
                    try:
                        gui = Editor(
                            'editor.xml', addon_path, 'default', '1080i', True,
                            dir_path=self.dir_path, file_name=self.file_name, choice=self.choice
                        )
                        gui.doModal()
                        del gui
                    except:
                        dialog.notification('File Editor', 'Unable To Create New File.', icon_path, 3000)
                        self.doExit()
            except:
                self.doExit()

    #=====================#

    def createDirectory(self):
        self.dir_path = dialog.browse(0, 'Select Location', 'files', '', False, False, home_path)
        if self.dir_path == home_path:
            if not self.rootOrCancel():
                return

        kb = xbmc.Keyboard('', 'Enter New Directory Name')
        kb.doModal()
        if kb.isConfirmed():
            self.dir_name = kb.getText()
            self.dir_path = os.path.join(self.dir_path, self.dir_name)
            try:
                for c in self.dir_name:
                    if not c.isalnum() and c not in '-._':
                        dialog.ok(
                            'Invalid Directory Name',
                            'Valid Characters:  letters, numbers, hypen, underscore, period.'
                        )
                        self.doExit()

                if os.path.exists(self.dir_path):
                    dialog.ok(
                        'Invalid Directory Name',
                        'A Directory With That Name Already Exists.\n' +
                        'Please Choose Another Directory Name.'
                    )
                    self.doExit()
                else:
                    try:
                        os.makedirs(self.dir_path)
                        dialog.notification('File Editor', 'Directory Created Successfully.', icon_path, 3000)
                    except:
                        dialog.notification('File Editor', 'Unable To Create New Directory.', icon_path, 3000)
                        self.doExit()
            except:
                self.doExit()

    #=====================#

    def editFile(self):
        self.file_path = dialog.browse(1, 'Select File To Edit', 'files', '', False, False, home_path)
        if self.file_path != home_path and os.path.exists(self.file_path):
            try:
                self.file_name = os.path.split(self.file_path)[-1]
                ext = self.file_name.split('.')[-1]
                if ext not in ['txt', 'xml', 'py', 'js', 'json']:
                    dialog.ok(
                        'You Cannot Edit This File Type.',
                        'Valid Extensions:  .txt  .xml  .py  .js  .json'
                    )
                    self.doExit()
                else:
                    gui = Editor(
                        'editor.xml', addon_path, 'default', '1080i', True,
                        file_path=self.file_path, file_name=self.file_name, choice=self.choice
                    )
                    gui.doModal()
                    del gui
            except:
                dialog.notification(
                    'File Editor', 'Unable To Open File.', icon_path, 3000)
                self.doExit()

    #=====================#

    def copyFile(self):
        self.file_path = dialog.browse(1, 'Select File To Copy', 'files', '', False, False, home_path)
        if self.file_path == home_path:
             return

        self.copy_dir_path = dialog.browse(0, 'Select Location To Insert File Copy', 'files', '', False, False, home_path)
        if self.copy_dir_path == home_path:
            if not self.rootOrCancel(): return

        self.original_path, self.start_path, self.end_path = self.getDirPaths(self.copy_dir_path)
        self.dir_path, self.file_name = os.path.split(self.file_path)

        try:
            self.copy_file_path = os.path.join(self.copy_dir_path, self.file_name)
            if not os.path.exists(self.copy_file_path):
                try:
                    if dialog.yesno('Copy File', 'Copy File "{}" To Directory "{}".'.format(self.file_name, self.end_path)):
                        shutil.copyfile(self.file_path, self.copy_file_path)
                        dialog.notification('File Editor', 'Copy File Successful.', icon_path, 3000)
                except:
                    dialog.notification('File Editor', 'Unable To Copy File.', icon_path, 3000)
                    self.doExit()
            else:
                self.copy_name = self.file_name.split('.')
                self.copy_name.insert(-1, 'copy')
                self.copy_name = '.'.join(self.copy_name)
                self.copy_file_path = os.path.join(self.copy_dir_path, self.copy_name)
                if not os.path.exists(self.copy_file_path):
                    try:
                        if dialog.yesno('Copy File', 'Copy File "{}" To Directory "{}".'.format(self.file_name, self.end_path)):
                            shutil.copyfile(self.file_path, self.copy_file_path)
                            dialog.notification('File Editor', 'Copy File Successful.', icon_path, 3000)
                    except:
                        dialog.notification('File Editor', 'Unable To Copy File.', icon_path, 3000)
                        self.doExit()
                else:
                    dialog.ok('Copy File', 'A Copy Of This File Already Exists.')
                    self.doExit()
        except:
            dialog.notification('File Editor', 'Unable To Copy File.', icon_path, 3000)
            self.doExit()
        
    #=====================#

    def copyTree(self, source, destination):
        try:
            for item in os.listdir(source):
                src = os.path.join(source, item)
                dest = os.path.join(destination, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dest , False, None)
                else:
                    shutil.copy2(src, dest )
        except:
            dialog.notification('File Editor', 'Unable To Copy Directory.', icon_path, 3000)
            self.doExit()
    
    #=====================#

    def copyDirectory(self):
        self.dir_path = dialog.browse(0, 'Select Directory To Copy', 'files', '', False, False, home_path)
        
        if self.dir_path != home_path:
            self.dir_copy_path = dialog.browse(0, 'Select Directory To Copy To', 'files', '', False, False, home_path)
            self.original_path1, self.start_path1, self.end_path1 = self.getDirPaths(self.dir_path)
            self.original_path2, self.start_path2, self.end_path2 = self.getDirPaths(self.dir_copy_path)
            self.temp_dir_path = os.path.join(self.dir_copy_path, self.end_path1)

            if dialog.yesno('Copy Directory', 'Copy Directory "{}" to Directory "{}"?'.format(self.end_path1, self.end_path2)):
                try:
                    if not os.path.exists(self.temp_dir_path):
                        os.makedirs(self.temp_dir_path)
                        self.copyTree(self.dir_path, self.temp_dir_path)
                        dialog.notification('File Editor', 'Copy Directory Successful.', icon_path, 3000)
                    else:
                        self.temp_dir_name = self.end_path1 + '_copy'
                        self.temp_dir_path = os.path.join(self.dir_copy_path, self.temp_dir_name)

                        if not os.path.exists(self.temp_dir_path):
                            os.makedirs(self.temp_dir_path)
                            self.copyTree(self.dir_path, self.temp_dir_path)
                            dialog.notification('File Editor', 'Copy Directory Successful.', icon_path, 3000)
                        else:
                            dialog.ok('Copy Directory', 'A Copy Of This Directory Already Exists.')
                            self.doExit()
                except Exception as e:
                    dialog.textviewer('', str(e))
                    dialog.notification('File Editor', 'Unable To Copy Directory.', icon_path, 3000)
                    self.doExit()

    #=====================#

    def renameFile(self):
        self.file_path = dialog.browse(1, 'Select File To Rename', 'files', '', False, False, home_path)
        if self.file_path != home_path and os.path.exists(self.file_path):
            try:
                self.temp_path, self.temp_name = os.path.split(self.file_path)
                kb = xbmc.Keyboard('{}'.format(self.temp_name), 'Enter The New Name For This File')
                kb.doModal()
                if kb.isConfirmed():
                    self.temp_name = kb.getText()
                    for c in self.temp_name:
                        if not c.isalnum() and c not in '-._':
                            dialog.ok(
                                'Invalid File Name',
                                'Valid Characters:  letters, numbers, hypen, underscore, period.\n' +
                                'Valid Extensions:  .txt  .xml  .py  .js  .json'
                            )
                            self.doExit()

                    text = self.temp_name.split('.')
                    if len(text) < 2 or text[-1] not in ['txt', 'xml', 'py', 'js', 'json']:
                        dialog.ok(
                            'Invalid File Name',
                            'Valid Characters:  letters, numbers, hypen, underscore, period.\n' +
                            'Valid Extensions:  .txt  .xml  .py  .js  .json'
                        )
                        self.doExit()

                    if os.path.exists(os.path.join(self.temp_path, self.temp_name)):
                        dialog.ok(
                            'Invalid File Name',
                            'A File With That Name Already Exists.\n' +
                            'Please Choose Another File Name.'
                        )
                        self.doExit()
                    else:
                        try:
                            if dialog.yesno(
                                'Rename This File?',
                                'This Is A Permenant Action.\n' +
                                'Rename File To "{}".'.format(self.temp_name)
                            ):
                                os.rename(self.file_path, os.path.join(self.temp_path, self.temp_name))
                                dialog.notification('File Editor', 'File Renamed.', icon_path, 3000)
                        except:
                            dialog.notification('File Editor', 'Unable To Rename File.', icon_path, 3000)
                            self.doExit()
            except:
                self.doExit()

    #=====================#
    
    def renameDirectory(self):
        self.dir_path = dialog.browse(0, 'Select Directory To Rename', 'files', '', False, False, home_path)
        if self.dir_path != home_path and os.path.isdir(self.dir_path):
            try:
                self.original_path, self.start_path, self.end_path = self.getDirPaths(self.dir_path)
                kb = xbmc.Keyboard('{}'.format(self.end_path), 'Enter The New Name For This Directory')
                kb.doModal()
                if kb.isConfirmed():
                    self.temp_name = kb.getText()
                    for c in self.temp_name:
                        if not c.isalnum() and c not in '-._':
                            dialog.ok(
                                'Invalid Directory Name',
                                'Valid Characters:  letters, numbers, hypen, underscore, period.'
                            )
                            self.doExit()

                    if os.path.exists(os.path.join(self.start_path, self.temp_name)):
                        dialog.ok(
                            'Invalid Directory Name',
                            'A Directory With That Name Already Exists.\n' +
                            'Please Choose Another Directory Name.'
                        )
                        self.doExit()

                    if dialog.yesno(
                        'Rename This Directory?',
                        'This Is A Permenant Action.\n' +
                        'Rename Directory To "{}".'.format(self.temp_name)
                    ):
                        os.rename(self.dir_path, os.path.join(self.start_path, self.temp_name))
                        dialog.notification('File Editor', 'Directory Renamed.', icon_path, 3000)
            except:
                dialog.notification('File Editor', 'Unable To Rename Directory.', icon_path, 3000)

    #=====================#

    def deleteFile(self):
        self.file_path = dialog.browse(1, 'Select File To Delete', 'files', '', False, False, home_path)
        if self.file_path != home_path and os.path.isfile(self.file_path):
            try:
                self.file_name = os.path.split(self.file_path)[-1]
                if dialog.yesno(
                    'Delete This File?',
                    'This Is A Permenant Action.\n' +
                    'Delete File "{}".'.format(self.file_name)
                ):
                    os.unlink(self.file_path)
                    dialog.notification('File Editor', 'File Deleted.', icon_path, 3000)
            except:
                dialog.notification('File Editor', 'Unable To Delete File.', icon_path, 3000)

    #=====================#

    def deleteDirectory(self):
        self.dir_path = dialog.browse(0, 'Select Directory To Delete', 'files', '', False, False, home_path)
        if self.dir_path != home_path and os.path.isdir(self.dir_path):
            try:
                self.original_path, self.start_path, self.end_path = self.getDirPaths(self.dir_path)
                if dialog.yesno(
                    'Delete This Directory And All Its Content?',
                    'This Is A Permenant Action.\n' +
                    'Delete Directory "{}".'.format(self.end_path)
                ):
                    shutil.rmtree(self.dir_path)
                    dialog.notification('File Editor', 'Directory Deleted.', icon_path, 3000)
            except:
                dialog.notification('File Editor', 'Unable To Delete Directory.', icon_path, 3000)

    #=====================#

    def getDirPaths(self, original_path):
        start_path = None
        end_path = None

        if '/' in original_path:
            split_path = original_path.split('/')
            if split_path[-1] != '':
                start_path = '/'.join(split_path[:-1])
                end_path = split_path[-1]
            else:
                start_path = '/'.join(split_path[:-2])
                end_path = split_path[-2]

        elif '\\' in original_path:
            split_path = original_path.split('\\')
            if split_path[-1] != '':
                start_path = '\\'.join(split_path[:-1])
                end_path = split_path[-1]
            else:
                start_path = '\\'.join(split_path[:-2])
                end_path = split_path[-2]

        return original_path, start_path, end_path

    #=====================#

    def rootOrCancel(self):
        option = dialog.select('Choose Option', ['Select The Root Directory', 'Cancel Operation'])
        return True if option is 0 else False

    #=====================#

    def doExit(self):
        sys.exit()

#=====================#

if __name__ == '__main__':
   fe = FileEditor()
   fe.startScript()
   
