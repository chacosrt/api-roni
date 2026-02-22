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
from sqlalchemy import func, or_


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


def activa_torneo(
    db: _orm.Session,
    id: int,
    token: str,
):

    sub = _auth.token_claim(token, "sub")

    torneo = db.query(_models.Torneos).filter(_models.Torneos.id == id).first()

    if (torneo.estatus == 1):

        torneo.estatus = 0

    else:

        torneo.estatus = 1

    
    torneo.modificado_por = _fn.clean_string(sub)
    torneo.modificado_el = _dt.datetime.now()

    
    db.commit()
    db.refresh(torneo)

    return torneo

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
    #db_torneos.estatus  =  _fn.is_null(torneo.estatus,0)
    
   
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


def nuevo_equipo(
    db: _orm.Session,
    equipo_jugador: _schemas.EquipoJugador,
    token: str,
):

    sub = _auth.token_claim(token, "sub")

    jugador = db.query(_models.Jugadores).filter(_models.Jugadores.id == equipo_jugador.id_jugador).first()

    jugador_exist = db.query(_models.Jugadores_Equipos).filter(_models.Jugadores_Equipos.id_jugador == equipo_jugador.id_jugador).first()   
    
    
    new_jugador = False
    
    
    db_jugador = _models.Jugadores(
        nombre = _fn.format_nombre_propio(jugador.nombre),
        ap_p = _fn.format_nombre_propio(jugador.ap_p),
        ap_m = _fn.format_nombre_propio(jugador.ap_m),
        edad  =  _fn.is_null(jugador.edad,0),
        liga  =  _fn.is_null(equipo_jugador.liga,0),
        equipo  =  _fn.is_null(equipo_jugador.equipo,0),
        dorsal  =   _fn.is_null(jugador.dorsal,0),
        expediente = _fn.clean_string(jugador.expediente),
        seccional = _fn.clean_string(jugador.seccional),
        direccion = _fn.clean_string(jugador.direccion),
        telefono = _fn.clean_string(jugador.telefono),
        img = _fn.clean_string(jugador.img),
        estatus = 1
        #delegado = _fn.is_null(jugador.delegado,False),
    
    )

    db_jugador.creado_por = _fn.clean_string(sub)
    db_jugador.creado_el = _dt.datetime.now()
    db_jugador.modificado_por = _fn.clean_string(sub)
    db_jugador.modificado_el = _dt.datetime.now()

    db_jugador_equipo = _models.Jugadores_Equipos(
            
        id_liga  =  _fn.is_null(db_jugador.liga,0),
        id_equipo  =  _fn.is_null(db_jugador.equipo,0),
        #id_jugador = db_jugador.id,
        
        
    )

    db_jugador_equipo.creado_por = _fn.clean_string(sub)
    db_jugador_equipo.creado_el = _dt.datetime.now()
    db_jugador_equipo.modificado_por = _fn.clean_string(sub)
    db_jugador_equipo.modificado_el = _dt.datetime.now()
        
    

    if(jugador_exist.id_padre != 0):

        jugador_padre = db.query(_models.Jugadores_Equipos).filter(_models.Jugadores_Equipos.id_jugador == jugador_exist.id_padre).filter(_models.Jugadores_Equipos.id_liga == equipo_jugador.liga).first()
        #db_jugador_equipo = jugador_padre.id_jugador

        if(jugador_padre == None):

            jugador_padre = db.query(_models.Jugadores_Equipos).filter(_models.Jugadores_Equipos.id_padre == jugador_exist.id_padre).filter(_models.Jugadores_Equipos.id_liga == equipo_jugador.liga).first()

            if(jugador_padre == None):
                new_jugador = True


                db.add(db_jugador)
                db.commit()
                db.refresh(db_jugador)         

                db_jugador_equipo.id_padre = jugador_exist.id_padre
                db_jugador.id
                db.add(db_jugador_equipo)
                db.commit()
                db.refresh(db_jugador_equipo)
    else:
            
            jugador_padre = db.query(_models.Jugadores_Equipos).filter(_models.Jugadores_Equipos.id_jugador == equipo_jugador.id_jugador).filter(_models.Jugadores_Equipos.id_liga == equipo_jugador.liga).first()
           

            if(jugador_padre == None):

                new_jugador = True
                db_jugador_equipo.id_padre = equipo_jugador.id_jugador

                db.add(db_jugador)
                db.commit()
                db.refresh(db_jugador)         

                db_jugador_equipo.id_jugador = db_jugador.id
                db.add(db_jugador_equipo)
                db.commit()
                db.refresh(db_jugador_equipo)

    return new_jugador

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


def get_jugadores_por_equipo_id(db: _orm.Session, token: str, id: int):
    jugador = db.query(_models.Jugadores).filter(_models.Jugadores.equipo == id).all()
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
        ap_p = _fn.format_nombre_propio(jugador.ap_p),
        ap_m = _fn.format_nombre_propio(jugador.ap_m),
        edad  =  _fn.is_null(jugador.edad,0),
        liga  =  _fn.is_null(jugador.liga,0),
        equipo  =  _fn.is_null(jugador.equipo,0),
        dorsal  =   _fn.is_null(jugador.dorsal,0),
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

    db_jugador_equipo = _models.Jugadores_Equipos(
        
        id_liga  =  _fn.is_null(jugador.liga,0),
        id_equipo  =  _fn.is_null(jugador.equipo,0),
        id_jugador = db_jugador.id
        
    )

    db_jugador_equipo.creado_por = _fn.clean_string(sub)
    db_jugador_equipo.creado_el = _dt.datetime.now()
    db_jugador_equipo.modificado_por = _fn.clean_string(sub)
    db_jugador_equipo.modificado_el = _dt.datetime.now()


    db.add(db_jugador_equipo)
    db.commit()
    db.refresh(db_jugador_equipo)

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
    db_jugador.ap_p = _fn.format_nombre_propio(jugador.ap_p)
    db_jugador.ap_m = _fn.format_nombre_propio(jugador.ap_m)
    db_jugador.edad  =  _fn.is_null(jugador.edad,0)
    db_jugador.liga  =  _fn.is_null(jugador.liga,0)
    db_jugador.equipo  =  _fn.is_null(jugador.equipo,0)
    db_jugador.dorsal  =   _fn.is_null(jugador.dorsal,0)
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

    db_jugador_equipo = db.query(_models.Jugadores_Equipos).filter(_models.Jugadores_Equipos.id_jugador == db_jugador.id).filter(_models.Jugadores_Equipos.id_liga == db_jugador.liga).first()
    db_jugador_equipo.id_liga = jugador.liga
    db_jugador_equipo.id_equipo = jugador.equipo

    db.commit()
    db.refresh(db_jugador_equipo)

    return db_jugador

# *************************************************************************************************************************************


def delete_jugador(db: _orm.Session, token: str, id: int):

    torneo = get_jugadores_por_id(db=db, token=token, id=id)

    db.query(_models.Jugadores_Equipos).filter(_models.Jugadores_Equipos.id_jugador == id).delete()
    db.commit()
    
    db.query(_models.Jugadores).filter(_models.Jugadores.id == id).delete()
    db.commit()


# *************************************************************************************************************************************
# SECCION: PARTIDOS
# *************************************************************************************************************************************

def get_partidos(
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
        db.query(_models.Partidos)
        .order_by(_models.Partidos.liga.asc())
        .limit(20)
        .offset(skip)        
        .all()
    )

    return results

# *************************************************************************************************************************************


def get_partidos_por_id(db: _orm.Session, token: str, id: int):
    partido = db.query(_models.Partidos).filter(_models.Partidos.id == id).first()
    return partido

# *************************************************************************************************************************************


def get_partidos_por_equipo_id(db: _orm.Session,
    token: str, 
    id: int,
    skip: int = 0,    
    limit: int = RETURN_DEFAULT_ROWS
):

    skip = _fn.is_null(skip, 0)
    limit = _fn.is_null(limit, RETURN_DEFAULT_ROWS)

    if (limit > RETURN_MAX_ROWS) and (
        _auth.token_decode(token)["roles"].upper() != "ADMINISTRATOR"
    ):
        _logger.warning(f"Solicitud maxima de registros excedida [{limit}]")
        limit = RETURN_DEFAULT_ROWS

    partido = db.query(_models.Partidos).filter((_models.Partidos.local == id) | (_models.Partidos.visitante == id)).order_by(_models.Partidos.id).all()
    return partido

# *************************************************************************************************************************************

def get_partidos_por_torneo(
    db: _orm.Session,
    token: str,
    id: int,
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
    
    torneo = db.query(_models.Torneos).filter(_models.Torneos.id == id).first()

    results = (
        db.query(_models.Partidos)
        .filter(_models.Partidos.liga == id)
        .filter(_models.Partidos.temporada == torneo.temporada)
        .order_by(_models.Partidos.id)
        .offset(skip)        
        .all()
    )

    return results

# *************************************************************************************************************************************

def get_partidos_por_jornada(
    db: _orm.Session,
    token: str,
    torneo: int,
    jornada: str,
    temporada: str,
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

    #torneo = db.query(_models.Torneos).filter(_models.Torneos.id == id).first()
    #temporada = torneo.temporada
    if torneo == 0:

        partidos = (
        db.query(_models.Partidos)        
        .filter(_models.Partidos.liga.in_([1,2]))          
        .filter(_models.Partidos.temporada == temporada)
        .filter(_models.Partidos.jornada == jornada)
        .order_by(_models.Partidos.liga.asc())   
        .all()
    )
        
    else:

        partidos = (
            db.query(_models.Partidos)        
            .filter(_models.Partidos.liga == torneo)
            .filter(_models.Partidos.temporada == temporada)
            .filter(_models.Partidos.jornada == jornada)
            .order_by(_models.Partidos.horario.asc())   
            .all()
        )

    
        


    return partidos


# *************************************************************************************************************************************


def create_partido(
    db: _orm.Session,
    partido: _schemas.PartidosCreate,
    token: str,
):

    sub = _auth.token_claim(token, "sub")
    ganador_partido = 0

    db_partido = _models.Partidos(
        fecha =_fn.format_date(partido.fecha),
        horario =_fn.clean_string(partido.horario),
        etapa = _fn.clean_string(partido.etapa),
        jornada = _fn.clean_string(partido.jornada),
        #temporada = _fn.clean_string(partido.etapa),
        campo =  _fn.is_null(partido.campo,0),
        liga  =  _fn.is_null(partido.liga,0),
        local  =  _fn.is_null(partido.local,0),
        visitante =  _fn.is_null(partido.visitante,0),
        goles_local  =  _fn.is_null(partido.goles_local,0),
        goles_visitante  =  _fn.is_null(partido.goles_visitante,0),
        #ganador =  _fn.is_null(partido.ganador,0),        
        observaciones = _fn.clean_string(partido.observaciones),
        
    )

    get_temporada = db.query(_models.Torneos).filter(_models.Torneos.id == partido.liga).first()

    if partido.estatus == 2 and partido.goles_local > partido.goles_visitante:

        ganador_partido = partido.local

    if partido.estatus == 2 and partido.goles_local < partido.goles_visitante:

        ganador_partido = partido.visitante

    if partido.estatus == 2 and partido.goles_local == partido.goles_visitante:

        ganador_partido = 0

    db_partido.estatus = partido.estatus
    db_partido.ganador = ganador_partido
    db_partido.temporada = get_temporada.temporada

    db_partido.creado_por = _fn.clean_string(sub)
    db_partido.creado_el = _dt.datetime.now()
    db_partido.modificado_por = _fn.clean_string(sub)
    db_partido.modificado_el = _dt.datetime.now()

    db.add(db_partido)
    db.commit()
    db.refresh(db_partido)

    #************ Seccion para insertar registro en tabla de posiciones ******************************************

    if partido.estatus == 2:

        pos_local = db.query(_models.Posiciones).filter(_models.Posiciones.liga==partido.liga).filter(_models.Posiciones.equipo==partido.local).filter(_models.Posiciones.temporada==get_temporada.temporada).first()

        pos_visitante = db.query(_models.Posiciones).filter(_models.Posiciones.liga==partido.liga).filter(_models.Posiciones.equipo==partido.visitante).filter(_models.Posiciones.temporada==get_temporada.temporada).first()

        
        
        if pos_local is None:   

            ganado = 0

            perdido = 0

            empatado = 0   

            puntos = 0

            if partido.goles_local > partido.goles_visitante:

                ganado = 1

                puntos = 3

            if partido.goles_local < partido.goles_visitante:

                perdido = 1

            if partido.goles_local == partido.goles_visitante:

                empatado = 1

                puntos = 1

            db_posicion = _models.Posiciones()

            db_posicion.temporada = get_temporada.temporada
            db_posicion.liga = _fn.is_null(partido.liga,0)
            db_posicion.equipo  = _fn.is_null(partido.local,0)
            db_posicion.juegos_jugados  =  1
            db_posicion.juegos_ganados  =  ganado
            db_posicion.juegos_empatados = empatado
            db_posicion.juegos_perdidos = perdido
            db_posicion.goles_favor = partido.goles_local
            db_posicion.goles_contra = partido.goles_visitante
            db_posicion.diferencia_goles = partido.goles_local - partido.goles_visitante
            db_posicion.puntos = puntos
            db_posicion.estatus = 1

            db_posicion.creado_por = _fn.clean_string(sub)
            db_posicion.creado_el = _dt.datetime.now()
            db_posicion.modificado_por = _fn.clean_string(sub)
            db_posicion.modificado_el = _dt.datetime.now()

            db.add(db_posicion)
            db.commit()
            db.refresh(db_posicion)

        else:

            partidos_list = db.query(_models.Partidos).filter(or_(_models.Partidos.local == partido.local,_models.Partidos.visitante == partido.local)).filter(_models.Partidos.temporada == get_temporada.temporada).filter(_models.Partidos.estatus == 2).all()

            jj =0
            jg = 0
            jp = 0
            je = 0
            gf = 0
            gc = 0
            pts = 0
            

            for partido_local in partidos_list:

                ganado = 0

                perdido = 0

                empatado = 0   

                puntos = 0

                if partido_local.local == partido.local:

                    if partido_local.goles_local > partido_local.goles_visitante:

                        ganado = 1

                        puntos = 3

                    if partido_local.goles_local < partido_local.goles_visitante:

                        perdido = 1

                    if partido_local.goles_local == partido_local.goles_visitante:

                        empatado = 1

                        puntos = 1

                    gf = gf + partido_local.goles_local
                    gc = gc + partido_local.goles_visitante

                if partido_local.visitante == partido.local:

                    if partido_local.goles_local > partido_local.goles_visitante:

                        perdido = 1


                    if partido_local.goles_local < partido_local.goles_visitante:

                        ganado = 1

                        puntos = 3

                    if partido_local.goles_local == partido_local.goles_visitante:

                        empatado = 1

                        puntos = 1

                    gf = gf + partido_local.goles_visitante
                    gc = gc + partido_local.goles_local

                jj = jj +1
                jg = jg + ganado
                je = je + empatado
                jp = jp + perdido                
                pts = pts + puntos

            pos_local.juegos_jugados  = jj
            pos_local.juegos_ganados  = jg
            pos_local.juegos_empatados = je
            pos_local.juegos_perdidos = jp
            pos_local.goles_favor = gf
            pos_local.goles_contra = gc
            pos_local.diferencia_goles = gf - gc      
            pos_local.puntos = pts

                

            pos_local.modificado_por = _fn.clean_string(sub)
            pos_local.modificado_el = _dt.datetime.now()

            db.commit()
            db.refresh(pos_local)

        


        if pos_visitante is None:   

            ganado = 0

            perdido = 0

            empatado = 0   

            puntos = 0

            if partido.goles_local > partido.goles_visitante:

                perdido = 1


            if partido.goles_local < partido.goles_visitante:

                ganado = 1

                puntos = 3

            if partido.goles_local == partido.goles_visitante:

                empatado = 1

                puntos = 1

            db_posicion = _models.Posiciones()

            db_posicion.temporada = get_temporada.temporada
            db_posicion.liga = _fn.is_null(partido.liga,0)
            db_posicion.equipo  = _fn.is_null(partido.visitante,0)
            db_posicion.juegos_jugados  =  1
            db_posicion.juegos_ganados  =  ganado
            db_posicion.juegos_empatados = empatado
            db_posicion.juegos_perdidos = perdido
            db_posicion.goles_favor = partido.goles_visitante
            db_posicion.goles_contra = partido.goles_local
            db_posicion.diferencia_goles = partido.goles_visitante - partido.goles_local
            db_posicion.puntos = puntos
            db_posicion.estatus = 1

            db_posicion.creado_por = _fn.clean_string(sub)
            db_posicion.creado_el = _dt.datetime.now()
            db_posicion.modificado_por = _fn.clean_string(sub)
            db_posicion.modificado_el = _dt.datetime.now()

            db.add(db_posicion)
            db.commit()
            db.refresh(db_posicion)

        else:

            partidos_list = db.query(_models.Partidos).filter(or_(_models.Partidos.local == partido.visitante,_models.Partidos.visitante == partido.visitante)).filter(_models.Partidos.temporada == get_temporada.temporada).filter(_models.Partidos.estatus == 2).all()

            jj =0
            jg = 0
            jp = 0
            je = 0
            gf = 0
            gc = 0
            pts = 0
            

            for partido_visita in partidos_list:

                ganado = 0

                perdido = 0

                empatado = 0   

                puntos = 0

                if partido_visita.local == partido.visitante:

                    if partido_visita.goles_local > partido_visita.goles_visitante:

                        ganado = 1

                        puntos = 3

                    if partido_visita.goles_local < partido_visita.goles_visitante:

                        perdido = 1

                    if partido_visita.goles_local == partido_visita.goles_visitante:

                        empatado = 1

                        puntos = 1

                    gf = gf + partido_visita.goles_local
                    gc = gc + partido_visita.goles_visitante

                if partido_visita.visitante == partido.visitante:

                    if partido_visita.goles_local > partido_visita.goles_visitante:

                        perdido = 1


                    if partido_visita.goles_local < partido_visita.goles_visitante:

                        ganado = 1

                        puntos = 3

                    if partido_visita.goles_local == partido_visita.goles_visitante:

                        empatado = 1

                        puntos = 1

                    gf = gf + partido_visita.goles_visitante
                    gc = gc + partido_visita.goles_local

                jj = jj +1
                jg = jg + ganado
                je = je + empatado
                jp = jp + perdido                
                pts = pts + puntos

            pos_visitante.juegos_jugados  = jj
            pos_visitante.juegos_ganados  = jg
            pos_visitante.juegos_empatados = je
            pos_visitante.juegos_perdidos = jp
            pos_visitante.goles_favor = gf
            pos_visitante.goles_contra = gc
            pos_visitante.diferencia_goles = gf - gc      
            pos_visitante.puntos = pts

                

            pos_visitante.modificado_por = _fn.clean_string(sub)
            pos_visitante.modificado_el = _dt.datetime.now()

            db.commit()
            db.refresh(pos_visitante)

            db_partido.registro_tabla = True
            db.commit()
            db.refresh(db_partido)

    suspensiones = db.query(_models.Tarjetas).filter(_models.Tarjetas.sanciones_vig == 1 ).all()

    for susp in suspensiones:

        if susp.jornada_regreso <= db_partido.jornada:

            susp.sanciones_vig = 0
            db.commit()
            db.refresh(susp)

    return db_partido 

# *************************************************************************************************************************************


def update_partido(
    db: _orm.Session,
    token: str,
    db_partido: _models.Partidos,
    partido: _schemas.PartidosCreate,
):
    sub = _auth.token_claim(token, "sub")
    ganador_partido = 0
    # db_actividades.clave = _fn.clean_string(actividad.clave).upper()
    db_partido.fecha =_fn.format_date(partido.fecha)
    db_partido.horario = _fn.clean_string(partido.horario)
    db_partido.etapa = _fn.clean_string(partido.etapa)
    db_partido.jornada = _fn.clean_string(partido.jornada)
    #db_partido.temporada = _fn.clean_string(partido.etapa)
    db_partido.campo =  _fn.is_null(partido.campo,0)
    db_partido.liga  =  _fn.is_null(partido.liga,0)
    db_partido.local  =  _fn.is_null(partido.local,0)
    db_partido.visitante =  _fn.is_null(partido.visitante,0)
    db_partido.goles_local  =  _fn.is_null(partido.goles_local,0)
    db_partido.goles_visitante  =  _fn.is_null(partido.goles_visitante,0)
    #db_partido.ganador =  _fn.is_null(partido.ganador,0)     
    db_partido.observaciones = _fn.clean_string(partido.observaciones)
    db_partido.estatus = _fn.is_null(partido.estatus,0)

    get_temporada = db.query(_models.Torneos).filter(_models.Torneos.id == partido.liga).first()

    if partido.estatus == 2 and partido.goles_local > partido.goles_visitante:

        ganador_partido = partido.local

    if partido.estatus == 2 and partido.goles_local < partido.goles_visitante:

        ganador_partido = partido.visitante

    if partido.estatus == 2 and partido.goles_local == partido.goles_visitante:

        ganador_partido = 0

    
    db_partido.ganador = ganador_partido
    db_partido.temporada = get_temporada.temporada
   
    db_partido.modificado_por = _fn.clean_string(sub)
    db_partido.modificado_el = _dt.datetime.now()

    db.commit()
    db.refresh(db_partido)

    #************ Seccion para insertar registro en tabla de posiciones ******************************************

    if partido.estatus == 2 and partido.etapa.upper() == "REGULAR":

        
        pos_local = db.query(_models.Posiciones).filter(_models.Posiciones.liga==partido.liga).filter(_models.Posiciones.equipo==partido.local).filter(_models.Posiciones.temporada==get_temporada.temporada).first()

        pos_visitante = db.query(_models.Posiciones).filter(_models.Posiciones.liga==partido.liga).filter(_models.Posiciones.equipo==partido.visitante).filter(_models.Posiciones.temporada==get_temporada.temporada).first()

        
        
        if pos_local is None:   

            ganado = 0

            perdido = 0

            empatado = 0   

            puntos = 0

            if partido.goles_local > partido.goles_visitante:

                ganado = 1

                puntos = 3

            if partido.goles_local < partido.goles_visitante:

                perdido = 1

            if partido.goles_local == partido.goles_visitante:

                empatado = 1

                puntos = 1

            db_posicion = _models.Posiciones()

            db_posicion.temporada = get_temporada.temporada
            db_posicion.liga = _fn.is_null(partido.liga,0)
            db_posicion.equipo  = _fn.is_null(partido.local,0)
            db_posicion.juegos_jugados  =  1
            db_posicion.juegos_ganados  =  ganado
            db_posicion.juegos_empatados = empatado
            db_posicion.juegos_perdidos = perdido
            db_posicion.goles_favor = partido.goles_local
            db_posicion.goles_contra = partido.goles_visitante
            db_posicion.diferencia_goles = partido.goles_local - partido.goles_visitante
            db_posicion.puntos = puntos
            db_posicion.estatus = 1

            db_posicion.creado_por = _fn.clean_string(sub)
            db_posicion.creado_el = _dt.datetime.now()
            db_posicion.modificado_por = _fn.clean_string(sub)
            db_posicion.modificado_el = _dt.datetime.now()

            db.add(db_posicion)
            db.commit()
            db.refresh(db_posicion)

        else:

            partidos_list = db.query(_models.Partidos).filter(or_(_models.Partidos.local == partido.local,_models.Partidos.visitante == partido.local)).filter(_models.Partidos.temporada == get_temporada.temporada).filter(_models.Partidos.estatus == 2).all()

            jj =0
            jg = 0
            jp = 0
            je = 0
            gf = 0
            gc = 0
            pts = 0
            

            for partido_local in partidos_list:

                ganado = 0

                perdido = 0

                empatado = 0   

                puntos = 0

                if partido_local.local == partido.local:

                    if partido_local.goles_local > partido_local.goles_visitante:

                        ganado = 1

                        puntos = 3

                    if partido_local.goles_local < partido_local.goles_visitante:

                        perdido = 1

                    if partido_local.goles_local == partido_local.goles_visitante:

                        empatado = 1

                        puntos = 1

                    gf = gf + partido_local.goles_local
                    gc = gc + partido_local.goles_visitante

                if partido_local.visitante == partido.local:

                    if partido_local.goles_local > partido_local.goles_visitante:

                        perdido = 1


                    if partido_local.goles_local < partido_local.goles_visitante:

                        ganado = 1

                        puntos = 3

                    if partido_local.goles_local == partido_local.goles_visitante:

                        empatado = 1

                        puntos = 1

                    gf = gf + partido_local.goles_visitante
                    gc = gc + partido_local.goles_local

                jj = jj +1
                jg = jg + ganado
                je = je + empatado
                jp = jp + perdido                
                pts = pts + puntos

            pos_local.juegos_jugados  = jj
            pos_local.juegos_ganados  = jg
            pos_local.juegos_empatados = je
            pos_local.juegos_perdidos = jp
            pos_local.goles_favor = gf
            pos_local.goles_contra = gc
            pos_local.diferencia_goles = gf - gc      
            pos_local.puntos = pts

                

            pos_local.modificado_por = _fn.clean_string(sub)
            pos_local.modificado_el = _dt.datetime.now()

            db.commit()
            db.refresh(pos_local)

        


        if pos_visitante is None:   

            ganado = 0

            perdido = 0

            empatado = 0   

            puntos = 0

            if partido.goles_local > partido.goles_visitante:

                perdido = 1


            if partido.goles_local < partido.goles_visitante:

                ganado = 1

                puntos = 3

            if partido.goles_local == partido.goles_visitante:

                empatado = 1

                puntos = 1

            db_posicion = _models.Posiciones()

            db_posicion.temporada = get_temporada.temporada
            db_posicion.liga = _fn.is_null(partido.liga,0)
            db_posicion.equipo  = _fn.is_null(partido.visitante,0)
            db_posicion.juegos_jugados  =  1
            db_posicion.juegos_ganados  =  ganado
            db_posicion.juegos_empatados = empatado
            db_posicion.juegos_perdidos = perdido
            db_posicion.goles_favor = partido.goles_visitante
            db_posicion.goles_contra = partido.goles_local
            db_posicion.diferencia_goles = partido.goles_visitante - partido.goles_local
            db_posicion.puntos = puntos
            db_posicion.estatus = 1

            db_posicion.creado_por = _fn.clean_string(sub)
            db_posicion.creado_el = _dt.datetime.now()
            db_posicion.modificado_por = _fn.clean_string(sub)
            db_posicion.modificado_el = _dt.datetime.now()

            db.add(db_posicion)
            db.commit()
            db.refresh(db_posicion)

        else:

            partidos_list = db.query(_models.Partidos).filter(or_(_models.Partidos.local == partido.visitante,_models.Partidos.visitante == partido.visitante)).filter(_models.Partidos.temporada == get_temporada.temporada).filter(_models.Partidos.estatus == 2).all()

            jj =0
            jg = 0
            jp = 0
            je = 0
            gf = 0
            gc = 0
            pts = 0
            

            for partido_visita in partidos_list:

                ganado = 0

                perdido = 0

                empatado = 0   

                puntos = 0

                if partido_visita.local == partido.visitante:

                    if partido_visita.goles_local > partido_visita.goles_visitante:

                        ganado = 1

                        puntos = 3

                    if partido_visita.goles_local < partido_visita.goles_visitante:

                        perdido = 1

                    if partido_visita.goles_local == partido_visita.goles_visitante:

                        empatado = 1

                        puntos = 1

                    gf = gf + partido_visita.goles_local
                    gc = gc + partido_visita.goles_visitante

                if partido_visita.visitante == partido.visitante:

                    if partido_visita.goles_local > partido_visita.goles_visitante:

                        perdido = 1


                    if partido_visita.goles_local < partido_visita.goles_visitante:

                        ganado = 1

                        puntos = 3

                    if partido_visita.goles_local == partido_visita.goles_visitante:

                        empatado = 1

                        puntos = 1

                    gf = gf + partido_visita.goles_visitante
                    gc = gc + partido_visita.goles_local

                jj = jj +1
                jg = jg + ganado
                je = je + empatado
                jp = jp + perdido                
                pts = pts + puntos

            pos_visitante.juegos_jugados  = jj
            pos_visitante.juegos_ganados  = jg
            pos_visitante.juegos_empatados = je
            pos_visitante.juegos_perdidos = jp
            pos_visitante.goles_favor = gf
            pos_visitante.goles_contra = gc
            pos_visitante.diferencia_goles = gf - gc      
            pos_visitante.puntos = pts

                

            pos_visitante.modificado_por = _fn.clean_string(sub)
            pos_visitante.modificado_el = _dt.datetime.now()

            db.commit()
            db.refresh(pos_visitante)

            db_partido.registro_tabla = True
            db.commit()
            db.refresh(db_partido)

    suspensiones = db.query(_models.Tarjetas).filter(_models.Tarjetas.sanciones_vig == 1 ).all()

    for susp in suspensiones:

        if susp.jornada_regreso <= db_partido.jornada:

            susp.sanciones_vig = 0
            db.commit()
            db.refresh(susp)
    
    return db_partido

# *************************************************************************************************************************************


def delete_partido(db: _orm.Session, token: str, id: int):
    
    db.query(_models.Partidos).filter(_models.Partidos.id == id).delete()
    db.commit()

# *************************************************************************************************************************************

def get_tabla_posiciones(db: _orm.Session, token: str, id_torneo:int, temporada:str):

    #torneo = db.query(_models.Torneos).filter(_models.Torneos.id == id_torneo).first()

    posiciones = (
        db.query(_models.Posiciones)
        .filter(_models.Posiciones.liga==id_torneo)
        .filter(_models.Posiciones.temporada==temporada)
        .order_by(_models.Posiciones.puntos.desc(),_models.Posiciones.diferencia_goles.desc(),_models.Posiciones.goles_contra.asc(),_models.Posiciones.goles_favor.desc())
        .all()
    )

    return posiciones

# *************************************************************************************************************************************

def get_tabla_temporadas(db: _orm.Session, token: str, id_torneo:int):

    #torneo = db.query(_models.Torneos).filter(_models.Torneos.id == id_torneo).first()

    posiciones = (
        db.query(_models.Posiciones)
        .filter(_models.Posiciones.liga==id_torneo)        
        .order_by(_models.Posiciones.id.desc())
        .all()
    )

    return posiciones

# *************************************************************************************************************************************
# SECCION: TARJETAS
# *************************************************************************************************************************************

def get_tarjetas(
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
        db.query(_models.Tarjetas)
        #.order_by(_models.Tarjetas.jornada.desc())
        .offset(skip)        
        .all()
    )

    return results

# *************************************************************************************************************************************


def get_tarjetas_por_id(db: _orm.Session, token: str, id: int):
    jugador = db.query(_models.Tarjetas).filter(_models.Tarjetas.id == id).first()
    return jugador

# *************************************************************************************************************************************


def create_tarjetas(
    db: _orm.Session,
    jugador: _schemas.TarjetasCreate,
    token: str,
):

    sub = _auth.token_claim(token, "sub")

    torneo = db.query(_models.Torneos).filter(_models.Torneos.id == jugador.id_liga).first()

    registroExist = db.query(_models.Tarjetas).filter(_models.Tarjetas.id_jugador == jugador.id_jugador).filter(_models.Tarjetas.temporada == torneo.temporada).first()

    jornada_actual = db.query(_models.Partidos).filter(_models.Partidos.temporada == torneo.temporada).filter(_models.Partidos.liga == torneo.id).order_by(_models.Partidos.jornada.desc()).first()

    if registroExist == None:
        

        db_jugador = _models.Tarjetas(

            id_liga = _fn.is_null(jugador.id_liga,0),
            id_equipo = _fn.is_null(jugador.id_equipo,0),
            id_jugador = _fn.is_null(jugador.id_jugador,0),
            ta = _fn.is_null(jugador.ta,0),
            tr = _fn.is_null(jugador.tr,0),
            suspensiones = _fn.is_null(jugador.suspensiones,0),
            numero_juegos = _fn.is_null(jugador.numero_juegos,0),
            jornada_regreso = _fn.is_null(jugador.jornada_regreso,0),
            temporada= _fn.clean_string(torneo.temporada),
            descripcion= _fn.clean_string(jugador.descripcion),        
            
        )

        jr = jornada_actual.jornada +2

        if jugador.tr == 1:        

            db_jugador.sanciones_vig = 1
            db_jugador.jornada_regreso = jr
        else:
            db_jugador.sanciones_vig = 0
            db_jugador.jornada_regreso = 0

        
        if db_jugador.suspensiones >= 1:

            jr = jornada_actual.jornada + jugador.numero_juegos + 1

            db_jugador.sanciones_vig = 1
            db_jugador.numero_juegos = jugador.numero_juegos
            db_jugador.jornada_regreso = jr

        db_jugador.estatus = 1

        db_jugador.creado_por = _fn.clean_string(sub)
        db_jugador.creado_el = _dt.datetime.now()
        db_jugador.modificado_por = _fn.clean_string(sub)
        db_jugador.modificado_el = _dt.datetime.now()

        db.add(db_jugador)
        db.commit()
        db.refresh(db_jugador)    

    else:

        db_jugador = None

    return db_jugador

#********************************************************************************************************************

def update_tarjetas(
    db: _orm.Session,
    token: str,
    db_jugador: _models.Tarjetas,
    jugador: _schemas.TarjetasCreate,
):
    sub = _auth.token_claim(token, "sub")

    tam = db_jugador.ta + jugador.ta
    tro = db_jugador.tr + jugador.tr
    susp = db_jugador.suspensiones + jugador.suspensiones
    tar_s = db_jugador.tar_susp + jugador.ta

    
    torneo = torneo = db.query(_models.Torneos).filter(_models.Torneos.id == jugador.id_liga).first()
    jornada_actual = db.query(_models.Partidos).filter(_models.Partidos.temporada == torneo.temporada).filter(_models.Partidos.liga == torneo.id).order_by(_models.Partidos.jornada.desc()).first()

    jr = 0

    desc = jugador.descripcion
    if tar_s == 4 or jugador.tr == 1:
        
        susp = db_jugador.suspensiones + 1
        jr = jornada_actual.jornada +2
        desc = "suspensión por acumulación de tarjetas"
        if tar_s == 4:
            tar_s = 0
        

    if jugador.tr == 1:        

        db_jugador.sanciones_vig = 1
        db_jugador.jornada_regreso = jr
    else:
        db_jugador.sanciones_vig = 0
        db_jugador.jornada_regreso = 0

        
    if jr > jornada_actual.jornada:

        db_jugador.sanciones_vig = 1
        jr = jornada_actual.jornada +2
    else:
        db_jugador.sanciones_vig = 0
        db_jugador.jornada_regreso = 0

    if db_jugador.suspensiones >= 1:

        jr = jornada_actual.jornada + jugador.numero_juegos + 1

        db_jugador.sanciones_vig = 1
        db_jugador.numero_juegos = jugador.numero_juegos
        db_jugador.jornada_regreso = jr

    db_jugador.suspensiones = _fn.is_null(susp,0)
    #db_jugador.numero_juegos = _fn.is_null(1,0)
    db_jugador.jornada_regreso = _fn.is_null(jr,0)
    db_jugador.temporada= _fn.clean_string(torneo.temporada)
    db_jugador.descripcion = _fn.clean_string(desc)
    db_jugador.tar_susp = _fn.is_null(tar_s,0)

        
    
    # db_actividades.clave = _fn.clean_string(actividad.clave).upper()
    #db_jugador.id_equipo = _fn.is_null(jugador.id_equipo,0)
    #db_jugador.id_jugador = _fn.is_null(jugador.id_jugador,0)
    db_jugador.ta = _fn.is_null(tam,0)
    db_jugador.tr = _fn.is_null(tro,0)
    

    db_jugador.modificado_por = _fn.clean_string(sub)
    db_jugador.modificado_el = _dt.datetime.now()

    db.commit()
    db.refresh(db_jugador)

    return db_jugador


# *************************************************************************************************************************************
# SECCION: GOLES
# *************************************************************************************************************************************

def get_goles(
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
        db.query(_models.Goleadores)
        .order_by(_models.Goleadores.goles.desc())
        .offset(skip)        
        .all()
    )

    return results

# *************************************************************************************************************************************


def get_goles_por_id(db: _orm.Session, token: str, id: int):
    jugador = db.query(_models.Goleadores).filter(_models.Goleadores.id == id).first()
    return jugador



# *************************************************************************************************************************************


def create_goles(
    db: _orm.Session,
    jugador: _schemas.GoleadoresCreate,
    token: str,
):

    sub = _auth.token_claim(token, "sub")

    torneo = db.query(_models.Torneos).filter(_models.Torneos.id == jugador.id_liga).first()

    registroExist = db.query(_models.Goleadores).filter(_models.Goleadores.id_jugador == jugador.id_jugador).filter(_models.Goleadores.temporada == torneo.temporada).first()

    jornada_actual = db.query(_models.Partidos).filter(_models.Partidos.temporada == torneo.temporada).filter(_models.Partidos.liga == torneo.id).order_by(_models.Partidos.jornada.desc()).first()

    if registroExist == None:
        

        db_jugador = _models.Goleadores(

            id_liga = _fn.is_null(jugador.id_liga,0),
            id_equipo = _fn.is_null(jugador.id_equipo,0),
            id_jugador = _fn.is_null(jugador.id_jugador,0),
            goles = _fn.is_null(jugador.goles,0),
            jj = _fn.is_null(jugador.jj,0),
            avg = jugador.goles / jugador.jj,            
            temporada= _fn.clean_string(torneo.temporada),
       
            
        )        

        db_jugador.creado_por = _fn.clean_string(sub)
        db_jugador.creado_el = _dt.datetime.now()
        db_jugador.modificado_por = _fn.clean_string(sub)
        db_jugador.modificado_el = _dt.datetime.now()

        db.add(db_jugador)
        db.commit()
        db.refresh(db_jugador)    

    else:

        db_jugador = None

    return db_jugador

#********************************************************************************************************************

def update_goles(
    db: _orm.Session,
    token: str,
    db_jugador: _models.Goleadores,
    jugador: _schemas.GoleadoresCreate,
):
    sub = _auth.token_claim(token, "sub")

    goles = db_jugador.goles + jugador.goles
    jj = db_jugador.jj + jugador.jj
    avg = goles / jj   

    db_jugador.goles = _fn.is_null(goles,0)
    db_jugador.jj = _fn.is_null(jj,0)
    db_jugador.avg = avg


    db_jugador.modificado_por = _fn.clean_string(sub)
    db_jugador.modificado_el = _dt.datetime.now()

    db.commit()
    db.refresh(db_jugador)

    return db_jugador   

# *************************************************************************************************************************************


def get_usuario_por_id(db: _orm.Session, token: str, id: int):
    usuario = db.query(_models.UsuarioLiga).filter(_models.UsuarioLiga.id == id).first()
    return usuario

# *************************************************************************************************************************************


def get_usuario_por_equipo(db: _orm.Session, token: str, id: int):
    usuario = db.query(_models.UsuarioLiga).filter(_models.UsuarioLiga.id_equipo == id).first()
    return usuario



# *************************************************************************************************************************************


def create_usuario(
    db: _orm.Session,
    usuario: _schemas.UsuariosLigaCreate,
    token: str,
):

    sub = _auth.token_claim(token, "sub")

    registroExist = db.query(_models.UsuarioLiga).filter(_models.UsuarioLiga.id_equipo == usuario.id_equipo).first()

    
    if registroExist == None:
        

        db_usuario = _models.UsuarioLiga(

            id_equipo  = _fn.is_null(usuario.id_equipo,0),
            nivel  = _fn.is_null(usuario.nivel,0),
            nombre_completo = _fn.clean_string(usuario.nombre_completo),
            email =  _fn.clean_string(usuario.email),
            telefono =  _fn.clean_string(usuario.telefono),
            #password =  _fn.clean_string(usuario.nombre_completo),
            #roles =  _fn.clean_string(usuario.nombre_completo),
            alias =  _fn.clean_string(usuario.alias),
            remote_id =  _fn.is_null(usuario.remote_id,0),
            estatus = _fn.is_null(usuario.estatus,1),

       
            
        )        

        db_usuario.creado_por = _fn.clean_string(sub)
        db_usuario.creado_el = _dt.datetime.now()
        db_usuario.modificado_por = _fn.clean_string(sub)
        db_usuario.modificado_el = _dt.datetime.now()

        db.add(db_usuario)
        db.commit()
        db.refresh(db_usuario)    

    else:

        db_usuario = None

    return db_usuario

#********************************************************************************************************************

def update_usuario(
    db: _orm.Session,
    token: str,
    db_usuario: _models.UsuarioLiga,
    usuario: _schemas.UsuariosLigaCreate,
):
    sub = _auth.token_claim(token, "sub")

    db_usuario.id_equipo  = _fn.is_null(usuario.id_equipo,0)
    db_usuario.nivel  = _fn.is_null(usuario.nivel,0)
    db_usuario.nombre_completo = _fn.clean_string(usuario.nombre_completo)
    db_usuario.email =  _fn.clean_string(usuario.email)
    db_usuario.telefono =  _fn.clean_string(usuario.telefono)
    #db_usuario.password =  _fn.clean_string(usuario.nombre_completo)
    #db_usuario.roles =  _fn.clean_string(usuario.nombre_completo)
    db_usuario.alias =  _fn.clean_string(usuario.alias)
    db_usuario.remote_id =  _fn.is_null(usuario.remote_id,0)
    db_usuario.estatus = _fn.is_null(usuario.estatus,1)


    db_usuario.modificado_por = _fn.clean_string(sub)
    db_usuario.modificado_el = _dt.datetime.now()

    db.commit()
    db.refresh(db_usuario)

    return db_usuario   


# *************************************************************************************************************************************

def get_archivos(
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
        db.query(_models.Archivos)
        .order_by(_models.Archivos.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return results

# *************************************************************************************************************************************


def get_archivos_por_id(db: _orm.Session, token: str, id: int):
    archivo = db.query(_models.Archivos).filter(_models.Archivos.id == id).first()
    return archivo


# **************************************************************************

def create_archivo(
    db: _orm.Session,
    file: _schemas.ArchivosCreate,
    token: str,
):

    sub = _auth.token_claim(token, "sub")

    #docExist = db.query(_models.Archivos).filter(_models.Archivos.file == usuario.id_equipo).first()

    db_file = _models.Archivos(

        nombre  =  _fn.clean_string(file.nombre),
        file  =  _fn.clean_string(file.file),
            
    )        

    db_file.creado_por = _fn.clean_string(sub)
    db_file.creado_el = _dt.datetime.now()
    db_file.modificado_por = _fn.clean_string(sub)
    db_file.modificado_el = _dt.datetime.now()

    db.add(db_file)
    db.commit()
    db.refresh(db_file)    



    return db_file


# *************************************************************************************************************************************

def update_archivo(
    db: _orm.Session,
    db_file: _models.Archivos,
    file: _schemas.ArchivosCreate,
    token: str,
):

    sub = _auth.token_claim(token, "sub")

    docExist = db.query(_models.Archivos).filter(_models.Archivos.id == db_file.id).first()

    docExist.nombre  =  _fn.clean_string(file.nombre)
    docExist.file  =  _fn.clean_string(file.file)             

    db_file.modificado_por = _fn.clean_string(sub)
    db_file.modificado_el = _dt.datetime.now()

    db.add(db_file)
    db.commit()
    db.refresh(db_file)    

    return db_file

# ****************************************************************************************


def delete_archivo(db: _orm.Session, token: str, id: int):

    archivo = get_archivos_por_id(db=db, token=token, id=id)
    
    db.query(_models.Archivos).filter(_models.Archivos.id == id).delete()
    db.commit()