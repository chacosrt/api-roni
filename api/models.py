import datetime as _dt
import sqlalchemy as _sql
import sqlalchemy.orm as _orm

# import sqlalchemy.orm as _orm
# import functions.fn as _fn
import database as _database


# *************************************************************************************************************************************
# CEDULAS
# *************************************************************************************************************************************

class Torneos(_database.Base):
    # nombre de la tabla
    __tablename__ = "torneos"
    # campos
    id = _sql.Column(_sql.Integer, primary_key=True, autoincrement=True, index=True)
    nombre_torneo = _sql.Column(_sql.String(250), default="")
    lugar = _sql.Column(_sql.String(250), default="")
    temporada = _sql.Column(_sql.String(100), default="")
    modalidad = _sql.Column(_sql.String(100), default="")
    dias = _sql.Column(_sql.Text, default="", )
    horarios = _sql.Column(_sql.Text, default="")
    fecha_inicio = _sql.Column(_sql.Date, default=_dt.date.today(), index=True)
    fecha_fin = _sql.Column(_sql.Date, default=_dt.date.today(), index=True)
    categoria = _sql.Column(_sql.String(100), default="")
    img = _sql.Column(_sql.Text, default="")
    estatus = _sql.Column(_sql.Integer, default=None,)

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

    
    """   regimenes_lista = _orm.relationship(
        "ConstanciaFiscal",
        primaryjoin=("foreign(Regimenes.id_constancia) == remote(ConstanciaFiscal.id_constancia)"),backref="regimenes_fiscales"
    ) """



