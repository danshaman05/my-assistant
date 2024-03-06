from enum import Enum

class IMHDLineType(Enum):
    BUS = 'bus'
    TRAM = 'tram'

class IMHDLineDirection(Enum):
    DUBRAVKA = 'DÚBRAVKA, PRI KRÍŽI'
    RACA = 'Rača'
    AUTOBUSOVA = "AUTOBUSOVÁ STANICA CEZ PETRŽALKU"


class IMHDLineDirectionAlias(Enum):
    """Note, that these are not the exact directions of the lines, but our custom aliases"""
    DUBRAVKA = 'Dúbravka'
    RACA = 'Rača'
    AUTOBUSOVA = 'Autobusová stanica'
