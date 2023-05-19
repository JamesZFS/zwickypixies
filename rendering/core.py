import vtk
import helpers
import config
from dataops.filters import mask_points


def split_particles(polydata: vtk.vtkPolyData, pretty_print=False):
    type_names = ['agn', 'star', 'wind', 'gas', 'baryon', 'dm']
    type_polydata = {name: mask_points(polydata, particle_type=name, array_name=config.ArrayName) for name in
                     type_names}
    #assert sum([type_polydata[name].GetNumberOfPoints() for name in type_names]) == polydata.GetNumberOfPoints()
    if pretty_print:
        for name, data in type_polydata.items():
            num = data.GetNumberOfPoints()
            percent = num / polydata.GetNumberOfPoints() * 100
            print(f'{name:8} {num:8} {percent:9.3f} %')

    return type_polydata


def create_type_explorer_actor(polydata: vtk.vtkPolyData, color: vtk.vtkColor3d = None, opacity: float = None,
                               radius: float = None, show=None):
    mapper = vtk.vtkPointGaussianMapper()
    mapper.SetInputData(polydata)
    mapper.ScalarVisibilityOff()
    mapper.EmissiveOff()
    if radius is not None: mapper.SetScaleFactor(radius)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    if color is not None: actor.GetProperty().SetColor(color)
    if opacity is not None: actor.GetProperty().SetOpacity(opacity)

    return actor


def create_data_view_actor(polydata: vtk.vtkPolyData, color: vtk.vtkColor3d = None, opacity: float = None,
                           radius: float = None, show=None):
    mapper = vtk.vtkPointGaussianMapper()
    mapper.SetInputData(polydata)
    mapper.SetScalarRange([config.RangeMin, config.RangeMax])
    mapper.SetScaleFactor(0.2)
    mapper.EmissiveOff()
    mapper.SetLookupTable(config.Lut)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetOpacity(0.2)
    return actor


def update_view_property(actor: vtk.vtkActor, color: vtk.vtkColor3d = None, opacity: float = None, radius: float = None,
                         show=None):
    if color:
        actor.GetProperty().SetColor(color)
    if opacity:
        actor.GetProperty().SetOpacity(opacity)
    if radius:
        actor.GetMapper().SetScaleFactor(radius)


def update_view_property_data_view(actor: vtk.vtkActor, color: vtk.vtkColor3d, opacity: float, radius: float,
                                   show=None):
    actor.GetProperty().SetOpacity(0.2)


def create_property_map() -> dict:
    colors = vtk.vtkNamedColors()
    return {
        'agn': (colors.GetColor3d('OrangeRed'), 0.9, 0.90, True),  # (color, opacity, radius, show)
        'star': (colors.GetColor3d('Yellow'), 0.6, 0.20, True),
        'wind': (colors.GetColor3d('Fuchsia'), 0.6, 0.30, True),
        'gas': (colors.GetColor3d('Lime'), 0.6, 0.20, True),
        'baryon': (colors.GetColor3d('Snow'), 0.1, 0.05, True),
        'dm': (colors.GetColor3d('RoyalBlue'), 0.1, 0.05, True),
    }


def create_view_color_map():
    colorTransferFunction = vtk.vtkColorTransferFunction()
    colorTransferFunction.AddRGBPoint(0.0, 0.0, 0.0, 0.0)
    colorTransferFunction.AddRGBPoint(64.0, 1.0, 0.0, 0.0)
    colorTransferFunction.AddRGBPoint(128.0, 0.0, 0.0, 1.0)
    colorTransferFunction.AddRGBPoint(192.0, 0.0, 1.0, 0.0)
    colorTransferFunction.AddRGBPoint(255.0, 0.0, 0.2, 0.0)
    return colorTransferFunction

def map_point_cloud_to_grid(polydata, bounds, grid_resolution):
    grid = vtk.vtkImageData()
    grid.SetDimensions(grid_resolution)
    grid.SetOrigin(bounds[0], bounds[2], bounds[4])
    grid.SetSpacing(
        (bounds[1] - bounds[0]) / (grid_resolution[0] - 1),
        (bounds[3] - bounds[2]) / (grid_resolution[1] - 1),
        (bounds[5] - bounds[4]) / (grid_resolution[2] - 1)
    )

    num_points = grid.GetNumberOfPoints()

    scalars = vtk.vtkFloatArray()
    scalars.SetNumberOfComponents(1)
    scalars.SetNumberOfTuples(num_points)
    scalars.SetName(config.ArrayName)

    for i in range(polydata.GetNumberOfPoints()):
        point = polydata.GetPoint(i)
        value = polydata.GetPointData().GetArray(config.ArrayName).GetValue(i)
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
