import uuid

class Path(object):
    @staticmethod
    def parse(value):
        if type(value) is uuid.UUID:
            return Path(value.bytes)

    def __init__(self, path = None):
        self.path = path

    @property
    def guid(self):
        try:
            return uuid.UUID(bytes = self.path)
        except:
            return None

    def is_match(self, other):
        return False

    def match_dict(self, dictionary):
        for path, value in dictionary.items():
            pass


Path.BROADCAST = Path("*")
    