from flask import Blueprint, render_template, request
import json
import mrpc

class FlaskForwarder(Blueprint):
    def __init__(self, *args, **kwargs):
        Blueprint.__init__(self, *args, **kwargs)
        self.add_url_rule("/rpc", "rpc", self.rpc, methods = ["POST"])

    def rpc(self):
        requestArgs = request.get_json()
        return json.dumps(mrpc.rpc(**requestArgs).get(timeout = 1))
