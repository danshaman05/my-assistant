import requests
from bs4 import BeautifulSoup

IMHD_URL_PREFIX = "https://imhd.sk"
SCHEDULES_PAGE_URL = "https://imhd.sk/ba/cestovne-poriadky"
SCHEDULES_PAGE_URL_OFFLINE = "/home/daniel/PycharmProjects/My_assistant/imhd_offline_pages/cestovne poriadky/ba/cestovne-poriadky.html"

# Slovnik: line = linka


def get_line_stops_page_url(line: int):
    """Get a line stops webpage (for both directions)."""
    r = requests.get(SCHEDULES_PAGE_URL)
    # print(r.content)
    soup = BeautifulSoup(r.content, features="lxml")

    linky = soup.css.select("a.Linka--lg")

    line_url = None
    for l in linky:
        if l.text == str(line):
            line_url = l['href']
            break
    return IMHD_URL_PREFIX + line_url




def get_next_departures(line: int, direction: str):
    """return 5 next departures"""

    """staci v tabulke s id SM14 najst td, ktory ma class="next-departure. To je najblizsi cas odchodu.
    
    Ja to asi spravim tak, ze ziskam si do dvoch poli (ktore budu predstavovat dve hodiny - aktualnu a dalsiu) vsetky odchody.
    Potom vyberiem len tie, co su rovne, alebo vacsie ako next-departure odchod.
    """

    # TODO
    # first_departure =




if __name__ == "__main__":
    get_line_stops_page_url(3)

    # Test function get_line_stops_page_url
    assert get_line_stops_page_url(3) == "https://imhd.sk/ba/linka/3/bd807c807f847f7f827c82"
    assert get_line_stops_page_url(9) == "https://imhd.sk/ba/linka/9/bd807c807f847f7f887c88"
    assert get_line_stops_page_url(33) == "https://imhd.sk/ba/linka/33/bd807c807f847f82827c8282"
    assert get_line_stops_page_url(42) == "https://imhd.sk/ba/linka/42/bd807c807f847f83817c8381"
    assert get_line_stops_page_url(83) == "https://imhd.sk/ba/linka/83/bd807c807f847f87827c8782"
    assert get_line_stops_page_url(84) == "https://imhd.sk/ba/linka/84/bd807c807f847f87837c8783"

    print("End of testing.")

