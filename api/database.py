import sqlalchemy as _sql
import sqlalchemy.ext.declarative as _declarative
import sqlalchemy.orm as _orm

# import urllib
# import pyodbc

import settings as _settings

#######################################################################################################
# EN CASO DE UTILIZAR SQLSERVER ESTOS SON LOS PARAMETROS Y CADENA DE CONEXION                         #
# NOTA: Estos parámetros deben estar en un archivo seguro y ser accesados desde settings.py           #
#       también puede ser necesario hacer algunos ajustes en el código.                               #
#######################################################################################################

# DRIVER = "ODBC Driver 17 for SQL Server"
# USERNAME = "database_user"
# PSSWD = "database_password"
# SERVERNAME = "192.168.xxx.xxx"
# #INSTANCENAME = "\SQLEXPRESS" --> no se utiliza
# DB = "database_name"
# #TABLE = "perftest" --> no se utiliza
#
# engine = _sql.create_engine(
#    f"mssql+pyodbc://{USERNAME}:{PSSWD}@{SERVERNAME}/{DB}?driver={DRIVER}", fast_executemany=True
# )


if _settings.DATABASE_ENGINE == "MS-SQL":
    engine = _sql.create_engine(
        f"mssql+pyodbc://{_settings.SQL_USERNAME}:{_settings.SQL_PSSWD}@{_settings.SQL_SERVERNAME}/{_settings.SQL_DB}?driver={_settings.SQL_DRIVER}",
        fast_executemany=True,
    )

if _settings.DATABASE_ENGINE == "SQLITE3":
    SQLALCHEMY_DATABASE_URL = _settings.SQLALCHEMY_DATABASE_URL
    engine = _sql.create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

if _settings.DATABASE_ENGINE == "PSQL":
    engine = _sql.create_engine(
        f"postgresql://{_settings.PSQL_USERNAME}:{_settings.PSQL_PSSWD}@{_settings.PSQL_SERVERNAME}/{_settings.PSQL_DB}"
    )

# crea la session
SessionLocal = _orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = _declarative.declarative_base()
