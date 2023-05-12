from PyQt5 import QtCore, QtWidgets
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


class TypeExplorerToolBar(QtWidgets.QWidget):
    def __init__(self, window, actors):
        super(TypeExplorerToolBar, self).__init__()
        self.window = window
        self.actors = actors
        self.toolbar = QtWidgets.QToolBar(self.window)
        self.toolbar.setOrientation(QtCore.Qt.Vertical)
        self.toolbar.setMovable(False)
        self.toolbar.setFixedWidth(250)
        self.setContentsMargins(10, 10, 10, 10)
        self.toolbar.setStyleSheet("QToolBar { border: none; }")
        self.color_buttons = {}
        self.opacity_sliders = {}
        self.radius_sliders = {}
        self.filter_box_groups = {}
        self.initToolBar()

    def initToolBar(self):
        # Add all filters
        for name, (color, opacity, radius) in self.actors.property_map.items():
            groupBox = CollapsibleGroupBox(name, self)
            layout = QtWidgets.QFormLayout()
            handler = self.make_view_property_update_handler(name)

            color_button = QtWidgets.QPushButton("")
            color_button.clicked.connect(self.make_button_click_handler(name))
            color_button.setStyleSheet(f"background-color: rgb({color[0] * 255}, {color[1] * 255}, {color[2] * 255});")
            self.color_buttons[name] = color_button
            layout.addRow("Color:", color_button)

            opacity_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            opacity_slider.setRange(0, 99)
            opacity_slider.setValue(self.property_value_to_slider_value(opacity))
            opacity_slider.valueChanged.connect(handler)
            self.opacity_sliders[name] = opacity_slider
            layout.addRow("Opacity:", opacity_slider)

            radius_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            radius_slider.setRange(0, 99)
            radius_slider.setValue(self.property_value_to_slider_value(radius))
            radius_slider.update()
            self.radius_sliders[name] = radius_slider
            radius_slider.valueChanged.connect(handler)
            layout.addRow("Radius:", radius_slider)

            self.filter_box_groups[name] = groupBox
            groupBox.setLayout(layout)
            self.toolbar.addWidget(groupBox)
            self.toolbar.addSeparator()


        # Add reset properties button
        reset_properties = QtWidgets.QPushButton('Reset View Properties', self.toolbar)
        reset_properties.clicked.connect(self.on_reset_view_properties)
        self.toolbar.addWidget(reset_properties)

        # Add reset camera button
        recenter = QtWidgets.QPushButton('Recenter Scene', self.toolbar)
        recenter.clicked.connect(self.recenter)
        self.toolbar.addWidget(recenter)

        self.window.addToolBar(QtCore.Qt.RightToolBarArea, self.toolbar)

    def make_view_property_update_handler(self, name):
        return lambda: self.on_view_property_changed(name)

    def make_button_click_handler(self, name):
        return lambda: self.color_picker(name)

    def on_view_property_changed(self, name):
        actor = self.actors.type_actors[name]
        color = self.actors.property_map[name][0]
        opacity = self.slider_value_to_property_value(self.opacity_sliders[name].value())
        radius = self.slider_value_to_property_value(self.radius_sliders[name].value())
        self.actors.property_map[name] = (color, opacity, radius)
        core.update_view_property(actor, color, opacity, radius)
        self.window.render()

    def deactivate_actor(self, name):
        actor = self.actors.type_actors[name]
        color = self.actors.property_map[name][0]
        opacity = self.slider_value_to_property_value(self.opacity_sliders[name].value())
        radius = self.slider_value_to_property_value(self.radius_sliders[name].value())
        self.actors.property_map[name] = (color, 0, radius)
        core.update_view_property(actor, color, 0, radius)
        self.window.render()
        return opacity

    def reactivate_actor(self, name, opacity):
        actor = self.actors.type_actors[name]
        color = self.actors.property_map[name][0]
        radius = self.slider_value_to_property_value(self.radius_sliders[name].value())
        self.actors.property_map[name] = (color, opacity, radius)
        core.update_view_property(actor, color, opacity, radius)
        self.window.render()

    def on_reset_view_properties(self):
        self.actors.property_map = core.create_default_property_map()
        for name, (color, opacity, radius) in self.actors.property_map.items():
            self.opacity_sliders[name].setValue(self.property_value_to_slider_value(opacity))
            self.radius_sliders[name].setValue(self.property_value_to_slider_value(radius))
            self.color_buttons[name].setStyleSheet(
                f"background-color: rgb({color[0] * 255}, {color[1] * 255}, {color[2] * 255});")
            actor = self.actors.type_actors[name]
            core.update_view_property(actor, color, opacity, radius)
        self.window.render()

    def slider_value_to_property_value(self, value: int) -> float:
        x = value / 100
        return x ** 2.4

    def property_value_to_slider_value(self, value: float) -> int:
        x = value ** (1 / 2.4)
        return int(x * 100)

    def create_array_entry(self, name):
        pass

    def recenter(self):
        self.window.recenter()

    def color_picker(self, name):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            actor = self.actors.type_actors[name]
            r, g, b, _ = color.getRgb()
            r = r / 255.0
            g = g / 255.0
            b = b / 255.0
            new_color = [r, g, b]
            self.color_buttons[name].setStyleSheet(f"background-color: rgb({new_color[0] * 255}, {new_color[1] * 255}, {new_color[2] * 255});")
            opacity = self.slider_value_to_property_value(self.opacity_sliders[name].value())
            radius = self.slider_value_to_property_value(self.radius_sliders[name].value())
            self.actors.property_map[name] = (new_color, opacity, radius)
            core.update_view_property(actor, new_color, opacity, radius)
            self.window.render()

    def clear(self):
        self.toolbar.clear()
        self.toolbar.destroy()
        self.close()

