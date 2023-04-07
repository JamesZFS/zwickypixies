# VTK Polydata helpers

import numpy as np
from vtkmodules.vtkCommonDataModel import vtkPolyData

# A list of array names and a dictionary to map array names to indices
index_to_array_name = []
array_name_to_index = {}


def print_meta_data(polydata):
    print(type(polydata))  # always print the type of the object and look it up in the vtk docs if you don't know how to use it

    # Print number of points and properties
    print('Number of points: ', polydata.GetNumberOfPoints())
    print('Number of point data arrays: ',
          polydata.GetPointData().GetNumberOfArrays())
    print('Number of cells: ', polydata.GetNumberOfCells())
    print('Number of cell data arrays: ',
          polydata.GetCellData().GetNumberOfArrays())

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
        print(
            f'Array {i:2}: {name:5} = {polydata.GetPointData().GetArray(i).GetTuple(0)}')

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
