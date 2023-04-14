from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkCommonCore import vtkPoints

def mask_points(polydata: vtkPolyData, particle_type: str):
    '''
    Mask points in the polydata based on the particle type

    polydata: input polydata (point data)
    particle_type: particle type, e.g. 'dm' (for dark matter), 'baryon', 'star', 'wind', 'gas', 'agn'
    '''

    mask_array = polydata.GetPointData().GetArray('mask')
    masked_polydata = vtkPolyData()
    masked_points = vtkPoints()

    # Iterate over the points and add the points that match the particle type to the masked points
    for i in range(polydata.GetNumberOfPoints()):
        mask = int(mask_array.GetValue(i))
        if mask > 3:
            print(bin(mask))
        # Check the bitmask to determine the particle type
        is_dm = ((mask & 0b00000010) == 0)
        is_baryon = not is_dm
        is_star = ((mask & 0b00100000) != 0) and is_baryon
        is_wind = ((mask & 0b01000000) != 0) and is_baryon
        is_gas = ((mask & 0b10000000) != 0) and is_baryon
        is_agn = ((mask & 0b00000100) != 0) and is_dm

        if particle_type == 'dm' and is_dm:
            masked_points.InsertNextPoint(polydata.GetPoint(i))
        elif particle_type == 'baryon' and is_baryon:
            masked_points.InsertNextPoint(polydata.GetPoint(i))
        elif particle_type == 'star' and is_star:
            masked_points.InsertNextPoint(polydata.GetPoint(i))
        elif particle_type == 'wind' and is_wind:
            masked_points.InsertNextPoint(polydata.GetPoint(i))
        elif particle_type == 'gas' and is_gas:
            masked_points.InsertNextPoint(polydata.GetPoint(i))
        elif particle_type == 'agn' and is_agn:
            masked_points.InsertNextPoint(polydata.GetPoint(i))

    # Set the masked points as the new points for the masked polydata
    masked_polydata.SetPoints(masked_points)

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

    # Iterate over the points and add the points that are between the specified thresholds
    for i in range(polydata.GetNumberOfPoints()):
        data = data_array.GetValue(i)
        print(data)
        if threshold_min <= data <= threshold_max:
            filtered_points.InsertNextPoint(polydata.GetPoint(i))

    # Set the masked points as the new points for the filtered polydata
    filtered_polydata.SetPoints(filtered_points)

    return filtered_polydata

    