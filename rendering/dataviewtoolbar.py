from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QLocale
from PyQt5.QtGui import QDoubleValidator

import config
from dataops.interpolator import Interpolator
from dataops.glyph import Glyph
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
        self.setChecked(config.ShowScanPlane)
        self.name = name
        self.toolbox.interpolator.get_plane_actor().SetVisibility(config.ShowScanPlane)
        self.setTitle(name)
        self.setStyleSheet(
            "QGroupBox { border: none; margin-top: 12px; } QGroupBox::title { subcontrol-origin: padding: 0px 5px 0px "
            "5px; }")
        self.toggled.connect(self.on_toggled)

    def init_checked(self):
        for i in range(self.layout().count()):
            self.layout().itemAt(i).widget().setVisible(config.ShowScanPlane)
            self.layout().itemAt(i).widget().setEnabled(config.ShowScanPlane)

    def on_toggled(self, checked):
        if checked:
            self.layout().setContentsMargins(10, 10, 10, 10)
        else:
            self.layout().setContentsMargins(0, 0, 0, 0)
        for i in range(self.layout().count()):
            self.layout().itemAt(i).widget().setVisible(checked)
            self.layout().itemAt(i).widget().setEnabled(checked)
        config.ShowLegend = checked
        self.toolbox.toggle_plane(checked)


def slider_to_glyph_scale(value):
    return value / 100 * 3.0 + 0.01  # 0.01 to 3.0


def glyph_scale_to_slider(scale):
    return int((scale - 0.01) / 3.0 * 100)


def glyph_opaticy_to_slider(opacity):
    return int(opacity ** (1 / 2.4) * 100)


def slider_to_glyph_opacity(value):
    return (value / 100) ** 2.4


def glyph_density_to_slider(density):
    return int(density ** (1/5) * 100)


def slider_to_glyph_density(value):
    return (value / 100) ** 5


class DataViewToolBar(QtWidgets.QWidget):
    def __init__(self, window, actors):
        from rendering.window import Window
        from rendering.actors import Actors
        super(DataViewToolBar, self).__init__()
        self.window: Window = window
        self.actors: Actors = actors
        self.toolbar = QtWidgets.QToolBar(self.window)
        self.toolbar.setOrientation(QtCore.Qt.Vertical)
        self.toolbar.toggleViewAction().setEnabled(False)
        self.toolbar.toggleViewAction().setVisible(False)
        self.toolbar.setMovable(False)
        self.toolbar.setFixedWidth(250)
        self.setContentsMargins(10, 10, 10, 10)
        self.toolbar.setStyleSheet("QToolBar { border: none; }")
        self.interpolator = Interpolator(self.actors.polydata)
        self.glyph = Glyph(self.actors.polydata)
        self.legend = create_legend(config.Lut)
        self.kernelSharpnessInput = None
        self.kernelRadiusInput = None
        self.min_thresh = None
        self.max_thresh = None
        self.scanPlaneSlider = None
        self.scanPlaneAxis = 'z'
        self.show_legend = True
        self.show_plane = False
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
        validator = QDoubleValidator()
        validator.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        layout = QtWidgets.QFormLayout(widget)
        self.min_thresh = QtWidgets.QLineEdit()
        self.min_thresh.setValidator(validator)
        self.min_thresh.returnPressed.connect(self.set_min_threshold)
        layout.addRow(QtWidgets.QLabel("Min:"), self.min_thresh)
        self.max_thresh = QtWidgets.QLineEdit()
        self.max_thresh.setValidator(validator)
        self.max_thresh.returnPressed.connect(self.set_max_threshold)
        layout.addRow(QtWidgets.QLabel("Max:"), self.max_thresh)

        self.toolbar.addWidget(widget)
        self.toolbar.addSeparator()

        # Add all filters
        for name, _ in self.actors.property_map.items():
            groupBox = CustomArrayBox(name, self)
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
        self.toolbar.addSeparator()

        # Ass legend toggler
        show_legend = QtWidgets.QCheckBox("Legend")
        show_legend.setChecked(config.ShowLegend)
        show_legend.stateChanged.connect(self.toggle_legend)
        self.toolbar.addWidget(show_legend)
        self.toolbar.addSeparator()

        # Scan plane
        groupBox = CollapsibleGroupBox("Scan Plane", self)
        layout = QtWidgets.QFormLayout()
        groupBox.setLayout(layout)

        axisComboBox = QtWidgets.QComboBox()
        axisComboBox.addItems(["x-axis", "y-axis", "z-axis"])
        axisComboBox.setCurrentIndex(2)
        axisComboBox.currentIndexChanged.connect(self.set_plane_axis)
        self.scanPlaneSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.scanPlaneSlider.setRange(0, 100)
        self.scanPlaneSlider.setValue(50)
        self.scanPlaneSlider.valueChanged.connect(self.onScanPlaneSliderChange)
        layout.addRow(axisComboBox, self.scanPlaneSlider)

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
        groupBox.init_checked()
        self.toolbar.addWidget(groupBox)

        # Glyph controls
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout()
        widget.setLayout(layout)

        self.glyph_widgets = []
        check_box = QtWidgets.QCheckBox("Velocity Glyph")
        check_box.stateChanged.connect(self.on_glyph_toggled)
        check_box.setChecked(config.ShowGlyph)
        layout.addRow(check_box)

        label = QtWidgets.QLabel("Glyph Scale:")
        glyph_scale_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        glyph_scale_slider.setRange(0, 100)
        glyph_scale_slider.valueChanged.connect(self.on_glyph_scale_slider_change)
        glyph_scale_slider.setValue(glyph_scale_to_slider(config.GlyphScale))
        layout.addRow(label, glyph_scale_slider)
        self.glyph_widgets += [label, glyph_scale_slider]

        label = QtWidgets.QLabel("Glyph Opacity:")
        glyph_opaticy_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        glyph_opaticy_slider.setRange(0, 100)
        glyph_opaticy_slider.valueChanged.connect(self.on_glyph_opacity_slider_change)
        glyph_opaticy_slider.setValue(glyph_opaticy_to_slider(config.GlyphOpacity))
        layout.addRow(label, glyph_opaticy_slider)
        self.glyph_widgets += [label, glyph_opaticy_slider]

        label = QtWidgets.QLabel("Glyph Density:")
        glyph_density_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        glyph_density_slider.setRange(0, 100)
        glyph_density_slider.valueChanged.connect(self.on_glyph_density_slider_change)
        glyph_density_slider.setValue(glyph_density_to_slider(config.GlyphDensity))
        layout.addRow(label, glyph_density_slider)
        self.glyph_widgets += [label, glyph_density_slider]

        check_box = QtWidgets.QCheckBox("Color Glyph")
        check_box.stateChanged.connect(self.on_glyph_color_toggled)
        check_box.setChecked(config.ColorGlyph)
        layout.addRow(check_box)
        self.glyph_widgets += [check_box]
        
        self.toolbar.addWidget(widget)
        self.toolbar.addSeparator()
        self.on_glyph_toggled(config.ShowGlyph)
        
        recenter = QtWidgets.QPushButton('Recenter Scene', self.toolbar)
        recenter.clicked.connect(self.recenter)
        self.toolbar.addWidget(recenter)

        # Add toolbar to window
        self.window.addToolBar(QtCore.Qt.RightToolBarArea, self.toolbar)
        self.window.ren.AddActor(self.interpolator.get_plane_actor())
        self.window.ren.AddActor(self.legend)
        self.window.ren.AddActor(self.glyph.get_actor())
        thmin = config.RangeMin
        thmax = config.RangeMax
        if config.ThresholdMin is not None:
            thmin = config.ThresholdMin
        if config.ThresholdMax is not None:
            thmax = config.ThresholdMax
        self.set_thresh_text(thmin, thmax)



    def onArrayComboBoxChange(self, index):
        array_name = self.sender().currentText()
        assert array_name in config.ArrayNameList
        if self.legend:
            self.window.ren.RemoveActor(self.legend)
        self.legend = create_legend(config.Lut)
        self.window.ren.AddActor(self.legend)
        if config.ThresholdMin is not None:
            config.ThresholdMin = None
        if config.ThresholdMax is not None:
            config.ThresholdMax = None
        config.ArrayName = array_name
        self.actors.update_actors()
        self.set_thresh_text(config.ThresholdMin, config.ThresholdMax)
        if self.interpolator:
            self.window.ren.RemoveActor(self.interpolator.get_plane_actor())
        self.interpolator = Interpolator(self.actors.polydata)
        self.window.ren.AddActor(self.interpolator.get_plane_actor())
        self.window.render()

    def recenter(self):
        self.window.recenter()

    def set_min_threshold(self):
        min_thresh = self.min_thresh.text()
        max_thresh = self.max_thresh.text()
        config.ThresholdMin = min(float(min_thresh), float(max_thresh))
        self.actors.update_actors()
        self.window.render()

    def set_max_threshold(self):
        min_thresh = self.min_thresh.text()
        max_thresh = self.max_thresh.text()
        config.ThresholdMax = max(float(min_thresh), float(max_thresh))
        self.actors.update_actors()
        self.window.render()

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
        self.interpolator.set_plane(self.scanPlaneAxis, alpha * config.CoordMax)
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
        self.window.ren.RemoveActor(self.glyph.get_actor())
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
        self.min_thresh.setText(f'{min_thresh:.4e}')
        self.max_thresh.setText(f'{max_thresh:.4e}')

    def toggle_legend(self, state):
        if state == QtCore.Qt.Checked:
            self.legend.VisibilityOn()
        else:
            self.legend.VisibilityOff()
        config.ShowLegend = state
        self.window.render()

    def toggle_plane(self, state):
        self.interpolator.get_plane_actor().SetVisibility(state)
        self.window.render()

    def set_plane_axis(self, index):
        self.scanPlaneAxis = ['x','y','z'][index]
        value = self.scanPlaneSlider.value()
        alpha = value / 100
        self.interpolator.set_plane(self.scanPlaneAxis, alpha * config.CoordMax)
        self.window.render()

    def on_glyph_toggled(self, state):
        config.ShowGlyph = state
        self.glyph.get_actor().SetVisibility(state)
        for widget in self.glyph_widgets:
            widget.setEnabled(state)
            widget.setVisible(state)
        self.window.render()

    def on_glyph_scale_slider_change(self, value):
        config.GlyphScale = slider_to_glyph_scale(value)
        self.glyph.set_scale(config.GlyphScale)
        self.window.render()

    def on_glyph_opacity_slider_change(self, value):
        config.GlyphOpacity = slider_to_glyph_opacity(value)
        self.glyph.set_opacity(config.GlyphOpacity)
        self.window.render()

    def on_glyph_color_toggled(self, state):
        config.ColorGlyph = state
        self.glyph.set_color_mode(state)
        self.window.render()

    def on_glyph_density_slider_change(self, value):
        config.GlyphDensity = slider_to_glyph_density(value)
        self.glyph.set_ratio(config.GlyphDensity)
        self.window.render()
