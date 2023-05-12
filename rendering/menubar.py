import os
import sys
from PyQt5 import QtWidgets, QtGui

class MenuBar(QtWidgets.QWidget):

    def __init__(self, window):
        super(MenuBar, self).__init__()
        self.window = window
        self.initMenuBar()

    def initMenuBar(self):
        menubar = self.window.menuBar()
        file_menu = menubar.addMenu('File')
        open_action = QtWidgets.QAction('Open', self.window)
        open_action.triggered.connect(self.openFile)
        file_menu.addAction(open_action)
        exit_action = QtWidgets.QAction('Exit', self.window)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        view_menu = menubar.addMenu('View')
        type_explorer_view = QtWidgets.QAction('Type Explorer', self.window)
        type_explorer_view.triggered.connect(self.set_view_handler('Type Explorer'))
        view_menu.addAction(type_explorer_view)
        data_view = QtWidgets.QAction('Data View', self.window)
        data_view.triggered.connect(self.set_view_handler('Data View'))
        view_menu.addAction(data_view)

        menubar.addSeparator()
        # Animation control
        # TODO: Implement animation logics
        play_icon = QtGui.QIcon("resources/icons/play.png")
        play_action = QtWidgets.QAction(self.window)
        play_action.setIcon(play_icon)
        play_action.triggered.connect(self.playAnimation)
        menubar.addAction(play_action)
        halt_icon = QtGui.QIcon("resources/icons/halt.png")
        halt_action = QtWidgets.QAction(self.window)
        halt_action.setIcon(halt_icon)
        halt_action.triggered.connect(self.haltAnimation)
        menubar.addAction(halt_action)
        stop_icon = QtGui.QIcon("resources/icons/stop.png")
        stop_action = QtWidgets.QAction(self.window)
        stop_action.setIcon(stop_icon)
        stop_action.triggered.connect(self.stopAnimation)
        menubar.addAction(stop_action)
        back_icon = QtGui.QIcon("resources/icons/back.png")
        back_action = QtWidgets.QAction(self.window)
        back_action.setIcon(back_icon)
        back_action.triggered.connect(self.backAnimation)
        menubar.addAction(back_action)
        forward_icon = QtGui.QIcon("resources/icons/forward.png")
        forward_action = QtWidgets.QAction(self.window)
        forward_action.setIcon(forward_icon)
        forward_action.triggered.connect(self.forwardAnimation)
        menubar.addAction(forward_action)

    def set_view_handler(self, view):
        return lambda: self.set_view(view)
    def openFile(self):
        filename, _filter = QtWidgets.QFileDialog.getOpenFileName(self.window, 'Open File', os.getenv('HOME'),
                                                                  'VTP Files (*.vtp)',
                                                                  options=QtWidgets.QFileDialog.DontUseNativeDialog
                                                                  )
        if filename:
            self.window.open_file(filename)

    def close(self):
        sys.exit(0)

    def set_view(self, view):
        self.window.set_view(view)

    def playAnimation(self):
        print('Playing animation...')

    def haltAnimation(self):
        print('Stopping animation...')

    def forwardAnimation(self):
        print('Stopping animation...')

    def backAnimation(self):
        print('Stopping animation...')

    def stopAnimation(self):
        print('Stopping animation...')