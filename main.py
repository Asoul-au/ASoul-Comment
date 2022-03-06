import getopt
import sys
from tools.fetch import *


def logSetup():
    logging.basicConfig(level=logging.DEBUG,
                        filename=".main.log",
                        filemode="a",
                        format="%(asctime)s-%(name)s-%(levelname)-9s-%(filename)-8s@%(lineno)s: %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S")


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
