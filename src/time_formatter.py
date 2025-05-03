import logging
from datetime import datetime
from logging import LogRecord

import pytz  # type: ignore[import-untyped]


class LocalTimeFormatter(logging.Formatter):
    """Кастомный форматтер для использования местного времени в логах."""

    def __init__(self, fmt: None = None, datefmt: None = None, tz_name: str = 'UTC') -> None:
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.local_tz = pytz.timezone(tz_name)

    def formatTime(self, record: LogRecord, datefmt: str | None = None) -> str:  # noqa N802,
        # Получаем время записи в UTC
        utc_dt = datetime.utcfromtimestamp(record.created).replace(tzinfo=pytz.utc)
        # Конвертируем в местное время
        local_dt = utc_dt.astimezone(self.local_tz)

        # Форматируем время в соответствии с предоставленным форматом
        if datefmt:
            s = local_dt.strftime(datefmt)
        else:
            s = local_dt.strftime("%Y-%m-%d %H:%M:%S %Z%z")
        return s
