import rendering.core as core
import helpers
import vtk


class Actors:

    def __init__(self, parent):
        self.parent = parent
        self.property_map = core.create_default_property_map()
        self.type_actors = {}
        self.update_actors(helpers.get_program_parameters())

    def update_actors(self, filename):
        for actor in self.type_actors.values():
            self.parent.ren.RemoveActor(actor)

        print(f'Reading {filename}...')
        reader = vtk.vtkXMLPolyDataReader()
        reader.SetFileName(filename)
        reader.Update()
        polydata: vtk.vtkPolyData = reader.GetOutput()

        self.type_polydata = core.split_particles(polydata)

        self.type_actors = {name: core.create_point_actor(data) for name, data in self.type_polydata.items()}
        for name, actor in self.type_actors.items():
            core.update_view_property(actor, *self.property_map[name])

        for actor in self.type_actors.values():
            self.parent.ren.AddActor(actor)

    def remove_actors(self):
        for actor in self.type_actors.values():
            self.parent.ren.RemoveActor(actor)
