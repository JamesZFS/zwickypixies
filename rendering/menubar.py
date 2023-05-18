import os
import re
import sys
from PyQt5 import QtWidgets, QtGui, QtCore

import config


class IntInputAction(QtWidgets.QWidgetAction):
    def __init__(self, parent):
        super(IntInputAction, self).__init__(parent)

        # Create QLineEdit and set its validator to allow only integer input
        self.int_input = QtWidgets.QLineEdit()
        self.int_input.setValidator(QtGui.QIntValidator())

        # Set default widget for this action
        self.setDefaultWidget(self.int_input)


class MenuBar(QtWidgets.QWidget):

    def __init__(self, window):
        super(MenuBar, self).__init__()
        self.window = window
        self.back_action = None
        self.forward_action = None
        self.animation_bar = None
        self.timestep_input = None
        self.initMenuBar()


    def initMenuBar(self):
        # Define menubar entries
        menubar = self.window.menuBar()
        file_menu = menubar.addMenu('File')
        open_action = QtWidgets.QAction('Open', self.window)
        open_action.triggered.connect(self.openFile)
        file_menu.addAction(open_action)
        exit_action = QtWidgets.QAction('Exit', self.window)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        self.view_menu = menubar.addMenu('View')
        type_explorer_view = QtWidgets.QAction('Type Explorer', self.window)
        type_explorer_view.triggered.connect(self.set_view_handler('Type Explorer'))
        self.view_menu.addAction(type_explorer_view)
        data_view = QtWidgets.QAction('Data View', self.window)
        data_view.triggered.connect(self.set_view_handler('Data View'))
        self.view_menu.addAction(data_view)
        volume_view = QtWidgets.QAction('Volume View', self.window)
        volume_view.triggered.connect(self.set_view_handler('Volume View'))
        self.view_menu.addAction(volume_view)
        show_menu = menubar.addMenu('Show')
        show_anim_ctrl = QtWidgets.QAction('Animation Controls', self.window)
        show_anim_ctrl.triggered.connect(self.toggle_animation_controls)
        show_menu.addAction(show_anim_ctrl)
        show_bot_bar = QtWidgets.QAction('Bottom Bar', self.window)
        show_bot_bar.triggered.connect(self.toggle_bottom_bar)
        show_menu.addAction(show_bot_bar)

        # Animation control
        self.animation_bar = QtWidgets.QToolBar()
        self.animation_bar.setFixedHeight(25)
        self.animation_bar.toggleViewAction().setEnabled(False)
        self.animation_bar.toggleViewAction().setVisible(False)
        self.animation_bar.setVisible(False)
        self.animation_bar.setMovable(False)
        self.animation_bar.setStyleSheet("""
            QToolButton:hover {
                background-color: transparent;
            }
        """)
        self.window.addToolBar(QtCore.Qt.TopToolBarArea, self.animation_bar)

        spacer1 = QtWidgets.QWidget()
        spacer1.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.animation_bar.addWidget(spacer1)
        play_icon = QtGui.QIcon("resources/icons/play.png")
        play_action = QtWidgets.QAction(self.window)
        play_action.setIcon(play_icon)
        play_action.triggered.connect(self.playAnimation)
        self.animation_bar.addAction(play_action)
        halt_icon = QtGui.QIcon("resources/icons/halt.png")
        halt_action = QtWidgets.QAction(self.window)
        halt_action.setIcon(halt_icon)
        halt_action.triggered.connect(self.haltAnimation)
        self.animation_bar.addAction(halt_action)
        stop_icon = QtGui.QIcon("resources/icons/stop.png")
        stop_action = QtWidgets.QAction(self.window)
        stop_action.setIcon(stop_icon)
        stop_action.triggered.connect(self.stopAnimation)
        self.animation_bar.addAction(stop_action)
        back_icon = QtGui.QIcon("resources/icons/back.png")
        self.back_action = QtWidgets.QAction(self.window)
        self.back_action.setIcon(back_icon)
        self.back_action.triggered.connect(self.backAnimation)
        self.animation_bar.addAction(self.back_action)
        self.timestep_input = QtWidgets.QLineEdit()
        self.timestep_input.setFixedWidth(30)
        self.timestep_input.setValidator(QtGui.QIntValidator())
        self.timestep_input.returnPressed.connect(self.set_timestep)
        if not self.window.actors.polydata:
            self.timestep_input.setDisabled(True)
        self.animation_bar.addWidget(self.timestep_input)
        forward_icon = QtGui.QIcon("resources/icons/forward.png")
        self.forward_action = QtWidgets.QAction(self.window)
        self.forward_action.setIcon(forward_icon)
        self.forward_action.triggered.connect(self.forwardAnimation)
        self.animation_bar.addAction(self.forward_action)
        spacer2 = QtWidgets.QWidget()
        spacer2.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.animation_bar.addWidget(spacer2)

    def set_view_handler(self, view):
        return lambda: self.set_view(view)
    def openFile(self):
        filename, _filter = QtWidgets.QFileDialog.getOpenFileName(self.window, 'Open File', os.getenv('HOME'),
                                                                  'VTP Files (*.vtp)',
                                                                  options=QtWidgets.QFileDialog.DontUseNativeDialog
                                                                  )
        if filename:
            self.window.open_file(filename)
            self.window.recenter()

    def close(self):
        sys.exit(0)

    def set_view(self, view):
        self.window.set_view(view)

    def playAnimation(self):
        print('Playing animation...')

    def haltAnimation(self):
        print('Stopping animation...')

    def forwardAnimation(self):
        if not self.window.actors.polydata:
            return
        self.forward_action.setDisabled(True)
        numbers = re.findall(r"\d+", config.File)
        if numbers:
            curr = numbers[0].zfill(3)
            if int(curr) == 0:
                self.back_action.setEnabled(True)
            if int(curr) == 624:
                return
            number = str(int(curr) + 2).zfill(3)
            config.CurrentTime = int(number)
            filename = config.File.replace(curr, number)
            self.timestep_input.setText(number)
            self.window.open_file(filename)
        else:
            print("No number found in the string.")
            exit(1)
        if int(number) != 624:
            self.forward_action.setEnabled(True)

    def backAnimation(self):
        if not self.window.actors.polydata:
            return
        self.back_action.setDisabled(True)
        numbers = re.findall(r"\d+", config.File)
        if numbers:
            curr = numbers[0].zfill(3)
            if int(curr) == 624:
                self.forward_action.setEnabled(True)
            if int(curr) == 0:
                return
            number = str(int(curr) - 2).zfill(3)
            config.CurrentTime = int(number)
            filename = config.File.replace(curr, number)
            self.timestep_input.setText(number)
            self.window.open_file(filename)
        else:
            print("No number found in the string.")
            exit(1)
        if int(number) != 0:
            self.back_action.setEnabled(True)

    def stopAnimation(self):
        print('Stopping animation...')

    def toggle_animation_controls(self):
        if self.animation_bar.isVisible():
            self.animation_bar.setVisible(False)
        else:
            self.animation_bar.setVisible(True)

    def toggle_bottom_bar(self):
        if self.window.bottombar.bottombar.isVisible():
            self.window.bottombar.bottombar.setVisible(False)
        else:
            self.window.bottombar.bottombar.setVisible(True)

    def set_timestep(self):
        timestep = self.timestep_input.text()
        try:
            if int(timestep) < 0 or int(timestep) > 624 or int(timestep) % 2 != 0:
                print("invalid timestep")
                self.timestep_input.clearFocus()
                self.timestep_input.setText(config.CurrentTime)
                return
            if int(timestep) == 0:
                self.back_action.setDisabled(True)
                self.forward_action.setEnabled(True)
            elif int(timestep) == 624:
                self.back_action.setEnabled(True)
                self.forward_action.setDisabled(True)
            timestep = timestep.zfill(3)
            numbers = re.findall(r"\d+", config.File)
            if numbers:
                curr = numbers[0].zfill(3)
                filename = config.File.replace(curr, timestep)
                config.CurrentTime = timestep
                self.window.open_file(filename)
                self.timestep_input.clearFocus()
            else:
                print("No number found in the string.")
                exit(1)
        except:
            self.timestep_input.clearFocus()
            self.timestep_input.setText(config.CurrentTime)
            return
