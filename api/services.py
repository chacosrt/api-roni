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

    jugador_exist = db.query(_models.Jugadores).filter(_models.Jugadores.expediente == jugador.expediente).filter(_models.Jugadores.liga == equipo_jugador.liga).first()   
    
    
    new_jugador = False
    
        
    if(jugador_exist == None ):

        new_jugador = True
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


        db.add(db_jugador)
        db.commit()
        db.refresh(db_jugador)  

          

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
    sub = _auth.token_claim(token, "sub")
    for jugador in results:

        db_jugador = _models.Jugadores_Equipos(
            id_liga = jugador.liga,
            id_equipo = jugador.equipo,
            id_jugador = jugador.id

        )  

        db_jugador.creado_por = _fn.clean_string(sub)
        db_jugador.creado_el = _dt.datetime.now()
        db_jugador.modificado_por = _fn.clean_string(sub)
        db_jugador.modificado_el = _dt.datetime.now()

        db.add(db_jugador)
        db.commit()
        db.refresh(db_jugador)

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

    return db_jugador

# *************************************************************************************************************************************


def delete_jugador(db: _orm.Session, token: str, id: int):

    torneo = get_jugadores_por_id(db=db, token=token, id=id)
    
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
        .order_by(_models.Partidos.jornada.desc())
        .offset(skip)
        .limit(limit)
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

    results = (
        db.query(_models.Partidos)
        .filter(_models.Partidos.liga == id)
        .order_by(_models.Partidos.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return results

# *************************************************************************************************************************************

def get_partidos_por_jornada(
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
    temporada = torneo.temporada

    results = (
        db.query(_models.Partidos)
        .distinct(_models.Partidos.jornada)
        .filter(_models.Partidos.liga == id)
        .filter(_models.Partidos.temporada == temporada)
        .order_by(_models.Partidos.jornada.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return results


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

    db_partido.estatus = 1
    db_partido.ganador = ganador_partido
    db_partido.temporada = get_temporada.temporada

    db_partido.creado_por = _fn.clean_string(sub)
    db_partido.creado_el = _dt.datetime.now()
    db_partido.modificado_por = _fn.clean_string(sub)
    db_partido.modificado_el = _dt.datetime.now()

    db.add(db_partido)
    db.commit()
    db.refresh(db_partido)

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

            if partido.goles_local > partido.goles_visitante:

                ganado = pos_local.juegos_ganados + 1

                perdido = pos_local.juegos_perdidos

                empatado = pos_local.juegos_empatados

                puntos = pos_local.puntos + 3

            if partido.goles_local < partido.goles_visitante:

                ganado = pos_local.juegos_ganados

                perdido = pos_local.juegos_perdidos + 1

                empatado = pos_local.juegos_empatados

                puntos = pos_local.puntos 

            if partido.goles_local == partido.goles_visitante:

                ganado = pos_local.juegos_ganados

                perdido = pos_local.juegos_perdidos

                empatado = pos_local.juegos_empatados + 1

                puntos = pos_local.puntos + 1

            pos_local.juegos_jugados  = pos_local.juegos_jugados + 1
            pos_local.juegos_ganados  = ganado
            pos_local.juegos_empatados = empatado
            pos_local.juegos_perdidos = perdido
            pos_local.goles_favor = pos_local.goles_favor + partido.goles_local
            pos_local.goles_contra = pos_local.goles_contra + partido.goles_visitante
            pos_local.diferencia_goles = pos_local.goles_favor - pos_local.goles_contra

            pos_local.modificado_por = _fn.clean_string(sub)
            pos_local.modificado_el = _dt.datetime.now()

            db.commit()
            db.refresh(db_posicion)


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

            if partido.goles_local > partido.goles_visitante:

                ganado = pos_visitante.juegos_ganados

                perdido = pos_visitante.juegos_perdidos + 1

                empatado = pos_visitante.juegos_empatados

                puntos = pos_visitante.puntos 

            if partido.goles_local < partido.goles_visitante:

                ganado = pos_visitante.juegos_ganados + 1

                puntos = pos_visitante.puntos + 3

            if partido.goles_local == partido.goles_visitante:

                empatado = pos_visitante.juegos_empatados + 1

                puntos = pos_visitante.puntos + 1

            pos_visitante.juegos_jugados  = pos_visitante.juegos_jugados + 1
            pos_visitante.juegos_ganados  =  ganado
            pos_visitante.juegos_empatados = empatado
            pos_visitante.juegos_perdidos = perdido
            pos_visitante.goles_favor = pos_visitante.goles_favor + partido.goles_visitante
            pos_visitante.goles_contra = pos_visitante.goles_contra + partido.goles_local
            pos_visitante.diferencia_goles = pos_visitante.goles_favor - pos_visitante.goles_contra

            pos_visitante.modificado_por = _fn.clean_string(sub)
            pos_visitante.modificado_el = _dt.datetime.now()

            db.commit()
            db.refresh(db_posicion)




    
    return db_partido

# *************************************************************************************************************************************


def delete_partido(db: _orm.Session, token: str, id: int):
    
    db.query(_models.Partidos).filter(_models.Partidos.id == id).delete()
    db.commit()

# *************************************************************************************************************************************

def get_tabla_posiciones(db: _orm.Session, token: str, id_torneo:int):

    posiciones = (
        db.query(_models.Posiciones)
        .filter(_models.Posiciones.liga==id_torneo)
        .order_by(_models.Posiciones.puntos.desc(),_models.Posiciones.diferencia_goles.desc(),_models.Posiciones.goles_contra.asc(),_models.Posiciones.goles_favor.desc())
        .all()
    )

    return posiciones