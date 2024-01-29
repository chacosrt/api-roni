import datetime as _dt
import sqlalchemy as _sql
import sqlalchemy.orm as _orm

# import sqlalchemy.orm as _orm
# import functions.fn as _fn
import database as _database


# *************************************************************************************************************************************
# CEDULAS
# *************************************************************************************************************************************

class CedulaSEP(_database.Base):
    # nombre de la tabla
    __tablename__ = "cedulas_sep"
    # campos
    id = _sql.Column(_sql.Integer, primary_key=True, autoincrement=True, index=True)
    anioreg = _sql.Column(_sql.Integer, default=None)
    carArea = _sql.Column(_sql.String(100), default="")
    carCons = _sql.Column(_sql.String(100), default="")
    carNivel = _sql.Column(_sql.String(100), default="")
    curp = _sql.Column(_sql.String(100), default="", index=True)
    desins = _sql.Column(_sql.String(100), default="")
    foja = _sql.Column(_sql.String(100), default="")
    idCedula = _sql.Column(_sql.Integer, default=None, index=True)
    inscons = _sql.Column(_sql.Integer, default=None)
    insedo = _sql.Column(_sql.Integer, default=None)
    libro = _sql.Column(_sql.String(100), default="", index=True)
    materno = _sql.Column(_sql.String(100), default="")
    maternoM = _sql.Column(_sql.String(100), default="")
    nombre = _sql.Column(_sql.String(100), default="")
    nombreM = _sql.Column(_sql.String(100), default="")
    numero = _sql.Column(_sql.Integer, default=None)
    paterno = _sql.Column(_sql.String(100), default="")
    paternoM = _sql.Column(_sql.String(100), default="")
    sexo = _sql.Column(_sql.String(100), default="")
    tipo = _sql.Column(_sql.String(100), default="")
    titulo = _sql.Column(_sql.String(255), default="")

    filename = _sql.Column(_sql.String(255), default="")
    idCedula = _sql.Column(_sql.String(255), default="")
    idProfesionista = _sql.Column(_sql.String(255), default="")
    sessionId = _sql.Column(_sql.String(255), default="")
    theStream = _sql.Column(_sql.String(255), default="")
    token = _sql.Column(_sql.String(255), default="")
    urlVideo = _sql.Column(_sql.String(255), default="")

    sort_field = _sql.Column(_sql.String(255), default="", index=True)
    search_field = _sql.Column(_sql.String(255), default="", index=True)
    creado_por = _sql.Column(_sql.String(50), default="", index=True)
    creado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)
    modificado_por = _sql.Column(_sql.String(50), default="", index=True)
    modificado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)


# *************************************************************************************************************************************

class CedulaBuho(_database.Base):
    # nombre de la tabla
    __tablename__ = "cedulas_buho"
    # campos
    id = _sql.Column(_sql.Integer, primary_key=True, autoincrement=True, index=True)
    cedula = _sql.Column(_sql.Integer, default=None, index=True)
    nombre_completo = _sql.Column(_sql.String(250), default="")
    carrera = _sql.Column(_sql.String(250), default="")
    universidad = _sql.Column(_sql.String(100), default="")
    estado = _sql.Column(_sql.String(100), default="")
    anio = _sql.Column(_sql.Integer, default=None)

    creado_por = _sql.Column(_sql.String(50), default="", index=True)
    creado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)
    modificado_por = _sql.Column(_sql.String(50), default="", index=True)
    modificado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)


# *************************************************************************************************************************************
# CONSTANCIAS FISCALES
# *************************************************************************************************************************************

class ConstanciaFiscal(_database.Base):
    # nombre de la tabla
    __tablename__ = "constancia_fiscal"
    # campos
    id = _sql.Column(_sql.Integer, primary_key=True, autoincrement=True, index=True)
    id_constancia = _sql.Column(_sql.String(100), default="", index=True)
    rfc = _sql.Column(_sql.String(100), default="")
    nombre = _sql.Column(_sql.String(100), default="")
    materno = _sql.Column(_sql.String(100), default="")
    paterno = _sql.Column(_sql.String(100), default="")
    curp = _sql.Column(_sql.String(100), default="", index=True)
    fecha_nacimiento = _sql.Column(_sql.DateTime, default=None, index=True)
    regimen_capital = _sql.Column(_sql.String(100), default="", index=True)
    razon_social = _sql.Column(_sql.String(250), default="")
    fecha_constitucion = _sql.Column(_sql.DateTime, default=None, index=True)
    fecha_inicio_operaciones = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)
    situacion_contribuyente = _sql.Column(_sql.String(100), default="")
    fecha_ultimo_cambio = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)

    entidad_federativa = _sql.Column(_sql.String(100), default="")
    municipio_delegacion = _sql.Column(_sql.String(100), default="")
    colonia = _sql.Column(_sql.String(100), default="")
    tipo_vialidad = _sql.Column(_sql.String(100), default="")
    nombre_vialidad = _sql.Column(_sql.String(100), default="", index=True)
    num_ext = _sql.Column(_sql.String(100), default="")
    num_int = _sql.Column(_sql.String(100), default="")
    cp = _sql.Column(_sql.String(100), default="")
    correo = _sql.Column(_sql.String(100), default="")
    al = _sql.Column(_sql.String(100), default="")

    creado_por = _sql.Column(_sql.String(50), default="", index=True)
    creado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)
    modificado_por = _sql.Column(_sql.String(50), default="", index=True)
    modificado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)

    

    

# *************************************************************************************************************************************
# PNN
# *************************************************************************************************************************************

class PNN(_database.Base):
    # nombre de la tabla
    __tablename__ = "plan_nacional_numeracion"
    # campos
    id = _sql.Column(_sql.Integer, primary_key=True, autoincrement=True, index=True)
    clave_censal = _sql.Column(_sql.Integer, default=0)	
    poblacion = _sql.Column(_sql.String(100), default="")	
    municipio = _sql.Column(_sql.String(100), default="")	
    estado = _sql.Column(_sql.String(100), default="")	
    presuscripcion = _sql.Column(_sql.String(100), default="")	
    region = _sql.Column(_sql.Integer, default=0)	
    asl = _sql.Column(_sql.Integer, default=0)		
    nir = _sql.Column(_sql.Integer, default=0)		
    serie = _sql.Column(_sql.Integer, default=0)		
    numeracion_inicial = _sql.Column(_sql.Integer, default=0)		
    numeracion_final = _sql.Column(_sql.Integer, default=0)		
    ocupacion = _sql.Column(_sql.Integer, default=0)		
    tipo_red = _sql.Column(_sql.String(100), default="")	
    modalidad = _sql.Column(_sql.String(100), default="")	
    razon_social = _sql.Column(_sql.String(100), default="")	
    fecha_asignacion = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)	
    fecha_consolidacion = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)	
    fecha_migracion = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)	
    nir_anterior = _sql.Column(_sql.Integer, default=0)		

    creado_por = _sql.Column(_sql.String(50), default="", index=True)
    creado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)
    modificado_por = _sql.Column(_sql.String(50), default="", index=True)
    modificado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)		

# *************************************************************************************************************************************
# REGIMENES FISCALES
# *************************************************************************************************************************************		

class Regimenes(_database.Base):
    # nombre de la tabla
    __tablename__ = "regimenes_fiscales"
    # campos
    id = _sql.Column(_sql.Integer, primary_key=True, autoincrement=True, index=True)
    id_constancia =  _sql.Column(_sql.String(100), default="", index=True)
    regimen = _sql.Column(_sql.Text, default="")
    fecha_alta = _sql.Column(_sql.DateTime, default=None, index=True)

    creado_por = _sql.Column(_sql.String(50), default="", index=True)
    creado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)
    modificado_por = _sql.Column(_sql.String(50), default="", index=True)
    modificado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)	

    
    regimenes_lista = _orm.relationship(
        "ConstanciaFiscal",
        primaryjoin=("foreign(Regimenes.id_constancia) == remote(ConstanciaFiscal.id_constancia)"),backref="regimenes_fiscales"
    )


# *************************************************************************************************************************************
# REGISTRO SANITARIO
# *************************************************************************************************************************************

class RegistroSanitario(_database.Base):
    # nombre de la tabla
    __tablename__ = "registro_sanitario"
    # campos
    id = _sql.Column(_sql.Integer, primary_key=True, autoincrement=True, index=True)
    num_registro = _sql.Column(_sql.String(100), default="")	
    denominacion_generica = _sql.Column(_sql.String(100), default="")
    denominacion_distintiva = _sql.Column(_sql.String(100), default="")
    tipo_medicamento = _sql.Column(_sql.String(100), default="")
    indicacion_terapeutica = _sql.Column(_sql.Text, default="")
    titular_registro = _sql.Column(_sql.String(100), default="")
    fabricante_medicamento = _sql.Column(_sql.String(100), default="")
    principio_activo = _sql.Column(_sql.String(100), default="")
    detalle_registro = _sql.Column(_sql.Text, default="")

    creado_por = _sql.Column(_sql.String(50), default="", index=True)
    creado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)
    modificado_por = _sql.Column(_sql.String(50), default="", index=True)
    modificado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)		


# *************************************************************************************************************************************
# WebSitesCheck
# *************************************************************************************************************************************
class WebSitesCheck(_database.Base):
    # nombre de la tabla
    __tablename__ = "web_sites_check"
    # campos
    id = _sql.Column(_sql.Integer, primary_key=True, autoincrement=True, index=True)
    bloque = _sql.Column(_sql.Integer, default=0)	
    url = _sql.Column(_sql.Text, default="")	
    status = _sql.Column(_sql.String(100), default="")	
    status_code = _sql.Column(_sql.Integer, default=0)	
    response_time = _sql.Column(_sql.Float, default=0)	
    issuer = _sql.Column(_sql.String(255), default="")	
    subject = _sql.Column(_sql.String(255), default="")	
    serial_number = _sql.Column(_sql.String(255), default="")	
    not_valid_before = _sql.Column(_sql.DateTime, default=None, index=True)
    not_valid_after = _sql.Column(_sql.DateTime, default=None, index=True)
    signature_algorithm = _sql.Column(_sql.String(255), default="")	
    server_info = _sql.Column(_sql.String(100), default="")	
    error = _sql.Column(_sql.Text, default="")	

    creado_por = _sql.Column(_sql.String(50), default="", index=True)
    creado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)
    modificado_por = _sql.Column(_sql.String(50), default="", index=True)
    modificado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)		

# *************************************************************************************************************************************
class WebSitesWarning(_database.Base):
    # nombre de la tabla
    __tablename__ = "web_sites_warnings"
    # campos
    id = _sql.Column(_sql.Integer, primary_key=True, autoincrement=True, index=True)
    bloque = _sql.Column(_sql.Integer, default=0)	
    free_warnings =	_sql.Column(_sql.Boolean, default=True)

    creado_por = _sql.Column(_sql.String(50), default="", index=True)
    creado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)
    modificado_por = _sql.Column(_sql.String(50), default="", index=True)
    modificado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)		

# *************************************************************************************************************************************
# Dias Festivos
# *************************************************************************************************************************************
class DiasFestivos(_database.Base):
    # nombre de la tabla
    __tablename__ = "dias_festivos"
    # campos
    id = _sql.Column(_sql.Integer, primary_key=True, autoincrement=True, index=True)
    fecha =_sql.Column(_sql.Date, default=_dt.date.today(), index=True)	
    dia_semana = _sql.Column(_sql.Text, default="")	
    descripcion = _sql.Column(_sql.Text, default="")
 
    creado_por = _sql.Column(_sql.String(50), default="", index=True)
    creado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)
    modificado_por = _sql.Column(_sql.String(50), default="", index=True)
    modificado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)	


# *************************************************************************************************************************************
# Dias Festivos
# *************************************************************************************************************************************
class Bines(_database.Base):
    # nombre de la tabla
    __tablename__ = "bines"
    # campos
    id = _sql.Column(_sql.Integer, primary_key=True, autoincrement=True, index=True)
    bin = _sql.Column(_sql.String(100), default="", index=True)
    brand = _sql.Column(_sql.Text, default="", index=True)
    type = _sql.Column(_sql.Text, default="", index=True)
    category = _sql.Column(_sql.Text, default="", index=True)
    issuer = _sql.Column(_sql.Text, default="", index=True)
    alpha_2 = _sql.Column(_sql.Text, default="", index=True)
    alpha_3 = _sql.Column(_sql.Text, default="", index=True)
    country = _sql.Column(_sql.Text, default="", index=True)
    latitude = _sql.Column(_sql.Text, default="", index=True)
    longitude = _sql.Column(_sql.Text, default="", index=True)
    bank_phone = _sql.Column(_sql.Text, default="", index=True)
    bank_url = _sql.Column(_sql.Text, default="", index=True)
 
    creado_por = _sql.Column(_sql.String(50), default="", index=True)
    creado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)
    modificado_por = _sql.Column(_sql.String(50), default="", index=True)
    modificado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)	 



# *************************************************************************************************************************************
# Dias Referencias
# *************************************************************************************************************************************
class Referencias(_database.Base):
    # nombre de la tabla
    __tablename__ = "referencias"

     # campos
    id = _sql.Column(_sql.Integer, primary_key=True, autoincrement=True, index=True)
    origen = _sql.Column(_sql.String(10), default="", index=True)
    valor = _sql.Column(_sql.Integer, default=0, index=True)

    creado_por = _sql.Column(_sql.String(50), default="", index=True)
    creado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)
    modificado_por = _sql.Column(_sql.String(50), default="", index=True)
    modificado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)	 
