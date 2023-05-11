import vtk
import helpers
from dataops.filters import mask_points

def split_particles(polydata: vtk.vtkPolyData, pretty_print=False):
    type_names = ['agn', 'star', 'wind', 'gas', 'baryon', 'dm']
    type_polydata = {name: mask_points(polydata, particle_type=name) for name in type_names}
    assert sum([type_polydata[name].GetNumberOfPoints() for name in type_names]) == polydata.GetNumberOfPoints()

    if pretty_print:
        for name, data in type_polydata.items():
            num = data.GetNumberOfPoints()
            percent = num / polydata.GetNumberOfPoints() * 100
            print(f'{name:8} {num:8} {percent:9.3f} %')
    
    return type_polydata


def create_point_actor(polydata: vtk.vtkPolyData, color: vtk.vtkColor3d = None, opacity: float = None, radius: float = None):
    mapper = vtk.vtkPointGaussianMapper()
    mapper.SetInputData(polydata)
    mapper.ScalarVisibilityOff()
    mapper.EmissiveOff()
    # mapper.SetSplatShaderCode(splat_shader_code)
    if radius is not None: mapper.SetScaleFactor(radius)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    if color is not None: actor.GetProperty().SetColor(color)
    if opacity is not None: actor.GetProperty().SetOpacity(opacity)

    return actor


def update_view_property(actor: vtk.vtkActor, color: vtk.vtkColor3d, opacity: float, radius: float):
    actor.GetProperty().SetColor(color)
    actor.GetProperty().SetOpacity(opacity)
    actor.GetMapper().SetScaleFactor(radius)


def create_default_property_map() -> dict:
    colors = vtk.vtkNamedColors()
    return {
        'agn':    (colors.GetColor3d('OrangeRed'),  0.9, 0.9),  # (color, opacity, radius)
        'star':   (colors.GetColor3d('Yellow'),     0.6, 0.2),
        'wind':   (colors.GetColor3d('Fuchsia'),    0.6, 0.3),
        'gas':    (colors.GetColor3d('Lime'),       0.6, 0.2),
        'baryon': (colors.GetColor3d('Snow'),       0.1, 0.05),
        'dm':     (colors.GetColor3d('RoyalBlue'),  0.1, 0.05),
    }
