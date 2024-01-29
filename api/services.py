import logging as _logging

import datetime as _dt
import calendar as _cal
import locale as _lc
import time as _t
import sqlite3 as _sql3
import psycopg2 as _psql
import psycopg2.extras as _psqlextras
import fastapi as _fastapi
import json as _json
import sqlalchemy.orm as _orm
import sqlalchemy.sql.expression as _expression


import auth as _auth
import settings as _settings
import functions.fn as _fn
import models as _models
import schemas as _schemas
import database as _database
import functions.rfc as _rfc

import models as _models
import schemas as _schemas
import datetime as _dt
import database as _database
import functions.fn as _fn
import auth as _auth
import settings as _settings
import sqlalchemy.orm as _orm
import jwt as _jwt
import requests as _requests
import pandas as pd
from array import array
from IPython.display import display
import ssl
import socket
from cryptography import x509
from cryptography.hazmat.backends import default_backend

_requests.packages.urllib3.disable_warnings()


RETURN_DEFAULT_ROWS = _settings.RETURN_DEFAULT_ROWS
RETURN_MAX_ROWS = _settings.RETURN_MAX_ROWS

_logger = _logging.getLogger(__name__)  # the __name__ resolve to "api.services"


# *************************************************************************************************************************************
# SECCION: DATABASE
# *************************************************************************************************************************************


def drop_db():
    return _database.Base.metadata.drop_all(bind=_database.engine)


# *************************************************************************************************************************************


def create_db():
    return _database.Base.metadata.create_all(bind=_database.engine)


# *************************************************************************************************************************************


def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# *************************************************************************************************************************************
# SECCION: Torneos
# *************************************************************************************************************************************

def get_torneos(
    db: _orm.Session,
    token: str,
    skip: int = 0,
    limit: int = RETURN_DEFAULT_ROWS,
):
    skip = _fn.is_null(skip, 0)
    limit = _fn.is_null(limit, RETURN_DEFAULT_ROWS)

    if (limit > RETURN_MAX_ROWS) and (
        _auth.token_decode(token)["roles"].upper() != "ADMINISTRATOR"
    ):
        _logger.warning(f"Solicitud maxima de registros excedida [{limit}]")
        limit = RETURN_DEFAULT_ROWS

    results = (
        db.query(_models.Torneos)
        .order_by(_models.Torneos.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return results

