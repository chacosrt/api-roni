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
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

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
from pandas_market_calendars import get_calendar
from bs4 import BeautifulSoup
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
# SECCION: CEDULAS
# *************************************************************************************************************************************


def verifica_cedula(
    db: _orm.Session,
    token: str,
    cedula: _schemas.Cedula,
    background_tasks: _fastapi.BackgroundTasks,
):

    cedula_sep = None
    response_parsed = []
    sub = _auth.token_claim(token, "sub")

    if cedula.forzar_busqueda == False:
        if cedula.cedula != "":
            cedula_sep = (
                db.query(_models.CedulaSEP)
                .filter(_models.CedulaSEP.idCedula == cedula.cedula)
                .first()
            )
        else:
            nombre_completo = (
                f"{cedula.nombre.upper()} {cedula.ap_p.upper()} {cedula.ap_m.upper()}"
            )
            cedula_sep = (
                db.query(_models.CedulaBuho)
                .filter(_models.CedulaBuho.nombre_completo.like(nombre_completo))
                .all()
            )

            if len(cedula_sep) == 0:
                cedula_sep = None

    if cedula_sep is None:

        if cedula.cedula != "":
            url = "https://cedulaprofesional.sep.gob.mx/cedula/buscaCedulaJson.action"
            data = (
                'json={"maxResult":"100","nombre":"","paterno":"","materno":"","idCedula":"'
                + cedula.cedula
                + '"}'
            )
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            response = _requests.request("POST", url, headers=headers, data=data)
            json = _json.loads(response.text)

            db_cedula = _models.CedulaSEP(
                anioreg=_fn.is_null(json["items"][0]["anioreg"], 0),
                carArea=_fn.clean_string(json["items"][0]["carArea"]),
                carCons=_fn.clean_string(json["items"][0]["carCons"]),
                carNivel=_fn.clean_string(json["items"][0]["carNivel"]),
                curp=_fn.clean_string(json["items"][0]["curp"]).upper(),
                desins=_fn.clean_string(json["items"][0]["desins"]),
                foja=_fn.clean_string(json["items"][0]["foja"]),
                idCedula=_fn.is_null(json["items"][0]["idCedula"], 0),
                inscons=_fn.is_null(json["items"][0]["inscons"], 0),
                insedo=_fn.is_null(json["items"][0]["insedo"], 0),
                libro=_fn.clean_string(json["items"][0]["libro"]),
                materno=_fn.format_nombre_propio(json["items"][0]["materno"]),
                maternoM=_fn.format_nombre_propio(json["items"][0]["maternoM"]),
                nombre=_fn.format_nombre_propio(json["items"][0]["nombre"]),
                nombreM=_fn.format_nombre_propio(json["items"][0]["nombreM"]),
                numero=_fn.is_null(json["items"][0]["numero"], 0),
                paterno=_fn.format_nombre_propio(json["items"][0]["paterno"]),
                paternoM=_fn.format_nombre_propio(json["items"][0]["paternoM"]),
                sexo=_fn.clean_string(json["items"][0]["sexo"]),
                tipo=_fn.clean_string(json["items"][0]["tipo"]),
                titulo=_fn.clean_string(json["items"][0]["titulo"]),
                filename=_fn.clean_string(json["filename"]),
                idProfesionista=_fn.clean_string(json["idProfesionista"]),
                sessionId=_fn.clean_string(json["sessionId"]),
                theStream=_fn.clean_string(json["theStream"]),
                token=_fn.clean_string(json["token"]),
                urlVideo=_fn.clean_string(json["urlVideo"]),
            )
            db_cedula.sort_field = _fn.clean_string(
                _fn.clean_string(db_cedula.idCedula)
                + " "
                + _fn.format_nombre_propio(db_cedula.nombre)
                + " "
                + _fn.format_nombre_propio(db_cedula.paterno)
                + " "
                + _fn.format_nombre_propio(db_cedula.materno)
                + " "
                + _fn.clean_string(db_cedula.titulo)
            )[:255]
            db_cedula.search_field = _fn.format_search_field(
                _fn.clean_string(db_cedula.idCedula)
                + _fn.format_nombre_propio(db_cedula.nombre)
                + _fn.format_nombre_propio(db_cedula.paterno)
                + _fn.format_nombre_propio(db_cedula.materno)
                + _fn.clean_string(db_cedula.titulo)
            )[:255]
            db_cedula.creado_por = _fn.clean_string(sub)
            db_cedula.creado_el = _dt.datetime.now()
            db_cedula.modificado_por = _fn.clean_string(sub)
            db_cedula.modificado_el = _dt.datetime.now()
            db.add(db_cedula)
            db.commit()
            db.refresh(db_cedula)

            response_parsed.append(_schemas.CedulaResp(**db_cedula.__dict__).dict())
        else:
            url = "https://www.buholegal.com/consultasep/"
            payload = {
                "nombre": cedula.nombre,
                "paterno": cedula.ap_p,
                "materno": cedula.ap_m,
            }
            response = _requests.post(url, data=payload)
            table_MN = pd.read_html(response.text, match="Cédula")
            df = table_MN[0]
            df.head(len(df))
            response = df.to_json(orient="records")
            json = _json.loads(response)

            background_tasks.add_task(crea_cedula_buho, db=db, token=token, cedula=json)
            for resp in json:

                names = format_nombre(resp["Nombre y Apellidos"])

                num_nombres = len(names)
                nombres, apellido1, apellido2 = "", "", ""

                # Cuando no existe nombre.
                if num_nombres == 0:
                    nombres = ""

                # Cuando el nombre consta de un solo elemento.
                elif num_nombres == 1:
                    nombres = names[0]

                # Cuando el nombre consta de dos elementos.
                elif num_nombres == 2:
                    nombres = names[0]
                    apellido1 = names[1]

                # Cuando el nombre consta de tres elementos.
                elif num_nombres == 3:
                    nombres = names[0]
                    apellido1 = names[1]
                    apellido2 = names[2]

                # Cuando el nombre consta de más de tres elementos.
                else:
                    nombres = names[0] + " " + names[1]
                    apellido1 = names[2]
                    apellido2 = names[3]

                esquema_cedula = _schemas.CedulaResp()
                esquema_cedula.idCedula = resp["Cédula"]
                esquema_cedula.nombre = nombres
                esquema_cedula.paterno = apellido1
                esquema_cedula.materno = apellido2
                esquema_cedula.titulo = resp["Carrera"]
                esquema_cedula.desins = resp["Universidad"]
                esquema_cedula.anioreg = resp["Año"]
                if cedula.filtro != "":
                    if (
                        cedula.filtro in resp["Carrera"]
                        or cedula.filtro.title() in resp["Carrera"]
                        or cedula.filtro.upper() in resp["Carrera"]
                    ):

                        response_parsed.append(esquema_cedula)

                else:
                    response_parsed.append(esquema_cedula)

    else:
        if type(cedula_sep) is list:

            for cedula in cedula_sep:
                names = format_nombre(cedula.nombre_completo)

                num_nombres = len(names)
                nombres, apellido1, apellido2 = "", "", ""

                # Cuando no existe nombre.
                if num_nombres == 0:
                    nombres = ""

                # Cuando el nombre consta de un solo elemento.
                elif num_nombres == 1:
                    nombres = names[0]

                # Cuando el nombre consta de dos elementos.
                elif num_nombres == 2:
                    nombres = names[0]
                    apellido1 = names[1]

                # Cuando el nombre consta de tres elementos.
                elif num_nombres == 3:
                    nombres = names[0]
                    apellido1 = names[1]
                    apellido2 = names[2]

                # Cuando el nombre consta de más de tres elementos.
                else:
                    nombres = names[0] + " " + names[1]
                    apellido1 = names[2]
                    apellido2 = names[3]

                cedula_response = _schemas.CedulaResp()
                cedula_response.idCedula = cedula.cedula
                cedula_response.nombre = nombres
                cedula_response.paterno = apellido1
                cedula_response.materno = apellido2
                cedula_response.titulo = cedula.carrera
                cedula_response.desins = cedula.universidad
                cedula_response.anioreg = cedula.anio
                response_parsed.append(cedula_response)
        else:

            response_parsed.append(_schemas.CedulaResp(**cedula_sep.__dict__).dict())

    return response_parsed


# *************************************************************************************************************************************


def crea_cedula_buho(
    cedula: array,
    token: str,
    db: _orm.Session,
):

    sub = _auth.token_claim(token, "sub")
    for resp in cedula:
        db_cedula = _models.CedulaBuho()
        db_cedula.cedula = _fn.clean_string(resp["Cédula"])
        db_cedula.nombre_completo = _fn.clean_string(resp["Nombre y Apellidos"])
        db_cedula.carrera = _fn.clean_string(resp["Carrera"])
        db_cedula.universidad = _fn.clean_string(resp["Universidad"])
        db_cedula.estado = _fn.clean_string(resp["Estado"])
        db_cedula.anio = _fn.is_null(resp["Año"], 0)
        db_cedula.creado_por = _fn.clean_string(sub)
        db_cedula.creado_el = _dt.datetime.now()
        db_cedula.modificado_por = _fn.clean_string(sub)
        db_cedula.modificado_el = _dt.datetime.now()

        cedula_exist = (
            db.query(_models.CedulaBuho)
            .filter(_models.CedulaBuho.cedula == resp["Cédula"])
            .first()
        )

        if cedula_exist is None:

            db.add(db_cedula)
            db.commit()
            db.refresh(db_cedula)


# *************************************************************************************************************************************


def verifica_constancia(rfc: str, id_constancia: str, db: _orm.Session, token: str):

    # Previene errores de SSL & DH ################################################################
    _requests.packages.urllib3.disable_warnings()
    _requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ":HIGH:!DH:!aNULL"
    try:
        _requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += (
            ":HIGH:!DH:!aNULL"
        )
    except AttributeError:
        # no pyopenssl support used / needed / available
        pass
    ###############################################################################################

    constancia_exist = (
        db.query(_models.ConstanciaFiscal)
        .filter(_models.ConstanciaFiscal.id_constancia == id_constancia)
        .first()
    )

    rfc_valid = _rfc.is_valid(number=rfc)

    if constancia_exist is None:
        if id_constancia.isnumeric() and rfc_valid == True:
            # Parámetros de consulta
            url = "https://siat.sat.gob.mx/app/qr/faces/pages/mobile/validadorqr.jsf?D1=10&D2=1&D3="
            # payload = '16090529555_HEGA720104UN8' #ConstanciaIdentificacionFiscal_RFC 14110846841_PPG0610038B1
            payload = id_constancia + "_" + rfc

            # _logger.info(f"[{_settings.JWT_AUDIENCE}] Consulta SAT URL={url}{payload}")

            response = _requests.get(url + payload, verify=False)

            soup = BeautifulSoup(response.content, "html5lib")

            # _logger.info(f"[{_settings.JWT_AUDIENCE}] Consulta SAT={soup}")

            try:
                table_identificacion = soup.find(
                    "ul", id="ubicacionForm:j_idt10:0:j_idt11"
                )

                df = pd.read_html(str(table_identificacion), header=0)
                df[1].columns = ["concepto", "valor"]

                response = df[1].to_json(orient="records")
                identificacion = _json.loads(response)

            except Exception as e:
                _logger.info("Error:" + str(e))
                identificacion = ""

            try:
                table_ubicacion = soup.find("ul", id="ubicacionForm:j_idt10:1:j_idt11")

                df = pd.read_html(str(table_ubicacion), header=0)
                df[1].columns = ["concepto", "valor"]

                response = df[1].to_json(orient="records")
                direccion = _json.loads(response)
            except Exception as e:
                _logger.info("Error:" + str(e))
                direccion = ""

            try:
                table_caracteristicas = soup.find(
                    "ul", id="ubicacionForm:j_idt10:2:j_idt11"
                )

                df = pd.read_html(str(table_caracteristicas), header=0)
                df[1].columns = ["concepto", "valor"]

                response = df[1].to_json(orient="records")
                caracteristicas = _json.loads(response)
            except Exception as e:
                _logger.info("Error:" + str(e))
                caracteristicas = ""

            if identificacion != "":
                constancia = {
                    "id_constancia": id_constancia,
                    "rfc": rfc,
                    "identificacion": identificacion,
                    "direccion": direccion,
                    "caracteristicas": caracteristicas,
                }

                db_constancia = create_constancia(
                    db=db, token=token, constancia=constancia
                )
                # db_constancia = _schemas.ConstanciaFiscalData(**db_constancia.__dict__).dict()
            else:
                db_constancia = _models.ConstanciaFiscal()
                db_constancia.id = 0
                db_constancia.situacion_contribuyente = (
                    "Datos no encontrados / Intente nuevamente"
                )

    else:
        db_constancia = constancia_exist

    return db_constancia


# *************************************************************************************************************************************


def create_constancia(
    db: _orm.Session,
    constancia: array,
    token: str,
):
    sub = _auth.token_claim(token, "sub")

    if len(constancia["identificacion"]) == 8:
        db_constancia = _models.ConstanciaFiscal(
            id_constancia=_fn.clean_string(constancia["id_constancia"]),
            rfc=_fn.clean_string(constancia["rfc"]),
            curp=_fn.clean_string(constancia["identificacion"][0]["valor"]).upper(),
            nombre=_fn.clean_string(constancia["identificacion"][1]["valor"]),
            materno=_fn.clean_string(constancia["identificacion"][3]["valor"]),
            paterno=_fn.clean_string(constancia["identificacion"][2]["valor"]),
            fecha_nacimiento=_dt.datetime.strptime(
                constancia["identificacion"][4]["valor"], "%d-%m-%Y"
            ).strftime("%Y-%m-%d %H:%M:%S"),
            fecha_inicio_operaciones=_dt.datetime.strptime(
                constancia["identificacion"][5]["valor"], "%d-%m-%Y"
            ).strftime("%Y-%m-%d %H:%M:%S"),
            situacion_contribuyente=_fn.clean_string(
                constancia["identificacion"][6]["valor"]
            ),
            fecha_ultimo_cambio=_dt.datetime.strptime(
                constancia["identificacion"][7]["valor"], "%d-%m-%Y"
            ).strftime("%Y-%m-%d %H:%M:%S"),
        )

    if len(constancia["identificacion"]) == 6:
        db_constancia = _models.ConstanciaFiscal(
            id_constancia=_fn.clean_string(constancia["id_constancia"]),
            rfc=_fn.clean_string(constancia["rfc"]),
            razon_social=_fn.clean_string(constancia["identificacion"][0]["valor"]),
            regimen_capital=_fn.clean_string(constancia["identificacion"][1]["valor"]),
            fecha_constitucion=_dt.datetime.strptime(
                constancia["identificacion"][2]["valor"], "%d-%m-%Y"
            ).strftime("%Y-%m-%d %H:%M:%S"),
            fecha_inicio_operaciones=_dt.datetime.strptime(
                constancia["identificacion"][3]["valor"], "%d-%m-%Y"
            ).strftime("%Y-%m-%d %H:%M:%S"),
            situacion_contribuyente=_fn.clean_string(
                constancia["identificacion"][4]["valor"]
            ),
            fecha_ultimo_cambio=_dt.datetime.strptime(
                constancia["identificacion"][5]["valor"], "%d-%m-%Y"
            ).strftime("%Y-%m-%d %H:%M:%S"),
        )

    db_constancia.entidad_federativa = _fn.clean_string(
        constancia["direccion"][0]["valor"]
    )
    db_constancia.municipio_delegacion = _fn.clean_string(
        constancia["direccion"][1]["valor"]
    )
    db_constancia.colonia = _fn.clean_string(constancia["direccion"][2]["valor"])
    db_constancia.tipo_vialidad = _fn.clean_string(constancia["direccion"][3]["valor"])
    db_constancia.nombre_vialidad = _fn.clean_string(
        constancia["direccion"][4]["valor"]
    )
    db_constancia.num_ext = _fn.clean_string(constancia["direccion"][5]["valor"])
    db_constancia.num_int = _fn.clean_string(constancia["direccion"][6]["valor"])
    db_constancia.cp = _fn.clean_string(constancia["direccion"][7]["valor"])
    db_constancia.correo = _fn.clean_string(constancia["direccion"][8]["valor"])
    db_constancia.al = _fn.clean_string(constancia["direccion"][9]["valor"])

    esquema = {}
    x = range(0, len(constancia["caracteristicas"]))

    for n in x:
        if n % 2 == 0:
            pos_fecha = n + 1
            fecha_alta = _dt.datetime.strptime(
                constancia["caracteristicas"][pos_fecha]["valor"], "%d-%m-%Y"
            ).strftime("%Y-%m-%d %H:%M:%S")

            regimen = _models.Regimenes(
                id_constancia=_fn.clean_string(constancia["id_constancia"]),
                regimen=_fn.clean_string(constancia["caracteristicas"][n]["valor"]),
                fecha_alta=fecha_alta,
            )

            regimen.creado_por = _fn.clean_string(sub)
            regimen.creado_el = _dt.datetime.now()
            regimen.modificado_por = _fn.clean_string(sub)
            regimen.modificado_el = _dt.datetime.now()

            db.add(regimen)
            db.commit()
            db.refresh(regimen)

    db_constancia.creado_por = _fn.clean_string(sub)
    db_constancia.creado_el = _dt.datetime.now()
    db_constancia.modificado_por = _fn.clean_string(sub)
    db_constancia.modificado_el = _dt.datetime.now()

    db.add(db_constancia)
    db.commit()
    db.refresh(db_constancia)

    results = db_constancia

    return results


# *************************************************************************************************************************************


def format_nombre(nombre: str):

    # Separar el nombre completo en espacios.
    palabras = nombre.split(" ")

    # Lista donde se guarda las palabras del nombre.
    names = []

    # Palabras de apellidos y nombres compuestos.
    especial_tokens = [
        "da",
        "de",
        "di",
        "do",
        "del",
        "la",
        "las",
        "le",
        "los",
        "mac",
        "mc",
        "van",
        "von",
        "y",
        "i",
        "san",
        "santa",
    ]

    prev = ""
    for token in palabras:
        _token = token.lower()

        if _token in especial_tokens:
            prev += token + " "

        else:
            names.append(prev + token)
            prev = ""

    return names


# *************************************************************************************************************************************
# SECCION: PNN
# *************************************************************************************************************************************


def format_telefono(db: _orm.Session, token: str, telefono: str):
    esquema_telefono = []

    if len(telefono) == 10:

        lada = telefono[0:2]
        numero = 0
        numero_complemento = telefono[-4:]

        if lada == "55" or lada == "56" or lada == "33" or lada == "81":

            numero = telefono[2:6]

        else:
            lada = telefono[0:3]
            numero = telefono[3:6]

        results = (
            db.query(_models.PNN)
            .filter(_models.PNN.nir == int(lada))
            .filter(_models.PNN.serie == int(numero))
            .order_by(_models.PNN.id)
            .first()
        )

        if results is None:

            numero_format = "(" + lada + ") " + numero + "-" + numero_complemento

            if lada == "800":
                tipo = "L"

            else:
                tipo = "N"

            json = {
                "telefono": telefono,
                "telefono_format": numero_format,
                "tipo_red": tipo,
                "estado": "",
                "compania_origen": "",
            }

            esquema_telefono.append(json)

        else:

            numero_format = "(" + lada + ") " + numero + "-" + numero_complemento

            if results.tipo_red == "FIJO":

                tipo = "F"

            if results.tipo_red == "MOVIL":

                tipo = "M"

            json = {
                "telefono": telefono,
                "telefono_format": numero_format,
                "tipo_red": tipo,
                "estado": results.estado,
                "compania_origen": results.razon_social,
            }

            esquema_telefono.append(json)

    else:
        json = {
            "telefono": telefono,
            "telefono_format": "",
            "tipo_red": "N",
            "estado": "",
            "compania_origen": "",
        }

        esquema_telefono.append(json)

    return esquema_telefono


# *************************************************************************************************************************************


def verifica_reg_sanitario(registro: str, db: _orm.Session, token: str):

    sub = _auth.token_claim(token, "sub")
    # Previene errores de SSL & DH ################################################################
    _requests.packages.urllib3.disable_warnings()
    _requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ":HIGH:!DH:!aNULL"
    try:
        _requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += (
            ":HIGH:!DH:!aNULL"
        )
    except AttributeError:
        # no pyopenssl support used / needed / available
        pass
    ###############################################################################################
    _argumento = 0
    # _search_value = '211M2014 SSA'

    reg_s = (
        db.query(_models.RegistroSanitario)
        .filter(_models.RegistroSanitario.num_registro == registro)
        .first()
    )

    if reg_s is None:

        with _requests.Session() as s:
            # define los headers a utilizar
            s.headers[
                "User-Agent"
            ] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"

            # realiza la consulta inicial
            consulta = s.get(
                "https://tramiteselectronicos02.cofepris.gob.mx/BuscadorPublicoRegistrosSanitarios/BusquedaRegistroSanitario.aspx"
            )
            soup = BeautifulSoup(consulta.text, "lxml")
            # llena los valores en la forma
            data = {i["name"]: i.get("value", "") for i in soup.select("input[name]")}
            data["__EVENTTARGET"] = "ctl00$MainContent$ctl00"
            data["ctl00$MainContent$DDL_Argumento"] = _argumento
            data["ctl00$MainContent$txtSearchValue"] = registro
            # ejecuta la consulta
            data.pop("ctl00$MainContent$btnRegresarVista")

            # obtiene los resultados la búsqueda con los parámetros deseados
            tabla_resultados = s.post(
                "https://tramiteselectronicos02.cofepris.gob.mx/BuscadorPublicoRegistrosSanitarios/BusquedaRegistroSanitario.aspx",
                data=data,
            )
            soup = BeautifulSoup(tabla_resultados.text, "lxml")
            # llena los valores en la forma
            data = {i["name"]: i.get("value", "") for i in soup.select("input[name]")}
            data["__EVENTTARGET"] = ""
            data["ctl00$MainContent$DDL_Argumento"] = _argumento
            data["ctl00$MainContent$txtSearchValue"] = registro
            data[
                "ctl00$MainContent$GV_RegistroSanitario$ctl02$BTN_Seleccionar"
            ] = "Seleccionar"
            # ejecuta la consulta
            data.pop("ctl00$MainContent$btnRegresarVista")

            # obtiene el detalle del registro sanitario
            registro_sanitario = s.post(
                "https://tramiteselectronicos02.cofepris.gob.mx/BuscadorPublicoRegistrosSanitarios/BusquedaRegistroSanitario.aspx",
                data=data,
            )
            soup = BeautifulSoup(registro_sanitario.text, "lxml")

            # print(soup)

        tabla_registro_sanitario = soup.find(
            "table", id="MainContent_GV_RegistroSanitario"
        )

        df = pd.read_html(str(tabla_registro_sanitario), header=0)

        df[0].columns = [
            "Número de Registro",
            "Denominación Genérica",
            "Denominación Distintiva",
            "Tipo de Medicamento",
            "Indicación Terapéutica",
            "Titular del Registro",
            "Fabricante del Medicamento",
            "Principio Activo",
            "",
        ]

        tabla_detalle_registro_sanitario = soup.find(
            "table", id="MainContent_registroSanitarioFormView"
        )

        detalle_registro_sanitario = pd.read_html(
            str(tabla_detalle_registro_sanitario), header=0
        )

        response = df[0].to_json(orient="records")
        json = _json.loads(response)

        # detalle = detalle_registro_sanitario[0].columns[0].to_json(orient='records')
        detalle = detalle_registro_sanitario[0].columns[0]
        detalle_json = detalle.replace("Datos del Registro Sanitario ", "")
        print(detalle_json)

        db_registro = _models.RegistroSanitario(
            num_registro=_fn.clean_string(json[0]["Número de Registro"]),
            denominacion_generica=_fn.clean_string(json[0]["Denominación Genérica"]),
            denominacion_distintiva=_fn.clean_string(
                json[0]["Denominación Distintiva"]
            ),
            tipo_medicamento=_fn.clean_string(json[0]["Tipo de Medicamento"]),
            indicacion_terapeutica=_fn.clean_string(json[0]["Indicación Terapéutica"]),
            titular_registro=_fn.clean_string(json[0]["Titular del Registro"]),
            fabricante_medicamento=_fn.clean_string(
                json[0]["Fabricante del Medicamento"]
            ),
            principio_activo=_fn.clean_string(json[0]["Principio Activo"]),
            detalle_registro=_fn.clean_string(detalle_json),
        )

        db_registro.creado_por = _fn.clean_string(sub)
        db_registro.creado_el = _dt.datetime.now()
        db_registro.modificado_por = _fn.clean_string(sub)
        db_registro.modificado_el = _dt.datetime.now()

        db.add(db_registro)
        db.commit()
        db.refresh(db_registro)

        results = db_registro

    else:

        results = reg_s

    return results


# *************************************************************************************************************************************


def generate_pdf(constancia: str, db: _orm.Session, token: str):

    # Load data from JSON file
    regimenes = (
        db.query(_models.Regimenes)
        .filter(_models.Regimenes.id_constancia == constancia)
        .all()
    )

    # Create a PDF canvas
    c = canvas.Canvas("output.pdf", pagesize=letter)

    # Add data to the PDF
    for regimen in regimenes:
        reg = _schemas.Regimenes(**regimen.__dict__).dict()
        constancia = reg["id_constancia"]
        regim = reg["regimen"]
        fecha_alta = reg["fecha_alta"]
        c.drawString(100, 750, f"ID CONSTANCIA: {constancia}")
        c.drawString(100, 700, f"REGIMEN: {regim}")
        c.drawString(100, 650, f"FECHA ALTA: {fecha_alta}")

    """ # Add a table to the PDF
    table_data = [[row['ID CONSTANCIA'], row['REGIMEN'], row['FECHA ALTA']] for row in regimenes]
    c.table(table_data) """

    # Save the PDF file
    # c.save()

    return c.save()


# *************************************************************************************************************************************


def websites_url_check(url: str):

    _requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "ALL:@SECLEVEL=1"

    response_data = {"url": url}

    try:
        response = _requests.get(url, timeout=5, verify=False)
        # response = _requests.head(url, timeout=5, verify=False)
        if response.status_code < 500:
            response_data["status"] = "online"
            response_data["status_code"] = response.status_code
            response_data["response_time"] = round(response.elapsed.total_seconds(), 2)
            response_data["error"] = ""
        else:
            response_data["status"] = "offline"
            response_data["status_code"] = response.status_code
            response_data["error"] = ""
    except _requests.exceptions.RequestException as e:
        response_data["status"] = "offline"
        response_data["error"] = str(e)

    try:
        hostname = url.split("://")[1].split("/")[0]
        port = 443

        # create SSL context
        context = ssl.create_default_context()
        context.set_ciphers("DEFAULT@SECLEVEL=1")
        context.minimum_version = ssl.TLSVersion.TLSv1_2

        # verify server certificate
        with context.wrap_socket(socket.socket(), server_hostname=hostname) as ssock:
            ssock.settimeout(5)
            ssock.connect((hostname, port))
            cert = ssock.getpeercert(binary_form=True)

        # extract certificate properties
        cert_parsed = x509.load_der_x509_certificate(cert, default_backend())

        # get certificate info
        response_data["issuer"] = str(cert_parsed.issuer)
        response_data["subject"] = str(cert_parsed.subject)
        response_data["serial_number"] = str(cert_parsed.serial_number)
        response_data["not_valid_before"] = str(cert_parsed.not_valid_before)
        response_data["not_valid_after"] = str(cert_parsed.not_valid_after)
        response_data["signature_algorithm"] = str(cert_parsed.signature_algorithm_oid)

        # get server info
        server_info = response.headers.get("Server")
        if server_info is not None:
            response_data["server_info"] = server_info

        # get OS info
        os_info = response.headers.get("X-Powered-By")
        if os_info is not None:
            response_data["os_info"] = os_info

    except Exception as e:
        if "certificate has expired" in str(e) or "certificate is not yet valid" in str(
            e
        ):
            response_data["warning"] = "The SSL certificate is expired or not yet valid"
        response_data["error"] = str(e)

    # json = _json.dumps(response_data)

    # json_load = _json.loads(json)

    return response_data


# *************************************************************************************************************************************


def websites_update_check(db: _orm.Session, token: str):
    sub = _auth.token_claim(token, "sub")
    urls = _settings.CHOICES
    bloque = folia_bloque(db=db)

    free_warning = True

    try:
        for url in urls:
            url_status = websites_url_check(url=url["clave"])
            url_schema = _schemas.WebSitesCheckCreate(**url_status)

            if url_schema.status_code == 0:
                url_schema.status_code = 502

            if url_schema.status == "offline":
                free_warning = False

            db_url = _models.WebSitesCheck(
                url=_fn.clean_string(url_schema.url),
                status=_fn.clean_string(url_schema.status),
                status_code=_fn.is_null(url_schema.status_code, 0),
                response_time=_fn.is_null(url_schema.response_time, 0),
                issuer=_fn.clean_string(url_schema.issuer),
                subject=_fn.clean_string(url_schema.subject),
                serial_number=_fn.clean_string(url_schema.serial_number),
                not_valid_before=_fn.format_datetime(url_schema.not_valid_before),
                not_valid_after=_fn.format_datetime(url_schema.not_valid_after),
                signature_algorithm=_fn.clean_string(url_schema.signature_algorithm),
                server_info=_fn.clean_string(url_schema.server_info),
                error=_fn.clean_string(url_schema.error),
            )

            db_url.bloque = _fn.is_null(bloque, 0)
            db_url.creado_por = _fn.clean_string(sub)
            db_url.creado_el = _dt.datetime.now()
            db_url.modificado_por = _fn.clean_string(sub)
            db_url.modificado_el = _dt.datetime.now()

            db.add(db_url)
            db.commit()
            db.refresh(db_url)

        results = (
            db.query(_models.WebSitesCheck)
            .filter(_models.WebSitesCheck.bloque == bloque)
            .all()
        )

        warning = db.query(_models.WebSitesWarning).first()

        if warning is None:
            db_warning = _models.WebSitesWarning(
                bloque=_fn.is_null(bloque, 0),
                free_warnings=_fn.is_null(free_warning, False),
            )

            db_warning.bloque = _fn.is_null(bloque, 0)
            db_warning.creado_por = _fn.clean_string(sub)
            db_warning.creado_el = _dt.datetime.now()
            db_warning.modificado_por = _fn.clean_string(sub)
            db_warning.modificado_el = _dt.datetime.now()

            db.add(db_warning)
            db.commit()
            db.refresh(db_warning)

        else:
            warning.bloque = _fn.is_null(bloque, 0)
            warning.free_warnings = _fn.is_null(free_warning, False)
            warning.modificado_por = _fn.clean_string(sub)
            warning.modificado_el = _dt.datetime.now()

            db.commit()
            db.refresh(warning)

        return results

    except Exception as e:
        _logger.error("Error:" + str(e))


# *************************************************************************************************************************************


def websites_status_check(db: _orm.Session, token: str):
    rows = len(_settings.CHOICES)
    # max_id = (
    #     db.query(_models.WebSitesCheck)
    #     .order_by(_models.WebSitesCheck.id.desc())
    #     .first()
    # )
    # results = (
    #     db.query(_models.WebSitesCheck)
    #     .filter(_models.WebSitesCheck.bloque == max_id.bloque)
    #     .order_by(_models.WebSitesCheck.id)
    #     .all()
    # )

    results = (
        db.query(_models.WebSitesCheck)
        #    .filter(_models.WebSitesCheck.bloque == max_id.bloque)
        .order_by(_models.WebSitesCheck.id.desc())
        .limit(rows)
        .all()
    )

    sorted_results = sorted(results, key=lambda x: x.id)

    return sorted_results


# *************************************************************************************************************************************


def websites_warning_check(db: _orm.Session, token: str):

    results = db.query(_models.WebSitesWarning).first()

    return results


# *************************************************************************************************************************************


def get_dia_habil(db: _orm.Session, token: str, fecha:_dt.date.today()):

   # Establecer la configuración regional en español
   # _lc.setlocale(_lc.LC_TIME, 'es_ES.UTF-8')
   
    dias_semana = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]

    dias_descanso = ["Saturday","Sunday"]

    fecha_entrega  = fecha + _dt.timedelta(days=1)
    dia_semana_numero = fecha_entrega.weekday()
    dia_semana_nombre = _cal.day_name[dia_semana_numero]

    siguiente_dia = {}
    siguiente_dia["dia_semana"] = dias_semana[dia_semana_numero]
    siguiente_dia["fecha"] = fecha_entrega

    dia_festivo = db.query(_models.DiasFestivos).filter(_models.DiasFestivos.fecha == fecha_entrega).first()

    if dia_festivo is None:

        if dia_semana_nombre in dias_descanso:

            fecha_entrega = get_dia_habil(db=db, token=token, fecha=fecha_entrega)
            siguiente_dia["dia_semana"] = fecha_entrega["dia_semana"]
            siguiente_dia["fecha"] = fecha_entrega["fecha"]

        else:
        
            siguiente_dia["dia_semana"] = dias_semana[dia_semana_numero]
            siguiente_dia["fecha"] = fecha_entrega

    else:

        fecha_entrega = get_dia_habil(db=db, token=token, fecha=fecha_entrega)
        siguiente_dia["dia_semana"] = fecha_entrega["dia_semana"]
        siguiente_dia["fecha"] = fecha_entrega["fecha"]


    return siguiente_dia

# *************************************************************************************************************************************


def create_dia_descanso(
    db: _orm.Session,
    dia: _schemas.DiaDescansoCreate,
    token: str,
):
    sub = _auth.token_claim(token, "sub")

    db_dia = _models.DiasFestivos(
        
        fecha = _fn.format_date(dia.fecha),
        dia_semana = _fn.clean_string(dia.dia_semana),
        descripcion = _fn.clean_string(dia.descripcion)
    )

    db_dia.creado_por = _fn.clean_string(sub)
    db_dia.creado_el = _dt.datetime.now()
    db_dia.modificado_por = _fn.clean_string(sub)
    db_dia.modificado_el = _dt.datetime.now()
    
    db.add(db_dia)
    db.commit()
    db.refresh(db_dia)

    return db_dia

# *************************************************************************************************************************************

def get_bin(
    db: _orm.Session,
    bin: str,
    token: str,
):
    sub = _auth.token_claim(token, "sub")

    bin = db.query(_models.Bines).filter(_models.Bines.bin == bin).first()

    return bin

# *************************************************************************************************************************************
def folia_bloque(db: _orm.Session):
    last_record = db.query(_expression.func.max(_models.WebSitesCheck.id)).scalar()
    next_record = _fn.is_null(last_record, 0) + 1
    return next_record


# *************************************************************************************************************************************

def calcula_numero( numero:str):

    if not numero.isdigit():
        return None
    
    numero = numero[::-1]  # Invertir la cadena
    
    sum = 0
    for n in range(len(numero)):
        temp = int(numero[n])
        if (n + 1) % 2 == 1:
            temp = temp + temp
            if temp > 9:
                temp = temp - 9
        sum = sum + temp
    
    while sum > 10:
        sum = sum - 10
    
    return int(str(10 - sum)[-1])

# *************************************************************************************************************************************

def genera_referencia(db: _orm.Session, token: str,origen:str ):

    ref = db.query(_models.Referencias).filter(_models.Referencias.origen==origen).first()
    # Convierte el numero a cadena y elimina espacios
    numero = ref.valor + 1
    base = str(numero).strip()
    
    # Valida la longitud y llena con 0s en caso necesario
    if len(base) != 6:
        base = base.zfill(6)
    
    # Calcula digito
    verificador = calcula_numero(base)

    referencia = (str(numero) + str(verificador))

    ref.valor = numero
    db.commit()
    db.refresh(ref)
    
    return {"referencia":referencia}

# *************************************************************************************************************************************

def folia_documentos(db: _orm.Session, token: str,origen:str ):

    ref = db.query(_models.Referencias).filter(_models.Referencias.origen==origen).first()
    # Convierte el numero a cadena y elimina espacios
    numero = ref.valor + 1
    base = str(numero).strip()
    
    # Valida la longitud y llena con 0s en caso necesario
    if len(base) != 6:
        base = base.zfill(6)
    
    # Calcula digito
    verificador = calcula_numero(base)

    folio = (str(numero) + str(verificador))

    ref.valor = numero
    db.commit()
    db.refresh(ref)
    
    return {"folio":folio}


# **************************************************************************************************************************************

def generate_card_number(card:_schemas.TarjetaLocal):
    
    # prefix: Constante 8
    # issuer: 3 dígitos correspondientes a la empresa emisora (034)
    # reference_number: referencia del cliente (8 dígitos - o menos -, incluye digito verificador)
    # type: 0 -->Lealtad, 1 --> crédito propio
    # card_index: consecutivo de credito(s) del cliente por default
    
    # llena con 0s a la izquierda si la longitud es menor a 8
    reference_number_str = str(card.reference_number).zfill(8) 
    
    # llena con 0s a la izquierda si la longitud es menor a 3
    card_index_str = str(card.card_index).zfill(2)
    
    # forma el numero de tarjeta
    prefix_issuer = str(card.prefix) + str(card.issuer).zfill(3)
    reference_number = reference_number_str[:8] # maximo 8 dígitos
    type_str = str(card.type)[:1] # un solo digito
    card_index = card_index_str[:2] # maximo 2 digitos
    card_number = prefix_issuer + reference_number + type_str + card_index
        
    # Calcula el digito verificador
    check_digit = calcula_numero(card_number)
    
    # Retorna el numero de tarjeta final
    return {"num_tarjeta":int(card_number + str(check_digit))}