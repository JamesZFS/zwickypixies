import vtkmodules.vtkInteractionStyle
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkLookupTable
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader, vtkXMLPolyDataWriter
from vtkmodules.vtkFiltersSources import vtkPlaneSource
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkFiltersPoints import (
    vtkGaussianKernel,
    vtkPointInterpolator
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkPointGaussianMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)
from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor

import numpy as np
from helpers import *
from filters import *
from animation import *
from conf import *



def get_program_parameters():
    import argparse
    description = 'Visualize a cosmology simulation polydata (vtp) file.'
    epilogue = ''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='path to Full.cosmo.xxx.vtp')
    args = parser.parse_args()
    return args.filename


def visualize_pts(polydata, array_name, filename):
    # Visualize as point gaussians, with a string array_name specifying the array to use for color
    colors = vtkNamedColors()

    # Set up color map
    lut = vtkLookupTable()
    # This creates a black to white lut.
    # lut.SetHueRange(0, 0)
    # lut.SetSaturationRange(0, 0)
    # lut.SetValueRange(0.2, 1.0)

    # This creates a blue to red lut.
    lut.SetHueRange(0.667, 0.0)

    # lut.SetNumberOfColors(256)
    # lut.Build()

    polydata.GetPointData().SetActiveScalars(array_name)
    range = polydata.GetPointData().GetScalars().GetRange()

    point_mapper = vtkPointGaussianMapper()
    point_mapper.SetInputData(polydata)
    point_mapper.SetScalarRange(range)
    point_mapper.SetLookupTable(lut)
    point_mapper.SetScaleFactor(0.2)  # radius
    point_mapper.EmissiveOff()
    point_mapper.SetSplatShaderCode(  # copied from https://kitware.github.io/vtk-examples/site/Python/Meshes/PointInterpolator/
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
    point_actor.GetProperty().SetOpacity(0.1)

    # Create a scan plane to show the interpolated cell data
    plane_source = vtkPlaneSource()
    plane_source.SetOrigin(0, 0, COORD_MAX / 2)  # TODO: move the "scan" plane with GUI
    plane_source.SetPoint1(COORD_MAX, 0, COORD_MAX / 2)
    plane_source.SetPoint2(0, COORD_MAX, COORD_MAX / 2)
    plane_source.SetResolution(CELL_RES, CELL_RES)
    plane_source.Update()

    plane: vtkPolyData = plane_source.GetOutput()

    # Interpolate from the point data to the cell data on the plane
    gaussian_kernel = vtkGaussianKernel()
    gaussian_kernel.SetSharpness(10)  # TODO: make it a GUI slider
    gaussian_kernel.SetRadius(3)

    interpolator = vtkPointInterpolator()
    interpolator.SetInputData(plane)
    interpolator.SetSourceData(polydata)
    interpolator.SetKernel(gaussian_kernel)
    interpolator.Update()

    # Debug print of interpolated data
    # data: vtkPolyData = interpolator.GetOutput()
    # print('Interpolated data:')
    # print('Number of points:', data.GetNumberOfPoints())
    # print('Number of cells:', data.GetNumberOfCells())
    # print('Number of point data arrays:', data.GetPointData().GetNumberOfArrays())
    # print('Number of cell data arrays:', data.GetCellData().GetNumberOfArrays())
    # arr = np.array(data.GetPointData().GetScalars())
    # print(arr, arr.shape, arr.mean())

    plane_mapper = vtkPolyDataMapper()
    plane_mapper.SetInputConnection(interpolator.GetOutputPort())
    plane_mapper.SetScalarRange(range)
    plane_mapper.SetLookupTable(lut)

    plane_actor = vtkActor()
    plane_actor.SetMapper(plane_mapper)
    # plane_actor.GetProperty().SetRepresentationToWireframe()
    # plane_actor.GetProperty().SetColor(colors.GetColor3d('Banana'))

    # Render a color map legend at the right side of the window
    legend = vtkScalarBarActor()
    legend.SetLookupTable(lut)
    legend.SetNumberOfLabels(8)
    legend.SetTitle(array_name)
    legend.SetVerticalTitleSeparation(6)
    legend.GetPositionCoordinate().SetValue(0.92, 0.1)
    legend.SetWidth(0.06)

    # TODO: add xyz axes

    renderer = vtkRenderer()
    renderWindow = vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindowInteractor = vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    renderer.AddActor(point_actor)
    renderer.AddActor(plane_actor)
    renderer.AddActor(legend)
    renderer.SetBackground(colors.GetColor3d('DimGray'))
    renderer.GetActiveCamera().Yaw(-20)
    renderer.GetActiveCamera().SetViewUp(0, 1, 0)
    renderer.ResetCamera()

    renderWindow.SetSize(2048, 2048)
    renderWindow.Render()
    renderWindow.SetWindowName(f'{array_name} of {filename}')
    renderWindowInteractor.Start()


def main():
    filename = get_program_parameters()

    # Read all the data from the file
    reader = vtkXMLPolyDataReader()
    reader.SetFileName(filename)
    reader.Update()

    polydata = reader.GetOutput()
    print_meta_data(polydata)

    # The code below shows how to dump first 100 points into another vtp file (for cheaper visualization)
    # sliced = slice_polydata(polydata, 100)
    # print_meta_data(sliced)
    # writer = vtkXMLPolyDataWriter()
    # writer.SetFileName('points.100.vtp')
    # writer.SetInputData(sliced)
    # writer.Write()

    # The code below shows how to get the points and mass arrays as numpy arrays
    # pts = get_numpy_pts(polydata)
    # mass = get_numpy_array(polydata, 'mass')
    # print('Points: ', pts)
    # print('Mass: ', mass)

    # Switch to different array_name to visualize different properties
    # visualize_pts(polydata, 'mass', filename)
    visualize_pts(polydata, 'phi', filename)


if __name__ == '__main__':
    main()
    