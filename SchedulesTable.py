from bs4 import element
from calendar_calculator import DayTypes


class SchedulesTable:
    def __init__(self, _id:str, title:str, content: element.Tag ):
        """TODO chceme tu mat atribut applicable_days?"""
        self._id = _id
        self.title = title
        self.content = content
        # list of day types for we can use this table. E.g.: ['']
        self.applicable_days: list[DayTypes] = self.get_applicable_days()


    def get_applicable_days(self):
        result_list = []
        title_lst = [type_raw.lower() for type_raw in self.title.split(',')]
        if 'pracovné dni' in title_lst:
            result_list.append(DayTypes.WORKING_DAY)
        if 'voľné dni' in title_lst:
            result_list.append(DayTypes.FREE_DAY)
        if 'školský rok' in title_lst:
            result_list.append(DayTypes.SCHOOL_DAY)
        if 'školské prázdniny' in title_lst:
            result_list.append(DayTypes.SCHOOL_HOLIDAY_DAY)
        return result_list