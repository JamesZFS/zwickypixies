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

from helpers import print_meta_data, slice_polydata




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
    name = re.split(r'\d\d\d', data_dir)
    # iterate over all files

    final = vtkPolyData()
    for num in range(0, 625, 2):
        if num > 10: break;
        fileName = name[0] + "{0:03d}".format(num) + name[1]
        print(fileName)


