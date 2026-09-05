from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime, func

Base = declarative_base()


def enum_values(enum_cls):
    """values_callable for SQLAlchemy Enum columns.

    Persist enum *values* ("patient", "match_it") instead of member names
    ("PATIENT", "MATCH_IT") so Postgres native enums match the migration and
    the JSON API contract. Without this, native PG enums reject inserts.
    """
    return [e.value for e in enum_cls]
