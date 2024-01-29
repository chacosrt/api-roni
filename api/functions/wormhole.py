import requests as _requests
import settings as _settings


async def log_wormhole(payload: str = ""):
    # ENVIA LOG A WORMHOLE --> CONVERTIRLO EN FUNCION
    try:
        _URL = _settings.WORMHOLE_URL + "/endpoint/"
        _PAYLOAD = payload
        _requests.post(_URL, data=_PAYLOAD, verify=False)
    except:
        pass

    return None
