from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QLocale
from PyQt5.QtGui import QDoubleValidator

import config
from dataops.interpolator import Interpolator
from helpers import create_legend

class CustomGroupBox(QtWidgets.QGroupBox):
    def __init__(self, name, toolbox):
        super(CustomGroupBox, self).__init__()
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


class DataViewToolBar(QtWidgets.QWidget):
    def __init__(self, window, actors):
        super(DataViewToolBar, self).__init__()
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
        self.interpolator = Interpolator(self.actors.polydata)
        self.legend = create_legend(config.Lut)
        self.kernelSharpnessInput = None
        self.kernelRadiusInput = None
        self.min_thresh = None
        self.max_thresh = None
        self.initToolBar()

    def initToolBar(self):
        # Add metric component
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)
        label = QtWidgets.QLabel("Metric:")
        arrayComboBox = QtWidgets.QComboBox()
        arrayComboBox.addItems(config.ArrayNameList)
        arrayComboBox.setCurrentIndex(config.ArrayNameList.index(config.ArrayName))
        arrayComboBox.setFixedWidth(100)
        arrayComboBox.currentIndexChanged.connect(self.onArrayComboBoxChange)
        layout.addRow(label, arrayComboBox)
        self.toolbar.addWidget(widget)

        # Add threshold control
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        label = QtWidgets.QLabel("Threshold:")
        layout.addWidget(label)
        validator = QDoubleValidator()
        validator.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.min_thresh = QtWidgets.QLineEdit()
        self.min_thresh.setValidator(validator)
        self.min_thresh.returnPressed.connect(self.set_min_threshold)
        layout.addWidget(self.min_thresh)
        self.max_thresh = QtWidgets.QLineEdit()
        self.max_thresh.setValidator(validator)
        self.max_thresh.returnPressed.connect(self.set_max_threshold)
        layout.addWidget(self.max_thresh)

        self.toolbar.addWidget(widget)
        self.toolbar.addSeparator()

        # Add all filters
        for name, _ in self.actors.property_map.items():
            groupBox = CustomGroupBox(name, self)
            layout = QtWidgets.QFormLayout()
            groupBox.setLayout(layout)
            groupBox.init_checked()
            self.toolbar.addWidget(groupBox)

        # Opacity control
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)
        label = QtWidgets.QLabel("Opacity:")
        pointOpacitySlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        pointOpacitySlider.setRange(0, 100)
        pointOpacitySlider.setValue(50)
        pointOpacitySlider.valueChanged.connect(self.onPointOpacitySliderChange)
        layout.addRow(label, pointOpacitySlider)
        self.toolbar.addWidget(widget)

        # Z-axis scan plane
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)
        label = QtWidgets.QLabel("Scan Plane Z:")
        scanPlaneSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        scanPlaneSlider.setRange(0, 100)
        scanPlaneSlider.setValue(50)
        scanPlaneSlider.valueChanged.connect(self.onScanPlaneSliderChange)
        layout.addRow(label, scanPlaneSlider)
        self.toolbar.addWidget(widget)
        self.toolbar.addSeparator()

        # Interpolator kernel controls
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
        self.toolbar.addWidget(widget)

        # Add reset camera button
        recenter = QtWidgets.QPushButton('Recenter Scene', self.toolbar)
        recenter.clicked.connect(self.recenter)
        self.toolbar.addWidget(recenter)

        # Add toolbar to window
        self.window.addToolBar(QtCore.Qt.RightToolBarArea, self.toolbar)
        self.window.ren.AddActor(self.interpolator.get_plane_actor())
        self.window.ren.AddActor(self.legend)


    def onArrayComboBoxChange(self, index):
        array_name = self.sender().currentText()
        assert array_name in config.ArrayNameList
        if self.interpolator:
            self.window.ren.RemoveActor(self.interpolator.get_plane_actor())
        self.interpolator = Interpolator(self.actors.polydata)
        self.window.ren.AddActor(self.interpolator.get_plane_actor())
        if self.legend:
            self.window.ren.RemoveActor(self.legend)
        self.legend = create_legend(config.Lut)
        self.window.ren.AddActor(self.legend)
        config.ThresholdMin = None
        config.ThresholdMax = None
        config.ArrayName = array_name
        self.actors.update_actors()
        self.window.render()

    def recenter(self):
        self.window.recenter()

    def set_min_threshold(self):
        min_thresh = self.min_thresh.text()
        config.ThresholdMin = float(min_thresh)
        self.actors.update_actors()

    def set_max_threshold(self):
        max_thresh = self.max_thresh.text()
        config.ThresholdMax = float(max_thresh)
        self.actors.update_actors()

    def onPointOpacitySliderChange(self, value):
        if value == 100:
            value -= 1e-5
        config.DataViewOpacity = (value / 100)**2.4
        for name, _ in self.actors.property_map.items():
            if config.ShowFilter[name]:
                self.actors.actors[name].GetProperty().SetOpacity(config.DataViewOpacity)
        self.window.render()

    def onScanPlaneSliderChange(self, value):
        if not self.interpolator: return
        alpha = value / 100
        self.interpolator.set_plane_z(alpha * config.CoordMax)
        self.window.render()

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
        self.window.render()

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
        self.window.render()

    def clear(self):
        self.window.ren.RemoveActor(self.interpolator.get_plane_actor())
        self.window.ren.RemoveActor(self.legend)
        self.toolbar.clear()
        self.toolbar.destroy()
        self.close()

    def deactivate_actor(self, name):
        self.actors.hide_actor(name)
        self.window.render()

    def reactivate_actor(self, name):
        self.actors.show_actor(name)
        self.window.render()

    def set_thresh_text(self, min_thresh, max_thresh):
        self.min_thresh.setText(str(min_thresh))
        self.max_thresh.setText(str(max_thresh))