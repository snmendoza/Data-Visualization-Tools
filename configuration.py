from configparser import ConfigParser
from os import path
home = path.expanduser("~")

#directory = path.dirname(__file__)
parser = ConfigParser()
parser.read(path.join(home, 'data-visualisation-tools/settings.ini'))

if __name__ == '__main__':
    sections = parser.sections()
    for sect in sections:
        print(sect, parser[sect])
        # configuration.parser['settings']['mass_header']
