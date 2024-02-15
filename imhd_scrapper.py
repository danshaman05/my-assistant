import requests
from bs4 import BeautifulSoup

IMHD_URL_PREFIX = "https://imhd.sk"
SCHEDULES_PAGE_URL = "https://imhd.sk/ba/cestovne-poriadky"
SCHEDULES_PAGE_URL_OFFLINE = "/home/daniel/PycharmProjects/My_assistant/imhd_offline_pages/cestovne poriadky/ba/cestovne-poriadky.html"

# Slovnik: line = linka


def get_line_stops_page_url(line: int):
    """Get a line stops webpage (for both directions)."""
    r = requests.get(SCHEDULES_PAGE_URL)
    soup = BeautifulSoup(r.content, features="lxml")
    linky = soup.css.select("a.Linka--lg")
    line_url = None
    for l in linky:
        if l.text == str(line):
            line_url = l['href']
            break
    return IMHD_URL_PREFIX + line_url

def get_line_schedules_for_direction_and_stop(line: int, direction: str, stop: str):
    """ 
    line: e.g. 3,
    direction: e.g. 'rača',
    stop: 'Jungmanova' """
    line_stops_page_url = get_line_stops_page_url(line)

    r = requests.get(line_stops_page_url)
    soup = BeautifulSoup(r.content, features="lxml")

    list_of_elements = soup.css.select('div[class^="ModuleGroup-left"] div[class^="ModuleGroup-left"] h2[class^="Heading h5"]')
    left_direction = list_of_elements[0]

    # the webpage contains two sides, one for each direction
    side = "left" if left_direction.text.lower() == direction.lower() else "right"

    list_of_a_elements = soup.css.select(f'div[class^=ModuleGroup-left] div[class^=ModuleGroup-{side}] tbody td.w-100 a ')

    for a in list_of_a_elements:
        # first stop is different, it has a span as a child element
        line_name = a.span.getText() if a.span else a.getText()
        if line_name.lower() == stop.lower():
            return IMHD_URL_PREFIX + a['href']
    raise ValueError("Your input is probably wrong. Check it, and if it is OK, contact a developer.")




def get_next_departures(line: int, direction: str):
    # TODO
    """return 5 next departures"""

    """staci v tabulke s id SM14 najst td, ktory ma class="next-departure. To je najblizsi cas odchodu.
    Ja to asi spravim tak, ze ziskam si do dvoch poli (ktore budu predstavovat dve hodiny - aktualnu a dalsiu) vsetky odchody.
    Potom vyberiem 5 takych, co su rovne, alebo vacsie ako next-departure odchod.
    """
    # first_departure =


if __name__ == "__main__":
    TESTING = True

    if TESTING:
        print("Start of testing.")
        assert get_line_stops_page_url(3) == "https://imhd.sk/ba/linka/3/bd807c807f847f7f827c82"
        assert get_line_stops_page_url(9) == "https://imhd.sk/ba/linka/9/bd807c807f847f7f887c88"
        assert get_line_stops_page_url(33) == "https://imhd.sk/ba/linka/33/bd807c807f847f82827c8282"
        assert get_line_stops_page_url(42) == "https://imhd.sk/ba/linka/42/bd807c807f847f83817c8381"
        assert get_line_stops_page_url(83) == "https://imhd.sk/ba/linka/83/bd807c807f847f87827c8782"
        assert get_line_stops_page_url(84) == "https://imhd.sk/ba/linka/84/bd807c807f847f87837c8783"

        assert get_line_schedules_for_direction_and_stop(3, "rača", "Jungmannova") == "https://imhd.sk/ba/cestovny-poriadok/linka/3/Jungmannova/smer-Ra%C4%8Da/bd807c807f847f7f827c8275c18075b680808775be7f75c97f75b3"
        assert get_line_schedules_for_direction_and_stop(3, "rača", "Farského") == "https://imhd.sk/ba/cestovny-poriadok/linka/3/Farsk%C3%A9ho/smer-Ra%C4%8Da/bd807c807f847f7f827c8275c18075b6858775be7f75c98075b3"
        assert get_line_schedules_for_direction_and_stop(84, "DÚBRAVKA, PRI KRÍŽI", "Dvory") == "https://imhd.sk/ba/cestovny-poriadok/linka/84/Dvory/smer-D%C3%BAbravka-Pri-kr%C3%AD%C5%BEi/bd807c807f847f87837c878375c17f75b6858375be7f75c98875b3"
        assert get_line_schedules_for_direction_and_stop(84, "DÚBRAVKA, PRI KRÍŽI", "Hodžovo nám.") == "https://imhd.sk/ba/cestovny-poriadok/linka/84/Hod%C5%BEovo-n%C3%A1m/smer-D%C3%BAbravka-Pri-kr%C3%AD%C5%BEi/bd807c807f847f87837c878375c17f75b6878275be7f75c9808175b3"
        assert get_line_schedules_for_direction_and_stop(31, "CINTORÍN SLÁVIČIE", "Kráľovské údolie") == "https://imhd.sk/ba/cestovny-poriadok/linka/31/Kr%C3%A1%C4%BEovsk%C3%A9-%C3%BAdolie/smer-Cintor%C3%ADn-Sl%C3%A1vi%C4%8Die/bd807c807f847f82807c828075c18075b681848075be7f75c98475b3"

        print("End of testing.")

