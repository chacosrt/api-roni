import fastapi as _fastapi
import fastapi.security as _security

import logging as _logging
import requests as _requests
import json as _json
import yaml as _yaml

import datetime as _dt
import time as _time
import pytz as _pytz
import jwt as _jwt

# import uuid as _uuid
# from typing import Dict

import settings as _settings

_logger = _logging.getLogger(__name__)

# *************************************************************************************************************************************


def token_decode(token: str) -> dict:
    try:
        token_value = _jwt.decode(
            
            token,
            _settings.JWT_SECRET,
            algorithms=[_settings.JWT_ALGORITHM],
            audience=_settings.JWT_AUDIENCE,
        )
        return token_value if token_value["exp"] >= _time.time() else None
    except:
        return {}


# *************************************************************************************************************************************


class token_bearer(_security.HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(token_bearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: _fastapi.Request):
        credentials: _security.HTTPAuthorizationCredentials = await super(
            token_bearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise _fastapi.HTTPException(
                    status_code=403, detail="Esquema de autorización inválido"
                )
            if not self.token_verify(credentials.credentials):
                raise _fastapi.HTTPException(
                    status_code=403, detail="Token inválido o fuera de vigencia."
                )
            return credentials.credentials
        else:
            raise _fastapi.HTTPException(
                status_code=403, detail="Código de autorización inválido"
            )

    def token_verify(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = token_decode(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid


# *************************************************************************************************************************************


def token_claim(token: str, claim: str):
    try:
        # credentials = token.split(" ")
        # return_value = token_decode(credentials[1])[claim.lower()]
        return_value = token_decode(token)[claim.lower()]
    except:
        return_value = ""

    return return_value


# *************************************************************************************************************************************


def token_get(sub: str, ttl: int, aud: str, roles: str, scope: str):
    start_time = _time.time()
    try:
        _URL = _settings.JWT_AUTHORIZATION_URL
        _DATA = {
            "sub": sub,
            "ttl": ttl,
            "aud": aud,
            "roles": roles,
            "scope": scope,
        }

        response = _requests.post(_URL, data=_json.dumps(_DATA), verify=False)
        data = _json.loads(response.content)
        return_value = data["access_token"]
    except:
        return_value = ""

    process_time = (_time.time() - start_time) * 1000
    formatted_process_time = "{0:.2f}".format(process_time)

    _logger.info(
        f"Token request completed_in={formatted_process_time}ms status_code={response.status_code}"
    )

    return return_value


# *************************************************************************************************************************************


def token_backend(backend: str, origin: str):

    start_datetime = _dt.datetime.now().astimezone(_pytz.utc)
    end_datetime = _dt.datetime.combine(_dt.datetime.now(), _dt.time.max).astimezone(
        _pytz.utc
    )
    ttl_seconds = int((end_datetime - start_datetime).total_seconds())
    aud = backend + ".gdar.mx"
    sub = origin + "@gdar.mx"

    # Obtiene el valor del token guardado (si existe) en el archivo .credentials.yaml
    with open(f"../.credentials.yaml") as stream:
        credentials = _yaml.safe_load(stream)

    update_file = False

    if credentials is None:
        credentials = {}

    # Si no obtiene ningun valor, genera un nuevo token
    try:
        JWT_BACKEND = credentials[backend]
    except:
        JWT_BACKEND = token_get(
            sub,
            ttl_seconds,
            aud,
            "system",
            "*",
        )
        update_file = True

    try:
        # verifica que el token sea valido
        _jwt.decode(
            JWT_BACKEND,
            _settings.JWT_SECRET,
            algorithms=[_settings.JWT_ALGORITHM],
            audience=aud,
        )
    except:
        # si el token es invalido, genera un nuevo token
        JWT_BACKEND = token_get(
            sub,
            ttl_seconds,
            aud,
            "system",
            "*",
        )
        update_file = True

    if update_file:
        # asigna el valor del token a JWT_BACKEND
        credentials[f"{backend}"] = JWT_BACKEND
        # Guarda el valor del token obtenido en el archivo .credentials.yaml
        with open("../.credentials.yaml", "w") as file:
            _yaml.dump(credentials, file)

    # retorna  el valor del token a JWT_BACKEND
    return JWT_BACKEND
