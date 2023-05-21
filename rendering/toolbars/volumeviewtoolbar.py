from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QLocale
from PyQt5.QtGui import QDoubleValidator

import config
from dataops.interpolator import Interpolator
from helpers import create_legend

class CustomArrayBox(QtWidgets.QGroupBox):
    def __init__(self, name, toolbox):
        super(CustomArrayBox, self).__init__()
        self.setStyleSheet("QGroupBox { border: none; }")
        self.setCheckable(True)
        self.setChecked(config.ShowFilter[name])
        self.name = name
        self.toolbox = toolbox
        self.opacity = 0
        self.setTitle(config.FilterListLongName[name])
        self.setStyleSheet(
            "QGroupBox { border: none; margin-top: 12px; } QGroupBox::title { subcontrol-origin: padding: 0px 5px 0px "
            "5px; }")
        self.toggled.connect(self.on_toggled)

    def init_checked(self):
        for i in range(self.layout().count()):
            self.layout().itemAt(i).widget().setVisible(self.isChecked())

    def on_toggled(self, checked):
        if checked:
            self.toolbox.reactivate_actor(self.name)
            config.ShowFilter[self.name] = True
        else:
            self.toolbox.deactivate_actor(self.name)
            config.ShowFilter[self.name] = False
        for i in range(self.layout().count()):
            self.layout().itemAt(i).widget().setVisible(checked)

    def add_separator(self):
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.layout().addWidget(line)

    def set_opacity(self, opacity):
        self.opacity = opacity


class CollapsibleGroupBox(QtWidgets.QGroupBox):
    def __init__(self, name, toolbox):
        super(CollapsibleGroupBox, self).__init__()
        self.setStyleSheet("QGroupBox { border: none; }")
        self.setCheckable(True)
        self.toolbox = toolbox
        self.setChecked(self.toolbox.show_plane)
        self.name = name
        self.toolbox.interpolator.get_plane_actor().SetVisibility(toolbox.show_plane)
        self.setTitle(name)
        self.setStyleSheet(
            "QGroupBox { border: none; margin-top: 12px; } QGroupBox::title { subcontrol-origin: padding: 0px 5px 0px "
            "5px; }")
        self.toggled.connect(self.on_toggled)

    def init_checked(self):
        for i in range(self.layout().count()):
            self.layout().itemAt(i).widget().setVisible(self.isChecked())
            self.layout().itemAt(i).widget().setEnabled(self.isChecked())

    def on_toggled(self, checked):
        if checked:
            self.layout().setContentsMargins(10, 10, 10, 10)
        else:
            self.layout().setContentsMargins(0, 0, 0, 0)
        for i in range(self.layout().count()):
            self.layout().itemAt(i).widget().setVisible(checked)
            self.layout().itemAt(i).widget().setEnabled(checked)
        self.toolbox.toggle_plane(checked)

class VolumeViewToolBar(QtWidgets.QWidget):
    def __init__(self, window, actors):
        super(VolumeViewToolBar, self).__init__()
        self.window = window
        self.actors = actors
        self.toolbar = QtWidgets.QToolBar(self.window)
        self.toolbar.setOrientation(QtCore.Qt.Vertical)
        self.toolbar.toggleViewAction().setEnabled(False)
        self.toolbar.toggleViewAction().setVisible(False)
        self.toolbar.setMovable(False)
        self.toolbar.setFixedWidth(250)
        self.setContentsMargins(10, 10, 10, 10)
        self.toolbar.setStyleSheet("QToolBar { border: none; }")
        self.initToolBar()

    def initToolBar(self):
        self.window.addToolBar(QtCore.Qt.RightToolBarArea, self.toolbar)

    def recenter(self):
        self.window.recenter()


    def clear(self):
        self.toolbar.clear()
        self.toolbar.destroy()
        self.close()
