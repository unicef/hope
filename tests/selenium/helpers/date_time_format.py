from datetime import datetime


class FormatTime:
    def __init__(
        self,
        day: int = 0,
        month: int = 0,
        year: int = 0,
        hour: int = 0,
        minute: int = 0,
        time: datetime | None = None,
    ):
        self._datetime = time
        self.day = day
        self.month = month
        self.year = year
        self.hour = hour
        self.minute = minute
        if self.year != 0:
            self._datetime = datetime(self.year, self.month, self.day, self.hour, self.minute)

    @property
    def numerically_formatted_date(self) -> str:
        # date format YYYY-MM-DD
        return str(self._datetime.strftime("%Y-%m-%d"))

    @property
    def date_in_text_format(self) -> str:
        # date format -d Mon YYYY
        return str(self._datetime.strftime("%-d %b %Y"))
