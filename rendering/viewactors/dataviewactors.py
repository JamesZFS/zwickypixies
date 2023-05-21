import vtk
import config
import numpy as np
from vtkmodules.util.numpy_support import vtk_to_numpy, numpy_to_vtk

from dataops.filters import threshold_points
import rendering.core as core


def get_data_view_actors(polydata: vtk.vtkPolyData, color: vtk.vtkColor3d = None, opacity: float = None,
                         radius: float = None, show=None):
    mapper = vtk.vtkPointGaussianMapper()
    mapper.SetInputData(polydata)
    mapper.SetScalarRange([config.RangeMin, config.RangeMax])
    mapper.SetScaleFactor(config.DataViewRadius)
    mapper.EmissiveOff()
    mapper.SetScaleArray('radius')  # assign heterogenous radius to each point
    core.update_radius(polydata, min_value=0.01, max_value=0.2)
    mapper.SetLookupTable(config.Lut)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetOpacity(config.DataViewOpacity)
    return actor


def create_data_view_actors(actor):
    pd = threshold_points(actor.polydata)
    split_polydata = core.split_particles(pd)
    actor.actors = {name: get_data_view_actors(data) for name, data in split_polydata.items()}
    for name, (color, opacity, radius, show) in actor.property_map.items():
        if show:
            actor.parent.ren.AddActor(actor.actors[name])
