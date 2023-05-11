from dataops.importer import *
from rendering.window import *
import config

def main():
    config.Lut = create_lookup_table('coolwarm')
    startWindow()

if __name__ == '__main__':
    main()