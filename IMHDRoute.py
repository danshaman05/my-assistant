from constants import IMHDVehicleType, IMHDRouteDirection, IMHDRouteDirectionAlias


class IMHDRoute():
    def __init__(self, id_number: int,
                 vehicle_type: IMHDVehicleType,
                 direction: IMHDRouteDirection,
                 direction_alias: IMHDRouteDirectionAlias,
                 start_station: str,
                 data: None | dict = None):
        self.id_number = id_number
        # FIXME: Nemaju nasledujuce atributy byt bez volania .value?
        self.type: str = vehicle_type.value
        self.direction: str = direction.value
        self.direction_alias: str = direction_alias.value
        self.start_station: str = start_station
        self.data: dict[int, list[str]] | None = data
        # TODO spravit triedu SchedulesTable, ktora si ulozi celu tabulku (bude cacheovat) a budeme z nej volat metodu "get_next_departures()?

    @property
    def identifier(self):
        return f"{self.type}_{self.id_number}"

    def is_operating_today(self) -> bool:
        """Return True, if line is operating today, else False. E.g. line 84 is not operating at weekends."""
        return bool(self.data)

    def set_data(self, data: dict):
        self.data = data
