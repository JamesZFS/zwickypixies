from vtkmodules.vtkCommonDataModel import vtkPiecewiseFunction
from vtkmodules.vtkRenderingCore import vtkPointGaussianMapper

import rendering.core as core
import config
import vtk

from dataops.filters import threshold_points


class Actors:

    def __init__(self, parent):
        self.parent = parent
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
            config.ThresholdMin = None
            config.ThresholdMax = None

    def update_scalars(self):
        self.polydata.GetPointData().SetActiveScalars(config.ArrayName)

    def update_actors(self):
        self.remove_actors()
        self.polydata.GetPointData().SetActiveScalars(config.ArrayName)
        range = self.polydata.GetPointData().GetScalars().GetRange()
        config.RangeMin = range[0]
        config.RangeMax = range[1]
        if config.CurrentView == 'Type Explorer':
            split_polydata = core.split_particles(self.polydata)
            self.actors = {name: core.create_type_explorer_actor(data) for name, data in split_polydata.items()}
            for name, actor in self.actors.items():
                core.update_view_property(actor, *self.property_map[name])
            for name, (color, opacity, radius, show) in self.property_map.items():
                if show:
                    self.parent.ren.AddActor(self.actors[name])
        elif config.CurrentView == 'Data View':
            pd = threshold_points(self.polydata)
            self.parent.toolbar.set_thresh_text(config.ThresholdMin, config.ThresholdMax)
            split_polydata = core.split_particles(pd)
            self.actors = {name: core.create_data_view_actor(data) for name, data in split_polydata.items()}
            for name, (color, opacity, radius, show) in self.property_map.items():
                if show:
                    self.parent.ren.AddActor(self.actors[name])
        elif config.CurrentView == 'Volume View':
            bounds = self.polycopy.GetBounds()
            grid_resolution = (100, 100, 100)
            grid = core.map_point_cloud_to_grid(self.polycopy, bounds, grid_resolution)
            color_map = core.create_view_color_map()
            grid_actor = core.create_grid_actor(grid, color_map)
            opacityTransferFunction = vtkPiecewiseFunction()
            opacityTransferFunction.AddPoint(20, 0)
            opacityTransferFunction.AddPoint(255, 1)
            grid_actor.GetProperty().SetColor(color_map)
            grid_actor.GetProperty().SetScalarOpacity(opacityTransferFunction)
            self.actors = {'grid': grid_actor}
            self.parent.ren.AddActor(grid_actor)


    def remove_actors(self):
        for actor in self.actors.values():
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