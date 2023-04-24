from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
from animation import *
import vtkmodules.vtkInteractionStyle
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkPointGaussianMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)
from dataops.filters import mask_points
import config

def getPolyData(filename: str = None):
    if filename:
        config.File = filename
    reader = vtkXMLPolyDataReader()
    reader.SetFileName(config.File)
    reader.Update()
    polydata = reader.GetOutput()
    return polydata

def getMapper(polydata, array_name: str, filter: str = None):
    if filter:
        config.Filter = filter
    polydata = mask_points(polydata, config.ArrayName, config.Filter)
    polydata.GetPointData().SetActiveScalars(array_name)
    range = polydata.GetPointData().GetScalars().GetRange()
    config.RangeMin = range[0]
    config.RangeMax = range[1]
    mapper = vtkPointGaussianMapper()
    mapper.SetInputData(polydata)
    mapper.SetScalarRange(range)
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
    mapper.SetLookupTable(config.Lut)
    
    return mapper

def getActor(array_name: str, filename: str = None, filter: str = None):
    if array_name in config.ArrayNameList:
        config.ArrayName = array_name
    if filename:
        config.File = filename
    actor = vtkActor()
    actor.SetMapper(getMapper(getPolyData(config.File), config.ArrayName, filter))
    actor.GetProperty().SetOpacity(0.2)
    return actor

