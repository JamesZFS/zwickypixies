from vtkmodules.vtkCommonDataModel import vtkPiecewiseFunction
import rendering.core as core


def create_volume_view_actors(actor):
    print('Computing volume...')
    bounds = actor.polycopy.GetBounds()
    grid_resolution = (100, 100, 100)
    grid = core.map_point_cloud_to_grid(actor.polycopy, bounds, grid_resolution)
    colorTransferFunction = core.create_view_color_transfer_function()
    volume = core.create_grid_volume(grid, colorTransferFunction)
    opacityTransferFunction = vtkPiecewiseFunction()
    opacityTransferFunction.AddPoint(20, 0)
    opacityTransferFunction.AddPoint(255, 1)
    volume.GetProperty().SetColor(colorTransferFunction)
    volume.GetProperty().SetScalarOpacity(opacityTransferFunction)
    actor.actors = {'grid': volume}
    actor.parent.ren.AddVolume(volume)