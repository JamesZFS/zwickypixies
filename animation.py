# TODO: Cyrill, please implement the functions in this file if you are interested

import vtkmodules.vtkInteractionStyle
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
import re
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkPointGaussianMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)

from helpers import print_meta_data, slice_polydata, get_numpy_pts

name = []
last = None

class vtkTimerCallback():
    # INSPIRED FROM https://kitware.github.io/vtk-examples/site/Python/Utilities/Animation/
    def __init__(self, steps, actor, iren, mapper):
        self.timer_count = 0
        self.steps = steps
        self.actor = actor
        self.mapper = mapper
        self.iren = iren
        self.timerId = None

    def execute(self, obj, event):
        step = 0
        while step < self.steps:
            fileName = name[0] + "{0:03d}".format((1 + step) * 2) + name[1]
            print(fileName)
            reader = vtkXMLPolyDataReader()
            reader.SetFileName(fileName)
            reader.Update()
            polydata = reader.GetOutput()
            polydata = slice_polydata(polydata, 10)
            #print(get_numpy_pts(polydata))
            global last
            print ( get_numpy_pts(polydata) - last)
            last = get_numpy_pts(polydata)
            self.mapper.SetInputData(polydata)

            polydata.GetPointData().SetActiveScalars("mass")
            rang = polydata.GetPointData().GetScalars().GetRange()

            self.mapper.SetScalarRange(rang)
            self.mapper.SetScaleFactor(0.2)  # radius
            self.mapper.EmissiveOff()
            self.mapper.SetSplatShaderCode(
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

            iren = obj
            iren.GetRenderWindow().Render()
            self.timer_count += 1
            step += 1
        if self.timerId:
            iren.DestroyTimer(self.timerId)


def trace_particle(data_dir: str, particle_ids: list):
    '''
    Trace the particles specified by the particle_ids list and render them as a set of animated spheres

    data_dir: directory of the cosmo data
    particle_ids: list of particle ids to trace
    '''
    # I'm not sure how to do this yet, but I think vtk has some animation support
    # https://kitware.github.io/vtk-examples/site/Python/Utilities/Animation/
    reader = vtkXMLPolyDataReader()
    colors = vtkNamedColors()

    # split path arround file number
    name_parts = re.split(r'\d\d\d', data_dir)
    name.append(name_parts[0])
    name.append(name_parts[1])

    fileName = name[0] + "000" + name[1]
    # print(fileName)
    reader.SetFileName(fileName)
    reader.Update()


    polydata = reader.GetOutput()
    polydata = slice_polydata(polydata, 10)
    global last
    last = get_numpy_pts(polydata)
    polydata.GetPointData().SetActiveScalars("mass")
    rang = polydata.GetPointData().GetScalars().GetRange()

    mapper = vtkPointGaussianMapper()
    mapper.SetInputData(polydata)
    mapper.SetScalarRange(rang)
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

    actor = vtkActor()
    actor.SetMapper(mapper)

    renderer = vtkRenderer()
    renderWindow = vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindowInteractor = vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    renderer.SetBackground(colors.GetColor3d('DimGray'))
    renderer.GetActiveCamera().Pitch(90)
    renderer.GetActiveCamera().SetViewUp(0, 0, 1)
    renderer.GetActiveCamera().SetPosition(-10, 0, 0)
    renderer.ResetCamera()

    renderWindow.SetWindowName("Animation")

    # Add the actor to the scene
    renderer.AddActor(actor)

    # Initialize must be called prior to creating timer events.
    renderWindowInteractor.Initialize()

    # Sign up to receive TimerEvent
    cb = vtkTimerCallback(311, actor, renderWindowInteractor, mapper)
    renderWindowInteractor.AddObserver('TimerEvent', cb.execute)
    cb.timerId = renderWindowInteractor.CreateRepeatingTimer(500)

    # start the interaction and timer
    renderWindow.Render()
    renderWindow.SetSize(900, 900)
    renderWindowInteractor.Start()



