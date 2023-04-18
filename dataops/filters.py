from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkCommonCore import vtkPoints, vtkDoubleArray

import config


def mask_points(polydata: vtkPolyData, array_name: str, particle_type: str = None):
    '''
    Mask points in the polydata based on the particle type

    polydata: input polydata (point data)
    array_name: name of the array to mask based on
    particle_type: particle type, e.g. 'dm' (for dark matter), 'baryon', 'star', 'wind', 'gas', 'agn'
    '''

    if not particle_type or particle_type == 'None':
        return polydata

    mask_array = polydata.GetPointData().GetArray('mask')
    data_array = polydata.GetPointData().GetArray(array_name)
    masked_polydata = vtkPolyData()
    masked_points = vtkPoints()
    masked_scalars = vtkDoubleArray()
    masked_scalars.SetName(array_name)

    for i in range(polydata.GetNumberOfPoints()):
        mask = int(mask_array.GetValue(i))
        is_dm =     ((mask & 0b000000010) == 0)
        is_baryon = not is_dm
        is_star =   ((mask & 0b000100000) != 0) and is_baryon
        is_wind =   ((mask & 0b001000000) != 0) and is_baryon
        is_gas =    ((mask & 0b010000000) != 0) and is_baryon
        is_agn =    ((mask & 0b100000000) != 0) and is_dm

        if particle_type == 'dm' and is_dm:
            masked_points.InsertNextPoint(polydata.GetPoint(i))
            masked_scalars.InsertNextValue(data_array.GetValue(i))
        elif particle_type == 'baryon' and is_baryon:
            masked_points.InsertNextPoint(polydata.GetPoint(i))
            masked_scalars.InsertNextValue(data_array.GetValue(i))
        elif particle_type == 'star' and is_star:
            masked_points.InsertNextPoint(polydata.GetPoint(i))
            masked_scalars.InsertNextValue(data_array.GetValue(i))
        elif particle_type == 'wind' and is_wind:
            masked_points.InsertNextPoint(polydata.GetPoint(i))
            masked_scalars.InsertNextValue(data_array.GetValue(i))
        elif particle_type == 'gas' and is_gas:
            masked_points.InsertNextPoint(polydata.GetPoint(i))
            masked_scalars.InsertNextValue(data_array.GetValue(i))
        elif particle_type == 'agn' and is_agn:
            masked_points.InsertNextPoint(polydata.GetPoint(i))
            masked_scalars.InsertNextValue(data_array.GetValue(i))

    masked_polydata.SetPoints(masked_points)
    masked_polydata.GetPointData().SetScalars(masked_scalars)
    return masked_polydata


def threshold_points(polydata: vtkPolyData, array_name: str, threshold_min: float = None, threshold_max: float = None):
    '''
    Threshold points in the polydata based on the array_name

    polydata: input polydata (point data)
    array_name: name of the array to threshold
    threshold_min: minimum value of the threshold
    threshold_max: maximum value of the threshold
    '''

    if threshold_min and threshold_max:
        config.ThresholdMin = threshold_min
        config.ThresholdMax = threshold_max
    data_array = polydata.GetPointData().GetArray(array_name)
    filtered_polydata = vtkPolyData()
    filtered_points = vtkPoints()
    filtered_scalars = vtkDoubleArray()
    filtered_scalars.SetName(array_name)

    for i in range(polydata.GetNumberOfPoints()):
        data = data_array.GetValue(i)
        if config.ThresholdMin <= data <= config.ThresholdMax:
            filtered_points.InsertNextPoint(polydata.GetPoint(i))
            filtered_scalars.InsertNextValue(data)

    filtered_polydata.SetPoints(filtered_points)
    filtered_polydata.GetPointData().SetScalars(filtered_scalars)

    return filtered_polydata

    