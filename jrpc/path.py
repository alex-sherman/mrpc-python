
class Path(object):
    def __init__(self, path = None):
        self.path = path

    @property
    def is_guid(self):
        if self.path is None:
            return False
        return self.path[0] != '/'
    