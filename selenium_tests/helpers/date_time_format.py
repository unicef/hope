from datetime import datetime


class FormatTime:
    def __init__(self, day: int, month: int, year: int, hour: int = 0, minute: int = 0):
        self.day = day
        self.month = month
        self.year = year
        self.hour = hour
        self.minute = minute
        self.datetime = datetime(year, month, day, hour, minute)

    @property
    def numerically_formatted_date(self) -> str:
        # date format YYYY-MM-DD
        return str(self.datetime.strftime('%Y-%m-%d'))

    @property
    def date_in_text_format(self) -> str:
        # date format -d Mon YYYY
        return str(self.datetime.strftime('%-d %b %Y'))
