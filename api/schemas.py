import datetime as _dt
import inspect as _inspect
import logging as _logging
import math as _math
import typing as _typing

import functions.arena as _arena
import functions.fn as _fn
import functions.pills as _pills
import functions.newton as _newton
import pydantic as _pydantic
import settings as _settings

_logger = _logging.getLogger(__name__)

# *************************************************************************************************************************************
# SECCION: TORNEOS
# *************************************************************************************************************************************

class _TorneosBase(_pydantic.BaseModel):

    nombre_torneo:  _typing.Optional[str] = ""
    temporada: _typing.Optional[str] = ""
    modalidad:  _typing.Optional[str] = ""
    lugar:  _typing.Optional[str] = ""
    dias:  _typing.Optional[str] = ""
    horarios:  _typing.Optional[str] = ""
    fecha_inicio: _typing.Optional[_dt.date]  = None
    fecha_fin: _typing.Optional[_dt.date]  = None
    categoria: _typing.Optional[str] = ""
    img: _typing.Optional[str] = ""
    estatus: _typing.Optional[int] = 0
# *************************************************************************************************************************************

# La clase Create hace referencia a la clase _Base
# y hereda los campos de la misma
class TorneosCreate(_TorneosBase):
    pass


# *************************************************************************************************************************************


class Torneos(_TorneosBase):

    id: int = 0

    @_pydantic.root_validator
    def values_fechas(cls, values) -> _typing.Dict:
        fecha = str(_fn.format_date(values["fecha_inicio"]))
        values.pop("fecha_inicio")        

        values["fecha_inicio"] = fecha
        return values

    class Config:
        orm_mode = True

