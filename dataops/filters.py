from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkCommonCore import vtkPoints, vtkIntArray, vtkDoubleArray

def mask_points(polydata: vtkPolyData, array_name: str, particle_type: str):
    '''
    Mask points in the polydata based on the particle type

    polydata: input polydata (point data)
    array_name: name of the array to mask based on
    particle_type: particle type, e.g. 'dm' (for dark matter), 'baryon', 'star', 'wind', 'gas', 'agn'
    '''

    mask_array = polydata.GetPointData().GetArray('mask')
    data_array = polydata.GetPointData().GetArray(array_name)
    masked_polydata = vtkPolyData()
    masked_points = vtkPoints()
    masked_scalars = vtkDoubleArray()
    masked_scalars.SetName(array_name)

    for i in range(polydata.GetNumberOfPoints()):
        mask = int(mask_array.GetValue(i))
        data = data_array.GetValue(i)
        is_dm =     ((mask & 0b000000010) == 0)
        is_baryon = not is_dm
        is_star =   ((mask & 0b000100000) != 0) and is_baryon
        is_wind =   ((mask & 0b001000000) != 0) and is_baryon
        is_gas =    ((mask & 0b010000000) != 0) and is_baryon
        is_agn =    ((mask & 0b100000000) != 0) and is_dm

        if particle_type == 'dm' and is_dm:
            masked_points.InsertNextPoint(polydata.GetPoint(i))
            masked_scalars.InsertNextValue(data)
        elif particle_type == 'baryon' and is_baryon:
            masked_points.InsertNextPoint(polydata.GetPoint(i))
            masked_scalars.InsertNextValue(data)
        elif particle_type == 'star' and is_star:
            masked_points.InsertNextPoint(polydata.GetPoint(i))
            masked_scalars.InsertNextValue(data)
        elif particle_type == 'wind' and is_wind:
            masked_points.InsertNextPoint(polydata.GetPoint(i))
            masked_scalars.InsertNextValue(data)
        elif particle_type == 'gas' and is_gas:
            masked_points.InsertNextPoint(polydata.GetPoint(i))
            masked_scalars.InsertNextValue(data)
        elif particle_type == 'agn' and is_agn:
            masked_points.InsertNextPoint(polydata.GetPoint(i))
            masked_scalars.InsertNextValue(data)

    masked_polydata.SetPoints(masked_points)
    masked_polydata.GetPointData().SetScalars(masked_scalars)
    return masked_polydata


def threshold_points(polydata: vtkPolyData, array_name: str, threshold_min: float, threshold_max: float):
    '''
    Threshold points in the polydata based on the array_name

    polydata: input polydata (point data)
    array_name: name of the array to threshold
    threshold_min: minimum value of the threshold
    threshold_max: maximum value of the threshold
    '''

    data_array = polydata.GetPointData().GetArray(array_name)
    filtered_polydata = vtkPolyData()
    filtered_points = vtkPoints()
    filtered_scalars = vtkDoubleArray()
    filtered_scalars.SetName(array_name)

    # Iterate over the points and add the points that are between the specified thresholds
    for i in range(polydata.GetNumberOfPoints()):
        data = data_array.GetValue(i)
        if threshold_min <= data <= threshold_max:
            filtered_points.InsertNextPoint(polydata.GetPoint(i))
            filtered_scalars.InsertNextValue(data)

    # Set the masked points and filtered scalars as the new point data for the filtered polydata
    filtered_polydata.SetPoints(filtered_points)
    filtered_polydata.GetPointData().SetScalars(filtered_scalars)

    return filtered_polydata

    