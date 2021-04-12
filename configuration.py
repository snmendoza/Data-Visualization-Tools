from configparser import ConfigParser
from os import path
home = path.expanduser("~")

#directory = path.dirname(__file__)
parser = ConfigParser()
dir = path.join(home, 'data-visualization-tools','settings.ini')
print(dir)
parser.read(dir)

if __name__ == '__main__':
    sections = parser.sections
    if not sections:
        print("No config parser sections found in {}".format(dir))
    for sect in sections:
        print(sect, parser[sect])
        # configuration.parser['settings']['mass_header']
