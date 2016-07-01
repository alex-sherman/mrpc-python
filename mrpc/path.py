import uuid

class Path(object):
    def __init__(self, path = None):
        self.service = None
        self.is_broadcast = False
        self.path = None

        if type(path) is uuid.UUID:
            path = path.hex

        if type(path) is str or type(path) is unicode:
            self.path = str(path)
            if path[0] == "*":
                path = path[1:]
                self.is_broadcast = True
            self.service = path
        else:
            raise ValueError("Invalid path")

    @property
    def guid(self):
        try:
            return uuid.UUID(hex = self.path)
        except:
            return None

    def __repr__(self):
        return "<Path: " + self.path + ">"

    def is_match(self, other):
        if not type(other) is Path:
            other = Path(other)
        if self.is_broadcast or other.is_broadcast:
            return True
        return self.service == other.service
    