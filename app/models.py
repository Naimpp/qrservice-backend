from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Equipo(Base):
    __tablename__ = "equipos"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, index=True, nullable=False)
    cliente = Column(String(200), nullable=False)
    telefono = Column(String(50), nullable=True)
    direccion = Column(String(300), nullable=True)
    tipo = Column(String(100), nullable=True)
    marca = Column(String(100), nullable=True)
    modelo = Column(String(100), nullable=True)
    serie = Column(String(100), nullable=True)
    fecha_ingreso = Column(Date, nullable=True)
    observaciones = Column(Text, nullable=True)
    pdf = Column(String(500), nullable=True)
    qr_base64 = Column(Text, nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())

    intervenciones = relationship("Intervencion", back_populates="equipo", cascade="all, delete-orphan")
    citas = relationship("Cita", back_populates="equipo")


class Intervencion(Base):
    __tablename__ = "intervenciones"

    id = Column(Integer, primary_key=True, index=True)
    equipo_id = Column(Integer, ForeignKey("equipos.id"), nullable=False)
    fecha = Column(Date, nullable=False)
    tipo_trabajo = Column(String(200), nullable=True)
    motivo = Column(Text, nullable=True)
    diagnostico = Column(Text, nullable=True)
    trabajo_realizado = Column(Text, nullable=True)
    repuestos = Column(Text, nullable=True)
    mediciones = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)
    pdf = Column(String(500), nullable=True)
    dias_garantia = Column(Integer, nullable=True)  # ⭐ NUEVO
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())

    equipo = relationship("Equipo", back_populates="intervenciones")


class Cita(Base):
    __tablename__ = "citas"

    id = Column(Integer, primary_key=True, index=True)
    equipo_id = Column(Integer, ForeignKey("equipos.id"), nullable=True)
    titulo = Column(String(200), nullable=False)
    motivo = Column(Text, nullable=False)
    cliente = Column(String(200), nullable=False)
    telefono = Column(String(50), nullable=True)
    direccion = Column(String(300), nullable=True)
    fecha_programada = Column(DateTime, nullable=False)
    recordatorio_minutos = Column(Integer, default=20)
    notificado = Column(Boolean, default=False)
    estado = Column(String(50), default="pendiente")
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())

    equipo = relationship("Equipo", back_populates="citas")