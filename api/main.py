from typing import List, Optional
import subprocess as _subprocess

import fastapi as _fastapi
import sqlalchemy.orm as _orm
import logging as _logging
import time as _time
import datetime as _dt
import random as _random
import string as _string

import settings as _settings
import auth as _auth
import services as _services
import schemas as _schemas

import fastapi.middleware.cors as _cors

import functions.fn as _fn
import functions.wormhole as _wormhole

# setup loggers
_logging.config.fileConfig(
    "../logging.conf",
    disable_existing_loggers=False,
    defaults={
        "logfilename": _settings.LOG_FILENAME,
    },
)

# get root logger
_logger = _logging.getLogger(
    __name__
)  # the __name__ resolve to "main" since we are at the root of the project.
# This will get the root logger since no logger in the configuration has this name.


# Se cambia docs_url a /api para "ocultar el path", de cualquier manera,
# en producción es recomendable establecer el valor en None para que no
# exista acceso.

app = _fastapi.FastAPI(
    title=_settings.APP_TITLE,
    root_path=_settings.APP_ROOT_PATH,
    docs_url=_settings.APP_DOCS_URL,
    redoc_url=_settings.APP_REDOC_URL,
)

_origins = [
    _settings.ORIGINS_URL,
    "http://localhost",
    "https://liga-metro.dinossolutions.com"
]
app.add_middleware(
    _cors.CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# extrae valores de jwt *********************************************************************************************************
@app.middleware("http")
async def log_requests(request: _fastapi.Request, call_next):
    idem = "".join(_random.choices(_string.ascii_uppercase + _string.digits, k=6))

    # extrae valores de jwt *****************************************************************************************************
    aud = "[" + _settings.JWT_AUDIENCE + "] "
    ip = str(request.client.host) + " "

    try:
        credentials = request.headers["authorization"].split(" ")[1]
        sub = _auth.token_claim(credentials, "sub") + " "
        jti = "- " + _auth.token_claim(credentials, "jti") + " "
    except:
        sub = ""
        jti = ""
    # ***************************************************************************************************************************

    _logger.info(f"{aud}{ip}{sub}{jti}[{idem}] start request path={request.url.path}")
    start_time = _time.time()

    response = await call_next(request)

    process_time = (_time.time() - start_time) * 1000
    formatted_process_time = "{0:.2f}".format(process_time)
    if response.status_code < 400:
        _logger.info(
            f"{aud}{ip}{sub}{jti}[{idem}] completed_in={formatted_process_time}ms status_code={response.status_code}"
        )
    elif response.status_code < 500:
        _logger.warning(
            f"{aud}{ip}{sub}{jti}[{idem}] completed_in={formatted_process_time}ms status_code={response.status_code}"
        )
    else:
        _logger.error(
            f"{aud}{ip}{sub}{jti}[{idem}] [{idem}] completed_in={formatted_process_time}ms status_code={response.status_code}"
        )

    await _wormhole.log_wormhole(
        f"{_fn.format_datetime(_dt.datetime.fromtimestamp(start_time))} {aud}{ip}{sub}{jti}[{idem}] start request path='{request.url.path}' completed_in={formatted_process_time}ms status_code={response.status_code}"
    )

    return response


# print(_fn.web_site_online("https://api.gdar.mx/marble"))

# define endpoints

# *************************************************************************************************************************************
# SECCION: PRINCIPAL
# *************************************************************************************************************************************


@app.get("/", tags=["API Status"])
async def home():
    return _fastapi.Response(status_code=_fastapi.status.HTTP_200_OK)


# *************************************************************************************************************************************
# SECCION: Torneos
# *************************************************************************************************************************************

@app.get(
    "/torneos_list/",
    response_model=List[_schemas.Torneos],
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Torneos"],
)
async def read_torneos(
    skip: Optional[int] = None,
    limit: Optional[int] = None,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_torneos = _services.get_torneos(
        db=db,
          token=token, 
          skip=skip, limit=limit
    )
    if len(db_torneos) == 0:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )
    return db_torneos

# *************************************************************************************************************************************
@app.get(
    "/torneos/{id}/id",
    response_model=_schemas.Torneos,
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Torneos"],
)
async def read_torneos_por_id(
    id: str,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_torneos = _services.get_torneos_por_id(
        db=db,
        token=token,
        id=_fn.parameter_id(id),
    )
    if db_torneos is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )

    return db_torneos

# *************************************************************************************************************************************


@app.post(
    "/torneos/{id}/activa",    
    response_model=_schemas.Torneos,
    status_code=_fastapi.status.HTTP_201_CREATED,
    tags=["Torneos"],
)
def active_torneo(
    id: str,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    # return _services.create_actividad(db=db, actividad=actividad)
    return _services.activa_torneo(db=db, token=token, id=_fn.parameter_id(id))


# *************************************************************************************************************************************


@app.post(
    "/torneos/",
    response_model=_schemas.Torneos,
    status_code=_fastapi.status.HTTP_201_CREATED,
    tags=["Torneos"],
)
def create_torneo(
    torneo: _schemas.TorneosCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    # return _services.create_actividad(db=db, actividad=actividad)
    return _services.create_torneo(db=db, token=token, torneo=torneo)


# *************************************************************************************************************************************


@app.post(
    "/torneos/{id}",
    response_model=_schemas.Torneos,
    status_code=_fastapi.status.HTTP_201_CREATED,
    tags=["Torneos"],
)
async def update_torneo(
    id: str,
    torneo: _schemas.TorneosCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_torneos = _services.get_torneos_por_id(
        db=db,
        token=token,
        id=_fn.parameter_id(id),
    )
    if db_torneos is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )

    return _services.update_torneo(
        db=db,
        token=token,
        db_torneos=db_torneos,
        torneo=torneo,
    )


# *************************************************************************************************************************************


@app.post(
    "/torneos/{id}/delete",
    status_code=_fastapi.status.HTTP_202_ACCEPTED,
    tags=["Torneos"],
)
async def delete_torneo(
    id: str,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_torneos = _services.get_torneos_por_id(
        db=db,
        token=token,
        id=_fn.parameter_id(id),
    )
    if db_torneos is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )
    _services.delete_torneo(
        db=db,
        token=token,
        id=_fn.parameter_id(id),
    )
    return {"message": f"El registro: {id} ha sido eliminado"}

# *************************************************************************************************************************************
# SECCION: EQUIPOS
# *************************************************************************************************************************************

@app.get(
    "/equipos_list/",
    response_model=List[_schemas.Equipos],
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Equipos"],
)
async def read_equipos(
    skip: Optional[int] = None,
    limit: Optional[int] = None,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_equipos = _services.get_equipos(
        db=db,
          token=token, 
          skip=skip, limit=limit
    )
    if len(db_equipos) == 0:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )
    return db_equipos


# *************************************************************************************************************************************
@app.get(
    "/equipos/{id}/id",
    response_model=_schemas.Equipos,
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Equipos"],
)
async def read_equipos_por_id(
    id: str,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_equipos = _services.get_equipos_por_id(
        db=db,
        token=token,
        id=_fn.parameter_id(id),
    )
    if db_equipos is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )

    return db_equipos

# *************************************************************************************************************************************
@app.get(
    "/equipos/{id}/id_torneo",
    response_model=List[_schemas.Equipos],
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Equipos"],
)
async def read_equipos_por_id_torneo(
    id: str,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_equipos = _services.get_equipos_por_id_torneo(
        db=db,
        token=token,
        id=_fn.parameter_id(id),
    )
    if db_equipos is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )

    return db_equipos

# *************************************************************************************************************************************


@app.post(
    "/equipos/",
    response_model=_schemas.Equipos,
    status_code=_fastapi.status.HTTP_201_CREATED,
    tags=["Equipos"],
)
def create_equipo(
    equipo: _schemas.EquiposCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    # return _services.create_actividad(db=db, actividad=actividad)
    return _services.create_equipo(db=db, token=token, equipo=equipo)


# *************************************************************************************************************************************


@app.post(
    "/equipos/{id}",
    response_model=_schemas.Torneos,
    status_code=_fastapi.status.HTTP_201_CREATED,
    tags=["Equipos"],
)
async def update_equipo(
    id: str,
    equipo: _schemas.EquiposCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_equipos = _services.get_equipos_por_id(
        db=db,
        token=token,
        id=_fn.parameter_id(id),
    )
    if db_equipos is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )

    return _services.update_equipo(
        db=db,
        token=token,
        db_equipos=db_equipos,
        equipo=equipo,
    )


# *************************************************************************************************************************************


@app.post(
    "/equipos/{id}/delete",
    status_code=_fastapi.status.HTTP_202_ACCEPTED,
    tags=["Equipos"],
)
async def delete_equipo(
    id: str,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_equipos = _services.get_equipos_por_id(
        db=db,
        token=token,
        id=_fn.parameter_id(id),
    )
    if db_equipos is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )
    _services.delete_equipo(
        db=db,
        token=token,
        id=_fn.parameter_id(id),
    )
    return {"message": f"El registro: {id} ha sido eliminado"}


# *************************************************************************************************************************************


@app.post(
    "/equipos/new_equipo/",
    #response_model=_schemas.Jugadores,
    status_code=_fastapi.status.HTTP_201_CREATED,
    tags=["Equipos"],
)
async def nuevo_equipo(
    equipo_jugador: _schemas.EquipoJugador,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    jugador = _services.nuevo_equipo(db=db, token=token, equipo_jugador=equipo_jugador)
    if jugador == False:

        raise _fastapi.HTTPException(
            status_code=404, detail="El jugador ya esta registrado en esta liga."
        )
       
    # return _services.create_actividad(db=db, actividad=actividad)
    return {"message": f"El jugador:  ha sido registrado"}


# *************************************************************************************************************************************
# SECCION: JUGADORES
# *************************************************************************************************************************************

@app.get(
    "/jugadores_list/",
    response_model=List[_schemas.Jugadores],
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Jugadores"],
)
async def read_jugadores(
    skip: Optional[int] = None,
    limit: Optional[int] = None,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_jugadores = _services.get_jugadores(
        db=db,
          token=token, 
          skip=skip, limit=limit
    )
    if len(db_jugadores) == 0:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )
    return db_jugadores


# *************************************************************************************************************************************
@app.get(
    "/jugadores/{id}/id",
    response_model=_schemas.Jugadores,
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Jugadores"],
)
async def read_jugadores_por_id(
    id: str,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_jugadores = _services.get_jugadores_por_id(
        db=db,
        token=token,
        id=_fn.parameter_id(id),
    )
    if db_jugadores is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="Error al guardar los datos"
        )

    return db_jugadores

# *************************************************************************************************************************************
@app.get(
    "/jugadores/{equipo_id}/equipo_id",
    response_model=List[_schemas.Jugadores],
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Jugadores"],
)
async def read_jugadores_por_equipo_id(
    equipo_id: str,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_jugadores = _services.get_jugadores_por_equipo_id(
        db=db,
        token=token,
        id=_fn.parameter_id(equipo_id),
    )
    if db_jugadores is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )

    return db_jugadores

# *************************************************************************************************************************************


@app.post(
    "/jugadores/",
    response_model=_schemas.Jugadores,
    status_code=_fastapi.status.HTTP_201_CREATED,
    tags=["Jugadores"],
)
def create_jugadores(
    jugador: _schemas.JugadoresCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    # return _services.create_actividad(db=db, actividad=actividad)
    return _services.create_jugador(db=db, token=token, jugador=jugador)


# *************************************************************************************************************************************


@app.post(
    "/jugadores/{id}",
    response_model=_schemas.Jugadores,
    status_code=_fastapi.status.HTTP_201_CREATED,
    tags=["Jugadores"],
)
async def update_jugadores(
    id: str,
    jugador: _schemas.JugadoresCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_jugadores = _services.get_jugadores_por_id(
        db=db,
        token=token,
        id=_fn.parameter_id(id),
    )
    if db_jugadores is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )

    return _services.update_jugador(
        db=db,
        token=token,
        db_jugador=db_jugadores,
        jugador=jugador,
    )


# *************************************************************************************************************************************


@app.post(
    "/jugadores/{id}/delete",
    status_code=_fastapi.status.HTTP_202_ACCEPTED,
    tags=["Jugadores"],
)
async def delete_jugador(
    id: str,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_jugadores = _services.get_jugadores_por_id(
        db=db,
        token=token,
        id=_fn.parameter_id(id),
    )
    if db_jugadores is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )
    _services.delete_jugador(
        db=db,
        token=token,
        id=_fn.parameter_id(id),
    )
    return {"message": f"El registro: {id} ha sido eliminado"}


# *************************************************************************************************************************************
# SECCION: PARTIDOS
# *************************************************************************************************************************************

@app.get(
    "/partidos_list/",
    response_model=List[_schemas.Partidos],
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Partidos"],
)
async def read_partidos(
    skip: Optional[int] = None,
    limit: Optional[int] = None,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_partidos = _services.get_partidos(
        db=db,
          token=token, 
          skip=skip, limit=limit
    )
    if len(db_partidos) == 0:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )
    return db_partidos


# *************************************************************************************************************************************
@app.get(
    "/partidos/{id}/id",
    response_model=_schemas.Partidos,
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Partidos"],
)
async def read_partidos_por_id(
    id: str,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_partidos = _services.get_partidos_por_id(
        db=db,
        token=token,
        id=_fn.parameter_id(id),
    )
    if db_partidos is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )

    return db_partidos

# *************************************************************************************************************************************

@app.get(
    "/partidos/{id}/id_equipo",
    response_model=List[_schemas.Partidos],
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Partidos"],
)
async def read_partidos_equipo_id(
    skip: Optional[int] = None,
    limit: Optional[int] = None,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_partidos = _services.get_partidos_por_equipo_id(
        db=db,
          token=token, 
          skip=skip, limit=limit
    )
    if len(db_partidos) == 0:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )
    return db_partidos

# *************************************************************************************************************************************

@app.get(
    "/partidos/{id}/id_torneo",
    response_model=List[_schemas.Partidos],
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Partidos"],
)
async def read_partidos_torneo_id(
    skip: Optional[int] = None,
    limit: Optional[int] = None,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_partidos = _services.get_equipos_por_id_torneo(
        db=db,
          token=token, 
          skip=skip, limit=limit
    )
    if len(db_partidos) == 0:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )
    return db_partidos

# *************************************************************************************************************************************

@app.get(
    "/partidos/{id_torneo}/{jornada}/{temporada}/jornadas",
    response_model=List[_schemas.Partidos],
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Partidos"],
)
async def read_partidos_jornada(
    id_torneo: str,
    jornada:str,
    temporada:str,
    skip: Optional[int] = None,
    limit: Optional[int] = None,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_partidos = _services.get_partidos_por_jornada(
        db=db,
          token=token, 
          skip=skip, limit=limit,
          torneo=_fn.parameter_id(id_torneo),
          jornada=jornada,
          temporada=temporada
    )
    if len(db_partidos) == 0:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )
    return db_partidos


# *************************************************************************************************************************************


@app.post(
    "/partidos/",
    response_model=_schemas.Partidos,
    status_code=_fastapi.status.HTTP_201_CREATED,
    tags=["Partidos"],
)
def create_partido(
    partido: _schemas.PartidosCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    # return _services.create_actividad(db=db, actividad=actividad)
    return _services.create_partido(db=db, token=token, partido=partido)


# *************************************************************************************************************************************


@app.post(
    "/partidos/{id}",
    response_model=_schemas.Partidos,
    status_code=_fastapi.status.HTTP_201_CREATED,
    tags=["Partidos"],
)
async def update_partido(
    id: str,
    partido: _schemas.PartidosCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_partidos = _services.get_partidos_por_id(
        db=db,
        token=token,
        id=_fn.parameter_id(id),
    )
    if db_partidos is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )

    return _services.update_partido(
        db=db,
        token=token,
        db_partido=db_partidos,
        partido=partido,
    )


# *************************************************************************************************************************************


@app.post(
    "/partidos/{id}/delete",
    status_code=_fastapi.status.HTTP_202_ACCEPTED,
    tags=["Partidos"],
)
async def delete_partido(
    id: str,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_partido = _services.get_partidos_por_id(
        db=db,
        token=token,
        id=_fn.parameter_id(id),
    )
    if db_partido is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )
    _services.delete_partido(
        db=db,
        token=token,
        id=_fn.parameter_id(id),
    )
    return {"message": f"El registro: {id} ha sido eliminado"}


# *************************************************************************************************************************************
# SECCION: ESTADISTICAS
# *************************************************************************************************************************************

@app.get(
    "/posiciones/{id_torneo}/{temporada}/list",
    response_model=List[_schemas.Posiciones],
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Estadisticas"],
)
async def read_tabla(
    id_torneo:str,
    temporada:str,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_torneos = _services.get_tabla_posiciones(
        db=db,
          token=token, 
          id_torneo=_fn.parameter_id(id_torneo),
          temporada = temporada

    )
    if len(db_torneos) == 0:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )
    return db_torneos

# *************************************************************************************************************************************

@app.get(
    "/posiciones/{id_torneo}/get_temporadas",
    response_model=List[_schemas.Posiciones],
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Estadisticas"],
)
async def read_tabla(
    id_torneo:str,   
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_torneos = _services.get_tabla_temporadas(
        db=db,
          token=token, 
          id_torneo=_fn.parameter_id(id_torneo),          

    )
    if len(db_torneos) == 0:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )
    return db_torneos


# *************************************************************************************************************************************

@app.get(
    "/tarjetas/list",
    response_model=List[_schemas.Tarjetas],
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Estadisticas"],
)
async def read_tarjetas(
    skip: Optional[int] = None,
    limit: Optional[int] = None,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_tarjetas = _services.get_tarjetas(
        db=db,
        token=token, 
        skip=skip,
        limit=limit

    )
    if len(db_tarjetas) == 0:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )
    
    return db_tarjetas
# *************************************************************************************************************************************

@app.get(
    "/tarjetas/{id_jugador}/get_tarjetas_id",
    response_model=_schemas.Tarjetas,
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Estadisticas"],
)
async def read_tabla(
    id_jugador:str,   
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_torneos = _services.get_tarjetas_por_id(
        db=db,
          token=token, 
          id=_fn.parameter_id(id_jugador),          

    )
    if db_torneos is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )
    return db_torneos
# *************************************************************************************************************************************


@app.post(
    "/tarjetas/",
    response_model=_schemas.Tarjetas,
    status_code=_fastapi.status.HTTP_201_CREATED,
    tags=["Estadisticas"],
)
def create_tarjetas(
    jugador: _schemas.TarjetasCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    # return _services.create_actividad(db=db, actividad=actividad)
    return _services.create_tarjetas(db=db, token=token, jugador=jugador)

# *************************************************************************************************************************************


@app.post(
    "/tarjetas/{id}",
    response_model=_schemas.Tarjetas,
    status_code=_fastapi.status.HTTP_201_CREATED,
    tags=["Estadisticas"],
)
async def update_tarjetas(
    id: str,
    jugador: _schemas.TarjetasCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_jugador = _services.get_tarjetas_por_id(
        db=db,
        token=token,
        id=_fn.parameter_id(id),
    )
    if db_jugador is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )

    return _services.update_tarjetas(
        db=db,
        token=token,
        db_jugador=db_jugador,
        jugador=jugador,
    )

# *************************************************************************************************************************************
# SECCION: GOLES
# *************************************************************************************************************************************


@app.get(
    "/goles/list",
    response_model=List[_schemas.Goleadores],
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Estadisticas"],
)
async def read_goles(
    skip: Optional[int] = None,
    limit: Optional[int] = None,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_goles = _services.get_goles(
        db=db,
        token=token, 
        skip=skip,
        limit=limit

    )
    if len(db_goles) == 0:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )
    
    return db_goles
# *************************************************************************************************************************************

@app.get(
    "/goles/{id}/get_goles_id",
    response_model=_schemas.Tarjetas,
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Estadisticas"],
)
async def read_goles_id(
    id:str,   
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_torneos = _services.get_goles_por_id(
        db=db,
          token=token, 
          id=_fn.parameter_id(id),          

    )
    if db_torneos is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )
    return db_torneos
# *************************************************************************************************************************************


@app.post(
    "/goles/",
    response_model=_schemas.Goleadores,
    status_code=_fastapi.status.HTTP_201_CREATED,
    tags=["Estadisticas"],
)
def create_goles(
    jugador: _schemas.GoleadoresCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    # return _services.create_actividad(db=db, actividad=actividad)
    return _services.create_goles(db=db, token=token, jugador=jugador)

# *************************************************************************************************************************************


@app.post(
    "/goles/{id}",
    response_model=_schemas.Goleadores,
    status_code=_fastapi.status.HTTP_201_CREATED,
    tags=["Estadisticas"],
)
async def update_goles(
    id: str,
    jugador: _schemas.GoleadoresCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_jugador = _services.get_goles_por_id(
        db=db,
        token=token,
        id=_fn.parameter_id(id),
    )
    if db_jugador is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )

    return _services.update_goles(
        db=db,
        token=token,
        db_jugador=db_jugador,
        jugador=jugador,
    )


# *************************************************************************************************************************************
# SECCION: ARCHIVOS
# *************************************************************************************************************************************

@app.get(
    "/archivos_list/",
    response_model=List[_schemas.Archivos],
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Archivos"],
)
async def read_archivos(
    skip: Optional[int] = None,
    limit: Optional[int] = None,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_archivos = _services.get_archivos(
        db=db,
          token=token, 
          skip=skip, limit=limit
    )
    if len(db_archivos) == 0:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )
    return db_archivos

# *************************************************************************************************************************************
@app.get(
    "/archivos/{id}/id",
    response_model=_schemas.Archivos,
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Archivos"],
)
async def read_archivos_por_id(
    id: str,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_archivos = _services.get_archivos_por_id(
        db=db,
        token=token,
        id=_fn.parameter_id(id),
    )
    if db_archivos is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )

    return db_archivos


# *************************************************************************************************************************************


@app.post(
    "/archivos/",
    response_model=_schemas.Archivos,
    status_code=_fastapi.status.HTTP_201_CREATED,
    tags=["Archivos"],
)
def create_torneo(
    archivo: _schemas.ArchivosCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    # return _services.create_actividad(db=db, actividad=actividad)
    return _services.create_archivo(db=db, token=token, file=archivo)


# *************************************************************************************************************************************


@app.post(
    "/archivos/{id}",
    response_model=_schemas.Archivos,
    status_code=_fastapi.status.HTTP_201_CREATED,
    tags=["Archivos"],
)
async def update_archivos(
    id: str,
    file: _schemas.ArchivosCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_file = _services.get_archivos_por_id(
        db=db,
        token=token,
        id=_fn.parameter_id(id),
    )
    if db_file is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )

    return _services.update_archivo(
        db=db,
        token=token,
        db_file=db_file,
        file=file,
    )



# *************************************************************************************************************************************
# SECCION: ADMIN
# *************************************************************************************************************************************


# Es posible ocultar rutas según la condicion de DEVELOPER_MODE (o cualquier otra condicion que pudira necesitarse)
# if _settings.DEVELOPER_MODE:


@app.get(
    "/admin/{id}/alpha_id",
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Admin"],
)
async def get_alpha_id(
    id: int,
    token: str = _fastapi.Depends(_auth.token_bearer()),
):

    # if _auth.token_decode(token)["roles"].upper() != "ADMINISTRATOR":
    #    raise _fastapi.HTTPException(
    #        status_code=_fastapi.status.HTTP_403_FORBIDDEN,
    #        detail="El usuario no tiene privilegios suficientes para ejecutar esta operacion",
    #    )

    alpha_id = _fn.alpha_id(id, to_num=False, pad_up=True, passkey=_settings.PASSKEY_ID)

    return {
        "alpha_id": alpha_id,
    }

# *************************************************************************************************************************************

@app.get(
    "/admin/{id_equipo}/get_usuario_equipo",
    response_model=_schemas.UsuariosLiga,
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Admin"],
)
async def read_usuarios_equipo(
    id_equipo:str,   
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_torneos = _services.get_usuario_por_equipo(
        db=db,
          token=token, 
          id=_fn.parameter_id(id_equipo),          

    )
    if db_torneos is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )
    return db_torneos

# *************************************************************************************************************************************


@app.post(
    "/admin/deploy/me",
    status_code=_fastapi.status.HTTP_202_ACCEPTED,
    tags=["Admin"],
)
async def deploy_me(
    token: str = _fastapi.Depends(_auth.token_bearer()),
):

    if _auth.token_decode(token)["roles"].upper() != "ADMINISTRATOR":
        raise _fastapi.HTTPException(
            status_code=403,
            detail="El usuario no tiene privilegios suficientes para ejecutar esta operacion",
        )
    cmd = ['/srv/.scripts/deploy_api.sh',  f'api-{_settings.APP_TITLE.lower()}']
    result = _subprocess.run(cmd, stdout=_subprocess.PIPE, stderr=_subprocess.PIPE)

    return {"output": result.stdout.decode("utf-8")}

# *************************************************************************************************************************************


@app.post(
    "/admin/update_fields/items",
    status_code=_fastapi.status.HTTP_202_ACCEPTED,
    tags=["Admin"],
)
async def update_item_update_fields(
    background_tasks: _fastapi.BackgroundTasks,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):

    if _auth.token_decode(token)["roles"].upper() != "ADMINISTRATOR":
        raise _fastapi.HTTPException(
            status_code=403,
            detail="El usuario no tiene privilegios suficientes para ejecutar esta operacion",
        )

    background_tasks.add_task(_services.admin_update_all_items, token)

    return {"message": "Los registros están siendo actualizados..."}


# *************************************************************************************************************************************


@app.post(
    "/admin/usuarios/",
    response_model=_schemas.UsuariosLiga,
    status_code=_fastapi.status.HTTP_201_CREATED,
    tags=["Admin"],
)
def create_usuario(
    usuario: _schemas.UsuariosLigaCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_partidos = _services.get_usuario_por_equipo(
        db=db,
        token=token,
        id=_fn.parameter_id(usuario.id_equipo),
    )
    if db_partidos != None:
        raise _fastapi.HTTPException(
            status_code=404, detail="Ya existe un usuario para ese equipo"
        )
    # return _services.create_actividad(db=db, actividad=actividad)
    return _services.create_usuario(db=db, token=token, usuario=usuario)


# *************************************************************************************************************************************


@app.post(
    "/admin/usuarios/{id}",
    response_model=_schemas.UsuariosLiga,
    status_code=_fastapi.status.HTTP_201_CREATED,
    tags=["Admin"],
)
async def update_usuario(
    id: str,
    usuario: _schemas.UsuariosLigaCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_partidos = _services.get_usuario_por_id(
        db=db,
        token=token,
        id=_fn.parameter_id(id),
    )
    if db_partidos is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )

    return _services.update_usuario(
        db=db,
        token=token,
        db_partido=db_partidos,
        usuario=usuario,
    )



# *************************************************************************************************************************************


@app.post(
    "/archivos/{id}/delete",
    status_code=_fastapi.status.HTTP_202_ACCEPTED,
    tags=["Archivos"],
)
async def delete_archivo(
    id: str,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_files = _services.get_archivos_por_id(
        db=db,
        token=token,
        id=_fn.parameter_id(id),
    )
    if db_files is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="No se encontraron registros."
        )
    _services.delete_archivo(
        db=db,
        token=token,
        id=_fn.parameter_id(id),
    )
    return {"message": f"El registro: {id} ha sido eliminado"}



# *************************************************************************************************************************************

# Create the database
# _services.drop_db()
_services.create_db()

# *************************************************************************************************************************************
