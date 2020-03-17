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
            'Create New File', 'Create New Directory', 'Edit Existing File',
            'Rename File', 'Rename Directory',
            'Delete Existing File', 'Delete Existing Directory'
        ]
        self.choice = dialog.select('Choose Option', self.options)

        if self.choice is not -1:
            if self.choice is 0: self.createNewFile()
            elif self.choice is 1: self.createNewDirectory()
            elif self.choice is 2: self.editExistingFile()
            elif self.choice is 3: self.renameFile()
            elif self.choice is 4: self.renameDirectory()
            elif self.choice is 5: self.deleteFile()
            elif self.choice is 6: self.deleteDirectory()

    #=====================#

    def createNewFile(self):
        self.dir_path = dialog.browse(0, 'Select Location', 'files', '', False, False, home_path)
        if self.dir_path != home_path:
            kb = xbmc.Keyboard('', 'Enter New File Name And Extension')
            kb.doModal()
            if kb.isConfirmed():
                self.file_name = kb.getText()
                try:
                    # check valid chars
                    for c in self.file_name:
                        if not c.isalnum() and c not in '-._':
                            dialog.ok(
                                'Invalid File Name',
                                'Valid Characters:  letters, numbers, hypen, underscore, period.\n' +
                                'Valid Extensions:  .txt  .xml  .py  .js  .json'
                            )
                            self.doExit()

                    # check file extension
                    text = self.file_name.split('.')
                    if len(text) < 2 or text[-1] not in ['txt', 'xml', 'py', 'js', 'json']:
                        dialog.ok(
                            'Invalid File Name',
                            'Valid Characters:  letters, numbers, hypen, underscore, period.\n' +
                            'Valid Extensions:  .txt  .xml  .py  .js  .json'
                        )
                        self.doExit()
                    
                    # check file doesnt already exist
                    if os.path.exists(os.path.join(self.dir_path, self.file_name)):
                        dialog.ok(
                            'Invalid File Name',
                            'A File With That Name Already Exists.\n' +
                            'Please Choose Another File Name.'
                        )
                        self.doExit()
                    
                    else:
                        try:
                            # open file for editing
                            gui = Editor(
                                'editor.xml', addon_path, 'default', '1080i', True,
                                dir_path=self.dir_path, file_name=self.file_name, choice=self.choice
                            )
                            gui.doModal()
                            del gui
                        except:
                            dialog.notification('File Editor', 'Unable To Create New File', icon_path, 3000)
                            self.doExit()
                except:
                    self.doExit()

    #=====================#

    def createNewDirectory(self):
        self.dir_path = dialog.browse(0, 'Select Location', 'files', '', False, False, home_path)
        if self.dir_path != home_path:
            kb = xbmc.Keyboard('', 'Enter New Directory Name')
            kb.doModal()
            if kb.isConfirmed():
                self.dir_name = kb.getText()
                self.dir_path = os.path.join(self.dir_path, self.dir_name)
                try:
                    # check for valid chars
                    for c in self.dir_name:
                        if not c.isalnum() and c not in '-._':
                            dialog.ok(
                                'Invalid Directory Name',
                                'Valid Characters:  letters, numbers, hypen, underscore, period.'
                            )
                            self.doExit()

                    # check file doesnt already exist
                    if os.path.exists(self.dir_path):
                        dialog.ok(
                            'Invalid Directory Name',
                            'A Directory With That Name Already Exists.\n' +
                            'Please Choose Another Directory Name.'
                        )
                        self.doExit()
                    else:
                        try:
                            # make new directory
                            os.makedirs(self.dir_path)
                            dialog.notification(
                                'File Editor', 'Directory Created Successfully', icon_path, 3000)
                        except:
                            dialog.notification('File Editor', 'Unable To Create New Directory', icon_path, 3000)
                            self.doExit()
                except:
                    self.doExit()

    #=====================#

    def editExistingFile(self):
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
                    # open file for editing
                    gui = Editor(
                        'editor.xml', addon_path, 'default', '1080i', True,
                        file_path=self.file_path, file_name=self.file_name, choice=self.choice
                    )
                    gui.doModal()
                    del gui

            except:
                dialog.notification('File Editor', 'Unable To Open File', icon_path, 3000)
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

                    # check valid chars
                    for c in self.temp_name:
                        if not c.isalnum() and c not in '-._':
                            dialog.ok(
                                'Invalid File Name',
                                'Valid Characters:  letters, numbers, hypen, underscore, period.\n' +
                                'Valid Extensions:  .txt  .xml  .py  .js  .json'
                            )
                            self.doExit()

                    # check file extension
                    text = self.temp_name.split('.')
                    if len(text) < 2 or text[-1] not in ['txt', 'xml', 'py', 'js', 'json']:
                        dialog.ok(
                            'Invalid File Name',
                            'Valid Characters:  letters, numbers, hypen, underscore, period.\n' +
                            'Valid Extensions:  .txt  .xml  .py  .js  .json'
                        )
                        self.doExit()
                    
                    # check file doesnt already exist and that we are renaming the correct file
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
                                'Rename File To "{}"'.format(self.temp_name)
                            ):
                                os.rename(self.file_path, os.path.join(self.temp_path, self.temp_name))
                                dialog.notification('File Editor', 'File Renamed.', icon_path, 3000)
                        except:
                            dialog.notification('File Editor', 'Unable To Rename File', icon_path, 3000)
                            self.doExit()
            except:
                self.doExit()

    #=====================#
    
    def renameDirectory(self):
        self.dir_path = dialog.browse(0, 'Select Directory To Rename', 'files', '', False, False, home_path)
        if self.dir_path != home_path and os.path.exists(self.dir_path):
            try:
                # get paths
                self.orig_path, self.start_path, self.end_path = self.getStartAndEndPath(self.dir_path)

                kb = xbmc.Keyboard('{}'.format(self.end_path), 'Enter The New Name For This Directory')
                kb.doModal()
                if kb.isConfirmed():
                    self.temp_name = kb.getText()

                    # check for valid chars
                    for c in self.temp_name:
                        if not c.isalnum() and c not in '-._':
                            dialog.ok(
                                'Invalid Directory Name',
                                'Valid Characters:  letters, numbers, hypen, underscore, period.'
                            )
                            self.doExit()
                    
                    # check file doesnt already exist
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
                        'Rename Directory To "{}"'.format(self.temp_name)
                    ):
                        os.rename(self.dir_path, os.path.join(self.start_path, self.temp_name))
                        dialog.notification('File Editor', 'Directory Renamed.', icon_path, 3000)

            except Exception, e:
                dialog.textviewer('', str(e))
                dialog.notification('File Editor', 'Unable To Rename Directory', icon_path, 3000)

    #=====================#

    def deleteFile(self):
        self.file_path = dialog.browse(1, 'Select File To Delete', 'files', '', False, False, home_path)
        if self.file_path != home_path and os.path.exists(self.file_path):
            try:
                self.file_name = os.path.split(self.file_path)[-1]
                if dialog.yesno(
                    'Delete This File?',
                    'This Is A Permenant Action.\n' +
                    'Delete File "{}"'.format(self.file_name)
                ):
                    os.unlink(self.file_path)
                    dialog.notification('File Editor', 'File Deleted.', icon_path, 3000)
            except:
                dialog.notification('File Editor', 'Unable To Delete File', icon_path, 3000)

    #=====================#

    def deleteDirectory(self):
        self.dir_path = dialog.browse(0, 'Select Directory To Delete', 'files', '', False, False, home_path)
        if self.dir_path != home_path and os.path.exists(self.dir_path):
            try:
                # get paths
                self.orig_path, self.start_path, self.end_path = self.getStartAndEndPath(self.dir_path)

                if dialog.yesno(
                    'Delete This Directory And All Its Content?',
                    'This Is A Permenant Action.\n' +
                    'Delete Directory "{}"'.format(self.end_path)
                ):
                    shutil.rmtree(self.dir_path)
                    dialog.notification('File Editor', 'Directory Deleted', icon_path, 3000)
            except:
                dialog.notification('File Editor', 'Unable To Delete Directory', icon_path, 3000)

    #=====================#

    def getStartAndEndPath(self, orig_path):
        start_path = None
        end_path = None

        if '/' in orig_path:
            split_path = orig_path.split('/')
            if split_path[-1] != '':
                start_path = '/'.join(split_path[:-1])
                end_path = split_path[-1]
            else:
                start_path = '/'.join(split_path[:-2])
                end_path = split_path[-2]

        elif '\\' in orig_path:
            split_path = orig_path.split('\\')
            if split_path[-1] != '':
                start_path = '\\'.join(split_path[:-1])
                end_path = split_path[-1]
            else:
                start_path = '\\'.join(split_path[:-2])
                end_path = split_path[-2]

        return orig_path, start_path, end_path

    #=====================#

    def doExit(self):
        sys.exit()

#=====================#

if __name__ == '__main__':
   fe = FileEditor()
   fe.startScript()
   
