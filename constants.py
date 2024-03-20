from enum import Enum

class IMHDVehicleType(Enum):
    BUS = 'bus'
    TRAM = 'tram'

class IMHDRouteDirection(Enum):
    DUBRAVKA = 'DÚBRAVKA, PRI KRÍŽI'
    RACA = 'Rača'
    AUTOBUSOVA = "AUTOBUSOVÁ STANICA CEZ PETRŽALKU"


class IMHDRouteDirectionAlias(Enum):
    """Note, that these are not the exact directions of the lines, but our custom aliases"""
    DUBRAVKA = 'Dúbravka'
    RACA = 'Rača'
    AUTOBUSOVA = 'Autobusová stanica'

