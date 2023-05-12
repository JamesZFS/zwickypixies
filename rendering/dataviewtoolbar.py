from PyQt5 import QtCore, QtWidgets
import config
from type_explorer import core


class CollapsibleGroupBox(QtWidgets.QGroupBox):
    def __init__(self, name, toolbox):
        super(CollapsibleGroupBox, self).__init__()
        self.setStyleSheet("QGroupBox { border: none; }")
        self.setCheckable(True)
        self.setChecked(True)
        self.name = name
        self.toolbox = toolbox
        self.opacity = 0
        self.setTitle(name)
        self.setStyleSheet(
            "QGroupBox { border: none; margin-top: 12px; } QGroupBox::title { subcontrol-origin: padding: 0px 5px 0px "
            "5px; }")
        self.toggled.connect(self.on_toggled)

    def on_toggled(self, checked):
        print("{} -> {}".format(checked, ~checked))
        if checked:
            print("deactivating {}".format(self.name))
            self.layout().setContentsMargins(10, 10, 10, 10)
            self.toolbox.reactivate_actor(self.name, self.opacity)

        else:
            print("reactivating {}".format(self.name))
            self.layout().setContentsMargins(0, 0, 0, 0)
            self.opacity = self.toolbox.deactivate_actor(self.name)


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
        self.toolbar.setMovable(False)
        self.toolbar.setFixedWidth(250)
        self.setContentsMargins(10, 10, 10, 10)
        self.toolbar.setStyleSheet("QToolBar { border: none; }")
        self.currActor = None
        self.interpolator = None
        self.legend = None
        self.kernelSharpnessInput = None
        self.kernelRadiusInput = None
        self.initToolBar()

    def initToolBar(self):
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
        self.toolbar.addSeparator()

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
        # TODO: Implement selection of arrays via this selection type
        groupBox = QtWidgets.QGroupBox()
        groupBox.setStyleSheet("QGroupBox { background-color: transparent; border: none; }")
        layout = QtWidgets.QVBoxLayout()
        entry_list = ["Dark Matter", "Baryon", "Stars", "Winds", "Gas", "AGN"]
        for entry in entry_list:
            checkBox = QtWidgets.QCheckBox(entry)
            checkBox.stateChanged.connect(lambda state, text=entry: self.onArrayCheckStateChanged(state, text))
            layout.addWidget(checkBox)

        groupBox.setLayout(layout)
        self.toolbar.addWidget(groupBox)
        self.toolbar.addSeparator()

        # Move the "scan" plane with GUI
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)
        label = QtWidgets.QLabel("Point Opacity:")
        pointOpacitySlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        pointOpacitySlider.setRange(0, 100)  # percentage
        pointOpacitySlider.setValue(50)
        pointOpacitySlider.valueChanged.connect(self.onPointOpacitySliderChange)
        layout.addRow(label, pointOpacitySlider)
        self.toolbar.addWidget(widget)
        self.toolbar.addSeparator()

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)
        label = QtWidgets.QLabel("Scan Plane Z:")
        scanPlaneSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        scanPlaneSlider.setRange(0, 100)  # percentage
        scanPlaneSlider.setValue(50)
        scanPlaneSlider.valueChanged.connect(self.onScanPlaneSliderChange)
        layout.addRow(label, scanPlaneSlider)
        self.toolbar.addWidget(widget)
        self.toolbar.addSeparator()

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

        self.toolbar.addWidget(widget)
        self.window.addToolBar(QtCore.Qt.RightToolBarArea, self.toolbar)

    def onArrayComboBoxChange(self, index):
        array_name = self.sender().currentText()
        self.updateActor(array_name=array_name)  # reload data every time? probably slow
        # todo: consider make a more narrow api for updating array name

    def onFilterComboBoxChange(self, index):
        filter = self.sender().currentText()
        self.updateActor(filter=filter)

    def onPointOpacitySliderChange(self, value):
        if not self.currActor: return
        alpha = value / 100
        self.currActor.GetProperty().SetOpacity(alpha ** 2.4)
        self.refresh()

    def onScanPlaneSliderChange(self, value):
        if not self.interpolator: return
        alpha = value / 100
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

    def clear(self):
        self.toolbar.clear()
        self.toolbar.destroy()
        self.close()

