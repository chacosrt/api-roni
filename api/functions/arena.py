import logging as _logging
import requests as _requests
import json as _json
import auth as _auth
import time as _time

import settings as _settings
import functions.fn as _fn
import services as _services
import schemas as _schemas

_logger = _logging.getLogger(__name__)


class bearer_auth_header(_requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


""" def persona_extra(persona_id: int):

    start_time = _time.time()
    # persona_id=_fn.parameter_id(persona_id)
    persona_id = _fn.alpha_id(
        int(persona_id), to_num=False, pad_up=True, passkey=_settings.PASSKEY_ID
    )
    url = _settings.ARENA_URL + f"/personas/{persona_id}/id"

    token = _auth.token_backend("arena", "marble")

    try:
        if persona_id != "":

            response = _services.cache_get_persona(id=persona_id)
            data = response
            if response is None:

                response = _requests.get(
                    url, auth=bearer_auth_header(token), verify=False
                )
                _status_code = response.status_code
                data = _json.loads(response.content)

                if response.status_code == 404:
                    return_value = _schemas.Persona().dict()
                else:
                    _status_code = "201"
                    _services.cache_post_persona(_schemas.PersonaCreate(**data))

                ### Log
                process_time = (_time.time() - start_time) * 1000
                formatted_process_time = "{0:.2f}".format(process_time)
                _logger.info(
                    f"[{_settings.JWT_AUDIENCE}] Remote request {url} completed_in={formatted_process_time}ms status_code={_status_code}"
                )
                ###
                return_value = data

            else:
                return_value = _schemas.Persona(**data.__dict__).dict()

        else:
            return_value = _schemas.Persona().dict()

    except Exception as e:
        _logger.info("Error:" + str(e))
        return_value = _schemas.Persona().dict()

    return return_value """
