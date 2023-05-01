import vtk
import numpy as np
import helpers


# copied from https://kitware.github.io/vtk-examples/site/Python/Meshes/PointInterpolator/
splat_shader_code = '''
//VTK::Color::Impl\n
float dist = dot(offsetVCVSOutput.xy,offsetVCVSOutput.xy);\n
if (dist > 1.0) {\n
    discard;\n
} else {\n
    float scale = (1.0 - dist);\n
    ambientColor *= scale;\n
    diffuseColor *= scale;\n
}\n
'''


def decode_mask(mask: int, return_dict: bool = False):
    is_dm = mask & (1 << 1) == 0
    is_baryon = not is_dm
    is_star = is_baryon and mask & (1 << 5) != 0
    is_wind = is_baryon and mask & (1 << 6) != 0
    is_gas = is_baryon and mask & (1 << 7) != 0
    is_agn = is_dm and mask & (1 << 8) != 0

    if return_dict:
        return {
            'is_dm': is_dm,
            'is_baryon': is_baryon,
            'is_star': is_star,
            'is_wind': is_wind,
            'is_gas': is_gas,
            'is_agn': is_agn
        }
    else:
        if is_agn: return 'agn'
        if is_dm: return 'dm'
        if is_star: return 'star'
        if is_wind: return 'wind'
        if is_gas: return 'gas'
        return 'baryon'


def split_particles(polydata: vtk.vtkPolyData):
    # Split polydata into multiple polydata based on the mask
    mask_array: vtk.vtkUnsignedShortArray = polydata.GetPointData().GetArray('mask')

    # create a dictionary of polydata
    def make_polydata():
        data = vtk.vtkPolyData()
        data.SetPoints(vtk.vtkPoints())
        return data
    
    type_names = ['agn', 'star', 'wind', 'gas', 'baryon', 'dm']
    type_polydata = {name: make_polydata() for name in type_names}

    # scatter points into the corresponding polydata
    for i in range(polydata.GetNumberOfPoints()):
        mask = mask_array.GetValue(i)
        name = decode_mask(mask)
        type_polydata[name].GetPoints().InsertNextPoint(polydata.GetPoint(i))

    # check counts
    assert sum([type_polydata[name].GetNumberOfPoints() for name in type_names]) == polydata.GetNumberOfPoints()

    # pretty print counts
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


def create_renderer(actors):
    # create a rendering window and renderer
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    renWin.SetWindowName('Particle Types')
    renWin.SetSize(2048, 2048)

    # create a renderwindowinteractor
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    # change interaction style to trackball
    style = vtk.vtkInteractorStyleTrackballCamera()
    iren.SetInteractorStyle(style)

    ren.SetBackground(0, 0, 0)
    for actor in actors:
        ren.AddActor(actor)
    
    # enable user interface interactor
    iren.Initialize()
    renWin.Render()
    iren.Start()

    return ren


def main():
    filename = helpers.get_program_parameters()

    # read polydata
    print(f'Reading {filename}...')
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(filename)
    reader.Update()
    polydata: vtk.vtkPolyData = reader.GetOutput()

    type_polydata = split_particles(polydata)

    # color different types
    colors = vtk.vtkNamedColors()
    property_map = {
        'agn':    (colors.GetColor3d('Red'),        0.9, 0.8),  # (color, opacity, radius)
        'star':   (colors.GetColor3d('Yellow'),     0.6, 0.2),
        'wind':   (colors.GetColor3d('Aqua'),       0.6, 0.3),
        'gas':    (colors.GetColor3d('Lime'),       0.6, 0.2),
        'baryon': (colors.GetColor3d('Snow'),       0.2, 0.1),
        'dm':     (colors.GetColor3d('RoyalBlue'),  0.2, 0.1),
    }

    # visualize type information
    type_actors = {name: create_point_actor(data) for name, data in type_polydata.items()}
    for name, actor in type_actors.items():
        update_view_property(actor, *property_map[name])
    
    # render!
    renderer = create_renderer(type_actors.values())


if __name__ == '__main__':
    main()
