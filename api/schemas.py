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
# SECCION: CEDULAS
# *************************************************************************************************************************************

class Cedula(_pydantic.BaseModel):
    nombre:_typing.Optional[str] = ""
    ap_p:_typing.Optional[str] = ""
    ap_m:_typing.Optional[str] = ""
    cedula:_typing.Optional[str] = ""
    filtro:_typing.Optional[str] = ""
    forzar_busqueda:_typing.Optional[bool] = False


# *************************************************************************************************************************************

class CedulaResp(_pydantic.BaseModel):
    idCedula: _typing.Optional[str] = ""
    nombre:_typing.Optional[str] = ""
    paterno:_typing.Optional[str] = ""
    materno:_typing.Optional[str] = ""
    titulo:_typing.Optional[str] = ""
    desins:_typing.Optional[str] = ""
    anioreg: _typing.Optional[int] = 0


# *************************************************************************************************************************************
# SECCION: REGIMENES
# *************************************************************************************************************************************


class _RegimenesBase(_pydantic.BaseModel):

    id_constancia: _typing.Optional[str] = ""	
    regimen: _typing.Optional[str] = ""	
    fecha_alta: _typing.Optional[_dt.datetime]  = None

# *************************************************************************************************************************************

# La clase Create hace referencia a la clase _Base
# y hereda los campos de la misma
class RegimenesCreate(_RegimenesBase):
    pass


# *************************************************************************************************************************************


class Regimenes(_RegimenesBase):

    id: int = 0

    @_pydantic.root_validator
    def values_fechas(cls,values) -> _typing.Dict:
        if values["fecha_alta"] is not None:
                fecha_alta = str(_fn.format_datetime(values["fecha_alta"]))
                values.pop("fecha_alta")
                fecha_hora_minutos = _dt.datetime.strptime(fecha_alta, "%Y-%m-%d %H:%M:%S.%f").strftime(
                    "%Y-%m-%d %H:%M"
                )

                fecha_sola = _dt.datetime.strptime(fecha_alta, "%Y-%m-%d %H:%M:%S.%f").strftime(
                    "%Y-%m-%d"
                )

                hora=_dt.datetime.strptime(fecha_alta, "%Y-%m-%d %H:%M:%S.%f").strftime(
                    "%H:%M"
                )
                
                values["fecha_alta"] = [fecha_alta,fecha_hora_minutos, fecha_sola,hora]
        return values

    class Config:
        orm_mode = True


# *************************************************************************************************************************************
# SECCION: CONSTANCIA FISCAL
# *************************************************************************************************************************************


class _ConstanciaFiscalBase(_pydantic.BaseModel):

    id_constancia: _typing.Optional[str] = ""
    rfc: _typing.Optional[str] = ""
    nombre: _typing.Optional[str] = ""
    paterno: _typing.Optional[str] = ""
    materno: _typing.Optional[str] = ""
    curp: _typing.Optional[str] = ""
    fecha_nacimiento: _typing.Optional[_dt.datetime]  = None
    regimen_capital: _typing.Optional[str] = ""
    razon_social: _typing.Optional[str] = ""
    fecha_constitucion: _typing.Optional[_dt.datetime]  = None
    fecha_inicio_operaciones: _typing.Optional[_dt.datetime]  = None
    situacion_contribuyente: _typing.Optional[str] = ""
    fecha_ultimo_cambio: _typing.Optional[_dt.datetime]  = None
    entidad_federativa: _typing.Optional[str] = ""
    municipio_delegacion: _typing.Optional[str] = ""
    colonia: _typing.Optional[str] = ""
    tipo_vialidad: _typing.Optional[str] = ""
    nombre_vialidad: _typing.Optional[str] = ""
    num_ext: _typing.Optional[str] = ""
    num_int: _typing.Optional[str] = ""
    cp: _typing.Optional[str] = ""
    correo: _typing.Optional[str] = ""
    al: _typing.Optional[str] = ""

# *************************************************************************************************************************************

# La clase Create hace referencia a la clase _Base
# y hereda los campos de la misma
class ConstanciaFiscalCreate(_ConstanciaFiscalBase):
    pass


# *************************************************************************************************************************************


class ConstanciaFiscal(_ConstanciaFiscalBase):

    id: int = 0
    

    @_pydantic.root_validator
    def values_fechas(cls,values) -> _typing.Dict:
        if values["fecha_nacimiento"] is not None:
            fecha_nacimiento = str(_fn.format_datetime(values["fecha_nacimiento"]))
            values.pop("fecha_nacimiento")
            fecha_hora_minutos = _dt.datetime.strptime(fecha_nacimiento, "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%Y-%m-%d %H:%M"
            )

            fecha_sola = _dt.datetime.strptime(fecha_nacimiento, "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%Y-%m-%d"
            )

            hora=_dt.datetime.strptime(fecha_nacimiento, "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%H:%M"
            )
            
            values["fecha_nacimiento"] = [fecha_nacimiento,fecha_hora_minutos, fecha_sola,hora]

        if values["fecha_constitucion"] is not None:
            fecha_constitucion = str(_fn.format_datetime(values["fecha_constitucion"]))
            values.pop("fecha_constitucion")
            fecha_hora_minutos = _dt.datetime.strptime(fecha_constitucion, "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%Y-%m-%d %H:%M"
            )

            fecha_sola = _dt.datetime.strptime(fecha_constitucion, "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%Y-%m-%d"
            )

            hora=_dt.datetime.strptime(fecha_constitucion, "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%H:%M"
            )
            
            values["fecha_constitucion"] = [fecha_constitucion,fecha_hora_minutos, fecha_sola,hora]

        else:
            values.pop("fecha_constitucion")
            


    class Config:
        orm_mode = True


# *************************************************************************************************************************************


class ConstanciaFiscalData(_ConstanciaFiscalBase):
    id: int = 0
    regimenes_fiscales: _typing.List[Regimenes] = []

    @_pydantic.root_validator
    def values_fechas(cls,values) -> _typing.Dict:
        if values["fecha_nacimiento"] is not None:
            fecha_nacimiento = str(_fn.format_datetime(values["fecha_nacimiento"]))
            values.pop("fecha_nacimiento")
            fecha_hora_minutos = _dt.datetime.strptime(fecha_nacimiento, "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%Y-%m-%d %H:%M"
            )

            fecha_sola = _dt.datetime.strptime(fecha_nacimiento, "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%Y-%m-%d"
            )

            hora=_dt.datetime.strptime(fecha_nacimiento, "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%H:%M"
            )
            
            values["fecha_nacimiento"] = [fecha_nacimiento,fecha_hora_minutos, fecha_sola,hora]


        if values["fecha_constitucion"] is not None:
            fecha_constitucion = str(_fn.format_datetime(values["fecha_constitucion"]))
            values.pop("fecha_constitucion")
            fecha_hora_minutos = _dt.datetime.strptime(fecha_constitucion, "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%Y-%m-%d %H:%M"
            )

            fecha_sola = _dt.datetime.strptime(fecha_constitucion, "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%Y-%m-%d"
            )

            hora=_dt.datetime.strptime(fecha_constitucion, "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%H:%M"
            )
            
            values["fecha_constitucion"] = [fecha_constitucion,fecha_hora_minutos, fecha_sola,hora]

        return values

    class Config:
        orm_mode = True

    

# *************************************************************************************************************************************
# SECCION: PNN
# *************************************************************************************************************************************


class _PNNBase(_pydantic.BaseModel):

    clave_censal: _typing.Optional[int] = 0
    poblacion: _typing.Optional[str] = ""	
    municipio: _typing.Optional[str] = ""	
    estado: _typing.Optional[str] = ""
    presuscripcion: _typing.Optional[str] = ""	
    region: _typing.Optional[int] = 0	
    asl: _typing.Optional[int] = 0		
    nir: _typing.Optional[int] = 0		
    serie: _typing.Optional[int] = 0		
    numeracion_inicial: _typing.Optional[int] = 0		
    numeracion_final: _typing.Optional[int] = 0	
    ocupacion: _typing.Optional[int] = 0		
    tipo_red: _typing.Optional[str] = ""	
    modalidad: _typing.Optional[str] = ""	
    razon_social: _typing.Optional[str] = ""	
    fecha_asignacion: _typing.Optional[_dt.datetime]  = None	
    fecha_consolidacion: _typing.Optional[_dt.datetime]  = None	
    fecha_migracion: _typing.Optional[_dt.datetime]  = None	
    nir_anterior: _typing.Optional[int] = 0

# *************************************************************************************************************************************

# La clase Create hace referencia a la clase _Base
# y hereda los campos de la misma
class PNNCreate(_PNNBase):
    pass


# *************************************************************************************************************************************


class PNN(_PNNBase):

    id: int = 0

    class Config:
        orm_mode = True

# *************************************************************************************************************************************
# SECCION: TELEFONO
# *************************************************************************************************************************************


class Telefono(_pydantic.BaseModel):

    telefono: _typing.Optional[str] = ""
    telefono_format: _typing.Optional[str] = ""	
    tipo_red: _typing.Optional[str] = ""	
    estado: _typing.Optional[str] = ""
    compania_origen: _typing.Optional[str] = ""	


# *************************************************************************************************************************************
# SECCION: REGISTRO SANITARIO
# *************************************************************************************************************************************


class _RegistroSanitarioBase(_pydantic.BaseModel):

    num_registro:  _typing.Optional[str] = ""
    denominacion_generica:  _typing.Optional[str] = ""
    denominacion_distintiva: _typing.Optional[str] = ""
    tipo_medicamento:  _typing.Optional[str] = ""
    indicacion_terapeutica:  _typing.Optional[str] = ""
    titular_registro:  _typing.Optional[str] = ""
    fabricante_medicamento:  _typing.Optional[str] = ""
    principio_activo:  _typing.Optional[str] = ""
    detalle_registro:  _typing.Optional[str] = ""


# *************************************************************************************************************************************

# La clase Create hace referencia a la clase _Base
# y hereda los campos de la misma
class RegistroSanitarioCreate(_RegistroSanitarioBase):
    pass


# *************************************************************************************************************************************


class RegistroSanitario(_RegistroSanitarioBase):

    id: int = 0


    class Config:
        orm_mode = True


# *************************************************************************************************************************************
# SECCION: REGISTRO SANITARIO
# *************************************************************************************************************************************


class _WebSitesCheckBase(_pydantic.BaseModel):

    bloque: _typing.Optional[int] = 0
    url: _typing.Optional[str] = ""
    status: _typing.Optional[str] = ""
    status_code: _typing.Optional[int] = 0
    response_time: _typing.Optional[float] = 0
    issuer: _typing.Optional[str] = ""
    subject: _typing.Optional[str] = ""
    serial_number: _typing.Optional[str] = ""
    not_valid_before: _typing.Optional[_dt.datetime] = None
    not_valid_after:  _typing.Optional[_dt.datetime] = None
    signature_algorithm: _typing.Optional[str] = ""
    server_info: _typing.Optional[str] = ""
    error: _typing.Optional[str] = ""


# *************************************************************************************************************************************

# La clase Create hace referencia a la clase _Base
# y hereda los campos de la misma
class WebSitesCheckCreate(_WebSitesCheckBase):
    pass


# *************************************************************************************************************************************


class WebSitesCheck(_WebSitesCheckBase):

    id: int = 0

    @_pydantic.root_validator
    def value_url_descripcion(cls, values) -> _typing.Dict:

        values["url_descripcion"] = _fn.get_choice_value(
            _settings.CHOICES,
            "clave",
            values["url"],
            "descripcion",
        )

        return values
    
    @_pydantic.root_validator
    def values_fechas(cls,values) -> _typing.Dict:
        if values["not_valid_before"] is not None:
            not_valid_before = str(_fn.format_datetime(values["not_valid_before"]))
            values.pop("not_valid_before")
            fecha_hora_minutos = _dt.datetime.strptime(not_valid_before, "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%Y-%m-%d %H:%M"
            )

            fecha_sola = _dt.datetime.strptime(not_valid_before, "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%Y-%m-%d"
            )

            hora=_dt.datetime.strptime(not_valid_before, "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%H:%M"
            )
            
            values["not_valid_before"] = fecha_hora_minutos


        if values["not_valid_after"] is not None:
            not_valid_after = str(_fn.format_datetime(values["not_valid_after"]))
            values.pop("not_valid_after")
            fecha_hora_minutos = _dt.datetime.strptime(not_valid_after, "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%Y-%m-%d %H:%M"
            )

            fecha_sola = _dt.datetime.strptime(not_valid_after, "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%Y-%m-%d"
            )

            hora=_dt.datetime.strptime(not_valid_after, "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%H:%M"
            )
            
            values["not_valid_after"] = fecha_hora_minutos

        return values
    
    class Config:
        orm_mode = True


# *************************************************************************************************************************************
class WebSitesWarningBase(_pydantic.BaseModel):
    
    bloque: _typing.Optional[int] = 0	
    free_warnings: _typing.Optional[bool] = False

# *************************************************************************************************************************************

# La clase Create hace referencia a la clase _Base
# y hereda los campos de la misma
class WWebSitesWarningCreate(WebSitesWarningBase):
    pass


# *************************************************************************************************************************************


class WebSitesWarning(WebSitesWarningBase):

    id: int = 0
    
    class Config:
        orm_mode = True   

# *************************************************************************************************************************************
# SECCION: DIAS DESCANSO
# *************************************************************************************************************************************
class _DiaDescansoBase(_pydantic.BaseModel):
    
    fecha: _typing.Optional[_dt.date] = None	
    dia_semana: _typing.Optional[str] = ""
    descripcion: _typing.Optional[str] = ""

# *************************************************************************************************************************************

# La clase Create hace referencia a la clase _Base
# y hereda los campos de la misma
class DiaDescansoCreate(_DiaDescansoBase):
    pass


# *************************************************************************************************************************************


class DiaDescanso(_DiaDescansoBase):

    id: int = 0
    
    class Config:
        orm_mode = True   

# *************************************************************************************************************************************
# SECCION: BINES
# *************************************************************************************************************************************
class _BinesBase(_pydantic.BaseModel):

    bin: _typing.Optional[str] = ""
    brand: _typing.Optional[str] = ""
    type: _typing.Optional[str] = ""
    category: _typing.Optional[str] = ""
    issuer: _typing.Optional[str] = ""
    alpha_2: _typing.Optional[str] = ""
    alpha_3: _typing.Optional[str] = ""
    country: _typing.Optional[str] = ""
    latitude: _typing.Optional[str] = ""
    longitude: _typing.Optional[str] = ""
    bank_phone: _typing.Optional[str] = ""
    bank_url: _typing.Optional[str] = ""

# *************************************************************************************************************************************

# La clase Create hace referencia a la clase _Base
# y hereda los campos de la misma
class BinesCreate(_BinesBase):
    pass


# *************************************************************************************************************************************


class Bines(_BinesBase):

    id: int = 0
    
    class Config:
        orm_mode = True   


# *************************************************************************************************************************************
# SECCION: TARJETAS
# *************************************************************************************************************************************
class TarjetaLocal(_pydantic.BaseModel):

    prefix: _typing.Optional[int] = 0
    issuer: _typing.Optional[int] = 0
    reference_number: _typing.Optional[int] = 0
    type: _typing.Optional[int] = 0
    card_index: _typing.Optional[int] = 0
    