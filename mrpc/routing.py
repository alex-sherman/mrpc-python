import mrpc
from mrpc.service import Service, method
from mrpc.path import Path

class Routing(Service):
    @method
    def list_routes(self):
        return mrpc.LocalNode.services.keys()

    @method
    def list_procedures(self, path):
        services = mrpc.LocalNode.get_services(Path(path))
        procedures = [method for service in services for method in service._methods()]
        return procedures

    @method
    def who_has(self, path):
        if mrpc.LocalNode.get_services(Path(path)):
            return mrpc.LocalNode.guid.hex
        raise mrpc.exception.NoReturn()