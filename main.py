from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader, vtkXMLPolyDataWriter
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
from helpers import *
from filters import *
from animation import *



def get_program_parameters():
    import argparse
    description = 'Visualize a cosmology simulation polydata (vtp) file.'
    epilogue = ''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='path to Full.cosmo.xxx.vtp')
    args = parser.parse_args()
    return args.filename


def visualize_pts(polydata, array_name):
    # Visualize as point gaussians, with a string array_name specifying the array to use for color
    colors = vtkNamedColors()

    polydata.GetPointData().SetActiveScalars(array_name)
    range = polydata.GetPointData().GetScalars().GetRange()

    point_mapper = vtkPointGaussianMapper()
    point_mapper.SetInputData(polydata)
    point_mapper.SetScalarRange(range)
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
    visualize_pts(polydata, 'mass')
    # visualize_pts(polydata, 'uu')


if __name__ == '__main__':
    main()
    