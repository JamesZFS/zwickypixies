import vtkmodules.vtkInteractionStyle
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader, vtkXMLPolyDataWriter
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkPointGaussianMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)

import numpy as np


index_to_array_name = []
array_name_to_index = {}


def get_program_parameters():
    import argparse
    description = 'Read a polydata file.'
    epilogue = ''''''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='path to Full.cosmo.xxx.vtp')
    args = parser.parse_args()
    return args.filename


def print_meta_data(polydata):
    print(type(polydata))
    # Print number of points and properties
    print('Number of points: ', polydata.GetNumberOfPoints())
    print('Number of point data arrays: ', polydata.GetPointData().GetNumberOfArrays())
    print('Number of cells: ', polydata.GetNumberOfCells())
    print('Number of cell data arrays: ', polydata.GetCellData().GetNumberOfArrays())

    # Print number of vertices and edges
    print('Number of vertices: ', polydata.GetNumberOfVerts())
    print('Number of lines: ', polydata.GetNumberOfLines())
    print('Number of polygons: ', polydata.GetNumberOfPolys())
    
    # Print the bounds
    xmin, xmax, ymin, ymax, zmin, zmax = polydata.GetBounds()
    print('Bounds: min = ({:6.3f}, {:6.3f}, {:6.3f}), max = ({:6.3f}, {:6.3f}, {:6.3f})'
          .format(xmin, ymin, zmin, xmax, ymax, zmax))

    # Print the names and dimensions of the point data arrays
    for i in range(polydata.GetPointData().GetNumberOfArrays()):
        name = polydata.GetPointData().GetArrayName(i)
        dim = polydata.GetPointData().GetArray(i).GetNumberOfComponents()
        dtype = polydata.GetPointData().GetArray(i).GetDataTypeAsString()
        print(f'Array {i:2}: {name:5}  {dim}d  {dtype}')
        index_to_array_name.append(name)
        array_name_to_index[name] = i

    # Investigate the first point
    print()
    print('First point: ', polydata.GetPoint(0))

    # Print the array data for the first point
    for i in range(polydata.GetPointData().GetNumberOfArrays()):
        name = polydata.GetPointData().GetArrayName(i)
        dim = polydata.GetPointData().GetArray(i).GetNumberOfComponents()
        dtype = polydata.GetPointData().GetArray(i).GetDataTypeAsString()
        print(f'Array {i:2}: {name:5} = {polydata.GetPointData().GetArray(i).GetTuple(0)}')
    
    print()


def slice_polydata(polydata, n_points):
    # Slice the polydata to the first n_points
    sliced_polydata = vtkPolyData()
    sliced_polydata.DeepCopy(polydata)
    sliced_polydata.GetPoints().Resize(n_points)
    sliced_polydata.GetPoints().Modified()
    return sliced_polydata


def get_numpy_array(polydata, array_name):
    # Convert a vtk array to a numpy array
    array = polydata.GetPointData().GetArray(array_name)
    n_components = array.GetNumberOfComponents()
    n_tuples = array.GetNumberOfTuples()
    if n_components == 1:
        return np.array(array)
    else:
        return np.array([array.GetTuple(i) for i in range(n_tuples)])
    

def get_numpy_pts(polydata):
    # Convert the points to a numpy array
    return np.array(polydata.GetPoints().GetData())


def visualize_pts(polydata, array_name):
    colors = vtkNamedColors()

    polydata.GetPointData().SetActiveScalars(array_name)
    range = polydata.GetPointData().GetScalars().GetRange()

    # Visualize as point gaussians
    point_mapper = vtkPointGaussianMapper()
    point_mapper.SetInputData(polydata)
    point_mapper.SetScalarRange(range)
    point_mapper.SetScaleFactor(0.2)  # radius
    point_mapper.EmissiveOff()
    point_mapper.SetSplatShaderCode(
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

    point_actor = vtkActor()
    point_actor.SetMapper(point_mapper)

    # # Create a sphere
    # sphereSource = vtkSphereSource()
    # sphereSource.SetCenter(0.0, 0.0, 0.0)
    # sphereSource.SetRadius(5.0)
    # # Make the surface smooth.
    # sphereSource.SetPhiResolution(100)
    # sphereSource.SetThetaResolution(100)

    # mapper = vtkPolyDataMapper()
    # mapper.SetInputConnection(sphereSource.GetOutputPort())

    # actor = vtkActor()
    # actor.SetMapper(mapper)
    # actor.GetProperty().SetColor(colors.GetColor3d("Cornsilk"))

    renderer = vtkRenderer()
    renderWindow = vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindowInteractor = vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    renderer.AddActor(point_actor)
    renderer.SetBackground(colors.GetColor3d('DimGray'))
    renderer.GetActiveCamera().Pitch(90)
    renderer.GetActiveCamera().SetViewUp(0, 0, 1)
    renderer.ResetCamera()

    renderWindow.SetSize(1024, 1024)
    renderWindow.Render()
    renderWindow.SetWindowName('Cosmology Data')
    renderWindowInteractor.Start()


def main():
    filename = get_program_parameters()

    # Read all the data from the file
    reader = vtkXMLPolyDataReader()
    reader.SetFileName(filename)
    reader.Update()

    polydata = reader.GetOutput()
    print_meta_data(polydata)

    # # Dump first 100 points to vtp file
    # sliced = slice_polydata(polydata, 10)
    # print_meta_data(sliced)
    
    # writer = vtkXMLPolyDataWriter()
    # writer.SetFileName('points10.vtp')
    # writer.SetInputData(sliced)
    # writer.Write()

    # pts = get_numpy_pts(polydata)
    # mass = get_numpy_array(polydata, 'mass')

    # print('Points: ', pts)
    # print('Mass: ', mass)

    visualize_pts(polydata, 'mass')


if __name__ == '__main__':
    main()
    