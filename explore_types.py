import vtk
import numpy as np
import helpers
from collections import Counter


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


def count_particle_types(polydata: vtk.vtkPolyData):
    # convert to numpy array
    masks = helpers.get_numpy_array(polydata, 'mask')

    # count number of points in each mask
    mask_counts = np.unique(masks, return_counts=True)
    counter = Counter(dict(zip(mask_counts[0], mask_counts[1])))

    # pretty print the counter
    print('Mask counts:')
    for key, value in counter.items():
        
        # decode mask
        mask = decode_mask(key, return_dict=True)
        desc = 'dark matter' if mask['is_dm'] else 'baryon'
        if mask['is_star']: desc += ', star'
        if mask['is_wind']: desc += ', wind'
        if mask['is_gas']: desc += ', gas'
        if mask['is_agn']: desc += ', agn'

        print(f'{key} ({desc}): {value}')


def assign_color_array(polydata: vtk.vtkPolyData):
    named_colors = vtk.vtkNamedColors()
    # Add a color array to the polydata based on the particle types
    color_map = {
        'agn': named_colors.GetColor3d('OrangeRed'),
        'dm': named_colors.GetColor3d('RoyalBlue'),
        'star': named_colors.GetColor3d('Yellow'),
        'wind': named_colors.GetColor3d('LimeGreen'),
        'gas': named_colors.GetColor3d('LightGrey'),
        'baryon': named_colors.GetColor3d('WhiteSmoke'),
    }
    # color_map['agn'].SetAlpha(1.0)
    # color_map['dm'].SetAlpha(0.1)
    # color_map['star'].SetAlpha(0.7)
    # color_map['wind'].SetAlpha(0.7)
    # color_map['gas'].SetAlpha(0.7)
    # color_map['baryon'].SetAlpha(0.2)

    # create a color array
    colors = vtk.vtkFloatArray()
    colors.SetNumberOfComponents(3)
    colors.SetName('colors')

    mask_array: vtk.vtkUnsignedShortArray = polydata.GetPointData().GetArray('mask')

    # assign colors to each point
    for i in range(polydata.GetNumberOfPoints()):
        ptype = decode_mask(mask_array.GetValue(i))
        color = color_map[ptype]
        colors.InsertNextTuple(color)

    polydata.GetPointData().AddArray(colors)


def create_actor(polydata: vtk.vtkPolyData):
    mapper = vtk.vtkPointGaussianMapper()
    mapper.SetInputData(polydata)
    # mapper.SetScalarRange(range)
    # mapper.ScalarVisibilityOff()
    mapper.SetScaleFactor(0.2)  # radius
    mapper.EmissiveOff()
    mapper.SetSplatShaderCode(
        # copied from https://kitware.github.io/vtk-examples/site/Python/Meshes/PointInterpolator/
        "//VTK::Color::Impl\n"
        "float dist = dot(offsetVCVSOutput.xy,offsetVCVSOutput.xy);\n"
        "if (dist > 1.0) {\n"
        "  discard;\n"
        "} else {\n"
        "  float scale = (1.0 - dist);\n"
        "  ambientColor *= scale;\n"
        "  diffuseColor *= scale;\n"
        "}\n"
    )

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    # actor.GetProperty().SetPointSize(2)
    # actor.GetProperty().SetOpacity(0.4)
    # actor.GetProperty().SetColor(1, 0, 0)

    return actor


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

    count_particle_types(polydata)
    assign_color_array(polydata)

    # visualize type information
    polydata.GetPointData().SetActiveScalars('colors')
    point_actor = create_actor(polydata)
    renderer = create_renderer([point_actor])


if __name__ == '__main__':
    main()
