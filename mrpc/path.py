import uuid
from .exception import InvalidPath

class Path(object):
    def __init__(self, path):
        self.name = None
        self.procedure = None;
        self.is_wildcard = False
        self.path = None

        if type(path) is str or type(path) is unicode:
            self.path = str(path)
            splitted = path.split(".")
            if len(splitted) == 2:
                self.name, self.procedure = splitted
                self.is_wildcard = self.name == "*"
            else:
                self.name = self.path
            # Ignore leading slashes for backwards compatibility
            if self.name[0] == '/':
                self.name = self.name[1:]
        else:
            raise InvalidPath("Invalid path: " + path)

    @property
    def guid(self):
        try:
            return uuid.UUID(hex = self.name)
        except:
            return None

    def __repr__(self):
        return "<Path: " + self.path + ">"

    def is_match(self, service_name, service, aliases):
        if not self.procedure == service_name:
            return False
        if self.is_wildcard:
            return True
        output = self.name in service.aliases + [aliases]
        return output
    