from constants import IMHDLineType, IMHDLineDirection, IMHDLineDirectionAlias
from imhd_scraper import get_next_departures_from_schedules_table
import asyncio


class IMHDLine():
    def __init__(self, _id: int,
                 line_type: IMHDLineType,
                 direction: IMHDLineDirection,
                 direction_alias: IMHDLineDirectionAlias,
                 start_station: str,
                 data: dict):
        self._id = _id
        # FIXME: Nemaju nasledujuce atributy byt bez volania .value?
        self.type: str = line_type.value
        self.direction: str = direction.value
        self.direction_alias: str = direction_alias.value
        self.start_station: str = start_station
        self.data: dict[int, list[str]] = data
        # TODO spravit triedu SchedulesTable, ktora si ulozi celu tabulku (bude cacheovat) a budeme z nej volat metodu "get_next_departures()?

    @property
    def html_class(self):
        return f"{self.type}_{self._id}"

    def is_operating_today(self) -> bool:
        """Return True, if line is operating today, else False. E.g. line 84 is not operating at weekends."""
        return bool(self.data)
