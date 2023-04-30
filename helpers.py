# VTK Polydata helpers

import numpy as np
from mpl_toolkits.mplot3d import axes3d
import matplotlib
import matplotlib.pyplot as plt
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor
from vtkmodules.vtkCommonCore import vtkLookupTable
import argparse
from scipy.interpolate import interp1d


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
    # print()
    # print('First point: ', polydata.GetPoint(0))

    # # Print the array data for the first point
    # for i in range(polydata.GetPointData().GetNumberOfArrays()):
    #     name = polydata.GetPointData().GetArrayName(i)
    #     dim = polydata.GetPointData().GetArray(i).GetNumberOfComponents()
    #     dtype = polydata.GetPointData().GetArray(i).GetDataTypeAsString()
    #     print(
    #         f'Array {i:2}: {name:5} = {polydata.GetPointData().GetArray(i).GetTuple(0)}')

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


def plt_vector_field(x:np.ndarray, y:np.ndarray, z:np.ndarray, u:np.ndarray, v:np.ndarray, w:np.ndarray, demo=False):
    """
    Input Parameters

    x,y,z (numpy.ndarray, z is optional): An array representing x,y,z-coordinates of the points in the 3D grid.
    u (numpy.ndarray): An array representing x-components of the vector field.
    v (numpy.ndarray): An array representing y-components of the vector field.
    w (numpy.ndarray is optional): An array representing z-components of the vector field.
    """
    matplotlib.use('tkagg')
    fig = plt.figure()
    ax=fig.add_subplot(projection="3d")
    if demo:
        x, y, z = np.meshgrid(np.arange(-2, 2, 0.5),
                            np.arange(-2, 2, 0.5),
                            np.arange(-2, 2, 0.5))

        u = 3*(np.sin(np.pi * x) * np.cos(np.pi * y) * np.cos(np.pi * z))
        v = x+y+z#2*(x+y) * np.sin(np.pi * y) * np.cos(np.pi * z)
        w = x**2#(x+z)*(x-y)*1.2
    ax.quiver(x, y, z, v, u, w, length=0.1, cmap='viridis')
    #ax.scatter(x, y, z, c=u, cmap='viridis')

    plt.show()


def plt_scatter_plot(x, y, z=None, c=None, cmap='viridis', demo=False):
    """
    Create a 3D scatter plot using matplotlib.

    Parameters:
        - x (numpy.ndarray): An array representing x-coordinates of the points.
        - y (numpy.ndarray): An array representing y-coordinates of the points.
        - z (numpy.ndarray, optional): An array representing z-coordinates of the points.
        - c (numpy.ndarray or None, optional): An array representing the color of each point. If None, default color
                                              will be used. Default is None.
        - cmap (str, optional): The colormap to use for coloring the points. Default is 'viridis'.
    """
    if z is not None:
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        if demo:
            x = np.random.rand(1000)  # Generate random x-coordinates
            y = np.random.rand(1000)  # Generate random y-coordinates
            z = np.random.rand(1000)  # Generate random z-coordinates
            c = np.random.rand(1000)  # Generate random color values 
        ax.scatter(x, y, z, c=c, cmap=cmap)
        plt.show()
    else:
        plt.plot(x, y, c=c, cmap=cmap)


def create_lookup_table_from_array(colors: np.ndarray, num_table_entries: int = 256):
    assert colors.shape[1] == 3, 'Colors must be a Nx3 array'
    # Build a 1d interpolation function from the given color array
    x = np.linspace(0, 1, colors.shape[0])
    color_map = interp1d(x, colors, axis=0)

    lut = vtkLookupTable()
    lut.SetScaleToLinear()
    lut.SetNumberOfTableValues(num_table_entries)
    for i, x in enumerate(np.linspace(0, 1, num_table_entries)):
        r, g, b = color_map(x)
        lut.SetTableValue(i, r, g, b)
    
    return lut


def create_lookup_table(mode: str = 'coolwarm', num_table_entries: int = 256):
    # Set up color map

    if mode == 'rainbow':
        lut = vtkLookupTable()
        lut.SetHueRange(0.667, 0.0)
        lut.SetSaturationRange(1.0, 1.0)
        lut.SetValueRange(1.0, 1.0)
        lut.SetNumberOfColors(num_table_entries)
        lut.Build()
    elif mode == 'gray':
        lut = vtkLookupTable()
        lut.SetHueRange(0, 0)
        lut.SetSaturationRange(0, 0)
        lut.SetValueRange(0.2, 1.0)
        lut.SetNumberOfColors(num_table_entries)
        lut.Build()
    elif mode == 'coolwarm':
        colors = np.array([
            [0.6980, 0.0941, 0.1686],  # Red
            [0.8392, 0.3765, 0.3020],
            [0.9569, 0.6471, 0.5098],
            [0.9922, 0.8588, 0.7804],
            [0.9686, 0.9686, 0.9686],  # White
            [0.8196, 0.8980, 0.9412],
            [0.5725, 0.7725, 0.8706],
            [0.2627, 0.5765, 0.7647],
            [0.1294, 0.4000, 0.6745],  # Blue
        ])
        lut = create_lookup_table_from_array(np.flip(colors, axis=0), num_table_entries)
    else:
        raise ValueError(f'Unknown color mode: {mode}')

    return lut


def create_legend(lut: vtkLookupTable, title=None):
    # Render a color map legend at the right side of the window
    legend = vtkScalarBarActor()
    legend.SetLookupTable(lut)
    legend.SetNumberOfLabels(8)
    if title: legend.SetTitle(title)
    legend.SetVerticalTitleSeparation(6)
    legend.GetPositionCoordinate().SetValue(0.92, 0.1)
    legend.SetWidth(0.06)
    
    return legend


def get_program_parameters():
    description = 'Visualize a cosmology simulation polydata (vtp) file.'
    epilogue = ''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='path to Full.cosmo.xxx.vtp')
    args = parser.parse_args()
    return args.filename
