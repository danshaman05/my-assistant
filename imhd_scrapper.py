import requests
from bs4 import BeautifulSoup
from datetime import datetime


IMHD_URL_PREFIX = "https://imhd.sk"
SCHEDULES_PAGE_URL = "https://imhd.sk/ba/cestovne-poriadky"
SCHEDULES_PAGE_URL_OFFLINE = "/home/daniel/PycharmProjects/My_assistant/imhd_offline_pages/cestovne poriadky/ba/cestovne-poriadky.html"

""" NEXT_SCHEDULES_COUNT sets how much next schedules we want to find out. Note, that the programme will look 
for schedules in this and the next hour only. Therefore, the number of schedules that programme outputs may be less than this number."""
NEXT_SCHEDULES_COUNT = 6


# Slovnik: line = linka mestskej hromadnej dopravy (Bratislava)

def get_soup(url):
    # OLD APPROACH:
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup

def get_line_stops_page_url(line: int):
    """Get a line stops webpage (for both directions)."""
    soup = get_soup(SCHEDULES_PAGE_URL)
    linky = soup.css.select("a.Linka--lg")
    line_url = None
    for l in linky:
        if l.text == str(line):
            line_url = l['href']
            break
    return IMHD_URL_PREFIX + line_url

def get_line_schedules_url(line: int, direction: str, stop: str):
    """ 
    line: e.g. 3,
    direction: e.g. 'rača',
    stop: 'Jungmanova'
    """
    line_stops_page_url = get_line_stops_page_url(line)

    soup = get_soup(line_stops_page_url)

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


def get_next_departures(line: int, direction: str, stop: str):
    # TODO
    """return a dictionary, where keys are hours (current and next), and values are minutes - departures"""

    """staci v tabulke s id SM14 najst td, ktory ma class="next-departure. To je najblizsi cas odchodu.
    Ja to asi spravim tak, ze ziskam si do dvoch poli (ktore budu predstavovat dve hodiny - aktualnu a dalsiu) vsetky odchody.
    Potom vyberiem 5 takych, co su rovne, alebo vacsie ako next-departure odchod.
    """
    url = get_line_schedules_url(line, direction, stop)
    soup = get_soup(url)

    now = datetime.now()
    current_hour = now.hour
    current_minute = now.minute

    first_row_td_elements = soup.css.select(f"table[id=SM14] tr[id=sm14T{current_hour}] td")

    # next_schedules is a dict, where key are hours (current and next), and values are minutes
    next_schedules = {current_hour: []}

    for td in first_row_td_elements:
        minute = td.getText()
        if minute:
            minute = int(minute)
            if minute >= current_minute:
                next_schedules[current_hour].append(minute)

    next_schedules_cnt = len(next_schedules[current_hour])   #count of all td elements
    if next_schedules_cnt < NEXT_SCHEDULES_COUNT:
        # let's scrap another row
        # Take all minutes from next hour. Then add first 6 (or lower) to next_schedules dictionary.
        next_hour = current_hour + 1
        second_row_td_elements = soup.css.select(f"table[id=SM14] tr[id=sm14T{next_hour}] td")
        if second_row_td_elements:
            next_schedules[next_hour] = []
            while next_schedules_cnt < 6 and second_row_td_elements:
                td = second_row_td_elements.pop(0)
                minute = td.getText()
                if minute:
                    minute = int(minute)
                    next_schedules[next_hour].append(minute)
                    next_schedules_cnt += 1
    # print(next_schedules)
    return next_schedules


if __name__ == "__main__":
    TESTING = False

    get_next_departures(3, "rača", "Jungmannova")

    if TESTING:
        print("Start of testing.")
        assert get_line_stops_page_url(3) == "https://imhd.sk/ba/linka/3/bd807c807f847f7f827c82"
        assert get_line_stops_page_url(9) == "https://imhd.sk/ba/linka/9/bd807c807f847f7f887c88"
        assert get_line_stops_page_url(33) == "https://imhd.sk/ba/linka/33/bd807c807f847f82827c8282"
        assert get_line_stops_page_url(42) == "https://imhd.sk/ba/linka/42/bd807c807f847f83817c8381"
        assert get_line_stops_page_url(83) == "https://imhd.sk/ba/linka/83/bd807c807f847f87827c8782"
        assert get_line_stops_page_url(84) == "https://imhd.sk/ba/linka/84/bd807c807f847f87837c8783"

        assert get_line_schedules_url(3, "rača", "Jungmannova") == "https://imhd.sk/ba/cestovny-poriadok/linka/3/Jungmannova/smer-Ra%C4%8Da/bd807c807f847f7f827c8275c18075b680808775be7f75c97f75b3"
        assert get_line_schedules_url(3, "rača", "Farského") == "https://imhd.sk/ba/cestovny-poriadok/linka/3/Farsk%C3%A9ho/smer-Ra%C4%8Da/bd807c807f847f7f827c8275c18075b6858775be7f75c98075b3"
        assert get_line_schedules_url(84, "DÚBRAVKA, PRI KRÍŽI", "Dvory") == "https://imhd.sk/ba/cestovny-poriadok/linka/84/Dvory/smer-D%C3%BAbravka-Pri-kr%C3%AD%C5%BEi/bd807c807f847f87837c878375c17f75b6858375be7f75c98875b3"
        assert get_line_schedules_url(84, "DÚBRAVKA, PRI KRÍŽI", "Hodžovo nám.") == "https://imhd.sk/ba/cestovny-poriadok/linka/84/Hod%C5%BEovo-n%C3%A1m/smer-D%C3%BAbravka-Pri-kr%C3%AD%C5%BEi/bd807c807f847f87837c878375c17f75b6878275be7f75c9808175b3"
        assert get_line_schedules_url(31, "CINTORÍN SLÁVIČIE", "Kráľovské údolie") == "https://imhd.sk/ba/cestovny-poriadok/linka/31/Kr%C3%A1%C4%BEovsk%C3%A9-%C3%BAdolie/smer-Cintor%C3%ADn-Sl%C3%A1vi%C4%8Die/bd807c807f847f82807c828075c18075b681848075be7f75c98475b3"

        print("End of testing.")

