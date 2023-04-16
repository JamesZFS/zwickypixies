import unittest
from importer import getPolyData
from filters import *

class TestMask(unittest.TestCase):
    def test_masksum(self):
        filename = '/home/leonardo/Documents/Cosmology/Full.cosmo.624.vtp'
        polydata = getPolyData(filename)
        array_name = 'mass'
        dm = mask_points(polydata, array_name, 'dm')
        baryon = mask_points(polydata, array_name, 'baryon')
        star = mask_points(polydata, array_name, 'star')
        wind = mask_points(polydata, array_name, 'wind')
        gas = mask_points(polydata, array_name, 'gas')
        agn = mask_points(polydata, array_name, 'agn')
        num_polydata = polydata.GetNumberOfPoints()
        num_dm = dm.GetNumberOfPoints()
        num_baryon = baryon.GetNumberOfPoints()
        num_star = star.GetNumberOfPoints()
        num_wind = wind.GetNumberOfPoints()
        num_gas = gas.GetNumberOfPoints()
        num_agn = agn.GetNumberOfPoints()
        print('Total Number of Points: ', num_polydata)
        print('Number of dm: ', num_dm)
        print('Number of baryon: ', num_baryon)
        print('Number of star: ', num_star)
        print('Number of wind: ', num_wind)
        print('Number of gas: ', num_gas)
        print('Number of agn: ', num_agn)
        assert num_polydata == num_dm + num_baryon
        assert num_polydata == num_dm + num_baryon and num_gas <= num_baryon and num_agn <= num_dm

if __name__ == '__main__':
    unittest.main()
