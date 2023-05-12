from vtkmodules.vtkRenderingCore import vtkPointGaussianMapper

import rendering.core as core
import config
import helpers
import vtk


class Actors:

    def __init__(self, parent):
        self.parent = parent
        self.property_map = core.create_type_explorer_property_map()
        self.actors = {}
        self.update_actors(helpers.get_program_parameters())
        self.current_view = 'Type Explorer'
        self.mapper = vtkPointGaussianMapper()
        self.polydata = None

    def update_actors(self, filename):
        for actor in self.actors.values():
            self.parent.ren.RemoveActor(actor)
        if config.File != filename:
            config.File = filename
            print(f'Reading {filename}...')
            reader = vtk.vtkXMLPolyDataReader()
            reader.SetFileName(filename)
            reader.Update()
            self.polydata: vtk.vtkPolyData = reader.GetOutput()

        if config.CurrentView == 'Type Explorer':
            type_polydata = core.split_particles(self.polydata)
            self.actors = {name: core.create_type_explorer_actor(data) for name, data in type_polydata.items()}
            for name, actor in self.actors.items():
                core.update_view_property(actor, *self.property_map[name])
        elif config.CurrentView == 'Data View':
            self.actors = {name: core.create_data_view_actor(data) for name, data in type_polydata.items()}
        for actor in self.actors.values():
            self.parent.ren.AddActor(actor)




    def remove_actors(self):
        for actor in self.actors.values():
            self.parent.ren.RemoveActor(actor)
