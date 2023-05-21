from vtkmodules.vtkCommonDataModel import vtkPiecewiseFunction
import vtk

import config


def create_volume_view_actors(actorhandler):
    bounds = actorhandler.polydata.GetBounds()

    grid_resolution = (100, 100, 100)
    grid = vtk.vtkImageData()
    grid.SetDimensions(grid_resolution)
    grid.SetOrigin(bounds[0], bounds[2], bounds[4])
    grid.SetSpacing(
        (bounds[1] - bounds[0]) / (grid_resolution[0] - 1),
        (bounds[3] - bounds[2]) / (grid_resolution[1] - 1),
        (bounds[5] - bounds[4]) / (grid_resolution[2] - 1)
    )
    scalars = vtk.vtkFloatArray()
    scalars.SetNumberOfComponents(1)
    scalars.SetNumberOfTuples(grid.GetNumberOfPoints())
    scalars.SetName(config.ArrayName)

    num_points = vtk.vtkTypeUInt32Array()
    num_points.SetNumberOfComponents(1)
    num_points.SetNumberOfTuples(grid.GetNumberOfPoints())

    for i in range(actorhandler.polydata.GetNumberOfPoints()):
        point = actorhandler.polydata.GetPoint(i)
        value = actorhandler.polydata.GetPointData().GetArray(config.ArrayName).GetValue(i)
        grid_point_id = grid.FindPoint(point)
        if grid_point_id >= 0:
            # accumulate
            scalars.SetValue(grid_point_id, scalars.GetValue(grid_point_id) + value)
            num_points.SetValue(grid_point_id, num_points.GetValue(grid_point_id) + 1)

    # normalize
    for i in range(grid.GetNumberOfPoints()):
        if num_points.GetValue(i) > 0:
            scalars.SetValue(i, scalars.GetValue(i) / num_points.GetValue(i))

    grid.GetPointData().SetScalars(scalars)

    color_map = vtk.vtkColorTransferFunction()

    color_map.AddRGBPoint(0.0, 0.0, 0.0, 0.0)
    color_map.AddRGBPoint(64.0, 1.0, 0.0, 0.0)
    color_map.AddRGBPoint(128.0, 0.0, 0.0, 1.0)
    color_map.AddRGBPoint(192.0, 0.0, 1.0, 0.0)
    color_map.AddRGBPoint(255.0, 1.0, 1.0, 1.0)
    mapper = vtk.vtkSmartVolumeMapper()
    mapper.SetInputData(grid)

    volume_property = vtk.vtkVolumeProperty()
    volume_property.SetColor(color_map)
    volume_property.SetScalarOpacityUnitDistance(0.1)
    volume_property.ShadeOff()

    grid_actor = vtk.vtkVolume()
    grid_actor.SetMapper(mapper)
    grid_actor.SetProperty(volume_property)

    opacityTransferFunction = vtkPiecewiseFunction()
    opacityTransferFunction.AddPoint(20, 1e-1)
    opacityTransferFunction.AddPoint(255, 1e-1)

    grid_actor.GetProperty().SetColor(color_map)
    grid_actor.GetProperty().SetScalarOpacity(opacityTransferFunction)
    actorhandler.actors = {'grid': grid_actor}
    actorhandler.parent.ren.AddVolume(grid_actor)