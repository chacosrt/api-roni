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
from PIL import Image
import base64
from io import BytesIO

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
    
    @_pydantic.root_validator
    def value_img(cls, values) -> _typing.Dict:
        try:
            imgn = values["img"].split(',')     
            form = imgn[0].split('/')[1]
            formato = form.split(';')[0]     
             # Decodificar la cadena base64 a bytes
            image_data = base64.b64decode(imgn[1])
            
            # Leer la imagen desde los bytes
            buffer = BytesIO(image_data)
            with Image.open(buffer) as img:
                # Redimensionar la imagen
                img = img.resize((100, 100), Image.Resampling.LANCZOS)
                 # Convertir a RGB si la imagen está en RGBA o cualquier otro modo no compatible
                if img.mode != "RGB":
                    img = img.convert("RGB")
                # Guardar la imagen redimensionada en un nuevo buffer
                output_buffer = BytesIO()
                img.save(output_buffer, format='jpeg', quality=85)  # Ajusta el formato y la calidad
                output_buffer.seek(0)
                
                # Convertir la imagen nuevamente a base64
                reduced_base64 = base64.b64encode(output_buffer.read()).decode('utf-8')

            values["img"] = f"{imgn[0].replace(formato,'jpeg')},{reduced_base64}"
           
        except Exception as e:
            _logger.error("[" + _inspect.stack()[0][3] + "] " + str(e))

            values["img"] = ""   

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

    @_pydantic.root_validator
    def value_img(cls, values) -> _typing.Dict:
        try:
            imgn = values["img_equipo"].split(',')          
             # Decodificar la cadena base64 a bytes
            image_data = base64.b64decode(imgn[1])
            
            # Leer la imagen desde los bytes
            buffer = BytesIO(image_data)
            with Image.open(buffer) as img:
                # Redimensionar la imagen
                img = img.resize((100, 100), Image.Resampling.LANCZOS)
                form = imgn[0].split('/')[1]
                formato = form.split(';')[0]   
                 # Convertir a RGB si la imagen está en RGBA o cualquier otro modo no compatible
                if img.mode != "RGB":
                    img = img.convert("RGB")
                # Guardar la imagen redimensionada en un nuevo buffer
                output_buffer = BytesIO()
                img.save(output_buffer, format='jpeg', quality=85)  # Ajusta el formato y la calidad
                output_buffer.seek(0)
                
                # Convertir la imagen nuevamente a base64
                reduced_base64 = base64.b64encode(output_buffer.read()).decode('utf-8')

            values["img_equipo"] = f"{imgn[0].replace(formato,'jpeg')},{reduced_base64}"
           
        except Exception as e:
            _logger.error("[" + _inspect.stack()[0][3] + "] " + str(e))

            values["img_equipo"] = ""   

        return values
 
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

    @_pydantic.root_validator
    def value_img(cls, values) -> _typing.Dict:
        try:
            imgn = values["img"].split(',')          
             # Decodificar la cadena base64 a bytes
            image_data = base64.b64decode(imgn[1])
            
            # Leer la imagen desde los bytes
            buffer = BytesIO(image_data)
            with Image.open(buffer) as img:
                # Redimensionar la imagen
                img = img.resize((100, 100), Image.Resampling.LANCZOS)
                form = imgn[0].split('/')[1]
                formato = form.split(';')[0]   
                 # Convertir a RGB si la imagen está en RGBA o cualquier otro modo no compatible
                if img.mode != "RGB":
                    img = img.convert("RGB")
                # Guardar la imagen redimensionada en un nuevo buffer
                output_buffer = BytesIO()
                img.save(output_buffer, format='jpeg', quality=85)  # Ajusta el formato y la calidad
                output_buffer.seek(0)
                
                # Convertir la imagen nuevamente a base64
                reduced_base64 = base64.b64encode(output_buffer.read()).decode('utf-8')

            values["img"] = f"{imgn[0].replace(formato,'jpeg')},{reduced_base64}"
           
        except Exception as e:
            _logger.error("[" + _inspect.stack()[0][3] + "] " + str(e))

            values["img"] = ""   

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
    jornada:  _typing.Optional[int] = 0
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
    registro_tabla:  _typing.Optional[bool] = False


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
    

    @_pydantic.root_validator
    def values_partido(cls, values) -> _typing.Dict:
        etapa = values["etapa"] 
        ganador = values["ganador"]
        estatus = values["estatus"]  
        goles_local = values["goles_local"]
        goles_visitante = values["goles_visitante"]

        if estatus == 2 and goles_local > goles_visitante:

            values["ganador_descripcion"] = values["nombre_local"]

        if estatus == 2 and goles_local < goles_visitante:

            values["ganador_descripcion"] = values["nombre_visitante"]

        if estatus == 2 and goles_local == goles_visitante:

            values["ganador_descripcion"] = "Empate"

        if estatus == 1 or estatus == 3:

            values["ganador_descripcion"] = "Por Definirse"

        if estatus == 4:

            values["ganador_descripcion"] = "Sin Ganador"


        #****** Estatus************

        if estatus == 1:

            values["estatus_descripcion"] = "Programado"

        if estatus == 2:

            values["estatus_descripcion"] = "Jugado"

        if estatus == 3:

            values["estatus_descripcion"] = "Pendianete"

        if estatus == 4:

            values["estatus_descripcion"] = "Suspendido"

    
    #****** Etapa************

        if etapa == "1":

            values["etapa_descripcion"] = "Práctica"

        if etapa == "2":

            values["etapa_descripcion"] = "Regular"

        if etapa == "3":

            values["etapa_descripcion"] = "Liguilla"

        
        return values
    
    
 
    class Config:
        orm_mode = True


# *************************************************************************************************************************************
# SECCION: Jornadas
# *************************************************************************************************************************************

class Jornadas(_pydantic.BaseModel):

    jornada:  _typing.Optional[int] = 0
    temporada:  _typing.Optional[str] = ""
    liga: _typing.Optional[int] = 0


# *************************************************************************************************************************************
# SECCION: Asignar jugador a otro equipo
# *************************************************************************************************************************************

class EquipoJugador(_pydantic.BaseModel):

    id_jugador:  _typing.Optional[int] = 0
    equipo:  _typing.Optional[int] = 0
    liga: _typing.Optional[int] = 0


# *************************************************************************************************************************************
# SECCION: Partidos
# *************************************************************************************************************************************

class _PosicionesBase(_pydantic.BaseModel):

    temporada: _typing.Optional[str] = ""
    liga:  _typing.Optional[int] = 0
    equipo:  _typing.Optional[int] = 0
    juegos_jugados:  _typing.Optional[int] = 0
    juegos_ganados:  _typing.Optional[int] = 0
    juegos_empatados:  _typing.Optional[int] = 0
    juegos_perdidos:  _typing.Optional[int] = 0
    goles_favor:  _typing.Optional[int] = 0
    goles_contra:  _typing.Optional[int] = 0
    diferencia_goles:  _typing.Optional[int] = 0
    puntos:  _typing.Optional[int] = 0
    estatus:  _typing.Optional[int] = 0
    


# *************************************************************************************************************************************

# La clase Create hace referencia a la clase _Base
# y hereda los campos de la misma
class PosicionesCreate(_PosicionesBase):
    pass


# *************************************************************************************************************************************


class Posiciones(_PosicionesBase):

    id: int = 0
    liga_tabla: Torneos
    equipo_tabla:Equipos
    

    class Config:
        orm_mode = True



# *************************************************************************************************************************************
# SECCION: Goleo
# *************************************************************************************************************************************

class _GoleadoresBase(_pydantic.BaseModel):

    id_liga:_typing.Optional[int] = 0
    id_equipo:_typing.Optional[int] = 0
    id_jugador: _typing.Optional[int] = 0
    goles: _typing.Optional[int] = 0
    jj: _typing.Optional[int] = 0
    avg: _typing.Optional[float] = 0
    temporada: _typing.Optional[str] = ""
    


# *************************************************************************************************************************************

# La clase Create hace referencia a la clase _Base
# y hereda los campos de la misma
class GoleadoresCreate(_GoleadoresBase):
    pass


# *************************************************************************************************************************************


class Goleadores(_GoleadoresBase):

    id: int = 0

    @_pydantic.root_validator
    def value_img_torneo(cls, values) -> _typing.Dict:
        try:
           
            return_value = _fn.get_field_value(
                    table_name="torneos",
                    search_field="id",
                    search_type="",
                    search_value=values["id_liga"],
                    return_field="nombre_torneo",
                    filter_optional="",
                    sort_optional="",
                )
            if return_value != "":
                values["nombre_torneo"] = return_value
            else:
                 values["nombre_torneo"] = ""
        except Exception as e:
            _logger.error("[" + _inspect.stack()[0][3] + "] " + str(e))

            values["nombre_torneo"] = ""


        return values
    
    @_pydantic.root_validator
    def value_img_equipos(cls, values) -> _typing.Dict:
        try:
           
            return_value = _fn.get_field_value(
                    table_name="equipos",
                    search_field="id",
                    search_type="",
                    search_value=values["id_equipo"],
                    return_field="img_equipo",
                    filter_optional="",
                    sort_optional="",
                )
            if return_value != "":
                values["img_equipo"] = return_value
            else:
                 values["img_equipo"] = ""
        except Exception as e:
            _logger.error("[" + _inspect.stack()[0][3] + "] " + str(e))

            values["img_equipo"] = ""

        try:
           
            return_value = _fn.get_field_value(
                    table_name="equipos",
                    search_field="id",
                    search_type="",
                    search_value=values["id_equipo"],
                    return_field="nombre",
                    filter_optional="",
                    sort_optional="",
                )
            if return_value != "":
                values["nombre_equipo"] = return_value
            else:
                 values["nombre_equipo"] = ""
        except Exception as e:
            _logger.error("[" + _inspect.stack()[0][3] + "] " + str(e))

            values["nombre_equipo"] = ""


        return values
    
    @_pydantic.root_validator
    def value_img_jugador(cls, values) -> _typing.Dict:
        try:
           
            return_value = _fn.get_field_value(
                    table_name="jugadores",
                    search_field="id",
                    search_type="",
                    search_value=values["id_jugador"],
                    return_field="img",
                    filter_optional="",
                    sort_optional="",
                )
            if return_value != "":
                values["img_jugador"] = return_value
            else:
                 values["img_jugador"] = ""
        except Exception as e:
            _logger.error("[" + _inspect.stack()[0][3] + "] " + str(e))

            values["img_jugador"] = ""

        try:
           
            return_value = _fn.get_field_value(
                    table_name="jugadores",
                    search_field="id",
                    search_type="",
                    search_value=values["id_jugador"],
                    return_field="nombre",
                    filter_optional="",
                    sort_optional="",
                )
            if return_value != "":
                values["nombre_jugador"] = return_value
            else:
                 values["nombre_jugador"] = ""
        except Exception as e:
            _logger.error("[" + _inspect.stack()[0][3] + "] " + str(e))

            values["nombre_jugador"] = ""

        return values

    class Config:
        orm_mode = True


# *************************************************************************************************************************************
# SECCION: TARJETAS
# *************************************************************************************************************************************

class _TarjetasBase(_pydantic.BaseModel):

    id_liga: _typing.Optional[int] = 0
    id_equipo: _typing.Optional[int] = 0
    id_jugador: _typing.Optional[int] = 0
    ta: _typing.Optional[int] = 0
    tr: _typing.Optional[int] = 0
    sanciones_vig:  _typing.Optional[int] = 0
    suspensiones: _typing.Optional[int] = 0
    numero_juegos: _typing.Optional[int] = 0
    jornada_regreso: _typing.Optional[int] = 0
    temporada: _typing.Optional[str] = ""
    descripcion: _typing.Optional[str] = ""
    estatus:  _typing.Optional[int] = 0
    


# *************************************************************************************************************************************

# La clase Create hace referencia a la clase _Base
# y hereda los campos de la misma
class TarjetasCreate(_TarjetasBase):
    pass


# *************************************************************************************************************************************


class Tarjetas(_TarjetasBase):

    id: int = 0

    @_pydantic.root_validator
    def value_img_torneo(cls, values) -> _typing.Dict:
        try:
           
            return_value = _fn.get_field_value(
                    table_name="torneos",
                    search_field="id",
                    search_type="",
                    search_value=values["id_liga"],
                    return_field="nombre_torneo",
                    filter_optional="",
                    sort_optional="",
                )
            if return_value != "":
                values["nombre_torneo"] = return_value
            else:
                 values["nombre_torneo"] = ""
        except Exception as e:
            _logger.error("[" + _inspect.stack()[0][3] + "] " + str(e))

            values["nombre_torneo"] = ""


        return values
    
    @_pydantic.root_validator
    def value_img_equipos(cls, values) -> _typing.Dict:
        try:
           
            return_value = _fn.get_field_value(
                    table_name="equipos",
                    search_field="id",
                    search_type="",
                    search_value=values["id_equipo"],
                    return_field="img_equipo",
                    filter_optional="",
                    sort_optional="",
                )
            if return_value != "":
                values["img_equipo"] = return_value
            else:
                 values["img_equipo"] = ""
        except Exception as e:
            _logger.error("[" + _inspect.stack()[0][3] + "] " + str(e))

            values["img_equipo"] = ""

        try:
           
            return_value = _fn.get_field_value(
                    table_name="equipos",
                    search_field="id",
                    search_type="",
                    search_value=values["id_equipo"],
                    return_field="nombre",
                    filter_optional="",
                    sort_optional="",
                )
            if return_value != "":
                values["nombre_equipo"] = return_value
            else:
                 values["nombre_equipo"] = ""
        except Exception as e:
            _logger.error("[" + _inspect.stack()[0][3] + "] " + str(e))

            values["nombre_equipo"] = ""


        return values
    

    @_pydantic.root_validator
    def value_img_jugador(cls, values) -> _typing.Dict:
        try:
           
            return_value = _fn.get_field_value(
                    table_name="jugadores",
                    search_field="id",
                    search_type="",
                    search_value=values["id_jugador"],
                    return_field="img",
                    filter_optional="",
                    sort_optional="",
                )
            if return_value != "":
                values["img_jugador"] = return_value
            else:
                 values["img_jugador"] = ""
        except Exception as e:
            _logger.error("[" + _inspect.stack()[0][3] + "] " + str(e))

            values["img_jugador"] = ""

        try:
           
            return_value = _fn.get_row_value(
                    table_name="jugadores",
                    search_field="id",
                    search_type="",
                    search_value=values["id_jugador"],
                    return_field="nombre",
                    filter_optional="",
                    sort_optional="",
                )
            if return_value != "":
                values["nombre_jugador"] = return_value[1] + ' ' + return_value[2] + ' ' + return_value[3]
            else:
                 values["nombre_jugador"] = ""
        except Exception as e:
            _logger.error("[" + _inspect.stack()[0][3] + "] " + str(e))

            values["nombre_jugador"] = ""


        return values
    
    class Config:
        orm_mode = True