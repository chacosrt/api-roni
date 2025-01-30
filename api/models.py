import datetime as _dt
import sqlalchemy as _sql
import sqlalchemy.orm as _orm

# import sqlalchemy.orm as _orm
# import functions.fn as _fn
import database as _database


# *************************************************************************************************************************************
# Torneos
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

    torneo_equipos = _orm.relationship(
        "Equipos", foreign_keys="Equipos.liga", backref="liga_equipo"
    )

    torneo_partidos = _orm.relationship(
        "Partidos", foreign_keys="Partidos.liga", backref="liga_partido"
    )

    torneo_posiciones = _orm.relationship(
        "Posiciones", foreign_keys="Posiciones.liga", backref="liga_tabla"
    )


# *************************************************************************************************************************************

class Equipos(_database.Base):
    # nombre de la tabla
    __tablename__ = "equipos"
    # campos
    id = _sql.Column(_sql.Integer, primary_key=True, autoincrement=True, index=True)
    liga = _sql.Column(_sql.Integer, _sql.ForeignKey("torneos.id"))
    nombre = _sql.Column(_sql.String(150), default="", index=True)
    delegado = _sql.Column(_sql.String(250), default="")
    img_equipo = _sql.Column(_sql.Text, default="")
    estatus = _sql.Column(_sql.Integer, default=None,)

    creado_por = _sql.Column(_sql.String(50), default="", index=True)
    creado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)
    modificado_por = _sql.Column(_sql.String(50), default="", index=True)
    modificado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)

    equipo_jugador = _orm.relationship(
        "Jugadores", foreign_keys="Jugadores.equipo", backref="equipo_jugador"
    )

    torneo_posicion = _orm.relationship(
        "Posiciones", foreign_keys="Posiciones.equipo", backref="equipo_tabla"
    )


# *************************************************************************************************************************************
# Jugadores
# *************************************************************************************************************************************		

class Jugadores(_database.Base):
    # nombre de la tabla
    __tablename__ = "jugadores"
    # campos
    id = _sql.Column(_sql.Integer, primary_key=True, autoincrement=True, index=True)
    nombre = _sql.Column(_sql.String(150), default="", index=True)
    ap_p = _sql.Column(_sql.String(150), default="", index=True)
    ap_m = _sql.Column(_sql.String(150), default="", index=True)
    edad  =  _sql.Column(_sql.Integer, default=0, index=True)
    liga  =  _sql.Column(_sql.Integer, default=0, index=True)
    equipo = _sql.Column(_sql.Integer, _sql.ForeignKey("equipos.id"))
    dorsal  =  _sql.Column(_sql.Integer, default=0, index=True)    
    expediente = _sql.Column(_sql.String(30), default="", index=True)
    seccional = _sql.Column(_sql.String(30), default="", index=True)
    direccion = _sql.Column(_sql.Text, default="")
    telefono = _sql.Column(_sql.String(30), default="", index=True)
    img = _sql.Column(_sql.Text, default="")
    delegado = _sql.Column(_sql.Boolean, default=False)    
    estatus = _sql.Column(_sql.Integer, default=None)

    creado_por = _sql.Column(_sql.String(50), default="", index=True)
    creado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)
    modificado_por = _sql.Column(_sql.String(50), default="", index=True)
    modificado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)	

    
    """   regimenes_lista = _orm.relationship(
        "ConstanciaFiscal",
        primaryjoin=("foreign(Regimenes.id_constancia) == remote(ConstanciaFiscal.id_constancia)"),backref="regimenes_fiscales"
    ) """

# *************************************************************************************************************************************
# Partidos
# *************************************************************************************************************************************		

class Partidos(_database.Base):
    # nombre de la tabla
    __tablename__ = "partidos"
    # campos
    id = _sql.Column(_sql.Integer, primary_key=True, autoincrement=True, index=True)
    fecha = _sql.Column(_sql.Date, default=_dt.date.today(), index=True)
    horario = _sql.Column(_sql.String(50), default="", index=True)
    etapa = _sql.Column(_sql.String(150), default="", index=True)
    jornada = _sql.Column(_sql.Integer, default=0, index=True)
    temporada = _sql.Column(_sql.String(150), default="", index=True)
    campo = _sql.Column(_sql.Integer, default=0, index=True)
    liga = _sql.Column(_sql.Integer, _sql.ForeignKey("torneos.id"))
    local  = _sql.Column(_sql.Integer, _sql.ForeignKey("equipos.id"))
    visitante = _sql.Column(_sql.Integer, _sql.ForeignKey("equipos.id"))
    goles_local  =  _sql.Column(_sql.Integer, default=0, index=True)
    goles_visitante  =  _sql.Column(_sql.Integer, default=0, index=True)
    ganador = _sql.Column(_sql.Integer, default=0, index=True)
    estatus = _sql.Column(_sql.Integer, default=0, index=True)
    observaciones = _sql.Column(_sql.Text, default="")

    creado_por = _sql.Column(_sql.String(50), default="", index=True)
    creado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)
    modificado_por = _sql.Column(_sql.String(50), default="", index=True)
    modificado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)	

# *************************************************************************************************************************************
# Tabla de posiciones
# *************************************************************************************************************************************		

class Posiciones(_database.Base):
    # nombre de la tabla
    __tablename__ = "posiciones"
    # campos
    id = _sql.Column(_sql.Integer, primary_key=True, autoincrement=True, index=True)
    temporada = _sql.Column(_sql.String(150), default="", index=True)
    liga = _sql.Column(_sql.Integer, _sql.ForeignKey("torneos.id"))
    equipo  = _sql.Column(_sql.Integer, _sql.ForeignKey("equipos.id"))
    juegos_jugados  =  _sql.Column(_sql.Integer, default=0, index=True)
    juegos_ganados  =  _sql.Column(_sql.Integer, default=0, index=True)
    juegos_empatados = _sql.Column(_sql.Integer, default=0, index=True)
    juegos_perdidos = _sql.Column(_sql.Integer, default=0, index=True)
    goles_favor = _sql.Column(_sql.Integer, default=0, index=True)
    goles_contra = _sql.Column(_sql.Integer, default=0, index=True)
    diferencia_goles = _sql.Column(_sql.Integer, default=0, index=True)
    puntos = _sql.Column(_sql.Integer, default=0, index=True)
    estatus = _sql.Column(_sql.Integer, default=0, index=True)
    
    creado_por = _sql.Column(_sql.String(50), default="", index=True)
    creado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)
    modificado_por = _sql.Column(_sql.String(50), default="", index=True)
    modificado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)	

# *************************************************************************************************************************************
# Equipos de Jugadores
# *************************************************************************************************************************************		

class Jugadores_Equipos(_database.Base):
    # nombre de la tabla
    __tablename__ = "jugadores_equipos"
    # campos
    id = _sql.Column(_sql.Integer, primary_key=True, autoincrement=True, index=True)
    
    id_liga = _sql.Column(_sql.Integer, default=0, index=True)
    id_equipo  = _sql.Column(_sql.Integer, default=0, index=True)
    id_jugador  = _sql.Column(_sql.Integer, default=0, index=True)
        
    creado_por = _sql.Column(_sql.String(50), default="", index=True)
    creado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)
    modificado_por = _sql.Column(_sql.String(50), default="", index=True)
    modificado_el = _sql.Column(_sql.DateTime, default=_dt.datetime.now(), index=True)


