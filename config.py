global File
global ArrayName
global Filter
global ThresholdMin
global ThresholdMax
global RangeMin
global RangeMax
global ArrayNameList
global FilterList
global NumPoints
global CoordMax
global CellRes
global Lut

File = 'None'
ArrayName = 'None'
Filter = 'None'
ThresholdMin = 'None'
ThresholdMax = 'None'
RangeMin = 'None'
RangeMax = 'None'
ArrayNameList = ['vx', 'vy', 'vz', 'mass', 'uu', 'hh', 'mu', 'rho', 'phi', 'id', 'mask']
FilterList = ['None', 'dm', 'baryon', 'star', 'wind', 'gas', 'agn']
NumPoints = 'None'

CoordMax = 64  # max x/y/z coordinate value
CellRes = 50  # number of cells in each dimension during interpolation 

Lut = None  # Lookup table for coloring the particles, shared by different actors
