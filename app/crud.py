from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from sqlalchemy import and_

from app import models
from app.schemas import (
    EquipoCreate,
    IntervencionCreate,
    CitaCreate,
    CitaUpdate
)

from app.qr import generar_qr


# =========================================================
# GENERAR CÓDIGO ÚNICO DEL EQUIPO
# =========================================================

def generar_codigo(db: Session):
    anio = date.today().year
    ultimo = (
        db.query(models.Equipo)
        .filter(models.Equipo.codigo.like(f"QR-{anio}-%"))
        .order_by(models.Equipo.id.desc())
        .first()
    )
    if ultimo is None:
        numero = 1
    else:
        ultimo_codigo = ultimo.codigo
        numero = int(ultimo_codigo.split("-")[-1]) + 1
    return f"QR-{anio}-{numero:06d}"


# =========================================================
# OBTENER EQUIPO POR CÓDIGO QR
# =========================================================

def obtener_equipo_por_codigo(db: Session, codigo: str):
    return (
        db.query(models.Equipo)
        .filter(models.Equipo.codigo == codigo)
        .first()
    )


# =========================================================
# CREAR NUEVO EQUIPO
# =========================================================

def crear_equipo(db: Session, equipo: EquipoCreate, codigo: str):
    nuevo = models.Equipo(
        codigo=codigo,
        cliente=equipo.cliente,
        telefono=equipo.telefono,
        direccion=equipo.direccion,
        tipo=equipo.tipo,
        marca=equipo.marca,
        modelo=equipo.modelo,
        serie=equipo.serie,
        fecha_ingreso=equipo.fecha_ingreso,
        observaciones=equipo.observaciones
    )
    
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    
    generar_qr(codigo)
    
    return {
        "id": nuevo.id,
        "codigo": nuevo.codigo,
        "cliente": nuevo.cliente,
        "telefono": nuevo.telefono,
        "direccion": nuevo.direccion,
        "tipo": nuevo.tipo,
        "marca": nuevo.marca,
        "modelo": nuevo.modelo,
        "serie": nuevo.serie,
        "fecha_ingreso": nuevo.fecha_ingreso,
        "observaciones": nuevo.observaciones,
        "pdf": nuevo.pdf
    }


# =========================================================
# CREAR NUEVA INTERVENCIÓN
# =========================================================

def crear_intervencion(db: Session, equipo: models.Equipo, intervencion: IntervencionCreate):
    nueva_intervencion = models.Intervencion(
        equipo_id=equipo.id,
        fecha=intervencion.fecha,
        tipo_trabajo=intervencion.tipo_trabajo,
        motivo=intervencion.motivo,
        diagnostico=intervencion.diagnostico,
        trabajo_realizado=intervencion.trabajo_realizado,
        repuestos=intervencion.repuestos,
        mediciones=intervencion.mediciones,
        observaciones=intervencion.observaciones
    )
    
    db.add(nueva_intervencion)
    db.commit()
    db.refresh(nueva_intervencion)
    
    return nueva_intervencion


# =========================================================
# OBTENER HISTORIAL DE UN EQUIPO
# =========================================================

def obtener_intervenciones(db: Session, equipo_id: int):
    return (
        db.query(models.Intervencion)
        .filter(models.Intervencion.equipo_id == equipo_id)
        .order_by(models.Intervencion.fecha.desc(), models.Intervencion.id.desc())
        .all()
    )


# =========================================================
# CRUD PARA CITAS
# =========================================================

def crear_cita(db: Session, cita: CitaCreate):
    equipo_id = None
    if cita.equipo_codigo:
        equipo = obtener_equipo_por_codigo(db, cita.equipo_codigo)
        if equipo:
            equipo_id = equipo.id
    
    nueva_cita = models.Cita(
        equipo_id=equipo_id,
        titulo=cita.titulo,
        motivo=cita.motivo,
        cliente=cita.cliente,
        telefono=cita.telefono,
        direccion=cita.direccion,
        fecha_programada=cita.fecha_programada,
        recordatorio_minutos=cita.recordatorio_minutos,
        estado="pendiente"
    )
    
    db.add(nueva_cita)
    db.commit()
    db.refresh(nueva_cita)
    
    return nueva_cita


def obtener_citas(db: Session, estado: str = None, desde: datetime = None, hasta: datetime = None):
    query = db.query(models.Cita)
    if estado:
        query = query.filter(models.Cita.estado == estado)
    if desde and hasta:
        query = query.filter(models.Cita.fecha_programada.between(desde, hasta))
    return query.order_by(models.Cita.fecha_programada.asc()).all()


def obtener_citas_pendientes(db: Session, horas_a_futuro: int = 24):
    ahora = datetime.now()
    limite = ahora + timedelta(hours=horas_a_futuro)
    
    return (
        db.query(models.Cita)
        .filter(
            and_(
                models.Cita.estado == "pendiente",
                models.Cita.notificado == False,
                models.Cita.fecha_programada > ahora,
                models.Cita.fecha_programada <= limite
            )
        )
        .order_by(models.Cita.fecha_programada.asc())
        .all()
    )


def obtener_cita_por_id(db: Session, cita_id: int):
    return db.query(models.Cita).filter(models.Cita.id == cita_id).first()


def actualizar_cita(db: Session, cita_id: int, cita_update: CitaUpdate):
    cita = obtener_cita_por_id(db, cita_id)
    if not cita:
        return None
    
    update_data = cita_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(cita, key, value)
    
    db.commit()
    db.refresh(cita)
    return cita


def marcar_cita_notificada(db: Session, cita_id: int):
    cita = obtener_cita_por_id(db, cita_id)
    if cita:
        cita.notificado = True
        db.commit()
        db.refresh(cita)
    return cita


def eliminar_cita(db: Session, cita_id: int):
    cita = obtener_cita_por_id(db, cita_id)
    if cita:
        db.delete(cita)
        db.commit()
        return True
    return False


def obtener_citas_por_equipo(db: Session, codigo: str):
    equipo = obtener_equipo_por_codigo(db, codigo)
    if not equipo:
        return []
    
    return (
        db.query(models.Cita)
        .filter(models.Cita.equipo_id == equipo.id)
        .order_by(models.Cita.fecha_programada.desc())
        .all()
    )