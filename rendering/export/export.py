import threading
import vtk
from vtkmodules.util.numpy_support import vtk_to_numpy, numpy_to_vtk
import numpy as np
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkPolyData
import config
import re
from rendering.export.exportactors import ExportActors


class Exporter:
    def __init__(self, window):
        self.window = window
        thread = threading.Thread(target=self.create_video)
        self.renderer = vtk.vtkRenderer()
        self.renderinterpolationsteps = 10
        self.actors = ExportActors(self.renderer)
        self.actors.set_property_map(self.window.actors.property_map)
        thread.start()
        print("Done")

    def disable_controls(self):
        self.window.menubar.menubar.setDisabled(True)
        self.window.menubar.animation_bar.setDisabled(True)
        self.window.toolbar.toolbar.setDisabled(True)
        self.window.iren.Disable()

    def enable_controls(self):
        self.window.menubar.menubar.setEnabled(True)
        self.window.menubar.animation_bar.setEnabled(True)
        self.window.toolbar.toolbar.setEnabled(True)
        self.window.iren.Enable()

    def create_video(self):
        self.disable_controls()
        renderWindow = vtk.vtkRenderWindow()
        renderWindow.SetSize(1920, 1080)
        renderWindow.SetOffScreenRendering(1)
        renderWindow.AddRenderer(self.renderer)
        filename1 = config.File
        filename2 = config.File
        timesteps = self.create_array(self.renderinterpolationsteps)
        frames = []
        frame = 0
        for i in range(620, 623, 2):
            self.window.bottombar.updateBottomBarProgress(i)
            numbers1 = re.findall(r"\d+", filename1)
            if numbers1:
                filename1 = filename1.replace(numbers1[0].zfill(3), str(i).zfill(3))
            numbers2 = re.findall(r"\d+", filename2)
            if numbers2:
                filename2 = filename2.replace(numbers2[0].zfill(3), str(i + 2).zfill(3))
            reader1 = vtk.vtkXMLPolyDataReader()
            reader1.SetFileName(filename1)
            reader1.Update()
            polydata1 = reader1.GetOutput()

            reader2 = vtk.vtkXMLPolyDataReader()
            reader2.SetFileName(filename2)
            reader2.Update()
            polydata2 = reader2.GetOutput()

            polydata1, polydata2 = self.eliminate_unequal_ids(polydata1, polydata2)
            for timestep in timesteps:
                polydata = self.interpolate(polydata1, polydata2, timestep)
                self.actors.set_polydata(polydata)
                self.actors.update_actors()
                self.renderer.ResetCamera()
                renderWindow.Render()
                windowToImageFilter = vtk.vtkWindowToImageFilter()
                windowToImageFilter.SetInput(renderWindow)
                windowToImageFilter.Update()
                writer = vtk.vtkPNGWriter()
                fpath = "rendering/.frames/frame{}.png".format(frame)
                writer.SetFileName(fpath)
                writer.SetInputConnection(windowToImageFilter.GetOutputPort())
                writer.Write()
                frames.append(fpath)
                frame += 1

        self.enable_controls()
        self.window.bottombar.clearBottomBarProgress()

    def eliminate_unequal_ids(self, polydata1, polydata2):
        points_data1 = polydata1.GetPointData()
        points_data2 = polydata2.GetPointData()

        ids1 = vtk_to_numpy(points_data1.GetArray('id'))
        ids2 = vtk_to_numpy(points_data2.GetArray('id'))
        _, unique_indices1 = np.unique(ids1, return_index=True)
        _, unique_indices2 = np.unique(ids2, return_index=True)

        ids1 = ids1[unique_indices1]
        ids2 = ids2[unique_indices2]
        common_ids = set(ids1).intersection(ids2)

        id_mask1 = np.isin(ids1, list(common_ids))
        id_mask2 = np.isin(ids2, list(common_ids))
        points1_np = vtk_to_numpy(polydata1.GetPoints().GetData())[unique_indices1]
        points2_np = vtk_to_numpy(polydata2.GetPoints().GetData())[unique_indices2]
        common_points1_np = points1_np[id_mask1]
        common_points2_np = points2_np[id_mask2]

        common_points1_vtk = vtkPoints()
        common_points1_vtk.SetData(numpy_to_vtk(common_points1_np))
        common_points2_vtk = vtkPoints()
        common_points2_vtk.SetData(numpy_to_vtk(common_points2_np))

        common_polydata1 = vtkPolyData()
        common_polydata1.SetPoints(common_points1_vtk)
        common_polydata2 = vtkPolyData()
        common_polydata2.SetPoints(common_points2_vtk)
        array_names = [points_data1.GetArrayName(i) for i in range(points_data1.GetNumberOfArrays())]

        for name in array_names:
            try:
                array1 = vtk_to_numpy(points_data1.GetArray(name))[unique_indices1]
                array2 = vtk_to_numpy(points_data2.GetArray(name))[unique_indices2]
                common_array1 = array1[id_mask1]
                common_array2 = array2[id_mask2]

                vtk_array1 = numpy_to_vtk(common_array1)
                vtk_array1.SetName(name)
                common_polydata1.GetPointData().AddArray(vtk_array1)

                vtk_array2 = numpy_to_vtk(common_array2)
                vtk_array2.SetName(name)
                common_polydata2.GetPointData().AddArray(vtk_array2)
            except:
                print(name)

        assert common_polydata1.GetNumberOfPoints() == common_polydata2.GetNumberOfPoints(), \
            "Number of points in the two polydata are not equal:{} -> {} {}".format(len(common_ids),
                                                                                    common_points1_np.shape,
                                                                                    common_points2_np.shape)
        return common_polydata1, common_polydata2

    def interpolate(self, polydata1, polydata2, t):
        points_data1 = polydata1.GetPointData()
        points_data2 = polydata2.GetPointData()
        points_data1.SetActiveScalars(config.ArrayName)
        points_data2.SetActiveScalars(config.ArrayName)
        interp_data = vtk.vtkPointData()
        for i in range(points_data1.GetNumberOfArrays()):
            arr1 = points_data1.GetArray(i)
            arr2 = points_data2.GetArray(i)
            interp_arr = vtk.vtkFloatArray()
            interp_arr.SetNumberOfComponents(arr1.GetNumberOfComponents())
            interp_arr.SetName(arr1.GetName())
            for j in range(arr1.GetNumberOfTuples()):
                tuple1 = arr1.GetTuple(j)
                tuple2 = arr2.GetTuple(j)
                interp_tuple = [(1 - t) * v1 + t * v2 for v1, v2 in zip(tuple1, tuple2)]
                interp_arr.InsertNextTuple(interp_tuple)
            interp_data.AddArray(interp_arr)

        scalars1 = points_data1.GetScalars()
        scalars2 = points_data2.GetScalars()
        interp_scalars = vtk.vtkFloatArray()
        interp_scalars.SetNumberOfComponents(scalars1.GetNumberOfComponents())
        interp_scalars.SetName(scalars1.GetName())
        for i in range(scalars1.GetNumberOfTuples()):
            tuple1 = scalars1.GetTuple(i)
            tuple2 = scalars2.GetTuple(i)
            interp_tuple = [(1 - t) * v1 + t * v2 for v1, v2 in zip(tuple1, tuple2)]
            interp_scalars.InsertNextTuple(interp_tuple)
        interp_data.SetScalars(interp_scalars)

        output = vtk.vtkPolyData()
        output.ShallowCopy(polydata1)
        output.GetPointData().ShallowCopy(interp_data)
        return output

    def create_array(self, n):
        def create_equidistant_array(n):
            if n <= 1:
                return [0, 1]
            interval = 1 / (n - 1)
            equidistant_array = [i * interval for i in range(n)]
            return equidistant_array
        arr = create_equidistant_array(n)
        return arr[0:-1]