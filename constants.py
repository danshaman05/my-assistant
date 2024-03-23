from enum import Enum


class DayTypes(Enum):
    WORKING_DAY = 'working_day'
    FREE_DAY = 'free_day'
    SCHOOL_DAY = 'school_day'
    SCHOOL_HOLIDAY_DAY = 'school_holiday_day'


class IMHDVehicleType(Enum):
    BUS = 'bus'
    TRAM = 'tram'


class IMHDRouteDirection(Enum):
    DUBRAVKA = 'DÚBRAVKA, PRI KRÍŽI'
    RACA = 'Rača'
    AUTOBUSOVA = "AUTOBUSOVÁ STANICA CEZ PETRŽALKU"
    PETRZALKA_KUTLIKOVA = "PETRŽALKA, KUTLÍKOVA"
    PETRZALKA_OVSISTE = "PETRŽALKA, OVSIŠTE"


class IMHDRouteDirectionAlias(Enum):
    """Note, that these are not the exact directions of the lines, but our custom aliases"""
    DUBRAVKA = 'Dúbravka'
    RACA = 'Rača'
    AUTOBUSOVA = 'Autobusová stanica'
    PETRZALKA = "Petržalka"
