__all__ = ["service", "exception"]
import node
LocalNode = node.Node()

import service
import proxy
import exception
import path

Service = service.Service
Proxy = proxy.Proxy
Path = path.Path

use_transport = LocalNode.use_transport
set_service = LocalNode.set_service

__author__ = "Alex Sherman <asherman1024@gmail.com>"
__copyright__ = "Copyright 2014"
__credits__ = ["Alex Sherman", "Peter Den Hartog"]
__license__ = "MIT"
__maintainer__ = "Alex Sherman"
__email__ = "asherman1024@gmail.com"
