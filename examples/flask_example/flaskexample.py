from mrpc.web import *
from flask import Flask, render_template
import mrpc
from mrpc.transport import SocketTransport

app = Flask(__name__)
mrpc.use_transport(SocketTransport(0, "192.168.1.4"))
app.register_blueprint(FlaskForwarder("service", __name__, url_prefix="/api"))

@app.route('/')
def index():
    return render_template("index.html")
app.run(host='0.0.0.0', port=8080, debug=True)