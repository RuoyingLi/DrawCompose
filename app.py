from settings import KEY, ENDPOINT
from flask import Flask, escape, request, render_template
import requests
from parser import interpret, create_yaml

create_yaml()
app = Flask(__name__)



def gui_strokes_2_azure_strokes(gui_strokes):
    ret = gui_strokes
    return ret

@app.route('/')
def hello_world():
    return render_template("drawl-gui.html")


@app.route("/strokes", methods=["POST", "GET"])
def strokes():
    r = request.json

    json = {
      "version" : 1,
      "language": "en-US",
      "unit" : "cm",
      "application" : "drawing",
      "tip" : 'rectangle',
      "strokes": []
    }
    for id, i in enumerate(r):
        points = " ".join([str(j['x']) + ", " + str(j['y']) + "," for j in i])[:-1]
        json['strokes'].append({'id' : id, 'points' : points})

    headers = {"Ocp-Apim-Subscription-Key": KEY}
    url = ENDPOINT + "inkrecognizer/v1.0-preview/recognize"
    #example_req_json = '{"version":1,"language":"en-US","unit":"mm","strokes":[{"id":183,"points":"11.89084,21.69333,11.84664,21.69333,11.74365,21.69333,11.58458,21.69333,11.3769,21.69333,11.13603,21.69333,10.91951,21.73753,10.70778,21.79632,10.53443,21.8966,10.40975,22.04479,10.33059,22.23934,10.28765,22.46819,10.27013,22.71949,10.26828,22.98349,10.2746,23.25317,10.28391,23.52744,10.29315,23.80157,10.34497,24.02904,10.45348,24.1945,10.66368,24.34503,10.9332,24.46251,11.27836,24.54349,11.64686,24.59245,12.00858,24.61708,12.34962,24.62536,12.66655,24.57985,12.91754,24.47099,13.09289,24.30136,13.20062,24.08598,13.25622,23.84014,13.2763,23.57667,13.27521,23.25736,13.26372,22.92023,13.24898,22.58729,13.19093,22.31304,13.07688,22.11477,12.91003,21.98819,12.65335,21.91897,12.35118,21.89021,12.03343,21.88656,11.76191,21.89608","language":"en-US"}]}'
    app.logger.info("Performing request...")
    r = requests.put(url, data=json, headers=headers)
    app.logger.info("Done.")
    app.logger.debug("Reply: {}".format(r.text))
    if not 'error' in r.text:
        app.logger.info("Interpreting json...")
        interpret(r.text)
        app.logger.info("Done.")
    else:
        app.logger.info("Request returned error")
        app.logger.info(r.text)
    return "<h1>Ok, cool!</h1>"

