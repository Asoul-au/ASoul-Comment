import getopt
import asyncio
import sys
from tools.fetch import *
from server.server import *
import uvicorn

if __name__ == "__main__":
    try:
        options, args = getopt.getopt(args=sys.argv[1:], shortopts="hfutr",
                                      longopts=["help", "fetch", "update", "update-all", "test", "start-server"])
    except getopt.GetoptError:
        raise NameError("Options incorrect, type --help for more info.")
    for opt, args in options:
        if opt in ('-h', '--help'):
            # TODO: print help panel
            sys.exit()
        elif opt in ('-f', '--fetch'):
            createDatabase()
            # TODO: Progress bar!
            # TODO: This would require a updated structure for storing more information.
            # TODO: So that means we should also create a `update` script for updating from different versions.
            updateDatabase(True)
        elif opt in ('-u', '--update'):
            updateDatabase(False)
        elif opt in '--update-all':
            updateDatabase(True)
        elif opt in '--start-server':
            # TODO: customization options like ip or port.
            startServer()
