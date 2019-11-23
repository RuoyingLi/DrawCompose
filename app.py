from settings import KEY, ENDPOINT
from flask import Flask, escape, request, render_template

app = Flask(__name__)


def gui_strokes_2_azure_strokes(gui_strokes):
    ret = gui_strokes
    return ret

@app.route('/')
def hello_world():
    return render_template("drawl-gui.html")


@app.route("/strokes", methods=["POST", "GET"])
def strokes():
    print(str(request.json))
    return "<h1>Ok, cool!</h1>"

