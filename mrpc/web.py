from flask import Blueprint, render_template, request
import json
import mrpc

_js = \
"""
var mrpc = function(prefix) {{
    function proxy(prefix) {{
        this.prefix = prefix;
        this.rpc = function rpc(path, procedure, value) {{
            var data = {{
                path: path,
                procedure: procedure,
                value: value
            }}
            return $.ajax({{
                url: prefix + "/rpc",
                dataType: "json",
                contentType: "application/json",
                method: "POST",
                data: JSON.stringify(data)
            }});
        }}
    }}
    return new proxy("{0}");
}}
"""

class FlaskForwarder(Blueprint):
    def __init__(self, *args, **kwargs):
        Blueprint.__init__(self, *args, **kwargs)
        self.add_url_rule("/rpc", "rpc", self.rpc, methods = ["POST"])
        self.add_url_rule("/mrpc.js", "mrpcjs", lambda: _js.format(self.url_prefix))

    def rpc(self):
        requestArgs = request.get_json()
        return json.dumps(mrpc.rpc(**requestArgs).get(timeout = 1))
