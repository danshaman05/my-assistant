import requests
from bs4 import BeautifulSoup


def get_radar():
    """Get Radar image from shmu.sk"""
    url = "https://www.shmu.sk/sk/?page=1&id=meteo_radar"
    r = requests.get(url)
    #print(repr(r))
    print(r.content)



if __name__ == "__main__":
    get_radar()