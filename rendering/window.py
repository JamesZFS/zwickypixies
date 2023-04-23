from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkRenderWindow,
    vtkRenderer
)
import sys
from vtkmodules.vtkCommonColor import vtkNamedColors
from PyQt5 import QtCore, QtWidgets, QtGui
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch
import os
from dataops import importer
from dataops.interpolator import Interpolator
import config
from helpers import *

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
        self.irenStyle = vtkInteractorStyleSwitch()
        self.irenStyle.SetCurrentStyleToTrackballCamera()
        self.renderWindowInteractor.SetInteractorStyle(self.irenStyle)
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
        self.currActor = None  # point data
        self.interpolator = None  # interpolator for the scan plane
        self.legend = None # Legend for the colorbar

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

        # Animation control
        #TODO: Implement animation logics
        play_icon = QtGui.QIcon("resources/icons/play.png")
        play_action = QtWidgets.QAction(self)
        play_action.setIcon(play_icon)
        play_action.triggered.connect(self.playAnimation)
        menubar.addAction(play_action)
        halt_icon = QtGui.QIcon("resources/icons/halt.png")
        halt_action = QtWidgets.QAction(self)
        halt_action.setIcon(halt_icon)
        halt_action.triggered.connect(self.haltAnimation)
        menubar.addAction(halt_action)
        stop_icon = QtGui.QIcon("resources/icons/stop.png")
        stop_action = QtWidgets.QAction(self)
        stop_action.setIcon(stop_icon)
        stop_action.triggered.connect(self.stopAnimation)
        menubar.addAction(stop_action)

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
        label = QtWidgets.QLabel("Metric:")
        arrayComboBox = QtWidgets.QComboBox()
        arrayComboBox.addItems(config.ArrayNameList)
        arrayComboBox.setCurrentIndex(config.ArrayNameList.index(config.ArrayName))
        arrayComboBox.setFixedWidth(100)
        arrayComboBox.currentIndexChanged.connect(self.onArrayComboBoxChange)
        layout.addRow(label, arrayComboBox)
        toolbar.addWidget(widget)
        toolbar.addSeparator()

        '''
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
        '''
        # Filtering
        #TODO: Implement selection of arrays via this selection type
        groupBox = QtWidgets.QGroupBox("Filters:")
        layout = QtWidgets.QVBoxLayout()
        entry_list = ["Dark Matter", "Baryon", "Stars", "Winds", "Gas", "AGN"]
        for entry in entry_list:
            checkBox = QtWidgets.QCheckBox(entry)
            checkBox.stateChanged.connect(lambda state, text=entry: self.onArrayCheckStateChanged(state, text))
            layout.addWidget(checkBox)

        groupBox.setLayout(layout)
        toolbar.addWidget(groupBox)
        toolbar.addSeparator()

        # Move the "scan" plane with GUI
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)
        label = QtWidgets.QLabel("Point Opacity:")
        pointOpacitySlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        pointOpacitySlider.setRange(0, 100)  # percentage
        pointOpacitySlider.setValue(50)
        pointOpacitySlider.valueChanged.connect(self.onPointOpacitySliderChange)
        layout.addRow(label, pointOpacitySlider)
        toolbar.addWidget(widget)
        toolbar.addSeparator()

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)
        label = QtWidgets.QLabel("Scan Plane Z:")
        scanPlaneSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        scanPlaneSlider.setRange(0, 100)  # percentage
        scanPlaneSlider.setValue(50)
        scanPlaneSlider.valueChanged.connect(self.onScanPlaneSliderChange)
        layout.addRow(label, scanPlaneSlider)
        toolbar.addWidget(widget)
        toolbar.addSeparator()

        # TODO two threshold inputboxes to select partial data

        # TODO two range inputboxes for color map control

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)
        label = QtWidgets.QLabel("Kernel Sharpness:")
        kernelSharpnessInput = QtWidgets.QLineEdit()
        kernelSharpnessInput.setText('10')
        kernelSharpnessInput.returnPressed.connect(self.onKernelSharpnessChange)
        self.kernelSharpnessInput = kernelSharpnessInput
        layout.addRow(label, kernelSharpnessInput)

        label = QtWidgets.QLabel("Kernel Radius:")
        kernelRadiusInput = QtWidgets.QLineEdit()
        kernelRadiusInput.setText('3')
        kernelRadiusInput.returnPressed.connect(self.onKernelRadiusChange)
        self.kernelRadiusInput = kernelRadiusInput
        layout.addRow(label, kernelRadiusInput)

        toolbar.addWidget(widget)

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
        self._pointDataChanged(actor)
        self.renderer.SetBackground(vtkNamedColors().GetColor3d('DimGray'))
        self.renderer.GetActiveCamera().Yaw(-20)
        self.renderer.GetActiveCamera().SetViewUp(0, 1, 0)
        self.renderer.ResetCamera()
        self.updateBottomBarText()

    def updateActor(self, filename: str = None, array_name: str = None, filter: str = None):
        if array_name:
            actor = importer.getActor(array_name, filename, filter)
        else:
            actor = importer.getActor(config.ArrayName, filename, filter)
        self._pointDataChanged(actor)
        self.bottomBarFileLabel.setText(" " + config.File)
        self.refresh()

    def _pointDataChanged(self, actor: vtkActor):
        # Update the actors of point and related filters
        assert actor is not None
        if self.currActor: self.renderer.RemoveActor(self.currActor)
        if self.interpolator: self.renderer.RemoveActor(self.interpolator.get_plane_actor())
        if self.legend: self.renderer.RemoveActor(self.legend)
        self.currActor = actor
        polydata = actor.GetMapper().GetInput()
        self.interpolator = Interpolator(polydata)
        self.legend = create_legend(config.Lut)
        self.renderer.AddActor(self.currActor)
        self.renderer.AddActor(self.interpolator.get_plane_actor())
        self.renderer.AddActor(self.legend)

    def refresh(self):
        self.renderWindowInteractor.Render()
        self.updateBottomBarText()

    def start(self):
        self.show()
        self.renderWindowInteractor.Initialize()

    def onArrayComboBoxChange(self, index):
        array_name = self.sender().currentText()
        self.updateActor(array_name=array_name)  # reload data every time? probably slow
        # todo: consider make a more narrow api for updating array name

    def onFilterComboBoxChange(self, index):
        filter = self.sender().currentText()
        self.updateActor(filter=filter)
    
    def onPointOpacitySliderChange(self, value):
        if not self.currActor: return
        alpha = value/100
        self.currActor.GetProperty().SetOpacity(alpha ** 2.4)
        self.refresh()

    def onScanPlaneSliderChange(self, value):
        if not self.interpolator: return
        alpha = value/100
        self.interpolator.set_plane_z(alpha * config.CoordMax)
        self.refresh()

    def onKernelSharpnessChange(self):
        if not self.interpolator: return
        try:
            sharpness = float(self.kernelSharpnessInput.text())
        except ValueError:
            return
        if sharpness < 0: sharpness = 0
        print('kernel sharpness: ', sharpness)
        self.kernelSharpnessInput.setText(str(sharpness))
        self.interpolator.set_kernel_sharpness(sharpness)
        self.refresh()

    def onKernelRadiusChange(self):
        if not self.interpolator: return
        try:
            radius = float(self.kernelRadiusInput.text())
        except ValueError:
            return
        if radius < 0: radius = 0
        print('kernel radius: ', radius)
        self.kernelRadiusInput.setText(str(radius))
        self.interpolator.set_kernel_radius(radius)
        self.refresh()

    def onArrayCheckStateChanged(self, state, text):
        if state == QtCore.Qt.Checked:
            print(f"{text} is checked")
        else:
            print(f"{text} is unchecked")

    def playAnimation(self):
        print('Playing animation...')

    def haltAnimation(self):
        print('Stopping animation...')

    def stopAnimation(self):
        print('Stopping animation...')

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
