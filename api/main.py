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
]
app.add_middleware(
    _cors.CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
# SECCION: CEDULAS
# *************************************************************************************************************************************

@app.post(
    "/cedula/",
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Cedulas"],
)
def verificar_cedula(
    background_tasks: _fastapi.BackgroundTasks,
    cedula: _schemas.Cedula,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
    
):
    db_cedula = _services.verifica_cedula(db=db, token=token,cedula=cedula,background_tasks=background_tasks)

    return db_cedula

# *************************************************************************************************************************************
# SECCION: CONSTANCIA FISCAL
# *************************************************************************************************************************************

@app.post(
    "/constancia/",
    response_model=_schemas.ConstanciaFiscalData,
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Constancia Fiscal"],
)
def verificar_constancia(
    constancia: str,
    rfc:str,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_constancia = _services.verifica_constancia(db=db,token=token,id_constancia=constancia,rfc=rfc)

    return db_constancia


# *************************************************************************************************************************************
# SECCION: PNN
# *************************************************************************************************************************************
@app.get(
    "/pnn_telefono/",
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["PLAN NACIONAL DE NUMERACION"],
)
async def get_telefono(
    telefono: str ,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
    
):
    db_pnn = _services.format_telefono(
        db=db, token=token, telefono=telefono
    )
    
    return db_pnn


# *************************************************************************************************************************************
# SECCION: REGISTRO SANITARIO
# *************************************************************************************************************************************

@app.post(
    "/registro/",
    response_model=_schemas.RegistroSanitario,
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Registro Sanitario"],
)
def get_reg_sanitario(
    registro: str,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_registro = _services.verifica_reg_sanitario(db=db,token=token,registro=registro)

    return db_registro

# *************************************************************************************************************************************
# SECCION: PDF GENERATOR
# *************************************************************************************************************************************

@app.post(
    "/pdf_generator/",
    #response_model=_schemas.RegistroSanitario,
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["PDF GENERATOR"],
)
def get_pdf(
    constancia: str,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_registro = _services.generate_pdf(db=db,token=token,constancia=constancia)

    return db_registro

# *************************************************************************************************************************************
# SECCION: WEB SITES CHECK
# *************************************************************************************************************************************

@app.get(
    "/web_sites_url/",
    #response_model=_schemas.RegistroSanitario,
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["WEB SITES CHECK"],
)
def websites_check_url(
    url: str,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_url = _services.websites_url_check(url=url)

    return db_url 

# *************************************************************************************************************************************

@app.get(
    "/web_sites_status/",
    response_model=List[_schemas.WebSitesCheck],
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["WEB SITES CHECK"],
)
def websites_check_status(
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_url = _services.websites_status_check(db=db,token=token)

    return db_url 

# *************************************************************************************************************************************

@app.get(
    "/web_sites_warning/",
    response_model=_schemas.WebSitesWarning,
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["WEB SITES CHECK"],
)
def websites_check_warning(
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_url = _services.websites_warning_check(db=db,token=token)

    return db_url 

# *************************************************************************************************************************************

@app.post(
    "/web_sites_update/",
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["WEB SITES CHECK"],
)
def websites_check_update(
    background_tasks: _fastapi.BackgroundTasks,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):

    background_tasks.add_task( _services.websites_update_check,db, token)

    return {"message": "Los registros están siendo actualizados..."}

# *************************************************************************************************************************************

@app.get(
    "/sig_dia_habil/",
    #response_model=_schemas.WebSitesWarning,
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["DIAS HABILES"],
)
def get_sig_dia(
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
    fecha: _dt.date = _dt.date.today()
):
    db_url = _services.get_dia_habil(db=db,token=token,fecha=fecha)

    return db_url


# *************************************************************************************************************************************

@app.post(
    "/create_dia_descanso/",
    response_model=_schemas.DiaDescanso,
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["DIAS HABILES"],
)
def create_dia_descanso(
    dia: _schemas.DiaDescansoCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
    
):
    db_url = _services.create_dia_descanso(db=db,token=token,dia=dia)

    return db_url

# *************************************************************************************************************************************
# SECCION: BINES
# *************************************************************************************************************************************

@app.get(
    "/bines/",
    response_model=_schemas.Bines,
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Bines"],
)
def get_bin(
    bin: str,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_bin = _services.get_bin(db=db,token=token,bin=bin)

    return db_bin

# *************************************************************************************************************************************
# SECCION: REFERENCIAS
# *************************************************************************************************************************************

@app.get(
    "/calcula_numero/",
    #response_model=_schemas.Bines,
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Referencias"],
)
def get_numero(
    numero: str,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_ref = _services.calcula_numero(numero=numero)

    return db_ref

# *************************************************************************************************************************************
@app.get(
    "/referencias/",
    #response_model=_schemas.Bines,
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Referencias"],
)
def get_referencia(
    origen: str,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_ref = _services.genera_referencia(db=db,token=token,origen=origen)

    return db_ref

# *************************************************************************************************************************************

@app.get(
    "/referencias/folia_documento",
    #response_model=_schemas.Bines,
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Referencias"],
)
def get_folio_documento(
    origen: str,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_ref = _services.folia_documentos(db=db,token=token,origen=origen)

    return db_ref

# *************************************************************************************************************************************
# SECCION: TARJETAS LOCALES
# *************************************************************************************************************************************

@app.post(
    "/genera_tarjeta/",
    #response_model=_schemas.Bines,
    status_code=_fastapi.status.HTTP_200_OK,
    tags=["Tarjetas"],
)
def get_tarjeta(
    card:_schemas.TarjetaLocal,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    token: str = _fastapi.Depends(_auth.token_bearer()),
):
    db_card = _services.generate_card_number(card=card)

    return db_card

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

# Create the database
# _services.drop_db()
_services.create_db()

# *************************************************************************************************************************************
