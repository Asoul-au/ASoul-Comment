import getopt
import sys
from tools.fetch import *


if __name__ == "__main__":
    try:
        options, args = getopt.getopt(args=sys.argv[1:], shortopts="hfrut",
                                      longopts=["help", "fetch", "run", "update", "update-all", "test"])
    except getopt.GetoptError:
        raise NameError("Options incorrect, type --help for more info.")
    for opt, args in options:
        if opt in ('-h', '--help'):
            # TODO: print help panel
            sys.exit()
        elif opt in ('-f', '--fetch'):
            createDatabase()
        elif opt in ('-u', '--update'):
            updateDatabase(False)
        elif opt in '--update-all':
            updateDatabase(True)
