import requests
from bs4 import BeautifulSoup


def get_aladin_url_img():
    """Get Aladin image URL from shmu.sk"""
    url = "https://www.shmu.sk/sk/?page=1&id=meteo_num_mgram&nwp_mesto=32737"
    r = requests.get(url)
    # print(r.content)
    soup = BeautifulSoup(r.content)
    aladin_img = soup.find('img', id="imageArea")
    return "https://www.shmu.sk" + aladin_img['src']




if __name__ == "__main__":
    print(get_aladin_url_img())