import asyncio
from collections import OrderedDict
from flask import Flask, render_template

from IMHDLine import IMHDLine
from shmu_scrapper import get_aladin_url_img
from imhd_scrapper import get_next_departures_from_schedules_table
from constants import IMHDLineDirection, IMHDLineDirectionAlias, IMHDLineType

app = Flask(__name__)

@app.route("/aladin")
def shmu_aladin():
    return render_template("shmu_aladin.html", aladin_img_src=get_aladin_url_img())

@app.route("/radar")
def shmu_radar():
    return render_template("shmu_radar.html")


@app.route("/")
@app.route("/moja-mhd")
async def moja_mhd():
    data: OrderedDict[(int, str), IMHDLine] = OrderedDict()
    # key is a line number, e.g. 3 means tram number 3

    # raca_3_data = get_next_departures_from_schedules_table(3,'rača','Jungmannova')
    # raca_3 = IMHDLine(3, IMHDLineType.TRAM.value, IMHDLineDirection.RACA.value, IMHDLineDirectionAlias.RACA.value, raca_3_data)
    # data[(3, IMHDLineDirectionAlias.RACA.value)] = raca_3


    input_data = [[3, IMHDLineDirection.RACA.value, "Jungmannova" ],
                  [83, IMHDLineDirection.DUBRAVKA.value, "Hálova"],
                  [84, IMHDLineDirection.DUBRAVKA.value, "Hálova"],
                  [88, IMHDLineDirection.AUTOBUSOVA.value, "Hálova"]]
    # asynchronously scrap imhd.sk
    tasks = [asyncio.create_task(get_next_departures_from_schedules_table(_id, direction, start_station)) for _id, direction, start_station in input_data]
    results = await asyncio.gather(*tasks)

    raca_3 = IMHDLine(3,
                           IMHDLineType.TRAM,
                           IMHDLineDirection.RACA,
                           IMHDLineDirectionAlias.RACA,
                           'Jungmannova',
                            results[0])
    data[(3, IMHDLineDirectionAlias.RACA.value)] = raca_3

    dubravka_83 = IMHDLine(83,
                           IMHDLineType.BUS,
                           IMHDLineDirection.DUBRAVKA,
                           IMHDLineDirectionAlias.DUBRAVKA,
                           'Hálova',
                           results[1])
    data[(83, IMHDLineDirectionAlias.DUBRAVKA.value)] = dubravka_83

    dubravka_84 = IMHDLine(84,
                           IMHDLineType.BUS,
                           IMHDLineDirection.DUBRAVKA,
                           IMHDLineDirectionAlias.DUBRAVKA,
                           'Hálova',
                           results[2])
    data[(84, IMHDLineDirectionAlias.DUBRAVKA.value)] = dubravka_84

    autobusova_88 = IMHDLine(88,
                           IMHDLineType.BUS,
                           IMHDLineDirection.AUTOBUSOVA,
                           IMHDLineDirectionAlias.AUTOBUSOVA,
                           'Hálova',
                            results[3])
    data[(88, IMHDLineDirectionAlias.AUTOBUSOVA.value)] = autobusova_88

    return render_template("moja_mhd.html", data=data)