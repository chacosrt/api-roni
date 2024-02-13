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

# *************************************************************************************************************************************


def get_torneos_por_id(db: _orm.Session, token: str, id: int):
    actividad = db.query(_models.Torneos).filter(_models.Torneos.id == id).first()
    return actividad

# *************************************************************************************************************************************


def create_torneo(
    db: _orm.Session,
    torneo: _schemas.TorneosCreate,
    token: str,
):

    sub = _auth.token_claim(token, "sub")

    db_torneos = _models.Torneos(
        nombre_torneo=_fn.format_nombre_propio(torneo.nombre_torneo),
        lugar=_fn.clean_string(torneo.lugar),
        temporada=_fn.clean_string(torneo.temporada),
        modalidad=_fn.clean_string(torneo.modalidad),
        dias=_fn.clean_string(torneo.dias),
        horarios=_fn.clean_string(torneo.horarios),
        fecha_inicio=_fn.format_date(torneo.fecha_inicio),
        fecha_fin=_fn.format_date(torneo.fecha_fin),
        categoria=_fn.clean_string(torneo.categoria),
        img=_fn.clean_string(torneo.img),  
    )

    db_torneos.estatus = 1

    db_torneos.creado_por = _fn.clean_string(sub)
    db_torneos.creado_el = _dt.datetime.now()
    db_torneos.modificado_por = _fn.clean_string(sub)
    db_torneos.modificado_el = _dt.datetime.now()

    db.add(db_torneos)
    db.commit()
    db.refresh(db_torneos)

    return db_torneos

# *************************************************************************************************************************************


def update_torneo(
    db: _orm.Session,
    token: str,
    db_torneos: _models.Torneos,
    torneo: _schemas.TorneosCreate,
):
    sub = _auth.token_claim(token, "sub")

    """ unidades =float(actividad.unidades)
    subtotal = float(actividad.subtotal)
    descuento = float(actividad.descuento)
    subtotal_neto = "{:.2f}".format(float(actividad.subtotal)-float(actividad.descuento))
    otros_conceptos = _fn.is_null(actividad.otros_conceptos, 0)
    total_previo_impuesto =  "{:.2f}".format(float(subtotal_neto)+float(otros_conceptos))


    impuesto =  "{:.2f}".format(float(actividad.impuesto))


    total =  "{:.2f}".format(float(total_previo_impuesto)+float(impuesto)) """

    # db_actividades.clave = _fn.clean_string(actividad.clave).upper()
    db_torneos.nombre_torneo=_fn.format_nombre_propio(torneo.nombre_torneo)
    db_torneos.lugar=_fn.clean_string(torneo.lugar)
    db_torneos.temporada=_fn.clean_string(torneo.temporada)
    db_torneos.modalidad=_fn.clean_string(torneo.modalidad)
    db_torneos.dias=_fn.clean_string(torneo.dias)
    db_torneos.horarios=_fn.clean_string(torneo.horarios)
    db_torneos.fecha_inicio=_fn.format_date(torneo.fecha_inicio)
    db_torneos.fecha_fin=_fn.format_date(torneo.fecha_fin)
    db_torneos.categoria=_fn.clean_string(torneo.categoria)
    db_torneos.img=_fn.clean_string(torneo.img)
    db_torneos.estatus  =  _fn.is_null(torneo.estatus,0)
    
   
    db_torneos.modificado_por = _fn.clean_string(sub)
    db_torneos.modificado_el = _dt.datetime.now()

    db.commit()
    db.refresh(db_torneos)

    return db_torneos

# *************************************************************************************************************************************


def delete_torneo(db: _orm.Session, token: str, id: int):

    torneo = get_torneos_por_id(db=db, token=token, id=id)
    
    db.query(_models.Torneos).filter(_models.Torneos.id == id).delete()
    db.commit()

# *************************************************************************************************************************************
# SECCION: EQUIPOS
# *************************************************************************************************************************************

def get_equipos(
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
        db.query(_models.Equipos)
        .order_by(_models.Equipos.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return results

# *************************************************************************************************************************************


def get_equipos_por_id(db: _orm.Session, token: str, id: int):
    equipo = db.query(_models.Equipos).filter(_models.Equipos.id == id).first()
    return equipo

# *************************************************************************************************************************************


def get_equipos_por_id_torneo(db: _orm.Session, token: str, id: int):
    equipo = db.query(_models.Equipos).filter(_models.Equipos.liga == id).all()
    return equipo

# *************************************************************************************************************************************


def create_equipo(
    db: _orm.Session,
    equipo: _schemas.EquiposCreate,
    token: str,
):

    sub = _auth.token_claim(token, "sub")

    db_equipos = _models.Equipos(
        nombre=_fn.format_nombre_propio(equipo.nombre),
        liga=_fn.is_null(equipo.liga,0),
        delegado=_fn.clean_string(equipo.delegado),
        img_equipo=_fn.clean_string(equipo.img_equipo),  
    )

    db_equipos.estatus = 1

    db_equipos.creado_por = _fn.clean_string(sub)
    db_equipos.creado_el = _dt.datetime.now()
    db_equipos.modificado_por = _fn.clean_string(sub)
    db_equipos.modificado_el = _dt.datetime.now()

    db.add(db_equipos)
    db.commit()
    db.refresh(db_equipos)

    return db_equipos

# *************************************************************************************************************************************


def update_equipo(
    db: _orm.Session,
    token: str,
    db_equipos: _models.Equipos,
    equipo: _schemas.EquiposCreate,
):
    sub = _auth.token_claim(token, "sub")

    # db_actividades.clave = _fn.clean_string(actividad.clave).upper()
    db_equipos.nombre=_fn.format_nombre_propio(equipo.nombre)
    db_equipos.liga=_fn.is_null(equipo.liga,0)
    db_equipos.delegado=_fn.clean_string(equipo.delegado)
    db_equipos.img_equipo=_fn.clean_string(equipo.img_equipo)
    db_equipos.estatus  =  _fn.is_null(equipo.estatus,0)
   
    db_equipos.modificado_por = _fn.clean_string(sub)
    db_equipos.modificado_el = _dt.datetime.now()

    db.commit()
    db.refresh(db_equipos)

    return db_equipos

# *************************************************************************************************************************************


def delete_equipo(db: _orm.Session, token: str, id: int):

    torneo = get_equipos_por_id(db=db, token=token, id=id)
    
    db.query(_models.Equipos).filter(_models.Equipos.id == id).delete()
    db.commit()

# *************************************************************************************************************************************
# SECCION: JUGADORES
# *************************************************************************************************************************************

def get_jugadores(
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
        db.query(_models.Jugadores)
        .order_by(_models.Jugadores.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return results

# *************************************************************************************************************************************


def get_jugadores_por_id(db: _orm.Session, token: str, id: int):
    jugador = db.query(_models.Jugadores).filter(_models.Jugadores.id == id).first()
    return jugador

# *************************************************************************************************************************************


def create_jugador(
    db: _orm.Session,
    jugador: _schemas.JugadoresCreate,
    token: str,
):

    sub = _auth.token_claim(token, "sub")

    db_jugador = _models.Jugadores(
        nombre = _fn.format_nombre_propio(jugador.nombre),
        ap_paterno = _fn.format_nombre_propio(jugador.ap_paterno),
        ap_materno = _fn.format_nombre_propio(jugador.ap_materno),
        edad  =  _fn.is_null(jugador.edad,0),
        liga  =  _fn.is_null(jugador.liga,0),
        dorsal  =   _fn.is_null(jugador.edad,0),
        expediente = _fn.clean_string(jugador.expediente),
        seccional = _fn.clean_string(jugador.seccional),
        direccion = _fn.clean_string(jugador.direccion),
        telefono = _fn.clean_string(jugador.telefono),
        img = _fn.clean_string(jugador.img),
        delegado = _fn.is_null(jugador.delegado,False),
        
    )

    db_jugador.estatus = 1

    db_jugador.creado_por = _fn.clean_string(sub)
    db_jugador.creado_el = _dt.datetime.now()
    db_jugador.modificado_por = _fn.clean_string(sub)
    db_jugador.modificado_el = _dt.datetime.now()

    db.add(db_jugador)
    db.commit()
    db.refresh(db_jugador)

    return db_jugador

# *************************************************************************************************************************************


def update_jugador(
    db: _orm.Session,
    token: str,
    db_jugador: _models.Jugadores,
    jugador: _schemas.JugadoresCreate,
):
    sub = _auth.token_claim(token, "sub")

    # db_actividades.clave = _fn.clean_string(actividad.clave).upper()
    db_jugador.nombre = _fn.format_nombre_propio(jugador.nombre)
    db_jugador.ap_paterno = _fn.format_nombre_propio(jugador.ap_paterno)
    db_jugador.ap_materno = _fn.format_nombre_propio(jugador.ap_materno)
    db_jugador.edad  =  _fn.is_null(jugador.edad,0)
    db_jugador.liga  =  _fn.is_null(jugador.liga,0)
    db_jugador.dorsal  =   _fn.is_null(jugador.edad,0)
    db_jugador.expediente = _fn.clean_string(jugador.expediente)
    db_jugador.seccional = _fn.clean_string(jugador.seccional)
    db_jugador.direccion = _fn.clean_string(jugador.direccion)
    db_jugador.telefono = _fn.clean_string(jugador.telefono)
    db_jugador.img = _fn.clean_string(jugador.img)
    db_jugador.delegado = _fn.is_null(jugador.delegado,False)
    db_jugador.estatus  =  _fn.is_null(jugador.estatus,0)
   
    db_jugador.modificado_por = _fn.clean_string(sub)
    db_jugador.modificado_el = _dt.datetime.now()

    db.commit()
    db.refresh(db_jugador)

    return db_jugador

# *************************************************************************************************************************************


def delete_jugador(db: _orm.Session, token: str, id: int):

    torneo = get_jugadores_por_id(db=db, token=token, id=id)
    
    db.query(_models.Jugadores).filter(_models.Jugadores.id == id).delete()
    db.commit()