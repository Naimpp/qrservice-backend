# =========================================================
# NOTIFICACIONES.PY - SISTEMA DE RECORDATORIOS
# =========================================================

import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import (
    obtener_citas_pendientes,
    marcar_cita_notificada
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =========================================================
# SERVICIO DE NOTIFICACIONES
# =========================================================

class NotificationService:
    """Servicio para enviar notificaciones (logs por ahora)"""
    
    @staticmethod
    def enviar_notificacion(cita, mensaje):
        """
        Envía una notificación.
        Aquí se integraría con Firebase u otro servicio push.
        """
        logger.info("=" * 50)
        logger.info(f"🔔 RECORDATORIO DE CITA")
        logger.info(f"📌 Título: {cita.titulo}")
        logger.info(f"👤 Cliente: {cita.cliente}")
        logger.info(f"📱 Teléfono: {cita.telefono or 'No registrado'}")
        logger.info(f"📍 Dirección: {cita.direccion or 'No registrada'}")
        logger.info(f"📝 Motivo: {cita.motivo}")
        logger.info(f"⏰ Fecha: {cita.fecha_programada.strftime('%d/%m/%Y %H:%M')}")
        logger.info(f"📋 Mensaje: {mensaje}")
        logger.info("=" * 50)
        return True


# =========================================================
# VERIFICADOR DE RECORDATORIOS
# =========================================================

def verificar_y_enviar_recordatorios():
    """Verifica citas pendientes y envía recordatorios si corresponde"""
    db = SessionLocal()
    try:
        # Buscar citas que necesitan recordatorio (próximas 2 horas)
        citas = obtener_citas_pendientes(db, horas_a_futuro=2)
        
        if not citas:
            logger.info("No hay citas pendientes de recordatorio")
            return
        
        logger.info(f"Verificando {len(citas)} citas para recordatorios")
        ahora = datetime.now()
        
        for cita in citas:
            tiempo_restante = (cita.fecha_programada - ahora).total_seconds() / 60
            
            # Si el tiempo restante es menor o igual a los minutos configurados
            if tiempo_restante <= cita.recordatorio_minutos:
                # Construir mensaje
                mensaje = f"📋 Motivo: {cita.motivo}\n👤 Cliente: {cita.cliente}"
                
                if cita.direccion:
                    mensaje += f"\n📍 Dirección: {cita.direccion}"
                if cita.telefono:
                    mensaje += f"\n📱 Teléfono: {cita.telefono}"
                
                # Enviar notificación
                NotificationService.enviar_notificacion(cita, mensaje)
                
                # Marcar como notificada para no enviar duplicados
                marcar_cita_notificada(db, cita.id)
                db.commit()
                
                logger.info(f"✅ Recordatorio enviado para cita #{cita.id}")
                
    except Exception as e:
        logger.error(f"❌ Error en verificación de recordatorios: {e}")
    finally:
        db.close()


# =========================================================
# EJECUTAR VERIFICACIÓN PERIÓDICA
# =========================================================

def ejecutar_periodicamente():
    """Función que se ejecuta cada 5 minutos"""
    logger.info("🔄 Ejecutando verificación de recordatorios...")
    verificar_y_enviar_recordatorios()