import vtk
import config
from PyQt5 import QtWidgets
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from rendering.menubar import MenuBar
from rendering.bottombar import BottomBar
from rendering.typeexplorertoolbar import TypeExplorerToolBar
from rendering.dataviewtoolbar import DataViewToolBar
from rendering.actors import Actors

'''
    
'''
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

        self.menubar = MenuBar(self)
        self.bottombar = BottomBar(self)
        self.actors = Actors(self)
        self.toolbar = None
        self.set_view(config.CurrentView)

    def open_file(self, filename):
        self.actors.remove_actors()
        self.actors.load_polytope(filename)
        self.actors.update_actors()
        if config.CurrentView == 'Type Explorer':
            self.toolbar = TypeExplorerToolBar(self, self.actors)
        elif config.CurrentView == 'Data View':
            self.toolbar = DataViewToolBar(self, self.actors)
        self.recenter()
        self.render()

    def render(self):
        self.iren.Render()

    def recenter(self):
        self.ren.ResetCamera()
        self.iren.Render()

    def start(self):
        self.iren.Initialize()
        self.show()

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
        else:
            print("Unknown view: {}".format(view))
            exit(1)

        self.actors.remove_actors()
        self.actors.update_actors()

def startWindow():
    app = QtWidgets.QApplication([])
    window = Window()
    window.start()
    app.exec_()
