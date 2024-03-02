from flask import Flask, render_template

from shmu_scrapper import get_aladin_url_img
from imhd_scrapper import get_next_departures_from_schedules_table

app = Flask(__name__)

@app.route("/")
@app.route("/aladin")
def shmu_aladin():
    return render_template("shmu_aladin.html", aladin_img_src=get_aladin_url_img())

@app.route("/radar")
def shmu_radar():
    return render_template("shmu_radar.html")


@app.route("/moja-mhd")
def moja_mhd():
    data: dict[(int, str), dict[str, list[str]]] = {}
    # key is a line number, e.g. 3 means tram number 3
    data[(3, 'rača')] = get_next_departures_from_schedules_table(3, 'rača', 'Jungmannova')

    # data[83] = get_next_departures_from_schedules_table(3, 'rača', 'Jungmannova')


    return render_template("moja_mhd.html", data=data)