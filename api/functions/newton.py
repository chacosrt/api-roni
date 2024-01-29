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


def inventario_extra(id_item: str):
    _status_code = ""

    start_time = _time.time()
    id_item = _fn.alpha_id(
        int(id_item), to_num=False, pad_up=True, passkey=_settings.PASSKEY_ID
    )

    url = _settings.NEWTON_URL + f"/inventarios/{id_item}/id_item"

    token = _auth.token_backend("newton", "marble")
    records = []
    try:
        if id_item != "":
            id_item = _fn.parameter_id(id_item)
            response = _services.cache_get_inventario_id_item(
                id_item=id_item
            )
            data = response
            if len(response) == 0 :
                response = _requests.get(
                    url, auth=bearer_auth_header(token), verify=False
                )
                _status_code = response.status_code
                data = _json.loads(response.content)

                if response.status_code == 404:
                    return_value = _schemas.Inventario().dict()
                else:
                    _status_code = "201"
                    for record in data:
                        _session = _orm.sessionmaker(bind=_database.engine)
                        db = _session()
                        response = (
                            db.query(_models.Inventario.id)
                            .filter(_models.Inventario.id == record["id"])
                            .first()
                        )
                        db.close()
                        # if len(response) is None: # causa error
                        if response is None:
                            _services.cache_post_inventario(_schemas.InventarioCreate(**record))
                    return_value = data
                    

                ### Log
                process_time = (_time.time() - start_time) * 1000
                formatted_process_time = "{0:.2f}".format(process_time)
                _logger.info(
                    f"[{_settings.JWT_AUDIENCE}] Remote request {url} completed_in={formatted_process_time}ms status_code={_status_code}"
                )
                ###
                return_value = data

            else:
                for record in data:
                     records.append(_schemas.Inventario(**record.__dict__).dict())
                return_value = records

        else:
            return_value = _schemas.Inventario().dict()

    except Exception as e:
        _logger.info("Error:" + str(e))
        return_value = _schemas.Inventario().dict()

    return return_value
