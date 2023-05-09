import vtk
from PyQt5 import QtCore, QtWidgets
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from type_explorer import core
import helpers

'''
    Standalone GUI application for exploring particle types at one time frame

    How to run:
        cd path/to/project-root
        python -m type_explorer.window path/to/Full.cosmo.600.vtp
    
    Features:
        - Interactive 3D visualization of particle types with different colors/opacity/radius
        - Toolbars for controlling view properties for each particle type
'''


# curve for mapping slider value to property value
def slider_value_to_property_value(value: int) -> float:
    x = value / 100
    return x ** 2.4
    
def property_value_to_slider_value(value: float) -> int:
    x = value ** (1/2.4)
    return int(x * 100)


class Window(QtWidgets.QMainWindow):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.setWindowTitle('Particle Type Explorer')
        self.resize(1536, 1024)

        self.frame = QtWidgets.QFrame(self)
        self.vl = QtWidgets.QVBoxLayout()

        # create renderer
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(0, 0, 0)
        vtk_widget = QVTKRenderWindowInteractor(self.frame)
        ren_win = vtk_widget.GetRenderWindow()
        ren_win.AddRenderer(self.ren)

        # setup interactor
        self.iren = ren_win.GetInteractor()
        style = vtk.vtkInteractorStyleTrackballCamera()
        self.iren.SetInteractorStyle(style)
        
        self.vl.addWidget(vtk_widget)
        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)

        self.frame.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.vl.setContentsMargins(0, 0, 0, 0)

        self._init_actors()
        self._init_tool_bar()

    def _init_actors(self):
        # initialize default view properties
        self.property_map = core.create_default_property_map()

        # initialize actors
        self.type_actors = {}  # maps type name to a point gaussian actor
        filename = helpers.get_program_parameters()
        self.update_actors(filename)
    
    def _init_tool_bar(self):
        toolbar = QtWidgets.QToolBar(self)
        toolbar.setOrientation(QtCore.Qt.Vertical)
        toolbar.setMovable(False)
        toolbar.setFixedWidth(350)
        toolbar.setStyleSheet("QToolBar { border: none; }")
        self.addToolBar(QtCore.Qt.RightToolBarArea, toolbar)

        # provide GUI for property map control
        self.color_buttons = {}  # maps type name to a color button
        self.opacity_sliders = {}
        self.radius_sliders = {}

        vwidget = QtWidgets.QWidget(toolbar)
        vlayout = QtWidgets.QFormLayout(vwidget)

        # header
        label = QtWidgets.QLabel('Particles', vwidget)
        hwidget = QtWidgets.QWidget(vwidget)
        hlayout = QtWidgets.QHBoxLayout(hwidget)
        color_label = QtWidgets.QLabel('Color', hwidget)
        color_label.setFixedWidth(40)
        hlayout.addWidget(color_label)
        opacity_label = QtWidgets.QLabel('Opacity', hwidget)
        opacity_label.setFixedWidth(80)
        hlayout.addWidget(opacity_label)
        radius_label = QtWidgets.QLabel('Radius', hwidget)
        radius_label.setFixedWidth(80)
        hlayout.addWidget(radius_label)
        vlayout.addRow(label, hwidget)

        def make_button_click_handler(name):
            return lambda: print(f'Clicked {name} button')
        
        def make_view_property_update_handler(name):
            return lambda: self.on_view_property_changed(name)

        # rows
        for name, (color, opacity, radius) in self.property_map.items():
            label = QtWidgets.QLabel(name, vwidget)
            handler = make_view_property_update_handler(name)

            hwidget = QtWidgets.QWidget(vwidget)
            hlayout = QtWidgets.QHBoxLayout(hwidget)
            
            color_button = QtWidgets.QPushButton(hwidget)
            color_button.setFixedWidth(40)
            color_button.setStyleSheet(f"background-color: rgb({color[0]*255}, {color[1]*255}, {color[2]*255});")
            # TODO: connect color_button to a color picker
            color_button.clicked.connect(make_button_click_handler(name))
            self.color_buttons[name] = color_button

            opacity_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, hwidget)
            opacity_slider.setFixedWidth(80)
            opacity_slider.setRange(0, 99)
            opacity_slider.setValue(property_value_to_slider_value(opacity))
            self.opacity_sliders[name] = opacity_slider
            opacity_slider.sliderMoved.connect(handler)

            radius_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, hwidget)
            radius_slider.setFixedWidth(80)
            radius_slider.setRange(0, 99)
            radius_slider.setValue(property_value_to_slider_value(radius))
            radius_slider.update()
            self.radius_sliders[name] = radius_slider
            radius_slider.sliderMoved.connect(handler)   

            hlayout.addWidget(color_button)
            hlayout.addWidget(opacity_slider)
            hlayout.addWidget(radius_slider)
            vlayout.addRow(label, hwidget)

        toolbar.addWidget(vwidget)
        toolbar.addSeparator()

        # reset button
        button = QtWidgets.QPushButton('Reset View Properties', toolbar)
        button.clicked.connect(self.on_reset_view_properties)
        toolbar.addWidget(button)

        button = QtWidgets.QPushButton('Reset Camera', toolbar)
        button.clicked.connect(self.on_reset_camera)
        toolbar.addWidget(button)

        self.toolbar = toolbar

    def on_view_property_changed(self, name):
        # update view property for a particle type from gui
        actor = self.type_actors[name]
        color = self.property_map[name][0]  # color is not updated for now
        opacity = slider_value_to_property_value(self.opacity_sliders[name].value())
        radius = slider_value_to_property_value(self.radius_sliders[name].value())
        self.property_map[name] = (color, opacity, radius)
        core.update_view_property(actor, color, opacity, radius)
        self.iren.Render()

    def on_reset_view_properties(self):
        self.property_map = core.create_default_property_map()
        # update sliders and actors
        for name, (color, opacity, radius) in self.property_map.items():
            self.opacity_sliders[name].setValue(property_value_to_slider_value(opacity))
            self.radius_sliders[name].setValue(property_value_to_slider_value(radius))
            actor = self.type_actors[name]
            core.update_view_property(actor, color, opacity, radius)
        # self.toolbar.update()  # buggy on my mac
        self.iren.Render()
    
    def on_reset_camera(self):
        self.ren.ResetCamera()
        self.iren.Render()

    def update_actors(self, filename):
        # update actors when file is changed

        # remove old actors
        for actor in self.type_actors.values():
            self.ren.RemoveActor(actor)

        # read polydata
        print(f'Reading {filename}...')
        reader = vtk.vtkXMLPolyDataReader()
        reader.SetFileName(filename)
        reader.Update()
        polydata: vtk.vtkPolyData = reader.GetOutput()

        # split particles by type
        self.type_polydata = core.split_particles(polydata)

        # create actors and initialize view properties
        self.type_actors = {name: core.create_point_actor(data) for name, data in self.type_polydata.items()}
        for name, actor in self.type_actors.items():
            core.update_view_property(actor, *self.property_map[name])

        # add actors to renderer
        for actor in self.type_actors.values():
            self.ren.AddActor(actor)
    
    def start(self):
        self.iren.Initialize()
        self.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = Window()
    window.start()
    app.exec_()
