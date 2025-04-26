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


if _settings.DATABASE_ENGINE == "MYSQL":
    engine = _sql.create_engine(
        f"mysql+mysqlconnector://{_settings.MYSQL_USERNAME}:{_settings.MYSQL_PSSWD}@{_settings.MYSQL_SERVERNAME}:3306/{_settings.MYSQL_DB}",pool_pre_ping=True,pool_size=10,         # aumenta si es necesario
        max_overflow=20,      # conexiones extra temporales
        pool_timeout=30 
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
