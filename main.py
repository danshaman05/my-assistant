import asyncio
from collections import OrderedDict
from flask import Flask, render_template, flash

from IMHDRoute import IMHDRoute
from scraper.shmu_scraper import get_aladin_url_img
from scraper.imhd_scraper import set_next_departures_from_schedules_table, set_next_departures_for_each_object
from constants import IMHDRouteDirection, IMHDRouteDirectionAlias, IMHDVehicleType
from scraper.errors import CriticalScraperError

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q999Tqrerfdcggr98340g8734238gfdsg9234059dfg8z\r\xec]/'

@app.route("/aladin")
def shmu_aladin():
    return render_template("shmu_aladin.html", aladin_img_src=get_aladin_url_img())

@app.route("/radar")
def shmu_radar():
    return render_template("shmu_radar.html")


@app.route("/")
@app.route("/my-mhd")
async def my_mhd():
    imhdroute_objects: OrderedDict[(int, str), IMHDRoute] = OrderedDict()
    """Key is a route number, e.g. 3 means tram number 3
    It is better to have data in mapped to route ids and directions in a dict, in a case we 
    would want to display IMHD routes in some specific groups or order."""

    imhdroute_objects[(3, IMHDRouteDirectionAlias.RACA)] = IMHDRoute(3,
                                                                     IMHDVehicleType.TRAM,
                                                                     IMHDRouteDirection.RACA,
                                                                     IMHDRouteDirectionAlias.RACA,
                      'Jungmannova')

    imhdroute_objects[(83, IMHDRouteDirectionAlias.DUBRAVKA)] = IMHDRoute(83,
                                                                          IMHDVehicleType.BUS,
                                                                          IMHDRouteDirection.DUBRAVKA,
                                                                          IMHDRouteDirectionAlias.DUBRAVKA,
                      "Hálova")

    imhdroute_objects[(84, IMHDRouteDirectionAlias.DUBRAVKA)] = IMHDRoute(84,
                                                                          IMHDVehicleType.BUS,
                                                                          IMHDRouteDirection.DUBRAVKA,
                                                                          IMHDRouteDirectionAlias.DUBRAVKA,
                      "Hálova")

    imhdroute_objects[(88, IMHDRouteDirectionAlias.DUBRAVKA)] = IMHDRoute(88,
                                                                          IMHDVehicleType.BUS,
                                                                          IMHDRouteDirection.AUTOBUSOVA,
                                                                          IMHDRouteDirectionAlias.AUTOBUSOVA,
                      "Hálova")

    imhdroute_objects[(83, IMHDRouteDirectionAlias.PETRZALKA)] = IMHDRoute(83,
                                                                          IMHDVehicleType.BUS,
                                                                          IMHDRouteDirection.PETRZALKA_KUTLIKOVA,
                                                                          IMHDRouteDirectionAlias.PETRZALKA,
                                                                          "Zochova")

    imhdroute_objects[(84, IMHDRouteDirectionAlias.PETRZALKA)] = IMHDRoute(84,
                                                                                     IMHDVehicleType.BUS,
                                                                                     IMHDRouteDirection.PETRZALKA_OVSISTE,
                                                                                     IMHDRouteDirectionAlias.PETRZALKA,
                                                                                     "Zochova")

    try:
        await set_next_departures_for_each_object(imhdroute_objects)
    except (CriticalScraperError, ValueError) as e:
        # We need to handle ValueError in the case someone will enter bad input (e.g. bad start station name).
        print(f"Scraping failed. {e}")
        flash(
            "We were unable to obtain information on the departures of some routes. Please contact the administrator.", "Error")

    return render_template("my_mhd.html", data=imhdroute_objects)