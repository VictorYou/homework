import os

class PathHandler(object):
    def __init__(self):
        pass

    def handle_path(self, curdir, path):
        if path.startswith('..'):
            new_path = curdir + os.sep + path
        else:
            new_path = path
        return new_path