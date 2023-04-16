from vtkmodules.vtkInteractionWidgets import vtkSliderWidget, vtkSliderRepresentation2D, vtkButtonRepresentation, \
    vtkButtonWidget, vtkTexturedButtonRepresentation2D
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkPointGaussianMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)
import sys
from vtkmodules.vtkCommonColor import vtkNamedColors
import vtkmodules.vtkCommonCore as vtkCommonCore
import vtkmodules.vtkRenderingCore as vtkRenderingCore
from vtk import vtkTextActor
from PyQt5 import QtCore, QtWidgets
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import os


class _Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.renderer = vtkRenderer()
        self.renderWindow = vtkRenderWindow()
        self.app = QtWidgets.QApplication(sys.argv)
        self.frame = QtWidgets.QFrame()
        self.resize(2048, 1024)
        self.setWindowTitle("Zwickypixies")
        self.vl = QtWidgets.QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.renderWindowInteractor = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.vl.addWidget(self.vtkWidget)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)
        self.frame.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.vl.setContentsMargins(0, 0, 0, 0)
        self.bottomBarLabel = None
        self.currActor = None
        self.initMenuBar()
        self.initBottomBar()
        self.initToolBar()

    def initMenuBar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        exit_action = QtWidgets.QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        open_action = QtWidgets.QAction('Open', self)
        open_action.triggered.connect(self.openFile)  # connect to the openFile method
        file_menu.addAction(open_action)

    def initToolBar(self):
        toolbar = QtWidgets.QToolBar(self)
        toolbar.setOrientation(QtCore.Qt.Vertical)
        toolbar.setMovable(False)
        toolbar.setFixedWidth(250)
        toolbar.setStyleSheet("QToolBar { border: none; }")
        self.addToolBar(QtCore.Qt.RightToolBarArea, toolbar)
        button1 = QtWidgets.QToolButton()
        button1.setText("Button 1")
        toolbar.addWidget(button1)
        button2 = QtWidgets.QToolButton()
        button2.setText("Button 2")
        toolbar.addWidget(button2)
        button3 = QtWidgets.QToolButton()
        button3.setText("Button 3")
        toolbar.addWidget(button3)
        toolbar.setMinimumHeight(self.frame.sizeHint().height())

    def initBottomBar(self):
        bottomBar = QtWidgets.QFrame(self.frame)
        bottomBar.setFixedHeight(20)
        bottomBar.setStyleSheet("background-color: rgba(255, 255, 255, 0.2);")
        bottomBar.setContentsMargins(0, 0, 0, 0)
        self.vl.addWidget(bottomBar)
        self.vl.setSpacing(0)
        self.bottomBarLabel = QtWidgets.QLabel(bottomBar)
        self.bottomBarLabel.setContentsMargins(0, 0, 0, 0)
        self.bottomBarLabel.setText("Your Text Here")
        self.bottomBarLabel.setMinimumSize(self.bottomBarLabel.sizeHint())

        # Add the label to the bottom bar
        bottomBarLayout = QtWidgets.QHBoxLayout(bottomBar)
        bottomBarLayout.addWidget(self.bottomBarLabel)
        bottomBarLayout.setContentsMargins(0, 0, 0, 0)

        # Set the layout for the bottom bar
        bottomBar.setLayout(bottomBarLayout)

    def initActor(self, actor: vtkActor):
        self.currActor = actor
        self.renderWindow.AddRenderer(self.renderer)
        self.renderer.AddActor(self.currActor)
        self.renderer.SetBackground(vtkNamedColors().GetColor3d('DimGray'))
        self.renderer.GetActiveCamera().Pitch(90)
        self.renderer.GetActiveCamera().SetViewUp(0, 0, 1)
        self.renderer.ResetCamera()

    def updateActor(self, actor: vtkActor):
        self.renderer.RemoveActor(self.currActor)
        self.currActor = actor
        self.renderer.AddActor(self.currActor)

    def start(self):
        self.show()
        self.renderWindowInteractor.Initialize()

    def openFile(self):
        filename, _filter = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', os.getenv('HOME'), options=QtWidgets.QFileDialog.DontUseNativeDialog)
        if filename:
            # handle the file opening logic here
            print(f'Opening file: {filename}')


def updateBottomBarText(window: _Window, text):
    window.bottomBarLabel.setText(" " + text)


def startWindow(actor: vtkActor):
    app = QtWidgets.QApplication(sys.argv)
    window = _Window()
    window.initActor(actor)
    window.start()
    sys.exit(app.exec_())
