from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
from helpers import *
from animation import *
from dataops.importer import *
from dataops.filters import *
from rendering.window import *
import config


def main():
    config.Lut = create_lookup_table('coolwarm')
    filename = get_program_parameters()
    reader = vtkXMLPolyDataReader()
    reader.SetFileName(filename)
    reader.Update()
    config.File = filename
    config.ArrayName = 'phi'
    polydata = reader.GetOutput()
    print_meta_data(slice_polydata(polydata, 200))

    point_actor = getActor(config.ArrayName, filename)
    startWindow(point_actor)


if __name__ == '__main__':
    main()