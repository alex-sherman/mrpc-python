import uuid

class MRPCNode(object):
    self_node = None
    
    def __init__(self, guid = None):
        if not (MRPCNode.self_node is None):
            raise RuntimeError("Only one MRPCNode can be instantiated")
        if guid is None:
            guid = uuid.uuid4()
        self.guid = guid

    @staticmethod
    def get_self_node():
        if MRPCNode.self_node is None:
            MRPCNode.self_node = MRPCNode()
        return MRPCNode.self_node

