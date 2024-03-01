import requests
from bs4 import BeautifulSoup
from datetime import datetime

import calendar_calculator
from SchedulesTable import SchedulesTable

IMHD_URL_PREFIX = "https://imhd.sk"
SCHEDULES_PAGE_URL = "https://imhd.sk/ba/cestovne-poriadky"
SCHEDULES_PAGE_URL_OFFLINE = "/home/daniel/PycharmProjects/My_assistant/imhd_offline_pages/cestovne poriadky/ba/cestovne-poriadky.html"

""" NEXT_SCHEDULES_COUNT sets how much next schedules we want to find out. Note, that the programme will look 
for schedules in this and the next hour only. Therefore, the number of schedules that programme outputs may be less than this number."""
NEXT_SCHEDULES_COUNT = 6

# EN/SK Dictionary:
# line = linka mestskej hromadnej dopravy (Bratislava)


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


def get_css_selector(table_id: str, departure_hour ):
    return f"table[id={table_id}] tr[id={table_id.lower()}T{departure_hour}] td"


def get_next_departures_from_schedules_table(line: int, direction: str, stop: str) -> dict:
    """return a dictionary, where keys are hours (current and next), and values are minutes - departures"""
    """
    Ziskam si do dvoch poli (ktore budu predstavovat dve hodiny - aktualnu a dalsiu) vsetky odchody.
    Potom vyberiem 6 (konstanta NEXT_SCHEDULES_COUNT) takych, co su rovne, alebo vacsie ako next-departure odchod.
    """
    url = get_line_schedules_url(line, direction, stop)
    soup = get_soup(url)

    now = datetime.now()
    current_hour: int = now.hour
    current_minute: int = now.minute

    # div with id "myTabContent" contains tables
    tables = soup.css.select("div[id=myTabContent] div[id^=SM]")
    print("len of tables: " + str(len(tables)))

    tables = [SchedulesTable(t.get('id'), t.h2.getText(), t) for t in tables]

    table_id = None
    for table in tables:
        applicable_days = table.get_applicable_days()
        if calendar_calculator.is_working_day():
            if calendar_calculator.DayTypes.WORKING_DAY in applicable_days:
                table_id = table._id
        elif calendar_calculator.DayTypes.FREE_DAY in applicable_days:
                table_id = table._id
        if calendar_calculator.is_school_holiday_day():
            if calendar_calculator.DayTypes.SCHOOL_HOLIDAY_DAY in applicable_days:
                table_id = table._id
        elif calendar_calculator.DayTypes.SCHOOL_DAY in applicable_days:
            table_id = table.id


    if table_id is None:
        print('table_id is None')
        return {}
    else:
        print("table_id:" + table_id)

    print()

    table_id_short = table_id.replace('-', '')  # get rid of a hyphen

    css_selector = get_css_selector(table_id_short, current_hour)
    first_row_td_elements = soup.css.select(css_selector)
    first_row_lst = [td.getText() for td in first_row_td_elements if td.getText()]   # TODO oddelime cisla od posledneho charu? A ulozime sem tuples? V tom pripade by sme j mohli nejak zvyraznit

    # next_schedules is a dict, where key are hours (current and next), and values are minutes
    next_schedules = {current_hour: []}

    """Do next_schedules sa ako values davaju stringy. Staci najst index toho, ktory je najblizsie k aktualnemu casu, 
    a potom vsetky prvky zo zonamu od toho indexu vyssie pridat."""
    for s in first_row_lst:
        if s:
            # some departures have specific symbol (route for this line is different)
            last_char = ''
            if s[-1].isalpha():
                last_char = s[-1]
                s = s[:-1]
            s = int(s)
            if s <= current_minute:
                continue
            else:
                s = str(s) + last_char
                next_schedules[current_hour].append(s)

    next_schedules_cnt = len(next_schedules[current_hour])   #count all added td elements
    if next_schedules_cnt < NEXT_SCHEDULES_COUNT:
        # let's scrap another row. Take all schedules from next hour. Then add first 6 (or less) to next_schedules dictionary.
        next_hour: int = current_hour + 1
        css_selector = get_css_selector(table_id_short, next_hour)
        second_row_td_elements = soup.css.select(css_selector)
        second_row_lst = [td.getText() for td in second_row_td_elements if td.getText()]
        if second_row_lst:
            next_schedules[next_hour] = []
            while next_schedules_cnt < 6 and second_row_lst:
                s = second_row_lst.pop(0)
                if s:
                    next_schedules[next_hour].append(s)
                    next_schedules_cnt += 1
    return next_schedules


if __name__ == "__main__":
    TESTING = True

    if TESTING:
        print("Start of testing.")
        # assert get_line_stops_page_url(3) == "https://imhd.sk/ba/linka/3/bd807c807f847f7f827c82"
        # assert get_line_stops_page_url(9) == "https://imhd.sk/ba/linka/9/bd807c807f847f7f887c88"
        # assert get_line_stops_page_url(33) == "https://imhd.sk/ba/linka/33/bd807c807f847f82827c8282"
        # assert get_line_stops_page_url(42) == "https://imhd.sk/ba/linka/42/bd807c807f847f83817c8381"
        # assert get_line_stops_page_url(83) == "https://imhd.sk/ba/linka/83/bd807c807f847f87827c8782"
        # assert get_line_stops_page_url(84) == "https://imhd.sk/ba/linka/84/bd807c807f847f87837c8783"
        #
        # assert get_line_schedules_url(3, "rača", "Jungmannova") == "https://imhd.sk/ba/cestovny-poriadok/linka/3/Jungmannova/smer-Ra%C4%8Da/bd807c807f847f7f827c8275c18075b680808775be7f75c97f75b3"
        # assert get_line_schedules_url(3, "rača", "Farského") == "https://imhd.sk/ba/cestovny-poriadok/linka/3/Farsk%C3%A9ho/smer-Ra%C4%8Da/bd807c807f847f7f827c8275c18075b6858775be7f75c98075b3"
        # assert get_line_schedules_url(84, "DÚBRAVKA, PRI KRÍŽI", "Dvory") == "https://imhd.sk/ba/cestovny-poriadok/linka/84/Dvory/smer-D%C3%BAbravka-Pri-kr%C3%AD%C5%BEi/bd807c807f847f87837c878375c17f75b6858375be7f75c98875b3"
        # assert get_line_schedules_url(84, "DÚBRAVKA, PRI KRÍŽI", "Hodžovo nám.") == "https://imhd.sk/ba/cestovny-poriadok/linka/84/Hod%C5%BEovo-n%C3%A1m/smer-D%C3%BAbravka-Pri-kr%C3%AD%C5%BEi/bd807c807f847f87837c878375c17f75b6878275be7f75c9808175b3"
        # assert get_line_schedules_url(31, "CINTORÍN SLÁVIČIE", "Kráľovské údolie") == "https://imhd.sk/ba/cestovny-poriadok/linka/31/Kr%C3%A1%C4%BEovsk%C3%A9-%C3%BAdolie/smer-Cintor%C3%ADn-Sl%C3%A1vi%C4%8Die/bd807c807f847f82807c828075c18075b681848075be7f75c98475b3"


        # Note: I cannot test get_next_departures(), because we have different schedules for different days (workdays, school holidays, etc.)
        # It needs to be tested manually.


        print("Linka 3:")
        print(get_next_departures_from_schedules_table(3, "rača", "Jungmannova"))
        # print(get_next_departures_from_schedules_table(3, 'rača', 'centrum'))
        # print("Linka 41:")
        # print(get_next_departures_from_schedules_table(41, 'Hlavná stanica', 'Na hrebienku'))


        # 84 je otestovana a funguje
        # print("Linka 84:")
        # print(get_next_departures_from_schedules_table(84, 'Petržalka, Ovsište', 'ŠVantnerova'))

        print("End of testing.")



