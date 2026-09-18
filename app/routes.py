from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date
import uuid
import base64
import qrcode
from io import BytesIO
import os

from app.database import get_db
from app import models
from app.schemas import (
    EquipoCreate, EquipoResponse, EquipoHistorial, Equipo,
    IntervencionCreate, Intervencion,
    CitaCreate, CitaResponse
)
from app.qr import generar_qr  # 🔥 Importar la función de QR

router = APIRouter()

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def generar_codigo_qr():
    return f"QR-{uuid.uuid4().hex[:8].upper()}"

def generar_qr_base64(codigo: str) -> str:
    """Genera un código QR en base64"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(codigo)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def convertir_fecha_a_string(fecha):
    """Convierte un objeto date o datetime a string ISO"""
    if fecha is None:
        return None
    if isinstance(fecha, (date, datetime)):
        return fecha.isoformat()
    return str(fecha)

def convertir_equipo_a_dict(equipo, qr_base64=None):
    """Convierte un objeto Equipo a dict con fechas como string"""
    return {
        "id": equipo.id,
        "codigo": equipo.codigo,
        "cliente": equipo.cliente,
        "telefono": equipo.telefono,
        "direccion": equipo.direccion,
        "tipo": equipo.tipo,
        "marca": equipo.marca,
        "modelo": equipo.modelo,
        "serie": equipo.serie,
        "fecha_ingreso": convertir_fecha_a_string(equipo.fecha_ingreso),
        "observaciones": equipo.observaciones,
        "pdf": equipo.pdf,
        "qr_base64": qr_base64 or equipo.qr_base64,
        "creado_en": convertir_fecha_a_string(equipo.creado_en),
        "actualizado_en": convertir_fecha_a_string(equipo.actualizado_en)
    }

def convertir_intervencion_a_dict(inter):
    """Convierte un objeto Intervencion a dict con fechas como string"""
    return {
        "id": inter.id,
        "equipo_id": inter.equipo_id,
        "fecha": convertir_fecha_a_string(inter.fecha),
        "tipo_trabajo": inter.tipo_trabajo,
        "motivo": inter.motivo,
        "diagnostico": inter.diagnostico,
        "trabajo_realizado": inter.trabajo_realizado,
        "repuestos": inter.repuestos,
        "mediciones": inter.mediciones,
        "observaciones": inter.observaciones,
        "pdf": inter.pdf,
        "dias_garantia": inter.dias_garantia,  # ⭐ NUEVO
        "creado_en": convertir_fecha_a_string(inter.creado_en),
        "actualizado_en": convertir_fecha_a_string(inter.actualizado_en)
    }

# ============================================================
# ENDPOINTS DE EQUIPOS
# ============================================================

@router.post("/equipos", response_model=EquipoResponse)
def crear_equipo(equipo: EquipoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo equipo con código QR"""
    
    try:
        # Generar código y QR
        codigo = generar_codigo_qr()
        qr_base64 = generar_qr_base64(codigo)
        
        # 🔥 GENERAR QR COMO ARCHIVO (usando qr.py)
        try:
            ruta_qr = generar_qr(codigo)
            print(f"✅ QR generado en: {ruta_qr}")
        except Exception as e:
            print(f"⚠️ Error generando archivo QR: {e}")
        
        # Convertir fecha_ingreso de string a date
        fecha_ingreso = None
        if equipo.fecha_ingreso:
            try:
                fecha_ingreso = datetime.strptime(equipo.fecha_ingreso, "%Y-%m-%d").date()
            except ValueError:
                try:
                    fecha_ingreso = datetime.strptime(equipo.fecha_ingreso, "%d/%m/%Y").date()
                except:
                    fecha_ingreso = datetime.now().date()
        
        # Crear el equipo
        nuevo_equipo = models.Equipo(
            codigo=codigo,
            cliente=equipo.cliente,
            telefono=equipo.telefono,
            direccion=equipo.direccion,
            tipo=equipo.tipo,
            marca=equipo.marca,
            modelo=equipo.modelo,
            serie=equipo.serie,
            fecha_ingreso=fecha_ingreso,
            observaciones=equipo.observaciones
        )
        
        db.add(nuevo_equipo)
        db.commit()
        db.refresh(nuevo_equipo)
        
        # Guardar el QR en base64 en la base de datos
        nuevo_equipo.qr_base64 = qr_base64
        db.commit()
        db.refresh(nuevo_equipo)
        
        print(f"✅ Equipo creado con código: {codigo}")
        print(f"✅ QR en base64 guardado en la base de datos")
        
        # Convertir a dict con fechas como string
        equipo_dict = convertir_equipo_a_dict(nuevo_equipo, qr_base64)
        
        # Crear objeto Equipo desde el dict
        equipo_response = Equipo(**equipo_dict)
        
        return EquipoResponse(
            equipo=equipo_response,
            qr_base64=qr_base64
        )
        
    except Exception as e:
        print(f"❌ Error al crear equipo: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/equipos", response_model=List[Equipo])
def listar_equipos(db: Session = Depends(get_db)):
    """Listar todos los equipos"""
    equipos = db.query(models.Equipo).all()
    
    resultado = []
    for equipo in equipos:
        equipo_dict = convertir_equipo_a_dict(equipo)
        resultado.append(Equipo(**equipo_dict))
    
    return resultado

@router.get("/equipos/buscar", response_model=List[EquipoHistorial])
def buscar_equipos(
    cliente: str,
    db: Session = Depends(get_db)
):
    """
    Buscar equipos por cliente, código o teléfono
    Búsqueda insensible a mayúsculas
    """
    print(f"🔍 Buscando: '{cliente}'")
    
    resultados = db.query(models.Equipo).filter(
        models.Equipo.cliente.ilike(f"%{cliente}%") |
        models.Equipo.codigo.ilike(f"%{cliente}%") |
        models.Equipo.telefono.ilike(f"%{cliente}%")
    ).all()
    
    print(f"📊 Encontrados: {len(resultados)} resultados")
    
    equipos_historial = []
    for equipo in resultados:
        intervenciones = db.query(models.Intervencion).filter(
            models.Intervencion.equipo_id == equipo.id
        ).order_by(models.Intervencion.fecha.desc()).all()
        
        equipo_dict = convertir_equipo_a_dict(equipo)
        
        intervenciones_list = []
        for inter in intervenciones:
            # ⭐ NUEVO: usa el helper, que ya incluye dias_garantia
            inter_dict = convertir_intervencion_a_dict(inter)
            intervenciones_list.append(Intervencion(**inter_dict))
        
        equipo_obj = Equipo(**equipo_dict)
        
        equipos_historial.append(
            EquipoHistorial(
                equipo=equipo_obj,
                intervenciones=intervenciones_list
            )
        )
    
    return equipos_historial

@router.get("/equipo/{codigo}", response_model=EquipoHistorial)
def obtener_equipo(codigo: str, db: Session = Depends(get_db)):
    """Obtener un equipo por su código QR"""
    
    equipo = db.query(models.Equipo).filter(
        models.Equipo.codigo == codigo
    ).first()
    
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    
    intervenciones = db.query(models.Intervencion).filter(
        models.Intervencion.equipo_id == equipo.id
    ).order_by(models.Intervencion.fecha.desc()).all()
    
    equipo_dict = convertir_equipo_a_dict(equipo)
    
    intervenciones_list = []
    for inter in intervenciones:
        # ⭐ NUEVO: usa el helper, que ya incluye dias_garantia
        inter_dict = convertir_intervencion_a_dict(inter)
        intervenciones_list.append(Intervencion(**inter_dict))
    
    equipo_obj = Equipo(**equipo_dict)
    
    return EquipoHistorial(
        equipo=equipo_obj,
        intervenciones=intervenciones_list
    )

# ============================================================
# ENDPOINTS DE INTERVENCIONES
# ============================================================

@router.post("/equipo/{codigo}/intervenciones", response_model=Intervencion)
def crear_intervencion(
    codigo: str,
    intervencion: IntervencionCreate,
    db: Session = Depends(get_db)
):
    """Agregar una intervención a un equipo"""
    
    equipo = db.query(models.Equipo).filter(
        models.Equipo.codigo == codigo
    ).first()
    
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    
    fecha_intervencion = None
    if intervencion.fecha:
        try:
            fecha_intervencion = datetime.strptime(intervencion.fecha, "%Y-%m-%d").date()
        except ValueError:
            try:
                fecha_intervencion = datetime.strptime(intervencion.fecha, "%d/%m/%Y").date()
            except:
                fecha_intervencion = datetime.now().date()
    
    # ⭐ NUEVO: guarda dias_garantia
    nueva_intervencion = models.Intervencion(
        equipo_id=equipo.id,
        fecha=fecha_intervencion or datetime.now().date(),
        tipo_trabajo=intervencion.tipo_trabajo,
        motivo=intervencion.motivo,
        diagnostico=intervencion.diagnostico,
        trabajo_realizado=intervencion.trabajo_realizado,
        repuestos=intervencion.repuestos,
        mediciones=intervencion.mediciones,
        observaciones=intervencion.observaciones,
        dias_garantia=intervencion.dias_garantia
    )
    
    db.add(nueva_intervencion)
    db.commit()
    db.refresh(nueva_intervencion)
    
    # ⭐ NUEVO: usa el helper, que ya incluye dias_garantia
    inter_dict = convertir_intervencion_a_dict(nueva_intervencion)
    
    return Intervencion(**inter_dict)

# ============================================================
# ENDPOINTS DE CITAS
# ============================================================

@router.post("/citas", response_model=CitaResponse)
def crear_cita(cita: CitaCreate, db: Session = Depends(get_db)):
    """Programar una nueva cita"""
    
    try:
        fecha_programada = datetime.fromisoformat(cita.fecha_programada)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usar ISO format (YYYY-MM-DDTHH:MM:SS)")
    
    nueva_cita = models.Cita(
        titulo=cita.titulo,
        motivo=cita.motivo,
        cliente=cita.cliente,
        telefono=cita.telefono,
        direccion=cita.direccion,
        fecha_programada=fecha_programada,
        recordatorio_minutos=cita.recordatorio_minutos,
        estado="pendiente"
    )
    
    if cita.equipo_codigo:
        equipo = db.query(models.Equipo).filter(
            models.Equipo.codigo == cita.equipo_codigo
        ).first()
        if equipo:
            nueva_cita.equipo_id = equipo.id
    
    db.add(nueva_cita)
    db.commit()
    db.refresh(nueva_cita)
    
    return nueva_cita

@router.get("/citas", response_model=List[CitaResponse])
def obtener_citas(db: Session = Depends(get_db)):
    """Obtener todas las citas"""
    return db.query(models.Cita).order_by(models.Cita.fecha_programada.desc()).all()

@router.get("/citas/pendientes", response_model=List[CitaResponse])
def obtener_citas_pendientes(db: Session = Depends(get_db)):
    """Obtener citas pendientes"""
    return db.query(models.Cita).filter(
        models.Cita.estado == "pendiente"
    ).order_by(models.Cita.fecha_programada.asc()).all()

@router.delete("/citas/{cita_id}")
def eliminar_cita(cita_id: int, db: Session = Depends(get_db)):
    """Eliminar una cita"""
    
    cita = db.query(models.Cita).filter(
        models.Cita.id == cita_id
    ).first()
    
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    db.delete(cita)
    db.commit()
    
    return {"message": "Cita eliminada correctamente"}