import vtk
import config
import numpy as np
from vtkmodules.util.numpy_support import vtk_to_numpy, numpy_to_vtk


# Create a glyph filter that aligns arrows with vectors
def get_glyphs(input_port: int, scale_factor=1.0):
    # Source for the glyph filter
    arrow = vtk.vtkArrowSource()
    arrow.SetTipResolution(3)
    arrow.SetTipLength(0.3)
    arrow.SetTipRadius(0.2)
    arrow.SetShaftResolution(3)
    arrow.SetShaftRadius(0.05)

    glyph = vtk.vtkGlyph3D()
    glyph.SetSourceConnection(arrow.GetOutputPort())
    glyph.SetInputConnection(input_port)
    glyph.SetScaleFactor(scale_factor)
    glyph.SetVectorModeToUseVector()     # orient by vector direction
    glyph.SetScaleModeToScaleByVector()  # scale by vector magnitude
    glyph.OrientOn()
    glyph.ScalingOn()
    glyph.Update()
    return glyph


def set_vectors_by_velocity(src: vtk.vtkPointData, min_scale=1.0, max_scale=2.0):
    # Get the velocity vector
    vx = vtk_to_numpy(src.GetArray('vx'))
    vy = vtk_to_numpy(src.GetArray('vy'))
    vz = vtk_to_numpy(src.GetArray('vz'))
    velocities = np.stack((vx, vy, vz), axis=-1)
    magnitudes = np.linalg.norm(velocities, axis=-1)
    velocities /= magnitudes[:, None]  # normalize
    max_magnitude = np.max(magnitudes)
    min_magnitude = np.min(magnitudes)
    # map the velocity magnitude to the given range
    velocities *= (magnitudes[:, None] - min_magnitude) / (max_magnitude - min_magnitude) * (max_scale - min_scale) + min_scale

    # Set the velocity vector as the active vector
    velocity_vtk = numpy_to_vtk(velocities)
    velocity_vtk.SetName('velocity')
    src.AddArray(velocity_vtk)
    src.SetActiveVectors('velocity')


# This class encapsulates the glyph filter to visualize the velocity field
class Glyph:
    def __init__(self, polydata: vtk.vtkPolyData):
        self.polydata = polydata
        set_vectors_by_velocity(polydata.GetPointData())

        # Choose a random subset of points
        self.ratio = 0.05  # ratio of points to keep
        self.mask_points = vtk.vtkMaskPoints()
        self.mask_points.SetInputData(polydata)
        self.mask_points.SetOnRatio(int(1 / self.ratio))
        # self.mask_points.RandomModeOn()

        # Create a glyph filter, mapper, and actor
        self.glyph = get_glyphs(self.mask_points.GetOutputPort(), scale_factor=1.0)

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(self.glyph.GetOutputPort())
        self.mapper.SetScalarModeToUsePointFieldData()
        self.mapper.SelectColorArray(config.ArrayName)
        self.mapper.ScalarVisibilityOff()
        self.mapper.UseLookupTableScalarRangeOn()
        self.mapper.SetLookupTable(config.Lut)

        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self.mapper)
        self.actor.GetProperty().SetOpacity(0.5)

    def get_actor(self):
        return self.actor
        
    def set_opacity(self, opacity: float):
        self.actor.GetProperty().SetOpacity(opacity)

    def set_color_mode(self, use_scalar_coloring: bool):
        if use_scalar_coloring:
            self.mapper.ScalarVisibilityOn()
        else:
            self.mapper.ScalarVisibilityOff()
        self.mapper.Update()
    
    def set_velocity_bounds(self, min_scale, max_scale):
        set_vectors_by_velocity(self.polydata.GetPointData(), min_scale, max_scale)
        self.glyph.Update()

    def set_scale(self, scale_factor):
        self.set_velocity_bounds(0.5 * scale_factor, 1.5 * scale_factor)
        # self.glyph.SetScaleFactor(scale_factor)
        # self.glyph.Update()

    def set_ratio(self, ratio):
        self.ratio = max(0.001, ratio)
        self.mask_points.SetOnRatio(int(1 / self.ratio))
        self.glyph.Update()
