from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkRenderWindow,
    vtkRenderer
)
import sys
from vtkmodules.vtkCommonColor import vtkNamedColors
from PyQt5 import QtCore, QtWidgets
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import os
from dataops import importer
import config

class _Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.renderer = vtkRenderer()
        self.renderWindow = vtkRenderWindow()
        self.renderWindow.AddRenderer(self.renderer)
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
        self.bottomBarFileLabel = None
        self.bottomBarArrayNameLabel = None
        self.bottomBarThresholdLabel = None
        self.bottomBarFilterLabel = None
        self.currActor = None
        self.initMenuBar()
        self.initBottomBar()
        self.initToolBar()

    def initMenuBar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        open_action = QtWidgets.QAction('Open', self)
        open_action.triggered.connect(self.openFile)
        file_menu.addAction(open_action)
        exit_action = QtWidgets.QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def initToolBar(self):
        toolbar = QtWidgets.QToolBar(self)
        toolbar.setOrientation(QtCore.Qt.Vertical)
        toolbar.setMovable(False)
        toolbar.setFixedWidth(250)
        toolbar.setStyleSheet("QToolBar { border: none; }")
        self.addToolBar(QtCore.Qt.RightToolBarArea, toolbar)

        # Create the QWidget to hold the label and the QComboBox
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)
        label = QtWidgets.QLabel("Array:")
        arrayComboBox = QtWidgets.QComboBox()
        arrayComboBox.addItems(config.ArrayNameList)
        arrayComboBox.setFixedWidth(100)
        arrayComboBox.currentIndexChanged.connect(self.onArrayComboBoxChange)
        layout.addRow(label, arrayComboBox)
        toolbar.addWidget(widget)
        toolbar.addSeparator()

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)
        label = QtWidgets.QLabel("Filter:")
        filterComboBox = QtWidgets.QComboBox()
        filterComboBox.addItems(config.FilterList)
        filterComboBox.setFixedWidth(100)
        filterComboBox.currentIndexChanged.connect(self.onFilterComboBoxChange)
        layout.addRow(label, filterComboBox)
        toolbar.addWidget(widget)
        toolbar.addSeparator()

    def initBottomBar(self):
        bottomBar = QtWidgets.QFrame(self.frame)
        bottomBar.setFixedHeight(20)
        bottomBar.setStyleSheet("background-color: rgba(255, 255, 255, 0.2);")
        bottomBarLayout = QtWidgets.QHBoxLayout(bottomBar)
        bottomBarLayout.setSpacing(0)
        bottomBarLayout.setContentsMargins(0, 0, 0, 0)
        bottomBar.setLayout(bottomBarLayout)

        self.bottomBarFileLabel = QtWidgets.QLabel(bottomBar)
        self.bottomBarFileLabel.setContentsMargins(0, 0, 0, 0)
        self.bottomBarFileLabel.setMinimumSize(self.bottomBarFileLabel.sizeHint())
        bottomBarLayout.addWidget(self.bottomBarFileLabel)

        self.bottomBarArrayNameLabel = QtWidgets.QLabel(bottomBar)
        self.bottomBarArrayNameLabel.setContentsMargins(0, 0, 0, 0)
        self.bottomBarArrayNameLabel.setMinimumSize(self.bottomBarArrayNameLabel.sizeHint())
        bottomBarLayout.addWidget(self.bottomBarArrayNameLabel)

        self.bottomBarThresholdLabel = QtWidgets.QLabel(bottomBar)
        self.bottomBarThresholdLabel.setContentsMargins(0, 0, 0, 0)
        self.bottomBarThresholdLabel.setMinimumSize(self.bottomBarThresholdLabel.sizeHint())
        bottomBarLayout.addWidget(self.bottomBarThresholdLabel)

        self.bottomBarFilterLabel = QtWidgets.QLabel(bottomBar)
        self.bottomBarFilterLabel.setContentsMargins(0, 0, 0, 0)
        self.bottomBarFilterLabel.setMinimumSize(self.bottomBarFilterLabel.sizeHint())
        bottomBarLayout.addWidget(self.bottomBarFilterLabel)

        self.vl.addWidget(bottomBar)
        self.vl.setSpacing(0)

    def updateBottomBarText(self):
        self.bottomBarFileLabel.setText(" File: " + config.File)
        self.bottomBarArrayNameLabel.setText("| Current Array: ({})  Range: [{:.5f}, {:.5f}]".format(config.ArrayName, config.RangeMin, config.RangeMax))
        self.bottomBarThresholdLabel.setText("| Threshold: [{}, {}]".format(config.ThresholdMin, config.ThresholdMax))
        self.bottomBarFilterLabel.setText("| Filter: ({})".format(config.Filter))

    def initActor(self, actor: vtkActor):
        self.currActor = actor
        self.renderer.AddActor(self.currActor)
        self.renderer.SetBackground(vtkNamedColors().GetColor3d('DimGray'))
        self.renderer.GetActiveCamera().Pitch(90)
        self.renderer.GetActiveCamera().SetViewUp(0, 0, 1)
        self.renderer.ResetCamera()
        self.updateBottomBarText()

    def updateActor(self, filename: str = None, array_name: str = None, filter: str = None):
        if array_name:
            actor = importer.getActor(array_name, filename, filter)
        else:
            actor = importer.getActor(config.ArrayName, filename, filter)
        self.renderer.RemoveActor(self.currActor)
        self.currActor = actor
        self.bottomBarFileLabel.setText(" " + config.File)
        self.renderer.AddActor(self.currActor)
        self.refresh()

    def refresh(self):
        self.renderWindowInteractor.Render()
        self.updateBottomBarText()

    def start(self):
        self.show()
        self.renderWindowInteractor.Initialize()

    def onArrayComboBoxChange(self, index):
        array_name = self.sender().currentText()
        self.updateActor(array_name=array_name)

    def onFilterComboBoxChange(self, index):
        filter = self.sender().currentText()
        self.updateActor(filter=filter)

    def openFile(self):
        filename, _filter = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', os.getenv('HOME'),'VTP Files (*.vtp)',
                                                                  options=QtWidgets.QFileDialog.DontUseNativeDialog
                                                                  )
        if filename:
            self.updateActor(filename=filename)


def startWindow(actor: vtkActor):
    app = QtWidgets.QApplication(sys.argv)
    window = _Window()
    window.initActor(actor)
    window.start()
    sys.exit(app.exec_())
