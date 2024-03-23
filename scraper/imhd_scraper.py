import asyncio

from bs4 import BeautifulSoup
from datetime import datetime
from pytz import timezone
import aiohttp
import json

import constants
import calendar_calculator
from IMHDRoute import IMHDRoute
from SchedulesTable import SchedulesTable
from scraper.errors import CriticalScraperError

IMHD_URL_PREFIX = "https://imhd.sk"
SCHEDULES_PAGE_URL = "https://imhd.sk/ba/cestovne-poriadky"
SCHEDULES_PAGE_URL_OFFLINE = "/home/daniel/PycharmProjects/My_assistant/imhd_offline_pages/cestovne poriadky/ba/cestovne-poriadky.html"
CACHED_LINKS_FILE = 'scraper/cached_links.json'

NEXT_SCHEDULES_MAX_COUNT = 6
"""NEXT_SCHEDULES_COUNT sets how much next schedules we want to find out. Note, that the programme will look 
for schedules in this and the next hour only. Therefore, the number of schedules that programme outputs may be less than this number."""

# EN/SK Dictionary:
# route = linka mestskej hromadnej dopravy (Bratislava)


async def _get_soup(session: aiohttp.ClientSession, url) -> BeautifulSoup:
    try:
        async with session.get(url) as response:
            if response.status == 200:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')
                return soup
            else:
                raise CriticalScraperError(f"Error: Bad response. URL: {url}")
    except aiohttp.ClientError as e:
        # Handle non-existent page
        raise CriticalScraperError(f"Error: An error occurred while fetching the page. Exception: {e}. URL: {url}")


def get_cached_link(*path_args: str) -> str | None:
    """Return cached link. If there is no link in file, return None."""
    if path_args[0] is None:
        raise CriticalScraperError("First argument cannot be None.")
    cached_links_dict = get_cached_links_dictionary()
    if not cached_links_dict:
        return None
    data = cached_links_dict
    for path_element in path_args:
        data = data.get(path_element, None)
        if not data:
            return None
    return data


def get_cached_links_dictionary() -> dict | None:
    with open(CACHED_LINKS_FILE, 'r') as file:
        d = json.load(file)
        if not d:
            return {}
        return d


def write_link_into_cache_file(link: str, *path_args: str):
    """Writes link in to cache file."""
    result_dict = get_cached_links_dictionary()

    subdict = result_dict
    for element in path_args[:-1]:
        if element not in subdict:
            subdict[element] = {}
        subdict = subdict[element]
    subdict[path_args[-1]] = link
    with open(CACHED_LINKS_FILE, 'w') as file:
        json.dump(result_dict, file, indent=4)



async def _get_route_stops_page_url(session: aiohttp.ClientSession, route: int):
    """For a given route get its stops webpage URL (stops for both directions)."""
    # try to get link from cached_links.json file:
    link = get_cached_link("route_stops_page", str(route))
    if link:
        return link

    soup = await _get_soup(session, SCHEDULES_PAGE_URL)
    routes = soup.css.select("a.Linka--lg")
    if not routes:
        raise CriticalScraperError("Error. Cannot get links of routes.")
    line_url = None
    for l in routes:
        if l.text == str(route):
            line_url = l['href']
            break
    link = IMHD_URL_PREFIX + line_url
    write_link_into_cache_file(link, "route_stops_page", str(route))
    return link

async def _get_route_schedules_url(session: aiohttp.ClientSession, route: int, direction: str, stop: str):
    """ 
    :param route: e.g. 3,
    :param direction: e.g. 'rača',
    :param stop: 'Jungmanova'
    """
    link = get_cached_link("route_schedules", str(route), direction, stop)
    if link:
        return link
    route_stops_page_url = await _get_route_stops_page_url(session, route)
    soup = await _get_soup(session, route_stops_page_url)

    list_of_elements = soup.css.select('div[class^="ModuleGroup-left"] div[class^="ModuleGroup-left"] h2[class^="Heading h5"]')
    if not list_of_elements:
        raise CriticalScraperError("Error: Cannot get list_of_elements.")
    left_direction = list_of_elements[0]

    # the webpage contains two columns, one for each direction
    column = "left" if left_direction.text.lower() == direction.lower() else "right"
    list_of_a_elements = soup.css.select(f'div[class^=ModuleGroup-left] div[class^=ModuleGroup-{column}] tbody td.w-100 a ')
    if not list_of_a_elements:
        raise CriticalScraperError("Error: Cannot get list_of_a_elements.")

    for a in list_of_a_elements:
        # first stop is different, it has a span as a child element
        route_name = a.span.getText() if a.span else a.getText()
        if route_name.lower() == stop.lower():
            link = IMHD_URL_PREFIX + a['href']
            write_link_into_cache_file(link, "route_schedules", str(route), direction, stop)
            return link
    raise ValueError("Your input is probably wrong. Check it, and if it is OK, contact a developer.")


def _get_css_selector_for_table_row(table_id: str, departure_hour) -> str:
    """Return CSS selector for particular schedules table id and hour."""
    return f"table[id={table_id}] tr[id={table_id.lower()}T{departure_hour}] td"


def select_table_for_today(tables_lst: list[SchedulesTable]) -> str | None:
    """Return None if there isn't any suitable table, else return table_id of selected table."""

    if not tables_lst:
        raise CriticalScraperError("List tables_lst cannot be empty!")
    tw = calendar_calculator.today_is_working_day()
    th = calendar_calculator.today_is_school_holiday_day()
    today_map = {
        constants.DayTypes.WORKING_DAY: tw,
        constants.DayTypes.FREE_DAY: not tw,
        constants.DayTypes.SCHOOL_HOLIDAY_DAY: th,
        constants.DayTypes.SCHOOL_DAY: not th,
    }
    for table in tables_lst:
        applicable_days = table.get_applicable_days()
        if today_map[applicable_days[0]]:
            if len(applicable_days) == 1:
                return table.table_id
            elif today_map[applicable_days[1]]:
                return table.table_id


async def set_next_departures_from_schedules_table(session: aiohttp.ClientSession, imhd_route_obj: IMHDRoute):
    """
    Return a dict, where keys are hours (current and next hour), and values are minutes - departures. Return empty dict if the route
    is not operating today."""
    """
    Ziskam si do dvoch poli (ktore budu predstavovat dve hodiny - aktualnu a dalsiu) vsetky odchody.
    Potom vyberiem 6 (konstanta NEXT_SCHEDULES_COUNT) takych, co su rovne, alebo vacsie ako next-departure odchod.
    """
    url = await _get_route_schedules_url(session, imhd_route_obj.id_number, imhd_route_obj.direction, imhd_route_obj.start_station)
    soup = await _get_soup(session, url)

    bratislava_timezone = timezone('Europe/Bratislava')
    now_utc = datetime.now()
    bratislava_now = now_utc.astimezone(bratislava_timezone)
    current_hour: int = bratislava_now.hour
    current_minute: int = bratislava_now.minute

    # div with id "myTabContent" contains tables
    tables = soup.css.select("div[id=myTabContent] div[id^=SM]")
    if not tables:
        raise CriticalScraperError("ERROR. Scraping failed. Cannot get tables.")
    tables = [SchedulesTable(t.get('id'), t.h2.getText(), t) for t in tables]
    table_id = select_table_for_today(tables)
    if table_id is None:
        return {}
    table_id_short = table_id.replace('-', '')  # get rid of a hyphen
    css_selector = _get_css_selector_for_table_row(table_id_short, current_hour)
    first_row_td_elements = soup.css.select(css_selector)
    first_row_lst = [td.getText() for td in first_row_td_elements if td.getText()]   # TODO oddelime cisla od posledneho charu? A ulozime sem tuples? V tom pripade by sme j mohli nejak zvyraznit

    # next_schedules is a dict, where key are hours (current and next), and values are minutes
    next_schedules = {current_hour: []}
    next_schedules_cnt = 0

    """Do next_schedules sa ako values davaju stringy. Staci najst index toho, ktory je najblizsie k aktualnemu casu, 
    a potom vsetky prvky zo zonamu od toho indexu vyssie pridat."""
    for s in first_row_lst:
        if s and next_schedules_cnt < NEXT_SCHEDULES_MAX_COUNT:
            # some departures have specific symbol (route for this line is different)
            last_char = ''
            if s[-1].isalpha():
                last_char = s[-1]
                s = s[:-1]
            s = int(s)
            if s <= current_minute:
                continue
            else:
                s = "{:02d}".format(s) + last_char
                next_schedules[current_hour].append(s)
                next_schedules_cnt += 1

    next_schedules_cnt = len(next_schedules[current_hour])   #count all added td elements
    if next_schedules_cnt < NEXT_SCHEDULES_MAX_COUNT:
        # let's scrap another row. Take all schedules from next hour. Then add first 6 (or less) to next_schedules dictionary.
        next_hour: int = current_hour + 1
        css_selector = _get_css_selector_for_table_row(table_id_short, next_hour)
        second_row_td_elements = soup.css.select(css_selector)
        second_row_lst = [td.getText() for td in second_row_td_elements if td.getText()]
        if second_row_lst:
            next_schedules[next_hour] = []
            while next_schedules_cnt < 6 and second_row_lst:
                s = second_row_lst.pop(0)
                if s:
                    next_schedules[next_hour].append(s)
                    next_schedules_cnt += 1

    imhd_route_obj.set_data(next_schedules)


async def set_next_departures_for_each_object(dict_of_imhdline_objects: dict[tuple[int, constants.IMHDRouteDirectionAlias], IMHDRoute]):
    # asynchronously scrap each IMHDLine object from imhd.sk
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(set_next_departures_from_schedules_table(session, obj)) for obj in dict_of_imhdline_objects.values()]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    TESTING = False

    if TESTING:
        print("Start of testing.")
        # assert _get_line_stops_page_url(3) == "https://imhd.sk/ba/linka/3/bd807c807f847f7f827c82"
        # assert _get_line_stops_page_url(9) == "https://imhd.sk/ba/linka/9/bd807c807f847f7f887c88"
        # assert _get_line_stops_page_url(33) == "https://imhd.sk/ba/linka/33/bd807c807f847f82827c8282"
        # assert _get_line_stops_page_url(42) == "https://imhd.sk/ba/linka/42/bd807c807f847f83817c8381"
        # assert _get_line_stops_page_url(83) == "https://imhd.sk/ba/linka/83/bd807c807f847f87827c8782"
        # assert _get_line_stops_page_url(84) == "https://imhd.sk/ba/linka/84/bd807c807f847f87837c8783"
        #
        # assert _get_line_schedules_url(3, "rača", "Jungmannova") == "https://imhd.sk/ba/cestovny-poriadok/linka/3/Jungmannova/smer-Ra%C4%8Da/bd807c807f847f7f827c8275c18075b680808775be7f75c97f75b3"
        # assert _get_line_schedules_url(3, "rača", "Farského") == "https://imhd.sk/ba/cestovny-poriadok/linka/3/Farsk%C3%A9ho/smer-Ra%C4%8Da/bd807c807f847f7f827c8275c18075b6858775be7f75c98075b3"
        # assert _get_line_schedules_url(84, "DÚBRAVKA, PRI KRÍŽI", "Dvory") == "https://imhd.sk/ba/cestovny-poriadok/linka/84/Dvory/smer-D%C3%BAbravka-Pri-kr%C3%AD%C5%BEi/bd807c807f847f87837c878375c17f75b6858375be7f75c98875b3"
        # assert _get_line_schedules_url(84, "DÚBRAVKA, PRI KRÍŽI", "Hodžovo nám.") == "https://imhd.sk/ba/cestovny-poriadok/linka/84/Hod%C5%BEovo-n%C3%A1m/smer-D%C3%BAbravka-Pri-kr%C3%AD%C5%BEi/bd807c807f847f87837c878375c17f75b6878275be7f75c9808175b3"
        # assert _get_line_schedules_url(31, "CINTORÍN SLÁVIČIE", "Kráľovské údolie") == "https://imhd.sk/ba/cestovny-poriadok/linka/31/Kr%C3%A1%C4%BEovsk%C3%A9-%C3%BAdolie/smer-Cintor%C3%ADn-Sl%C3%A1vi%C4%8Die/bd807c807f847f82807c828075c18075b681848075be7f75c98475b3"


        # Note: I cannot test get_next_departures(), because we have different schedules for different days (workdays, school holidays, etc.)
        # It needs to be tested manually.


        # print("Linka 3:")
        # print(set_next_departures_from_schedules_table(3, "rača", "Jungmannova"))
        # print(get_next_departures_from_schedules_table(3, 'rača', 'centrum'))
        # print("Linka 41:")
        # print(get_next_departures_from_schedules_table(41, 'Hlavná stanica', 'Na hrebienku'))


        # 84 je otestovana a funguje
        # print("Linka 84:")
        # print(get_next_departures_from_schedules_table(84, 'Petržalka, Ovsište', 'ŠVantnerova'))

        # print(get_cached_links_dictionary())
        # write_link_into_cache_file("imhd.sk", "hlavny")
        # print(get_cached_links_dictionary())
        # write_link_into_cache_file("iny", "hlavny")
        # print(get_cached_links_dictionary())
        # write_link_into_cache_file("link.....", "route_stops_url", "key2")
        # print(get_cached_links_dictionary())

        # print(get_cached_link("route_stops_url", "key2"))

        print("End of testing.")
