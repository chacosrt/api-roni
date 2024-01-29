# import pydantic as _pydantic
# class Settings(_pydantic.BaseSettings):
#     pass

import yaml as _yaml
import json as _json

# *************************************************************************************************************************************
# BACKEND
# *************************************************************************************************************************************

""" with open("../.backend.yaml") as stream:
    config = _yaml.safe_load(stream)

ROOT_URL = config["root_url"]
JANUS_URL = config["janus_url"]
WORMHOLE_URL = config["wormhole_url"]
ARENA_URL = config["arena_url"]
QUADRANT_URL = config["quadrant_url"]
MARBLE_URL = config["marble_url"]
PILLS_URL = config["pills_url"]
TRACKER_URL = config["tracker_url"]
NEWTON_URL = config["newton_url"]
HUBBLE_URL = config["hubble_url"] """

# *************************************************************************************************************************************
# SETTINGS
# *************************************************************************************************************************************

# Obtiene los valores para validar el JWToken de un archivo externo
# En producción deberá estar en una ruta no accesible y con los permisos correspondientes
with open("../.settings.yaml") as stream:
    config = _yaml.safe_load(stream)

DEVELOPER_MODE = config["developer_mode"]

PASSKEY_ID = config["passkey_id"]


JWT_SECRET = config["secret"]
JWT_ALGORITHM = config["algorithm"]
JWT_AUDIENCE = config["audience"]
#WT_AUTHORIZATION_URL = JANUS_URL + "/badge"
# config["authorization_url"]
JWT_AUTHORIZATION_TTL = config["authorization_ttl"]

DATABASE_ENGINE = config["database_engine"]

SQL_DRIVER = config["sqlserver_driver"]
SQL_USERNAME = config["sqlserver_username"]
SQL_PSSWD = config["sqlserver_password"]
SQL_SERVERNAME = config["sqlserver_servername"]
# SQL_INSTANCENAME = "\SQLEXPRESS" --> no se utiliza
SQL_DB = config["sqlserver_databasename"]
# SQL_TABLE = "perftest" --> no se utiliza

PSQL_USERNAME = config["postgresql_username"]
PSQL_PSSWD = config["postgresql_password"]
PSQL_SERVERNAME = config["postgresql_servername"]
PSQL_DB = config["postgresql_databasename"]

MYSQL_USERNAME = config["mysql_username"]
MYSQL_PSSWD = config["mysql_password"]
MYSQL_SERVERNAME = config["mysql_servername"]
MYSQL_DB = config["mysql_databasename"]

# Nombre de la base de datos/cadena de conexión ... en este caso sqllite3
SQLITE_FILENAME = config["sqlite_filename"]
SQLALCHEMY_DATABASE_URL = "sqlite:///" + SQLITE_FILENAME
# SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc://{SQL_USERNAME}:{SQL_PSSWD}@{SQL_SERVERNAME}/{SQL_DB}?driver={SQL_DRIVER}"
# Número máximo de registros (por default) que retornará la base de datos
RETURN_DEFAULT_ROWS = 20
RETURN_MAX_ROWS = 100

DEFAULT_PRECISSION = 4
CACHE_TTL_PACK = 10
CACHE_TTL_CT = 10
CACHE_TTL_PERSONAS = 10
CACHE_TTL_INVENTARIOS = 10

LOG_FILENAME = config["log_filename"]

APP_TITLE = config["app_title"]
APP_ROOT_PATH = config["app_root_path"]
APP_DOCS_URL = config["app_docs_url"]
APP_REDOC_URL = config["app_redoc_url"]

ORIGINS_URL = config["origins_url"]


# *************************************************************************************************************************************
# SECCION: REFERENCIA - VALORES CONSTANTES
# *************************************************************************************************************************************

ONLY_LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
ONLY_NUMBERS = "0123456789"
ALPHABET = ONLY_LETTERS + ONLY_NUMBERS

# Obtiene los valores del archivo EXTRAS
with open("../data/extras.json") as json_file:
    EXTRAS = _json.load(json_file)
    EXTRAS.sort(key=lambda x: (x["grupo"], x["descripcion"]))

# Obtiene los valores del archivo CHOICES
with open("../data/choices.json") as json_file:
    CHOICES = _json.load(json_file)
    CHOICES.sort(key=lambda x: (x["grupo"], x["id"]))

# Asigna los valores obtenidos de acuerdo al grupo
#ITEM = list(filter(lambda x: x["grupo"].upper() == "TIPO_ITEM", CHOICES))

# Elimina de memoria la variable CHOICES
#del CHOICES


# Obtiene los valores del archivo PERFILES
# with open("../data/perfiles.json") as json_file:
#    PERFILES = _json.load(json_file)
#    PERFILES.sort(key=lambda x: (x["persona_fisica_o_moral"], x["clave"]))
