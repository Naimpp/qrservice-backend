from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


# =========================================================
# EQUIPO
# =========================================================

class Equipo(Base):

    __tablename__ = "equipos"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    codigo = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    cliente = Column(
        String(100),
        nullable=False
    )

    telefono = Column(
        String(30),
        nullable=True
    )

    direccion = Column(
        String(200),
        nullable=True
    )

    tipo = Column(
        String(50),
        nullable=True
    )

    marca = Column(
        String(50),
        nullable=True
    )

    modelo = Column(
        String(50),
        nullable=True
    )

    serie = Column(
        String(100),
        nullable=True
    )

    fecha_ingreso = Column(
        Date,
        nullable=True
    )

    pdf = Column(
        String(255),
        nullable=True
    )

    observaciones = Column(
        String(1000),
        nullable=True
    )

    # 🔥 NUEVO CAMPO - QR en base64
    qr_base64 = Column(
        Text,
        nullable=True
    )

    # 🔥 TIMESTAMPS
    creado_en = Column(
        DateTime,
        default=func.now()
    )

    actualizado_en = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now()
    )

    # =====================================================
    # RELACIÓN CON INTERVENCIONES
    # =====================================================

    intervenciones = relationship(
        "Intervencion",
        back_populates="equipo",
        cascade="all, delete-orphan"
    )

    # =====================================================
    # RELACIÓN CON CITAS
    # =====================================================

    citas = relationship(
        "Cita",
        back_populates="equipo",
        cascade="all, delete-orphan"
    )


# =========================================================
# INTERVENCIÓN
# =========================================================

class Intervencion(Base):

    __tablename__ = "intervenciones"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    equipo_id = Column(
        Integer,
        ForeignKey(
            "equipos.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    fecha = Column(
        Date,
        nullable=False
    )

    tipo_trabajo = Column(
        String(100),
        nullable=True
    )

    motivo = Column(
        String(500),
        nullable=True
    )

    diagnostico = Column(
        String(1000),
        nullable=True
    )

    trabajo_realizado = Column(
        String(2000),
        nullable=True
    )

    repuestos = Column(
        String(1000),
        nullable=True
    )

    mediciones = Column(
        String(1000),
        nullable=True
    )

    observaciones = Column(
        String(2000),
        nullable=True
    )

    pdf = Column(
        String(255),
        nullable=True
    )

    # 🔥 TIMESTAMPS
    creado_en = Column(
        DateTime,
        default=func.now()
    )

    actualizado_en = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now()
    )

    equipo = relationship(
        "Equipo",
        back_populates="intervenciones"
    )


# =========================================================
# CITA
# =========================================================

class Cita(Base):

    __tablename__ = "citas"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    equipo_id = Column(
        Integer,
        ForeignKey(
            "equipos.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    titulo = Column(
        String(200),
        nullable=False
    )

    motivo = Column(
        String(500),
        nullable=False
    )

    cliente = Column(
        String(100),
        nullable=False
    )

    telefono = Column(
        String(30),
        nullable=True
    )

    direccion = Column(
        String(200),
        nullable=True
    )

    fecha_programada = Column(
        DateTime,
        nullable=False
    )

    recordatorio_minutos = Column(
        Integer,
        default=20
    )

    notificado = Column(
        Boolean,
        default=False
    )

    estado = Column(
        String(20),
        default="pendiente"
    )

    creado_en = Column(
        DateTime,
        default=func.now()
    )

    actualizado_en = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now()
    )

    equipo = relationship(
        "Equipo",
        back_populates="citas"
    )