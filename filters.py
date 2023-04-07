# TODO: Leo, please implement the functions in this file

from vtkmodules.vtkCommonDataModel import vtkPolyData


def mask_points(polydata: vtkPolyData, particle_type: str):
    '''
    Mask points in the polydata based on the particle type
    
    polydata: input polydata (point data)
    particle_type: particle type, e.g. 'dm' (for dark matter), 'baryon', 'star', 'wind', 'gas', 'agn'
    '''
    mask_array = polydata.GetPointData().GetArray('mask')
    
    masked_polydata = vtkPolyData()
    
    # TODO: make a new polydata with the points that have the specified particle type
    # Maybe we can also find a vtk filter api to do this in a pipeline fashion and return the output port
    # e.g. https://vtk.org/doc/nightly/html/classvtkMaskPoints.html  (copilot suggested this for me, mind blown)
    raise NotImplementedError

    return masked_polydata  # or output port


def threshold_points(polydata: vtkPolyData, array_name: str, threshold_min: float, threshold_max: float):
    '''
    Threshold points in the polydata based on the array_name
    
    polydata: input polydata (point data)
    array_name: name of the array to threshold
    threshold_min: minimum value of the threshold
    threshold_max: maximum value of the threshold
    '''
    array = polydata.GetPointData().GetArray(array_name)

    filtered_polydata = vtkPolyData()
    
    # TODO: make a new polydata with the points that have the specified array value within the threshold range
    # Maybe we can also find a vtk filter api to do this in a pipeline fashion and return the output port
    # e.g. https://vtk.org/doc/nightly/html/classvtkThresholdPoints.html
    raise NotImplementedError

    return filtered_polydata  # or output port

    