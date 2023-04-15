from vtkmodules.vtkInteractionWidgets import vtkSliderWidget, vtkSliderRepresentation2D, vtkButtonRepresentation, \
    vtkButtonWidget, vtkTexturedButtonRepresentation2D
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkPointGaussianMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)
from vtkmodules.vtkCommonColor import vtkNamedColors
import vtkmodules.vtkCommonCore as vtkCommonCore
import vtkmodules.vtkRenderingCore as vtkRenderingCore
from vtk import vtkTextActor
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class Window:
    def __init__(self, actor: vtkActor):
        self.renderer = vtkRenderer()
        self.renderWindow = vtkRenderWindow()
        self.renderWindow.AddRenderer(self.renderer)
        self.renderWindowInteractor = vtkRenderWindowInteractor()
        self.renderWindowInteractor.SetRenderWindow(self.renderWindow)

        self.renderer.AddActor(actor)
        self.renderer.SetBackground(vtkNamedColors().GetColor3d('DimGray'))
        self.renderer.GetActiveCamera().Pitch(90)
        self.renderer.GetActiveCamera().SetViewUp(0, 0, 1)
        self.renderer.ResetCamera()

        self.renderWindow.SetSize(1536, 1024)
        self.renderWindow.Render()
        self.renderWindow.SetWindowName('Cosmology Data')

    def start(self):
        self.renderWindowInteractor.Start()
