from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime, date

# ============================================================
# ESQUEMAS DE EQUIPOS
# ============================================================

class EquipoBase(BaseModel):
    cliente: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    tipo: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    serie: Optional[str] = None
    fecha_ingreso: Optional[str] = None
    observaciones: Optional[str] = None

class EquipoCreate(EquipoBase):
    pass

class EquipoUpdate(BaseModel):
    cliente: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    tipo: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    serie: Optional[str] = None
    observaciones: Optional[str] = None

class Equipo(EquipoBase):
    id: int
    codigo: str
    pdf: Optional[str] = None
    qr_base64: Optional[str] = None
    creado_en: Optional[datetime] = None
    actualizado_en: Optional[datetime] = None

    @field_validator('fecha_ingreso', mode='before')
    @classmethod
    def convert_date_to_string(cls, v):
        if isinstance(v, date):
            return v.isoformat()
        return v

    class Config:
        from_attributes = True

class EquipoResponse(BaseModel):
    equipo: Equipo
    qr_base64: str

# ============================================================
# ESQUEMAS DE INTERVENCIONES
# ============================================================

class IntervencionBase(BaseModel):
    fecha: str
    tipo_trabajo: Optional[str] = None
    motivo: Optional[str] = None
    diagnostico: Optional[str] = None
    trabajo_realizado: Optional[str] = None
    repuestos: Optional[str] = None
    mediciones: Optional[str] = None
    observaciones: Optional[str] = None
    dias_garantia: Optional[int] = None  # ⭐ NUEVO

class IntervencionCreate(IntervencionBase):
    pass

class IntervencionUpdate(BaseModel):
    tipo_trabajo: Optional[str] = None
    motivo: Optional[str] = None
    diagnostico: Optional[str] = None
    trabajo_realizado: Optional[str] = None
    repuestos: Optional[str] = None
    mediciones: Optional[str] = None
    observaciones: Optional[str] = None
    dias_garantia: Optional[int] = None  # ⭐ NUEVO

class Intervencion(IntervencionBase):
    id: int
    equipo_id: int
    pdf: Optional[str] = None
    dias_garantia: Optional[int] = None  # ⭐ NUEVO
    creado_en: Optional[datetime] = None
    actualizado_en: Optional[datetime] = None

    @field_validator('fecha', mode='before')
    @classmethod
    def convert_date_to_string(cls, v):
        if isinstance(v, date):
            return v.isoformat()
        return v

    class Config:
        from_attributes = True

# ============================================================
# ESQUEMAS DE HISTORIAL
# ============================================================

class EquipoHistorial(BaseModel):
    equipo: Equipo
    intervenciones: List[Intervencion]

# ============================================================
# ESQUEMAS DE CITAS
# ============================================================

class CitaBase(BaseModel):
    titulo: str
    motivo: str
    cliente: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    fecha_programada: str
    recordatorio_minutos: int = 20
    equipo_codigo: Optional[str] = None

class CitaCreate(CitaBase):
    pass

class CitaUpdate(BaseModel):
    titulo: Optional[str] = None
    motivo: Optional[str] = None
    cliente: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    fecha_programada: Optional[str] = None
    recordatorio_minutos: Optional[int] = None
    estado: Optional[str] = None
    notificado: Optional[bool] = None

class CitaResponse(BaseModel):
    id: int
    titulo: str
    motivo: str
    cliente: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    fecha_programada: datetime
    recordatorio_minutos: int
    notificado: bool
    estado: str
    equipo_id: Optional[int] = None
    creado_en: Optional[datetime] = None
    actualizado_en: Optional[datetime] = None

    class Config:
        from_attributes = True