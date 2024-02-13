import requests
from bs4 import BeautifulSoup


def get_line_schedules_page(line: int, direction: str):
    """Get webpage where are schedules for particular line."""
    schedules_page_url = "https://imhd.sk/ba/cestovne-poriadky"
    r = requests.get(schedules_page_url)
    # print(r.content)
    soup = BeautifulSoup(r.content, features="lxml")

    # 3 rows - elektricky, trolejbusy, autobusy
    # linka = soup.find("a", class="", string="")


    linky = soup.css.select("a .Linka--lg")
    print(linky)

    line_url = None
    for l in linky:
        if l.get_text() == str(line):
            line_url = l.href
            break
    print(line_url)


    # linka = soup.find_all("a", { "string": str(line)})
    # print("linka:", linka)


# line = linka
def get_next_departures(line: int, direction: str):
    """return 5 next departures"""

    """staci v tabulke s id SM14 najst td, ktory ma class="next-departure. To je najblizsi cas odchodu.
    
    Ja to asi spravim tak, ze ziskam si do dvoch poli (ktore budu predstavovat dve hodiny - aktualnu a dalsiu) vsetky odchody.
    Potom vyberiem len tie, co su rovne, alebo vacsie ako next-departure odchod.
    """

    # TODO
    # first_departure =




if __name__ == "__main__":
    get_line_schedules_page(3, "Rača")
