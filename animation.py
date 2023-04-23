from vtkmodules.vtkCommonColor import vtkNamedColors

from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
import re
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPointGaussianMapper
)

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
    def __init__(self, filename: str):
        self.rendering = True
        self.filename = filename
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
        self.timeSteps = 312



    def loadData(self):
        reader = vtkXMLPolyDataReader()
        colors = vtkNamedColors()

        # split path arround file number
        name_parts = re.split(r'\d\d\d', self.filename)
        name = [name_parts[0], name_parts[1]]

        print("Start Loading")
        percentage = 10
        for step in range(self.timeSteps):
            path = name[0] + "{0:03d}".format((1 + step) * 2) + name[1]
            reader = vtkXMLPolyDataReader()
            reader.SetFileName(path)
            reader.Update()
            polydata = reader.GetOutput()
            # polydata.GetPointData().SetActiveScalars("mass")
            # polydata = slice_polydata(polydata, 20)
            self.polydata.append(polydata)
            if step / (self.timeSteps - 1) * 100 >= percentage:
                print("Loading " + str(percentage) + "% complete")
                percentage += 10
        self.dataLoaded = True
        self.currentTime = 0
        print("Finished Loading")

    def setAtribute(self, attr="mass"):
        self.attribute = attr

    def getActor(self):
        return self.actor

    def initAnimation(self, startTime=0):
        if startTime >= self.timeSteps:
            Exception("To late time step")

        self.currentTime = startTime
        self._loadTime()

    def nextTimeStep(self):
        if self.currentTime + 1 >= self.timeSteps:
            return False
        self.currentTime += 1
        self._loadTime()
        return True

    def _loadTime(self):
        if not self.dataLoaded:
            Exception("Data Not loaded")
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
