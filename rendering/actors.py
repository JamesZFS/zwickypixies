from vtkmodules.vtkRenderingCore import vtkPointGaussianMapper
from rendering.viewactors.dataviewactors import create_data_view_actors
import rendering.core as core
import config
import vtk
from rendering.viewactors.typeexploreractors import create_type_explorer_actors
from rendering.viewactors.volumeviewactors import create_volume_view_actors


class Actors:

    def __init__(self, parent):
        from rendering.window import Window
        self.parent: Window = parent
        self.property_map = core.create_property_map()
        self.actors = {}
        self.mapper = vtkPointGaussianMapper()
        self.polydata = None
        self.polycopy = None

    def load_polytope(self, filename):
        if config.File != filename:
            config.File = filename
            print(f'Reading {filename}...')
            reader = vtk.vtkXMLPolyDataReader()
            reader.SetFileName(filename)
            reader.Update()
            self.polydata: vtk.vtkPolyData = reader.GetOutput()
            self.polycopy = self.polydata
            self.update_scalars()

    def update_scalars(self):
        self.polydata.GetPointData().SetActiveScalars(config.ArrayName)

    def update_actors(self):
        self.remove_actors()
        self.polydata.GetPointData().SetActiveScalars(config.ArrayName)
        range = self.polydata.GetPointData().GetScalars().GetRange()
        config.RangeMin = range[0]
        config.RangeMax = range[1]
        if config.CurrentView == 'Type Explorer':
            create_type_explorer_actors(self)
        elif config.CurrentView == 'Data View':
            create_data_view_actors(self)
        elif config.CurrentView == 'Volume View':
            create_volume_view_actors(self)

    def remove_actors(self):
        for name, actor in self.actors.items():
            if name == 'grid':
                self.parent.ren.RemoveVolume(actor)
            else:
                self.parent.ren.RemoveActor(actor)
        self.actors = {}

    def add_actors(self):
        for actor in self.actors.values():
            self.parent.ren.AddActor(actor)

    def show_actor(self, name):
        if self.property_map[name][3]:
            return
        self.edit_property_map(name, 3, True)
        self.parent.ren.AddActor(self.actors[name])

    def hide_actor(self, name):
        if not self.property_map[name][3]:
            return
        self.edit_property_map(name, 3, False)
        self.parent.ren.RemoveActor(self.actors[name])

    def edit_property_map(self, name, index, val):
        lst = list(self.property_map[name])
        lst[index] = val
        self.property_map[name] = tuple(lst)