from collections import OrderedDict
from flask import Flask, render_template

from IMHDLine import IMHDLine
from shmu_scrapper import get_aladin_url_img
from imhd_scrapper import get_next_departures_from_schedules_table
from constants import IMHDLineDirection, IMHDLineDirectionAlias, IMHDLineType

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
    data: OrderedDict[(int, str), IMHDLine] = OrderedDict()
    # key is a line number, e.g. 3 means tram number 3

    # raca_3_data = get_next_departures_from_schedules_table(3,'rača','Jungmannova')
    # raca_3 = IMHDLine(3, IMHDLineType.TRAM.value, IMHDLineDirection.RACA.value, IMHDLineDirectionAlias.RACA.value, raca_3_data)
    # data[(3, IMHDLineDirectionAlias.RACA.value)] = raca_3

    raca_3 = IMHDLine(3,
                           IMHDLineType.TRAM,
                           IMHDLineDirection.RACA,
                           IMHDLineDirectionAlias.RACA,
                           'Jungmannova')
    data[(3, IMHDLineDirectionAlias.RACA.value)] = raca_3

    dubravka_83 = IMHDLine(83,
                           IMHDLineType.BUS,
                           IMHDLineDirection.DUBRAVKA,
                           IMHDLineDirectionAlias.DUBRAVKA,
                           'Hálova')
    data[(83, IMHDLineDirectionAlias.DUBRAVKA.value)] = dubravka_83

    dubravka_84 = IMHDLine(84,
                           IMHDLineType.BUS,
                           IMHDLineDirection.DUBRAVKA,
                           IMHDLineDirectionAlias.DUBRAVKA,
                           'Hálova')
    data[(84, IMHDLineDirectionAlias.DUBRAVKA.value)] = dubravka_84

    autobusova_88 = IMHDLine(88,
                           IMHDLineType.BUS,
                           IMHDLineDirection.AUTOBUSOVA,
                           IMHDLineDirectionAlias.AUTOBUSOVA,
                           'Hálova')
    data[(88, IMHDLineDirectionAlias.AUTOBUSOVA.value)] = autobusova_88

    return render_template("moja_mhd.html", data=data)