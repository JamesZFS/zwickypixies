from typing import List
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkCommonCore import vtkPoints, vtkDoubleArray
from vtkmodules.util.numpy_support import vtk_to_numpy, numpy_to_vtk
from vtkmodules.vtkFiltersCore import vtkThreshold
from vtk import VTK_DOUBLE
import vtk
import numpy as np
import config

def mask_points(polydata: vtkPolyData, array_name: str = None, particle_type: str = None):
    '''
    Mask points in the polydata based on the particle type

    polydata: input polydata (point data)
    array_name: name of the array to mask based on
    particle_type: particle type, e.g. 'dm' (for dark matter), 'baryon', 'star', 'wind', 'gas', 'agn'
    '''

    if not particle_type or particle_type == 'None':
        return polydata

    mask_array = vtk_to_numpy(polydata.GetPointData().GetArray('mask')).astype(np.int32)
    data_array = None
    if array_name:
        data_array = vtk_to_numpy(polydata.GetPointData().GetArray(array_name))
    points_array = vtk_to_numpy(polydata.GetPoints().GetData())

    is_dm = ((mask_array & 0b000000010) == 0) & ~((mask_array & 0b100000000) != 0)
    is_star = ((mask_array & 0b000100000) != 0) & ~is_dm
    is_wind = ((mask_array & 0b001000000) != 0) & ~is_dm
    is_gas = ((mask_array & 0b010000000) != 0) & ~is_dm
    is_agn = ((mask_array & 0b100000000) != 0) & ~is_star & ~is_wind & ~is_gas
    is_baryon = ~is_dm & ~is_star & ~is_wind & ~is_gas & ~is_agn

    particle_mask = None
    if particle_type == 'dm':
        particle_mask = is_dm
    elif particle_type == 'baryon':
        particle_mask = is_baryon
    elif particle_type == 'star':
        particle_mask = is_star
    elif particle_type == 'wind':
        particle_mask = is_wind
    elif particle_type == 'gas':
        particle_mask = is_gas
    elif particle_type == 'agn':
        particle_mask = is_agn

    if particle_mask is not None:
        masked_points = points_array[particle_mask]

        vtk_masked_points = vtkPoints()
        masked_polydata = vtkPolyData()

        vtk_masked_points.SetData(numpy_to_vtk(masked_points))
        masked_polydata.SetPoints(vtk_masked_points)
        if array_name:
            masked_scalars = data_array[particle_mask]
            masked_polydata.GetPointData().SetScalars(numpy_to_vtk(masked_scalars, deep=True, array_type=VTK_DOUBLE))
        return masked_polydata
    else:
        return polydata


def threshold_points(polydata: vtkPolyData, array_name: str, threshold_min: float = None, threshold_max: float = None):
    '''
    Threshold points in the polydata based on the array_name

    polydata: input polydata (point data)
    array_name: name of the array to threshold
    threshold_min: minimum value of the threshold
    threshold_max: maximum value of the threshold
    '''
    print(threshold_min)
    print(threshold_max)
    if threshold_min and threshold_max:
        config.ThresholdMin = threshold_min
        config.ThresholdMax = threshold_max

    threshold_filter = vtkThreshold()
    threshold_filter.SetInputData(polydata)
    #threshold_filter.SetInputArrayToProcess(0, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS, array_name)
    threshold_filter.ThresholdBetween(config.ThresholdMin, config.ThresholdMax)

    return threshold_filter.GetOutputPort(config.THRESHOLD_PORT)

