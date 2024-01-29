import logging as _logging
import requests as _requests
import json as _json
import auth as _auth
import time as _time

import settings as _settings
import functions.fn as _fn
import services as _services
import schemas as _schemas
import models as _models
import database as _database
import sqlalchemy.orm as _orm

_logger = _logging.getLogger(__name__)


class bearer_auth_header(_requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


def pack_extra(codigo_pack_id: str):
    _status_code = ""

    start_time = _time.time()
    codigo_pack_id = _fn.alpha_id(
        int(codigo_pack_id), to_num=False, pad_up=True, passkey=_settings.PASSKEY_ID
    )

    url = _settings.PILLS_URL + f"/packs/{codigo_pack_id}/id"

    token = _auth.token_backend("pills", "marble")
    records = []
    try:
        if codigo_pack_id != "":
            codigo_pack_id = _fn.parameter_id(codigo_pack_id)
            response = _services.cache_get_packs_codigo_pack_id(
                codigo_pack_id=codigo_pack_id
            )
            data = response
            if response is None:
                response = _requests.get(
                    url, auth=bearer_auth_header(token), verify=False
                )
                _status_code = response.status_code
                data = _json.loads(response.content)

                if response.status_code == 404:
                    _session = _orm.sessionmaker(bind=_database.engine)
                    db = _session()
                    db_pack = _models.Pack()
                    db_pack.descripcion = "No existen datos"
                    db_pack.estatus = 404
                    db_pack.id = codigo_pack_id
                    db_pack.creado_por = "system@gdar.mx"
                    db_pack.modificado_por = "system@gdar.mx"
                    db.add(db_pack)
                    db.commit()
                    db.refresh(db_pack)
                    return_value = records.append(
                        _schemas.PackCreate(**db_pack.__dict__).dict()
                    )
                else:
                    _status_code = "201"
                    codigo_atc = data["codigo_atc"]
                    url_clase = _settings.PILLS_URL + f"/clases_terapeuticas/{codigo_atc}/codigo_atc"
                    response = _requests.get(url_clase, auth=bearer_auth_header(token), verify=False )
                    data_clase = _json.loads(response.content)
                    _services.cache_post_clase_terapeutica(_schemas.ClaseTerapeuticaCreate(**data_clase[0]))
                    _services.cache_post_pack(_schemas.PackCreate(**data))

                ### Log
                process_time = (_time.time() - start_time) * 1000
                formatted_process_time = "{0:.2f}".format(process_time)
                _logger.info(
                    f"[{_settings.JWT_AUDIENCE}] Remote request {url} completed_in={formatted_process_time}ms status_code={_status_code}"
                )
                ###
                return_value = data

            else:
                return_value = _schemas.Pack(**data.__dict__).dict()

        else:
            return_value = _schemas.Pack().dict()

    except Exception as e:
        _logger.info("Error:" + str(e))
        return_value = _schemas.Pack().dict()

    return return_value
