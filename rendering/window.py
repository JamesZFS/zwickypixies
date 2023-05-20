import re
import os
import vtk
import config
from PyQt5 import QtWidgets
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from rendering.menubar import MenuBar
from rendering.bottombar import BottomBar
from rendering.typeexplorertoolbar import TypeExplorerToolBar
from rendering.dataviewtoolbar import DataViewToolBar
from rendering.actors import Actors
from rendering.volumeviewtoolbar import VolumeViewToolBar

class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle('Zwickypixies')
        self.resize(2048, 1024)

        self.frame = QtWidgets.QFrame(self)
        self.vl = QtWidgets.QVBoxLayout()

        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(0, 0, 0)
        vtk_widget = QVTKRenderWindowInteractor(self.frame)
        ren_win = vtk_widget.GetRenderWindow()
        ren_win.AddRenderer(self.ren)

        self.iren = ren_win.GetInteractor()
        style = vtk.vtkInteractorStyleTrackballCamera()
        self.iren.SetInteractorStyle(style)

        self.vl.addWidget(vtk_widget)
        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)

        self.frame.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.vl.setContentsMargins(0, 0, 0, 0)

        self.actors = Actors(self)
        self.menubar = MenuBar(self)
        self.bottombar = BottomBar(self)
        self.toolbar = None

    def open_file(self, filename):
        self.actors.remove_actors()
        self.actors.load_polytope(filename)
        self.actors.update_actors()
        numbers = re.findall(r"\d+", filename)
        if numbers:
            numbers = numbers[0].zfill(3)
            if int(numbers) == 0:
                self.menubar.back_action.setDisabled(True)
            elif int(numbers) == 624:
                self.menubar.forward_action.setDisabled(True)
            else:
                self.menubar.back_action.setEnabled(True)
                self.menubar.forward_action.setEnabled(True)
            self.menubar.timestep_input.setEnabled(True)
            config.CurrentTime = numbers
            self.menubar.timestep_input.setText(numbers)
        else:
            print("No number found in the string.")
            exit(1)
        if self.toolbar:
            self.toolbar.clear()
            del self.toolbar
            self.toolbar = None
        if config.CurrentView == 'Type Explorer':
            self.toolbar = TypeExplorerToolBar(self, self.actors)
        elif config.CurrentView == 'Data View':
            self.toolbar = DataViewToolBar(self, self.actors)
        elif config.CurrentView == 'Volume View':
            self.toolbar = VolumeViewToolBar(self, self.actors)
        self.render()
        self.update_bottombar()

    def render(self):
        self.iren.Render()

    def recenter(self):
        self.ren.ResetCamera()
        self.iren.Render()

    def start(self):
        self.iren.Initialize()
        self.show()
        # For fast testing
        file = 'data/Full.cosmo.600.vtp'
        if os.path.isfile(file):
            self.open_file(file)
            self.recenter()        

    def set_view(self, view):
        if config.CurrentView == view:
            return
        config.CurrentView = view
        if not self.actors.polydata:
            return
        self.toolbar.clear()
        if view == 'Type Explorer':
            self.toolbar = TypeExplorerToolBar(self, self.actors)
        elif view == 'Data View':
            self.toolbar = DataViewToolBar(self, self.actors)
        elif view == 'Volume View':
            self.toolbar = VolumeViewToolBar(self, self.actors)
        else:
            print("Unknown view: {}".format(view))
            exit(1)

        self.actors.remove_actors()
        self.actors.update_actors()

    def update_bottombar(self):
        self.bottombar.updateBottomBarText()

def startWindow():
    app = QtWidgets.QApplication([])
    window = Window()
    window.start()
    app.exec_()
