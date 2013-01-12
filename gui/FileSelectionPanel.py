# -*- coding: utf-8 -*-

"""
***************************************************************************
    FileSelectionPanel.py
    ---------------------
    Date                 : August 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import os
from PyQt4 import QtGui, QtCore
from sextante.core.SextanteUtils import SextanteUtils

class FileSelectionPanel(QtGui.QWidget):

    def __init__(self, isFolder):
        super(FileSelectionPanel, self).__init__(None)
        self.isFolder = isFolder;
        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setMargin(0)
        self.text = QtGui.QLineEdit()
        self.text.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.horizontalLayout.addWidget(self.text)
        self.pushButton = QtGui.QPushButton()
        self.pushButton.setText("...")
        self.pushButton.clicked.connect(self.showSelectionDialog)
        self.horizontalLayout.addWidget(self.pushButton)
        self.setLayout(self.horizontalLayout)

    def showSelectionDialog(self):
        # find the file dialog's working directory
        settings = QtCore.QSettings()
        text = str(self.text.text())
        if os.path.isdir(text):
            path = text
        elif os.path.isdir( os.path.dirname(text) ):
            path = os.path.dirname(text)
        elif settings.contains("/SextanteQGIS/LastInputPath"):
            path = str(settings.value( "/SextanteQGIS/LastInputPath",QtCore.QVariant( "" ) ).toString())
        else:
            path = ""

        if self.isFolder:
            folder = QtGui.QFileDialog.getExistingDirectory (self, "Select folder", path)
            if folder:
                self.text.setText(str(folder))
                settings.setValue("/SextanteQGIS/LastInputPath", os.path.dirname(str(folder)))
        else:
            filenames = QtGui.QFileDialog.getOpenFileNames(self, "Open file", path, "*.*")
            if filenames:
                self.text.setText(str(filenames.join(";")))
                settings.setValue("/SextanteQGIS/LastInputPath", os.path.dirname(str(filenames[0])))

    def getValue(self):
        s = str(self.text.text())
        if SextanteUtils.isWindows():
            s = s.replace("\\", "/")
        return s
