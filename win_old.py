from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
from vtkmodules.vtkCommonDataModel import vtkPiecewiseFunction
from rendering.window import startWindow
import vtk
from vtk.util import numpy_support
from helpers import *
from dataops.filters import *
from animation import *
from main import *
import config

filename = get_program_parameters()
# Read all the data from the file
reader = vtkXMLPolyDataReader()
reader.SetFileName(filename)
reader.Update()
config.File = filename
config.ArrayName = 'mass'
polydata = reader.GetOutput()
sliced_polydata = slice_polydata(polydata, 20000)
print_meta_data(sliced_polydata)
# data = get_numpy_pts(sliced_polydata)
data = get_numpy_pts(polydata)
uus = get_numpy_array(polydata=polydata, array_name='uu')
np.set_printoptions(threshold=10)



def create_color_map(polydata, array_name):
    data_range = polydata.GetPointData().GetArray(array_name).GetRange()

    colorTransferFunction = vtk.vtkColorTransferFunction()
    # color_map.SetColorSpaceToRGB()

    colorTransferFunction.AddRGBPoint(0.0, 0.0, 0.0, 0.0)
    colorTransferFunction.AddRGBPoint(64.0, 1.0, 0.0, 0.0)
    colorTransferFunction.AddRGBPoint(128.0, 0.0, 0.0, 1.0)
    colorTransferFunction.AddRGBPoint(192.0, 0.0, 1.0, 0.0)
    colorTransferFunction.AddRGBPoint(255.0, 0.0, 0.2, 0.0)
    # color_map.AddRGBPoint(data_range[0], 0, 0, 1)  # Blue for the lower end of the range
    # color_map.AddRGBPoint(data_range[1], 1, 0, 0)  # Red for the higher end of the range

    return colorTransferFunction


def create_point_cloud_actor(polydata, array_name, color_map):
    polydata.GetPointData().SetActiveScalars(array_name)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)
    mapper.SetLookupTable(color_map)
    mapper.SetScalarRange(0, 1)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetPointSize(2)

    return actor


def create_3d_grid(bounds, grid_resolution):
    grid = vtk.vtkImageData()
    grid.SetDimensions(grid_resolution)
    grid.SetOrigin(bounds[0], bounds[2], bounds[4])
    grid.SetSpacing(
        (bounds[1] - bounds[0]) / (grid_resolution[0] - 1),
        (bounds[3] - bounds[2]) / (grid_resolution[1] - 1),
        (bounds[5] - bounds[4]) / (grid_resolution[2] - 1)
    )

    return grid


def map_point_cloud_to_grid(polydata, grid, array_name):
    num_points = grid.GetNumberOfPoints()
    scalars = vtk.vtkFloatArray()
    scalars.SetNumberOfComponents(1)
    scalars.SetNumberOfTuples(num_points)
    scalars.SetName(array_name)

    for i in range(polydata.GetNumberOfPoints()):
        point = polydata.GetPoint(i)
        value = polydata.GetPointData().GetArray(array_name).GetValue(i)
        grid_point_id = grid.FindPoint(point)
        if grid_point_id >= 0:
            scalars.SetValue(grid_point_id, value)

    grid.GetPointData().SetScalars(scalars)

    return grid



def create_grid_actor(grid, color_map):
    mapper = vtk.vtkSmartVolumeMapper()
    mapper.SetInputData(grid)

    volume_property = vtk.vtkVolumeProperty()
    volume_property.SetColor(color_map)
    volume_property.SetScalarOpacityUnitDistance(0.1)
    volume_property.ShadeOff()

    volume = vtk.vtkVolume()
    volume.SetMapper(mapper)
    volume.SetProperty(volume_property)

    return volume


def create_grid_outline(grid):
    outline = vtk.vtkOutlineFilter()
    outline.SetInputData(grid)
    outline.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(outline.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    return actor


def main():
    filename = get_program_parameters()
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(filename)
    reader.Update()
    polydata = reader.GetOutput()

    # If needed, you can slice the polydata here
    # sliced_polydata = slice_polydata(polydata, 20000)

    bounds = polydata.GetBounds()
    array_name = 'phi'

    grid_resolution = (100, 100, 100)
    grid = create_3d_grid(bounds, grid_resolution)
    grid = map_point_cloud_to_grid(polydata, grid, array_name)

    color_map = create_color_map(polydata, array_name)
    grid_actor = create_grid_actor(grid, color_map)
    # grid_outline_actor = create_grid_outline(grid)

    opacityTransferFunction = vtkPiecewiseFunction()
    opacityTransferFunction.AddPoint(20, 1e-2)
    opacityTransferFunction.AddPoint(255, 1e-1)

    renderer = vtk.vtkRenderer()
    print(type(grid_actor))
    grid_actor.GetProperty().SetColor(color_map)
    grid_actor.GetProperty().SetScalarOpacity(opacityTransferFunction)
    renderer.AddActor(grid_actor)
    # renderer.AddActor(grid_outline_actor)

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)
    interactor.Initialize()
    interactor.Start()


if __name__ == '__main__':
    main()