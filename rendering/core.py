import vtk
import config
import numpy as np
from vtkmodules.util.numpy_support import vtk_to_numpy, numpy_to_vtk


def split_particles(polydata: vtk.vtkPolyData, pretty_print=False):
    pts_np = vtk_to_numpy(polydata.GetPoints().GetData())
    mask_np = vtk_to_numpy(polydata.GetPointData().GetArray('mask')).astype(np.int32)
    active_scalar_name = polydata.GetPointData().GetScalars().GetName()
    scalar_np = vtk_to_numpy(polydata.GetPointData().GetScalars())
    hh_np = vtk_to_numpy(polydata.GetPointData().GetArray('hh'))

    type_mask = {'dm': mask_np & (1 << 1) == 0}
    type_mask['baryon'] = ~type_mask['dm']
    type_mask['star'] = type_mask['baryon'] & (mask_np & (1 << 5) != 0)
    type_mask['wind'] = type_mask['baryon'] & (mask_np & (1 << 6) != 0)
    type_mask['gas'] = type_mask['baryon'] & (mask_np & (1 << 7) != 0)
    type_mask['agn'] = type_mask['dm'] & (mask_np & (1 << 8) != 0)
    type_mask['dm'] = type_mask['dm'] & ~type_mask['agn']
    type_mask['baryon'] = type_mask['baryon'] & ~type_mask['star'] & ~type_mask['wind'] & ~type_mask['gas']

    def make_polydata(pts, scalars, hh):
        out = vtk.vtkPolyData()
        point_data = vtk.vtkPoints()
        point_data.SetData(numpy_to_vtk(pts))
        out.SetPoints(point_data)
        
        active_scalar_arr = numpy_to_vtk(scalars)
        active_scalar_arr.SetName(active_scalar_name)
        out.GetPointData().AddArray(active_scalar_arr)

        hh_arr = numpy_to_vtk(hh)
        hh_arr.SetName('hh')
        out.GetPointData().AddArray(hh_arr)

        out.GetPointData().SetActiveScalars(active_scalar_name)
        return out

    type_polydata = {name: make_polydata(pts_np[mask], scalar_np[mask], hh_np[mask]) for name, mask in type_mask.items()}

    # pretty print counts
    if pretty_print:
        for name, data in type_polydata.items():
            num = data.GetNumberOfPoints()
            percent = num / polydata.GetNumberOfPoints() * 100 if polydata.GetNumberOfPoints() > 0 else 0
            print(f'{name:8} {num:8} {percent:9.3f} %')

    # check counts
    assert sum([type_polydata[name].GetNumberOfPoints() for name in type_mask]) == polydata.GetNumberOfPoints()

    return type_polydata



def create_type_explorer_actor(polydata: vtk.vtkPolyData, color: vtk.vtkColor3d = None, opacity: float = None,
                               radius: float = None, show=None):
    mapper = vtk.vtkPointGaussianMapper()
    mapper.SetInputData(polydata)
    mapper.ScalarVisibilityOff()
    mapper.EmissiveOff()
    mapper.SetScaleArray('radius')  # assign heterogenous radius to each point
    if radius is not None:
        update_radius(polydata, min_value=0.5 * radius, max_value=1.5 * radius)

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
    # mapper.SetScaleFactor(0.1)
    mapper.EmissiveOff()
    mapper.SetScaleArray('radius')  # assign heterogenous radius to each point
    update_radius(polydata, min_value=0.01, max_value=0.2)
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
        polydata = actor.GetMapper().GetInput()
        update_radius(polydata, min_value=0.5 * radius, max_value=1.5 * radius)


# Normalize sph smoothing length to a given max value, and store it to radius array
def update_radius(polydata: vtk.vtkPolyData, min_value: float = 0.01, max_value: float = 1.):
    hh = vtk_to_numpy(polydata.GetPointData().GetArray('hh'))
    if len(hh) == 0: return
    hmax = hh.max()
    hmin = hh.min()
    if hmax - hmin < 1e-6:
        rad = np.ones_like(hh) * max_value
    else:
        rad = min_value + (max_value - min_value) * (hh - hmin) / (hmax - hmin)
    rad_arr = numpy_to_vtk(rad)
    rad_arr.SetName('radius')
    polydata.GetPointData().AddArray(rad_arr)


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


def create_view_color_transfer_function():
    colorTransferFunction = vtk.vtkColorTransferFunction()
    colorTransferFunction.AddRGBPoint(0.0, 0.0, 0.0, 0.0)
    colorTransferFunction.AddRGBPoint(64.0, 1.0, 0.0, 0.0)
    colorTransferFunction.AddRGBPoint(128.0, 0.0, 0.0, 1.0)
    colorTransferFunction.AddRGBPoint(192.0, 0.0, 1.0, 0.0)
    colorTransferFunction.AddRGBPoint(255.0, 1.0, 1.0, 1.0)
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

    scalars = vtk.vtkFloatArray()
    scalars.SetNumberOfComponents(1)
    scalars.SetNumberOfTuples(grid.GetNumberOfPoints())
    scalars.SetName(config.ArrayName)

    num_points = vtk.vtkTypeUInt32Array()
    num_points.SetNumberOfComponents(1)
    num_points.SetNumberOfTuples(grid.GetNumberOfPoints())

    for i in range(polydata.GetNumberOfPoints()):
        point = polydata.GetPoint(i)
        value = polydata.GetPointData().GetArray(config.ArrayName).GetValue(i)
        grid_point_id = grid.FindPoint(point)
        if grid_point_id >= 0:
            # Accumulate the value and the number of points to compute the average
            scalars.SetValue(grid_point_id, scalars.GetValue(grid_point_id) + value)
            num_points.SetValue(grid_point_id, num_points.GetValue(grid_point_id) + 1)

    # Compute the average
    for i in range(grid.GetNumberOfPoints()):
        if num_points.GetValue(i) > 0:
            scalars.SetValue(i, scalars.GetValue(i) / num_points.GetValue(i))

    grid.GetPointData().SetScalars(scalars)
    return grid

def create_grid_volume(grid, color_map):
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
