from sqlalchemy import (
    DateTime,
    FunctionElement,
)
from sqlalchemy.ext.compiler import compiles


class NowPlusXDays(FunctionElement):
    type = DateTime()

    def __init__(self, days, *args):
        self.days = days
        super(NowPlusXDays, self).__init__(*args)


@compiles(NowPlusXDays, "postgresql")
def pg_now_plus_x_days(element, compiler, **kw):
    return f"NOW() + INTERVAL '{element.days} DAYS'"


@compiles(NowPlusXDays, "sqlite")
def sqlite_now_plus_x_days(element, compiler, **kw):
    return f"DATETIME('now', '+{element.days} days')"
