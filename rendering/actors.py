from vtkmodules.vtkRenderingCore import vtkPointGaussianMapper

import rendering.core as core
import config
import helpers
import vtk


class Actors:

    def __init__(self, parent):
        self.parent = parent
        self.data_view_property_map = core.create_data_view_property_map()
        self.type_explorer_property_map = core.create_type_explorer_property_map()
        self.property_map = None
        self.actors = {}
        self.mapper = vtkPointGaussianMapper()
        self.polydata = None
        self.update_actors(helpers.get_program_parameters())

    def update_actors(self, filename, keep_map=False):
        for actor in self.actors.values():
            self.parent.ren.RemoveActor(actor)
        if config.File != filename:
            config.File = filename
            print(f'Reading {filename}...')
            reader = vtk.vtkXMLPolyDataReader()
            reader.SetFileName(filename)
            reader.Update()
            self.polydata: vtk.vtkPolyData = reader.GetOutput()
        self.polydata.GetPointData().SetActiveScalars(config.ArrayName)
        range = self.polydata.GetPointData().GetScalars().GetRange()
        config.RangeMin = range[0]
        config.RangeMax = range[1]
        split_polydata = core.split_particles(self.polydata)
        if config.CurrentView == 'Type Explorer':
            if not keep_map: self.property_map = self.type_explorer_property_map
            self.actors = {name: core.create_type_explorer_actor(data) for name, data in split_polydata.items()}
        elif config.CurrentView == 'Data View':
            if not keep_map: self.property_map = self.data_view_property_map
            self.actors = {name: core.create_data_view_actor(data) for name, data in split_polydata.items()}
        for name, actor in self.actors.items():
            core.update_view_property(actor, *self.property_map[name])
        for actor in self.actors.values():
            self.parent.ren.AddActor(actor)

    def remove_actors(self):
        for actor in self.actors.values():
            self.parent.ren.RemoveActor(actor)
