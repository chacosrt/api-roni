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
    
    @_pydantic.root_validator
    def values_dias_horarios(cls, values) -> _typing.Dict:
        dias = values["dias"].strip()
        horarios = values["horarios"].strip()

        values["dias_select"] = dias.split(",")
        values["horarios_select"] = horarios.split(",")
        return values

    class Config:
        orm_mode = True


# *************************************************************************************************************************************
# SECCION: Equipos
# *************************************************************************************************************************************

class _EquiposBase(_pydantic.BaseModel):

    nombre:  _typing.Optional[str] = ""
    liga: _typing.Optional[int] = 0
    delegado:  _typing.Optional[str] = ""
    img_equipo: _typing.Optional[str] = ""
    estatus: _typing.Optional[int] = 0
# *************************************************************************************************************************************

# La clase Create hace referencia a la clase _Base
# y hereda los campos de la misma
class EquiposCreate(_EquiposBase):
    pass


# *************************************************************************************************************************************


class Equipos(_EquiposBase):

    id: int = 0
    liga_equipo:Torneos

    """ @_pydantic.root_validator
    def value_nombre_liga(cls, values) -> _typing.Dict:
        try:
            nombre_torneo = _fn.get_field_value(
                    table_name="torneos",
                    search_field="id",
                    search_type="str",
                    search_value=values["liga"],
                    return_field="nombre_torneo",
                    filter_optional="",
                    sort_optional="",
                )

            values["nombre_torneo"] = nombre_torneo
           
        except Exception as e:
            #_logger.error("[" + _inspect.stack()[0][3] + "] " + str(e))

            values["nombre_torneo"] = ""   

        return values
 """
    class Config:
        orm_mode = True

# *************************************************************************************************************************************
# SECCION: JUGADORES
# *************************************************************************************************************************************

class _JugadoressBase(_pydantic.BaseModel):

    nombre:  _typing.Optional[str] = ""
    ap_p:  _typing.Optional[str] = ""
    ap_m:  _typing.Optional[str] = ""
    edad: _typing.Optional[int] = 0
    liga: _typing.Optional[int] = 0
    equipo: _typing.Optional[int] = 0
    dorsal: _typing.Optional[int] = 0
    expediente:  _typing.Optional[str] = ""
    seccional:  _typing.Optional[str] = ""
    direccion:  _typing.Optional[str] = ""
    telefono:  _typing.Optional[str] = ""
    img:  _typing.Optional[str] = ""
    delegado: _typing.Optional[bool] = False
    estatus: _typing.Optional[int] = 0

# *************************************************************************************************************************************

# La clase Create hace referencia a la clase _Base
# y hereda los campos de la misma
class JugadoresCreate(_JugadoressBase):
    pass


# *************************************************************************************************************************************


class Jugadores(_JugadoressBase):

    id: int = 0
    equipo_jugador: Equipos

    @_pydantic.root_validator
    def value_nombre_completo(cls, values) -> _typing.Dict:
        try:
            
            nombre_completo = values["nombre"] + " " +values["ap_p"] + " " +values["ap_m"]
            values["nombre_completo"] = nombre_completo
           
        except Exception as e:
            #_logger.error("[" + _inspect.stack()[0][3] + "] " + str(e))

            values["nombre_completo"] = ""   

        return values
 
    class Config:
        orm_mode = True

# *************************************************************************************************************************************
# SECCION: Partidos
# *************************************************************************************************************************************

class _PartidosBase(_pydantic.BaseModel):

    fecha: _typing.Optional[_dt.date]  = None
    horario: _typing.Optional[str] = ""
    etapa:  _typing.Optional[str] = ""
    jornada:  _typing.Optional[str] = ""
    temporada:  _typing.Optional[str] = ""
    campo: _typing.Optional[int] = 0
    liga: _typing.Optional[int] = 0
    local: _typing.Optional[int] = 0
    visitante: _typing.Optional[int] = 0
    goles_local: _typing.Optional[int] = 0
    goles_visitante: _typing.Optional[int] = 0
    ganador: _typing.Optional[int] = 0
    estatus: _typing.Optional[int] = 0
    observaciones:  _typing.Optional[str] = ""


# *************************************************************************************************************************************

# La clase Create hace referencia a la clase _Base
# y hereda los campos de la misma
class PartidosCreate(_PartidosBase):
    pass


# *************************************************************************************************************************************


class Partidos(_PartidosBase):

    id: int = 0
    liga_partido: Torneos

    @_pydantic.root_validator
    def values_fechas(cls, values) -> _typing.Dict:
        fecha = str(_fn.format_date(values["fecha"]))
        values.pop("fecha")        

        values["fecha"] = fecha
        return values
    
    @_pydantic.root_validator
    def value_nombre_equipos(cls, values) -> _typing.Dict:
        try:
           
            return_value = _fn.get_field_value(
                    table_name="equipos",
                    search_field="id",
                    search_type="",
                    search_value=values["local"],
                    return_field="nombre",
                    filter_optional="",
                    sort_optional="",
                )
            if return_value != "":
                values["nombre_local"] = return_value
            else:
                 values["nombre_local"] = ""
        except Exception as e:
            _logger.error("[" + _inspect.stack()[0][3] + "] " + str(e))

            values["nombre_local"] = ""

        try:
           
            return_value = _fn.get_field_value(
                    table_name="equipos",
                    search_field="id",
                    search_type="",
                    search_value=values["visitante"],
                    return_field="nombre",
                    filter_optional="",
                    sort_optional="",
                )
            if return_value != "":
                values["nombre_visitante"] = return_value
            else:
                 values["nombre_visitante"] = ""
        except Exception as e:
            _logger.error("[" + _inspect.stack()[0][3] + "] " + str(e))

            values["nombre_visitante"] = ""


        return values
    
    @_pydantic.root_validator
    def value_img_equipos(cls, values) -> _typing.Dict:
        try:
           
            return_value = _fn.get_field_value(
                    table_name="equipos",
                    search_field="id",
                    search_type="",
                    search_value=values["local"],
                    return_field="img_equipo",
                    filter_optional="",
                    sort_optional="",
                )
            if return_value != "":
                values["img_local"] = return_value
            else:
                 values["img_local"] = ""
        except Exception as e:
            _logger.error("[" + _inspect.stack()[0][3] + "] " + str(e))

            values["img_local"] = ""

        try:
           
            return_value = _fn.get_field_value(
                    table_name="equipos",
                    search_field="id",
                    search_type="",
                    search_value=values["visitante"],
                    return_field="img_equipo",
                    filter_optional="",
                    sort_optional="",
                )
            if return_value != "":
                values["img_visitante"] = return_value
            else:
                 values["img_visitante"] = ""
        except Exception as e:
            _logger.error("[" + _inspect.stack()[0][3] + "] " + str(e))

            values["img_visitante"] = ""


        return values
    
 
    class Config:
        orm_mode = True
