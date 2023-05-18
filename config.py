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
ArrayName = 'phi'
Filter = 'None'
ThresholdMin = 'None'
ThresholdMax = 'None'
RangeMin = 'None'
RangeMax = 'None'
CurrentTime = "-1"
CurrentView = 'Type Explorer'
ArrayNameList = ['vx', 'vy', 'vz', 'mass', 'uu', 'hh', 'mu', 'rho', 'phi', 'id', 'mask']
FilterList = ['dm', 'baryon', 'star', 'wind', 'gas', 'agn']
FilterListLongName = {'dm':'Dark Matter', 'baryon':'Baryon', 'star':'Star', 'wind':'Wind', 'gas':'Gas', 'agn':'Active Galactic Nuclei'}
NumPoints = 'None'
threshod_port = 0
CurrentFilters = []
ShowFilter = {'dm':True, 'baryon':True, 'star':True, 'wind':True, 'gas':True, 'agn':True}
DataViewOpacity = 0.2
DataViewRadius = 0.2
CoordMax = 64  # max x/y/z coordinate value
CellRes = 50  # number of cells in each dimension during interpolation 

Lut = None  # Lookup table for coloring the particles, shared by different actors
