from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
from animation import *
import config

def getPolyData(filename):
    reader = vtkXMLPolyDataReader()
    reader.SetFileName(filename)
    reader.Update()
    config.currentFile = filename
    polydata = reader.GetOutput()
    return polydata

def getMapper(polydata, array_name):
    polydata.GetPointData().SetActiveScalars(array_name)
    range = polydata.GetPointData().GetScalars().GetRange()
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
    return mapper

def getActor(filename, array_name):
    if not array_name in ['vx', 'vy', 'vz', 'mass', 'uu', 'hh', 'mu', 'rho', 'phi', 'id', 'mask']:
        return vtkActor()
    actor = vtkActor()
    actor.SetMapper(getMapper(getPolyData(filename), array_name))
    return actor



