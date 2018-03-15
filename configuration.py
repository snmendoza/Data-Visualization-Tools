from configparser import ConfigParser
from os import path
directory = path.dirname(__file__)
parser = ConfigParser()
parser.read(path.join(directory, 'config.ini'))

if __name__ == '__main__':
    sections = parser.sections()
    for sect in sections:
        print(sect, parser[sect])
        # configuration.parser['settings']['mass_header']
