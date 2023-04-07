# TODO: Cyrill, please implement the functions in this file if you are interested

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


def trace_particle(data_dir: str, particle_ids: list):
    '''
    Trace the particles specified by the particle_ids list and render them as a set of animated spheres

    data_dir: directory of the cosmo data
    particle_ids: list of particle ids to trace
    '''
    # I'm not sure how to do this yet, but I think vtk has some animation support
    # https://kitware.github.io/vtk-examples/site/Python/Utilities/Animation/
    raise NotImplementedError
