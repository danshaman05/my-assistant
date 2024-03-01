from datetime import datetime, timedelta
from workalendar.europe import Slovakia
from enum import Enum

class DayTypes(Enum):
    WORKING_DAY = 'working_day'
    FREE_DAY = 'free_day'
    SCHOOL_DAY = 'school_day'
    SCHOOL_HOLIDAY_DAY = 'school_holiday_day'


def _get_datetime_objects_between_2_dates(start_date: datetime, end_date: datetime):
    lst = []
    interval = timedelta(days=1)
    current_date = start_date
    while current_date <= end_date:
        lst.append(current_date)
        current_date += interval
    return lst


#Prazdniny 2024
_vianocne_first_day = datetime(2024, 1, 1)
_vianocne = [_vianocne_first_day + timedelta(days=x) for x in range(7)]

_jarne_first_day = datetime(2024, 3, 4)
_jarne = [_jarne_first_day + timedelta(days=x) for x in range(4)]

_velkonocne_first_day = datetime(2024, 3, 28)
_velkonocne_last_day = datetime(2024, 4, 2)
_velkonocne = _get_datetime_objects_between_2_dates(_velkonocne_first_day, _velkonocne_last_day)

_letne_first_day = datetime(2024, 7, 1)
_letne_last_day =  datetime(2024, 8, 31)
_letne = _get_datetime_objects_between_2_dates(_letne_first_day, _letne_last_day)

# all school holidays
_skolske_prazdniny = _vianocne + _jarne + _velkonocne + _letne

# Get current date but set it to midnight:
today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


def is_working_day():
    cal = Slovakia()
    return cal.is_working_day(today)

def is_school_holiday_day():
    return today in _skolske_prazdniny



"""Cele toto mozno nebude fungovat, lebo neviem ze ci linky DPB sa riadia iba podla letnych prazdnin, alebo aj podla
 velkonocnych napriklad. Zrejme tam to zavisi vzdy od jednotlivej linky - od pismenok pri casoch. Kvoli tomu by bolo 
 lepsie mozno fakt parsovat planovac cesty (https://imhd.sk/ba/planovac-cesty) a to tak, ze zadam jednu dalsiu zastavku danym smerom.
 
 Je zaujimave, ze napr. linka 39 ma poriadok len pre pracovne a volne dni.
 Linka 83 ma poriadok pre pracovne (skolsky rok) , pre pracovne dni (skol. prazdniny) a pre volne dni.
 Linka 88 a 93 to maju rovnako ako 83.
 
 Je tu vsak problem, ze Planovac trasy zobrazi vsetky linky, ktore idu na danu zastavku. Ja niekedy potrebujem ale len jednu linku - elektricku.
 
 Mozem to poriesit tak, ze na stranke budem mat odkazy:
 - elektricka 3 ( ukaze odchody z Jungmannovej)
 - smer Dubravka - pouzije IMHD Planovac - ukaze busy 83, 84 ku Jarke
 - smer autobusova stanica - pouzije IMHD Planovac - (linka 88, mozno aj elektricku ukaze)
 
 Ale najprv by som skusil uz moj prvy navrh - pouzitim "custom" calendara. Treba však zistiť, či pre každú linku máme rovnaké názvy tabuliek a či sedia s prázdninami (SM14, SM9, ...)
 
 
 Edited 21.2.2024:
 Trebalo by aj testovat nejako toto. Jedna moznost je nacitat pre danu linku cestu k jednej najblizsej zastavke 
 a porovnat s nasimi departures. Ma potom vyznam mat dva sposoby zistovania odchodov liniek? Mozno ma, 
 pokial z planovaca vieme parsnut len malo liniek.
 
Takto by som mohol spravit nejake testy, a tie by sa kazdy den spustali. Ak by nastal nejaky problem, tak na moj mail
by sa poslalo varovanie, ze planovac nefunguje dobre. Tiez by sa to zobrazilo na stranke.

Edited 12:50:
I have found out, that "planovac trasy" will show only 4 next connections. If we want to show more, we need to click on "Neskôr".
 """


