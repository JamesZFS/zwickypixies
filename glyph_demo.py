import vtk
import numpy as np
from vtkmodules.util.numpy_support import vtk_to_numpy, numpy_to_vtk
from helpers import create_lookup_table, create_legend
import config


# Create a glyph filter that aligns arrows with vectors
def get_glyphs(input_port: int, scale_factor=1.0):
    # Source for the glyph filter
    arrow = vtk.vtkArrowSource()
    arrow.SetTipResolution(3)
    arrow.SetTipLength(0.3)
    arrow.SetTipRadius(0.1)
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
    velocity = np.stack((vx, vy, vz), axis=-1)
    magnitudes = np.linalg.norm(velocity, axis=-1)
    velocity /= magnitudes[:, None]  # normalize
    max_magnitude = np.max(magnitudes)
    min_magnitude = np.min(magnitudes)
    # map the velocity magnitude to the range 
    velocity *= (magnitudes[:, None] - min_magnitude) / (max_magnitude - min_magnitude) * (max_scale - min_scale) + min_scale

    # Set the velocity vector as the active vector
    velocity_vtk = numpy_to_vtk(velocity)
    velocity_vtk.SetName('velocity')
    src.AddArray(velocity_vtk)
    src.SetActiveVectors('velocity')

def main():
    filename = '/home/leonardo/Documents/Cosmology/Full.cosmo.480.vtp'
    lut = create_lookup_table('coolwarm')

    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(filename)
    reader.Update()

    polydata: vtk.vtkPolyData = reader.GetOutput()
    polydata.GetPointData().SetActiveScalars(config.ArrayName)
    set_vectors_by_velocity(polydata.GetPointData())

    # Choose a random subset of points
    ratio = 0.05  # ratio of points to keep
    mask_points = vtk.vtkMaskPoints()
    mask_points.SetInputData(polydata)
    mask_points.SetOnRatio(int(1 / ratio))
    mask_points.RandomModeOn()

    # Visualize as point gaussians
    point_mapper = vtk.vtkPointGaussianMapper()
    point_mapper.SetInputConnection(mask_points.GetOutputPort())
    point_mapper.EmissiveOff()
    point_mapper.SetScaleFactor(0.1)
    point_mapper.SetLookupTable(lut)

    point_actor = vtk.vtkActor()
    point_actor.SetMapper(point_mapper)
    point_actor.GetProperty().SetOpacity(0.5)

    # Create a glyph filter, mapper, and actor
    glyph = get_glyphs(mask_points.GetOutputPort(), scale_factor=1.0)

    glyph_mapper = vtk.vtkPolyDataMapper()
    glyph_mapper.SetInputConnection(glyph.GetOutputPort())
    glyph_mapper.SetScalarModeToUsePointFieldData()
    glyph_mapper.SelectColorArray(config.ArrayName)
    glyph_mapper.ScalarVisibilityOn()
    # glyph_mapper.ScalarVisibilityOff()
    glyph_mapper.SetLookupTable(lut)

    glyph_actor = vtk.vtkActor()
    glyph_actor.SetMapper(glyph_mapper)
    glyph_actor.GetProperty().SetOpacity(0.5)

    # Color bar
    legend = create_legend(lut, config.ArrayName)

    ren = vtk.vtkRenderer()
    ren.AddActor(point_actor)
    ren.AddActor(glyph_actor)
    ren.AddActor(legend)
    ren.SetBackground(0, 0, 0)

    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    renWin.SetSize(1024, 1024)

    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    iren.Initialize()
    iren.Start()

if __name__ == "__main__":
    main()