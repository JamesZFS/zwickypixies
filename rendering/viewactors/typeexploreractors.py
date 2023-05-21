import vtk
import rendering.core as core


def get_type_explorer_actors(polydata: vtk.vtkPolyData, color: vtk.vtkColor3d = None, opacity: float = None,
                             radius: float = None, show=None):
    mapper = vtk.vtkPointGaussianMapper()
    mapper.SetInputData(polydata)
    mapper.ScalarVisibilityOff()
    mapper.EmissiveOff()
    mapper.SetScaleArray('radius')  # assign heterogenous radius to each point
    if radius is not None:
        core.update_radius(polydata, min_value=0.5 * radius, max_value=1.5 * radius)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    if color is not None: actor.GetProperty().SetColor(color)
    if opacity is not None: actor.GetProperty().SetOpacity(opacity)
    return actor


def create_type_explorer_actors(actorhandler):
    split_polydata = core.split_particles(actorhandler.polydata)
    actorhandler.actors = {name: get_type_explorer_actors(data) for name, data in split_polydata.items()}
    for name, actor in actorhandler.actors.items():
        core.update_view_property(actor, *actorhandler.property_map[name])
    for name, (color, opacity, radius, show) in actorhandler.property_map.items():
        if show:
            actorhandler.parent.ren.AddActor(actorhandler.actors[name])
