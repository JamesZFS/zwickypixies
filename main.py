from rendering.window import *
from helpers import *
import config

def main():
    config.Lut = create_lookup_table('coolwarm')
    startWindow()

if __name__ == '__main__':
    main()
