from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
import re
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPointGaussianMapper
)
from tqdm import tqdm
from os.path import isdir
from helpers import *

"""
    To use:
    1. create Animation
    2. load data
    (2.1 set Attribute)
    3. initialize animation
    4. bind to renderwindowinteractor
    5. start animation
    
    e.g:
    anim = Animation("data/Cosmolog/Full.cosmo.000.vtk")
    anim.loadData()
    anim.setAtribute("mass")
    anim.initAnimation()
    anim.addToRenderer(renderWindowInteractor, 500)
    anim.startAnimation()
    
    
    animation can be paused with anim.stopAnimation()
    and continued with anim.startAnimation()
"""


class vtkTimerCallback():
    # INSPIRED FROM https://kitware.github.io/vtk-examples/site/Python/Utilities/Animation/
    def __init__(self, animation, iren):
        self.animation = animation
        self.iren = iren
        self.timerId = None

    def execute(self, obj, event):
        if self.animation.rendering:
            stepped = self.animation.nextTimeStep()
            self.iren.GetRenderWindow().Render()
            #if not stepped:
            #    self.iren.DestroyTimer(self.timerId)

class Animation:
    def __init__(self, dirname: str, stepStart: int, stepEnd: int, numParticles=100, cycle=True):
        self.rendering = True
        self.dirname = dirname # path to directory containing the vtp files
        assert isdir(dirname), "dirname must be a directory"
        self.dataLoaded = False
        self.currentTime = 0
        self.attribute = "mass"
        self.actor = vtkActor()
        self.mapper = vtkPointGaussianMapper()
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
        self.actor.SetMapper(self.mapper)
        self.polydata = []
        self.stepRange = range(max(0, stepStart), min(312, stepEnd))
        self.cycle = cycle
        self.numParticles = numParticles

    def loadData(self):
        reader = vtkXMLPolyDataReader()
        for step in tqdm(self.stepRange, desc='Loading Data'):
            path = f'{self.dirname}/Full.cosmo.{step * 2:03d}.vtp'
            reader = vtkXMLPolyDataReader()
            reader.SetFileName(path)
            reader.Update()
            polydata = reader.GetOutput()
            polydata = slice_polydata(polydata, self.numParticles)
            self.polydata.append(polydata)

        self.dataLoaded = True
        self.currentTime = 0

    def setAtribute(self, attr="mass"):
        self.attribute = attr

    def getActor(self):
        return self.actor

    def initAnimation(self, startTime=0):
        if startTime >= self.stepRange.stop:
            raise Exception("To late time step")

        self.currentTime = startTime
        self._loadTime()

    def nextTimeStep(self):
        self.currentTime += 1
        if self.currentTime >= self.stepRange.stop:
            if self.cycle:
                self.currentTime = self.stepRange.start
                return True
            else:
                return False
        self._loadTime()
        return True

    def _loadTime(self):
        assert self.dataLoaded
        self.polydata[self.currentTime].GetPointData().SetActiveScalars(self.attribute)
        self.mapper.SetScalarRange(self.polydata[self.currentTime].GetPointData().GetScalars().GetRange())
        self.mapper.SetInputData(self.polydata[self.currentTime])
        self.mapper.Update()

    def addToRenderer(self, renderWindowInteractor, time=500):
        cb = vtkTimerCallback(self, renderWindowInteractor)
        renderWindowInteractor.AddObserver('TimerEvent', cb.execute)
        cb.timerId = renderWindowInteractor.CreateRepeatingTimer(time)

    def stopAnimation(self):
        self.rendering = False

    def startAnimation(self):
        self.rendering = True


def main():
    # noinspection PyUnresolvedReferences
    import vtkmodules.vtkInteractionStyle
    # noinspection PyUnresolvedReferences
    import vtkmodules.vtkRenderingOpenGL2
    from vtkmodules.vtkCommonColor import vtkNamedColors
    from vtkmodules.vtkRenderingCore import (
        vtkRenderWindow,
        vtkRenderWindowInteractor,
        vtkRenderer
    )

    colors = vtkNamedColors()

    # Setup a renderer, render window, and interactor
    renderer = vtkRenderer()
    renderer.SetBackground(colors.GetColor3d("MistyRose"))
    renderWindow = vtkRenderWindow()
    renderWindow.SetWindowName("Animation")
    renderWindow.AddRenderer(renderer)
    renderWindow.SetSize(512, 512)

    renderWindowInteractor = vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    # Initialize must be called prior to creating timer events.
    renderWindowInteractor.Initialize()

    # Add the actor to the scene
    anim = Animation("data", 0, 50)
    renderer.AddActor(anim.getActor())
    anim.loadData()
    anim.setAtribute("mass")
    anim.initAnimation()
    # Add the actor to the scene
    anim.addToRenderer(renderWindowInteractor, 50)
    anim.startAnimation()

    # start the interaction and timer
    renderWindow.Render()
    renderWindowInteractor.Start()


if __name__ == '__main__':
    main()
