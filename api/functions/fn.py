import datetime as _dt
import hashlib as _hashlib
import logging as _logging
import math as _math
import random as _random
import string as _string
import unicodedata as _unicodedata
import database as _database

import requests as _requests
import settings as _settings

_ALPHA_SPREAD = 100000000  # evita que alpha_id, parameter_id retorne cadenas cortas

_logger = _logging.getLogger(__name__)


def web_site_online(url, timeout=5):
    try:
        req = _requests.head(url, timeout=timeout)
        # HTTP errors are not raised by default, this statement does that
        req.raise_for_status()
        _logger.info(f"{url} is online.")
        return True
    except _requests.HTTPError as e:
        _logger.error(
            f"{url} Checking internet connection failed, status code {0}.".format(
                e.response.status_code
            )
        )
    except _requests.ConnectionError:
        _logger.error(f"{url} No internet connection available.")
    return False


def left(value, length):
    value = str(is_null(value, ""))
    if length < 1:
        return ""
    else:
        return value[:length]


def right(value, length):
    value = str(is_null(value, ""))
    if length < 1:
        return ""
    else:
        return value[-length:]


def mid(value, start, length):
    value = str(is_null(value, ""))
    if length < 1:
        return ""
    else:
        return value[start : start + length]


# *************************************************************************************************************************************


def is_null(value, returnValue):
    try:
        if value is None:
            return returnValue
        elif str(value) == "None":
            return returnValue
        else:
            return value
    except:
        value = value
        return value


# *************************************************************************************************************************************


def clean_string(value):
    value = is_null(value, "")
    try:
        value = " ".join(
            _unicodedata.normalize("NFD", value)
            .encode("ascii", "ignore")
            .decode("utf-8")
            .split()
        )
    except:
        value = value
    return str(value)


# *************************************************************************************************************************************


def remove_spaces(value):
    try:
        value = value.translate({ord(c): None for c in _string.whitespace})
    except:
        value = value
    return str(value)


# *************************************************************************************************************************************


def format_codigo_postal_mx(value):
    value = str("0" + right(clean_string(value)), 5)
    return str(value)


# *************************************************************************************************************************************


def format_search_field(value):
    value = remove_spaces(clean_string(value)).lower()
    value = value.replace("`", "")
    value = value.replace("'", "")
    value = value.replace('"', "")
    value = value.replace("-", "")
    value = value.replace("(", "")
    value = value.replace(")", "")
    value = value.replace("+", "")
    value = value.replace("-", "")
    value = value.replace("*", "")
    value = value.replace(".", "")
    value = value.replace(",", "")
    value = value.replace(":", "")
    value = value.replace(";", "")

    value = value.replace("aa", "a")
    value = value.replace("ee", "e")
    value = value.replace("ii", "i")
    value = value.replace("oo", "o")
    value = value.replace("uu", "u")
    value = value.replace("rr", "r")

    value = value.replace("ll", "l")

    value = value.replace("b", "B")
    value = value.replace("v", "B")

    value = value.replace("c", "C")
    value = value.replace("s", "C")
    value = value.replace("z", "C")

    value = value.replace("k", "K")
    value = value.replace("qu", "K")

    value = value.replace("g", "G")
    value = value.replace("j", "G")
    value = value.replace("x", "G")
    value = value.replace("y", "G")
    value = value.replace("i", "G")

    value = value.replace("h", "")
    value = value.replace("w", "|")

    return str(value)


# *************************************************************************************************************************************


def is_date(value):
    try:
        if isinstance(value, _dt.datetime):
            return True
        else:
            if value != _dt.datetime.strptime(value, "%Y-%m-%d").strftime("%Y-%m-%d"):
                raise ValueError
            return True
    except ValueError:
        return False


# *************************************************************************************************************************************


def is_datetime(value):
    try:
        if isinstance(value, _dt.datetime):
            return True
        else:
            if value != _dt.datetime.strptime(value, "%Y-%m-%d %H:%M:%S").strftime(
                "%Y-%m-%d %H:%M:%S"
            ):
                raise ValueError
            return True
    except ValueError:
        return False


# *************************************************************************************************************************************


def is_datetime_ms(value):
    try:
        if isinstance(value, _dt.datetime):
            return True
        else:

            if value != _dt.datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            ):
                raise ValueError
            return True
    except ValueError:
        return False


# *************************************************************************************************************************************


def format_date(value):
    if isinstance(value, _dt.datetime):
        # return value.strftime("%Y-%m-%d")
        return value.date()
    else:
        value = is_null(str(value), "")
        if is_date(value):
            return _dt.datetime.strptime(value, "%Y-%m-%d").strftime("%Y-%m-%d")
        if is_datetime(value):
            return _dt.datetime.strptime(value, "%Y-%m-%d %H:%M:%S").strftime(
                "%Y-%m-%d"
            )
        if is_datetime_ms(value):
            return _dt.datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%Y-%m-%d"
            )

        return None


# *************************************************************************************************************************************


def format_datetime(value):
    if isinstance(value, _dt.datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S.%f")
    else:
        value = is_null(str(value), "")
        if is_date(value):
            return _dt.datetime.strptime(value, "%Y-%m-%d").strftime(
                "%Y-%m-%d 00:00:00.000000"
            )[:-3]
        if is_datetime(value):
            return _dt.datetime.strptime(value, "%Y-%m-%d %H:%M:%S").strftime(
                "%Y-%m-%d %H:%M:%S.000000"
            )[:-3]
        if is_datetime_ms(value):
            return _dt.datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            )[:-3]
        return None


# *************************************************************************************************************************************


def format_nombre_propio(value):
    value = is_null(value, "")
    value = clean_string(value).title()

    # Tipos de sociedades Mercantiles
    value = value.replace("S.a. ", "S.A. ")
    value = value.replace("C.v. ", "C.V. ")
    value = value.replace("R.l. ", "R.L. ")
    value = value.replace("S.c. ", "S.C. ")
    value = value.replace("N.c. ", "N.C. ")
    value = value.replace("C.s. ", "C.S. ")
    value = value.replace("S.a.s. ", "S.A.S. ")
    value = value.replace("S.a.p.i. ", "S.A.P.I. ")

    # Valores en nombres y apellidos
    value = value.replace("De La ", "de la ")
    value = value.replace("De Los ", "de los ")
    value = value.replace("De Las ", "de las ")
    value = value.replace("Del ", "del ")
    value = value.replace("De ", "de ")
    value = value.replace("Las ", "las ")
    value = value.replace("La ", "la ")
    value = value.replace("Los ", "los ")
    value = value.replace("Y ", "y ")

    # CONJUNCIONES
    value = value.replace(" Y ", " y ")
    value = value.replace(" E ", " e ")
    value = value.replace(" Ni ", " ni ")
    value = value.replace(" O ", " o ")
    value = value.replace(" U ", " u ")
    value = value.replace(" Pero ", " pero ")
    value = value.replace(" Mas ", " mas ")
    value = value.replace(" Sino ", " sino ")
    value = value.replace(" Aunque ", " aunque ")
    value = value.replace(" Porque ", " porque ")
    value = value.replace(" Pues ", " pues ")
    value = value.replace(" Si ", " si ")
    value = value.replace(" Tan ", " tan ")
    value = value.replace(" Tanto ", " tanto ")
    value = value.replace(" Que ", " que ")
    value = value.replace(" Luego ", " luego ")
    # value = value.replace(" Para ", " para ")
    value = value.replace(" Que ", " que ")
    value = value.replace(" Si ", " si ")

    # ARTICULOS
    value = value.replace(" El ", " el ")
    value = value.replace(" La ", " la ")
    value = value.replace(" Los ", " los ")
    value = value.replace(" Las ", " las ")
    value = value.replace(" Un ", " un ")
    value = value.replace(" Una ", " una ")
    value = value.replace(" Unos ", " unos ")
    value = value.replace(" Unas ", " unas ")
    value = value.replace(" Del ", " del ")
    value = value.replace(" Al ", " al ")

    # CONJUNCIONES
    value = value.replace(" Y ", " y ")
    value = value.replace(" O ", " o ")

    # PREPOSICIONES
    value = value.replace(" A ", " a ")
    value = value.replace(" Ante ", " ante ")
    value = value.replace(" Bajo ", " bajo ")
    value = value.replace(" Cabe ", " cabe ")
    value = value.replace(" Con ", " con ")
    value = value.replace(" Contra ", " contra ")
    value = value.replace(" De ", " de ")
    value = value.replace(" Desde ", " desde ")
    value = value.replace(" En ", " en ")
    value = value.replace(" Entre ", " entre ")
    value = value.replace(" Hacia ", " hacia ")
    value = value.replace(" Hasta ", " hasta ")
    value = value.replace(" Para ", " para ")
    value = value.replace(" Por ", " por ")
    value = value.replace(" Segun ", " segun ")
    value = value.replace(" Sin ", " sin ")
    value = value.replace(" So ", " so ")
    value = value.replace(" Sobre ", " sobre ")
    value = value.replace(" Tras ", " tras ")

    return str(value)


def clean_nombre_propio(value):
    value = is_null(value, "")
    value = clean_string(value).title()

    # Tipos de sociedades Mercantiles
    value = value.replace("S.a. ", " ")
    value = value.replace("C.v. ", " ")
    value = value.replace("R.l. ", " ")
    value = value.replace("S.c. ", " ")
    value = value.replace("N.c. ", " ")
    value = value.replace("C.s. ", " ")
    value = value.replace("S.a.s. ", " ")
    value = value.replace("S.a.p.i. ", " ")

    # Valores en nombres y apellidos
    value = value.replace("De La ", " ")
    value = value.replace("De Los ", " ")
    value = value.replace("De Las ", " ")
    value = value.replace("Del ", " ")
    value = value.replace("De ", " ")
    value = value.replace("Las ", " ")
    value = value.replace("La ", " ")
    value = value.replace("Los ", " ")
    value = value.replace("Y ", " ")

    # CONJUNCIONES
    value = value.replace(" Y ", " ")
    value = value.replace(" E ", " ")
    value = value.replace(" Ni ", " ")
    value = value.replace(" O ", " ")
    value = value.replace(" U ", " ")
    value = value.replace(" Pero ", " ")
    value = value.replace(" Mas ", " ")
    value = value.replace(" Sino ", " ")
    value = value.replace(" Aunque ", " ")
    value = value.replace(" Porque ", " ")
    value = value.replace(" Pues ", " ")
    value = value.replace(" Si ", " ")
    value = value.replace(" Tan ", " ")
    value = value.replace(" Tanto ", " ")
    value = value.replace(" Que ", " ")
    value = value.replace(" Luego ", " ")
    # value = value.replace(" Para ", " ")
    value = value.replace(" Que ", " ")
    value = value.replace(" Si ", " ")

    # ARTICULOS
    value = value.replace(" El ", " ")
    value = value.replace(" La ", " ")
    value = value.replace(" Los ", " ")
    value = value.replace(" Las ", " ")
    value = value.replace(" Un ", " ")
    value = value.replace(" Una ", " ")
    value = value.replace(" Unos ", " ")
    value = value.replace(" Unas ", " ")
    value = value.replace(" Del ", " ")
    value = value.replace(" Al ", " ")

    # PREPOSICIONES
    value = value.replace(" A ", " ")
    value = value.replace(" Ante ", " ")
    value = value.replace(" Bajo ", " ")
    value = value.replace(" Cabe ", " ")
    value = value.replace(" Con ", " ")
    value = value.replace(" Contra ", " ")
    value = value.replace(" De ", " ")
    value = value.replace(" Desde ", " ")
    value = value.replace(" En ", " ")
    value = value.replace(" Entre ", " ")
    value = value.replace(" Hacia ", " ")
    value = value.replace(" Hasta ", " ")
    value = value.replace(" Para ", " ")
    value = value.replace(" Por ", " ")
    value = value.replace(" Segun ", " ")
    value = value.replace(" Sin ", " ")
    value = value.replace(" So ", " ")
    value = value.replace(" Sobre ", " ")
    value = value.replace(" Tras ", " ")

    return str(value.lstrip())


def format_number(number, precission):

    number = is_null(number, 0)

    factor = "1"
    for x in range(0, precission):
        factor = factor + "0"
    factor = int(factor)

    precission_number = int(number * factor) / factor

    return precission_number


def zero(x, y):
    try:
        return x / y
    except ZeroDivisionError:
        return 0


def get_choice_value(
    choices: list, search_key: str, search_value: str, return_value: str
):
    if not isinstance(search_value, (int, float, bool)):
        search_value = is_null(search_value, "")
        results = list(
            filter(
                lambda x: x[search_key].lower() == search_value.lower(),
                choices,
            )
        )
    else:
        results = list(
            filter(
                lambda x: x[search_key] == search_value,
                choices,
            )
        )

    if len(results) > 0:
        return_value = results[0][return_value]
    else:
        return_value = ""

    return return_value


def alpha_id(idnum, to_num=False, pad_up=False, passkey=None):

    if isinstance(idnum, (int, float)):
        idnum = idnum + _ALPHA_SPREAD

    try:

        index = _settings.ONLY_LETTERS
        if passkey:
            passkey = bytes(passkey, "utf-8")
            i = list(index)
            passhash = _hashlib.sha256(passkey).hexdigest()
            passhash = (
                _hashlib.sha512(passkey).hexdigest()
                if len(passhash) < len(index)
                else passhash
            )
            p = list(passhash)[0 : len(index)]
            index = "".join(list(zip(*sorted(list(zip(p, i)))))[1])

        base = len(index)

        if to_num:
            idnum = idnum[::-1]
            out = 0
            length = len(idnum) - 1
            t = 0
            while True:
                bcpow = int(pow(base, length - t))
                out = out + index.index(idnum[t : t + 1]) * bcpow
                t += 1
                if t > length:
                    break

            if pad_up:
                pad_up -= 1
                if pad_up > 0:
                    out -= int(pow(base, pad_up))
        else:
            if pad_up:
                pad_up -= 1
                if pad_up > 0:
                    idnum += int(pow(base, pad_up))

            out = []
            t = int(_math.log(idnum, base))
            while True:
                bcp = int(pow(base, t))
                a = int(idnum / bcp) % base
                out.append(index[a : a + 1])
                idnum = idnum - (a * bcp)
                t -= 1
                if t < 0:
                    break

            out = "".join(out[::-1])

        return out

    except ValueError:
        _logger.error(f"Error al obtener alpha_id [{idnum}]")
        return None


def random_with_N_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10**n) - 1
    return _random.randint(range_start, range_end)


def parameter_id(value):
    if not isinstance(value, (int, float)):
        value = remove_spaces(value)

    return_value = -1

    if _settings.DEVELOPER_MODE:
        if value.isnumeric():
            # if isinstance(value, (int, float)):
            return_value = int(value)
            return_value = return_value + _ALPHA_SPREAD
        else:
            return_value = alpha_id(
                value, to_num=True, pad_up=True, passkey=_settings.PASSKEY_ID
            )
    else:
        if not isinstance(value, (int, float)):
            return_value = alpha_id(
                value, to_num=True, pad_up=True, passkey=_settings.PASSKEY_ID
            )

    if return_value != -1:
        if return_value is None:
            return_value = -1
        else:
            return_value = return_value - _ALPHA_SPREAD

    return return_value
#*********************************************************************************************************

def get_field_value(
    table_name: str,
    search_field: str,
    search_value: str,
    search_type: str,
    return_field: str,
    filter_optional: str,
    sort_optional: str,
):
    # ADVERTENCIA DE SEGURIDAD - RIESGO DE SQLinjection
    # Esta función está diseñada para ejecutarse internamente dentro de la aplicacion
    # en un ambiente controlado.
    # NUNCA enviar parámetros a esta función desde una ruta expuesta sobre la que
    # no se tenga control de la misma

    is_mysql = True if _settings.DATABASE_ENGINE == "MYSQL" else False
    is_sqlite = True if _settings.DATABASE_ENGINE == "SQLITE3" else False
    is_psql = True if _settings.DATABASE_ENGINE == "PSQL" else False

    if search_type == "str":
        search_value = "'" + is_null(search_value, "") + "'"
    else:
        search_value = is_null(search_value, 0)

    # ADVERTENCIA DE SEGURIDAD - RIESGO DE SQLinjection ------------------------------------------------------------------------------------
    sql = f"SELECT {return_field} as return_value FROM {table_name} WHERE {search_field} = {search_value} {filter_optional} {sort_optional}"
    # --------------------------------------------------------------------------------------------------------------------------------------

    if is_mysql:
        conn = _database.engine.raw_connection()

    cursor = conn.cursor()
    cursor.execute(sql)

    rows = cursor.fetchmany(1)

    return_value = ""

    for row in rows:
        return_value = row[0]

    cursor.close()
    conn.close()

    return return_value
