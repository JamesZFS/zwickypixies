from vtkmodules.vtkFiltersSources import vtkPlaneSource
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkFiltersPoints import (
    vtkGaussianKernel,
    vtkPointInterpolator
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
)

import config

class Interpolator:
    def __init__(self, polydata: vtkPolyData):
        self.polydata = polydata
        
        self.plane_source = vtkPlaneSource()
        self.plane_source.SetOrigin(0, 0, config.CoordMax / 2)  # TODO: move the "scan" plane with GUI
        self.plane_source.SetPoint1(config.CoordMax, 0, config.CoordMax / 2)
        self.plane_source.SetPoint2(0, config.CoordMax, config.CoordMax / 2)
        self.plane_source.SetResolution(config.CellRes, config.CellRes)
        self.plane_source.Update()

        # Interpolate from the point data to the cell data on the plane
        self.gaussian_kernel = vtkGaussianKernel()
        self.gaussian_kernel.SetSharpness(10)  # TODO: make it a GUI slider
        self.gaussian_kernel.SetRadius(3)

        interpolator = vtkPointInterpolator()
        interpolator.SetInputConnection(self.plane_source.GetOutputPort())
        interpolator.SetSourceData(self.polydata)
        interpolator.SetKernel(self.gaussian_kernel)
        interpolator.Update()

        # Debug print of interpolated data
        # data: vtkPolyData = interpolator.GetOutput()
        # print('Interpolated data:')
        # print('Number of points:', data.GetNumberOfPoints())
        # print('Number of cells:', data.GetNumberOfCells())
        # print('Number of point data arrays:', data.GetPointData().GetNumberOfArrays())
        # print('Number of cell data arrays:', data.GetCellData().GetNumberOfArrays())
        # arr = np.array(data.GetPointData().GetScalars())
        # print(arr, arr.shape, arr.mean())

        plane_mapper = vtkPolyDataMapper()
        plane_mapper.SetInputConnection(interpolator.GetOutputPort())
        plane_mapper.SetScalarRange(config.RangeMin, config.RangeMax)
        plane_mapper.SetLookupTable(config.Lut)

        self.plane_actor = vtkActor()
        self.plane_actor.SetMapper(plane_mapper)

    def get_plane_actor(self):
        return self.plane_actor
    
    def set_plane_z(self, z):
        # Move the plane in the z direction, z: [0, CoordMax] float
        self.plane_source.SetOrigin(0, 0, z)
        self.plane_source.SetPoint1(config.CoordMax, 0, z)
        self.plane_source.SetPoint2(0, config.CoordMax, z)
        self.plane_source.Update()

    def set_kernel_sharpness(self, sharpness):
        self.gaussian_kernel.SetSharpness(sharpness)
        self.gaussian_kernel.Modified()
