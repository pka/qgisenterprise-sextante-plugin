# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SextanteToolbox.ui'
#
# Created: Sat Jun 15 23:14:30 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_SextanteToolbox(object):
    def setupUi(self, SextanteToolbox):
        SextanteToolbox.setObjectName(_fromUtf8("SextanteToolbox"))
        SextanteToolbox.resize(289, 438)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.verticalLayout = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.externalAppsButton = QtGui.QPushButton(self.dockWidgetContents)
        self.externalAppsButton.setObjectName(_fromUtf8("externalAppsButton"))
        self.verticalLayout.addWidget(self.externalAppsButton)
        self.searchBox = QgsFilterLineEdit(self.dockWidgetContents)
        self.searchBox.setObjectName(_fromUtf8("searchBox"))
        self.verticalLayout.addWidget(self.searchBox)
        self.algorithmTree = QtGui.QTreeWidget(self.dockWidgetContents)
        self.algorithmTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.algorithmTree.setHeaderHidden(True)
        self.algorithmTree.setObjectName(_fromUtf8("algorithmTree"))
        self.algorithmTree.headerItem().setText(0, _fromUtf8("1"))
        self.verticalLayout.addWidget(self.algorithmTree)
        self.modeComboBox = QtGui.QComboBox(self.dockWidgetContents)
        self.modeComboBox.setObjectName(_fromUtf8("modeComboBox"))
        self.verticalLayout.addWidget(self.modeComboBox)
        SextanteToolbox.setWidget(self.dockWidgetContents)

        self.retranslateUi(SextanteToolbox)
        QtCore.QMetaObject.connectSlotsByName(SextanteToolbox)

    def retranslateUi(self, SextanteToolbox):
        SextanteToolbox.setWindowTitle(QtGui.QApplication.translate("SextanteToolbox", "SEXTANTE Toolbox", None, QtGui.QApplication.UnicodeUTF8))
        self.externalAppsButton.setText(QtGui.QApplication.translate("SextanteToolbox", "Click here to learn more\n"
"about SEXTANTE", None, QtGui.QApplication.UnicodeUTF8))
        self.searchBox.setToolTip(QtGui.QApplication.translate("SextanteToolbox", "Enter algorithm name to filter list", None, QtGui.QApplication.UnicodeUTF8))

try:
  from qgis.gui import QgsFilterLineEdit
except ImportError:
  from PyQt4.QtGui import QLineEdit as QgsFilterLineEdit

