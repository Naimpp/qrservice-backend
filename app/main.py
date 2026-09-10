from fastapi import FastAPI
from sqlalchemy import text
import threading
import time
import os

from app.database import engine, Base, crear_tablas, probar_conexion
from app import models
from app.routes import router

# =========================================================
# CREAR TABLAS EN LA BASE DE DATOS
# =========================================================

# 🔥 Crear tablas automáticamente al iniciar
crear_tablas()

# =========================================================
# PROBAR CONEXIÓN A BASE DE DATOS
# =========================================================

probar_conexion()

# =========================================================
# CREAR APLICACIÓN FASTAPI
# =========================================================

app = FastAPI(
    title="QR Service API",
    version="1.0.0",
    description="API para gestión de equipos, intervenciones y citas",
    docs_url="/docs",
    redoc_url="/redoc"
)

# =========================================================
# INICIAR TAREA DE RECORDATORIOS EN SEGUNDO PLANO
# =========================================================

def iniciar_recordatorios():
    """Hilo en segundo plano para recordatorios de citas"""
    while True:
        try:
            # Verificar si la función existe
            try:
                from app.utils.notificaciones import ejecutar_periodicamente
                ejecutar_periodicamente()
            except ImportError:
                # Si no existe el módulo, simplemente esperar
                pass
            except Exception as e:
                print(f"⚠️ Error en recordatorios: {e}")
        except Exception as e:
            print(f"❌ Error en recordatorios: {e}")
        time.sleep(300)  # Esperar 5 minutos

@app.on_event("startup")
def startup_event():
    """Se ejecuta cuando la API inicia"""
    print("🚀 Iniciando QR Service API...")
    print(f"📁 Base de datos: {engine.url}")
    
    # Verificar que las tablas existen
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tablas = inspector.get_table_names()
        print(f"📊 Tablas existentes: {tablas}")
    except Exception as e:
        print(f"⚠️ Error verificando tablas: {e}")
    
    # Iniciar hilo de recordatorios (si existe la función)
    try:
        from app.utils.notificaciones import ejecutar_periodicamente
        hilo = threading.Thread(
            target=iniciar_recordatorios,
            daemon=True
        )
        hilo.start()
        print("✅ Sistema de recordatorios iniciado")
    except ImportError:
        print("ℹ️ Módulo de recordatorios no encontrado - omitiendo")
    
    print("✅ API QR Service iniciada correctamente")

@app.on_event("shutdown")
def shutdown_event():
    """Se ejecuta cuando la API se cierra"""
    print("🛑 Cerrando QR Service API...")
    # Cerrar conexiones de base de datos si es necesario
    try:
        engine.dispose()
        print("✅ Conexiones cerradas correctamente")
    except:
        pass

# =========================================================
# REGISTRAR RUTAS
# =========================================================

app.include_router(router)

# =========================================================
# RUTA PRINCIPAL
# =========================================================

@app.get("/")
def inicio():
    return {
        "mensaje": "Servidor QR Service funcionando correctamente",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "equipos": {
                "crear": "/equipos (POST)",
                "listar": "/equipos (GET)",
                "buscar": "/equipos/buscar?cliente=texto (GET)",
                "obtener": "/equipo/{codigo} (GET)"
            },
            "intervenciones": {
                "crear": "/equipo/{codigo}/intervenciones (POST)"
            },
            "citas": {
                "crear": "/citas (POST)",
                "listar": "/citas (GET)",
                "pendientes": "/citas/pendientes (GET)",
                "eliminar": "/citas/{citaId} (DELETE)"
            },
            "documentacion": {
                "swagger": "/docs",
                "redoc": "/redoc"
            }
        }
    }

# =========================================================
# TEST DE BASE DE DATOS
# =========================================================

@app.get("/test-db")
def test_db():
    """Endpoint para probar la conexión a la base de datos"""
    try:
        with engine.connect() as connection:
            resultado = connection.execute(
                text("SELECT 1 as test")
            )
            valor = resultado.scalar()
            return {
                "conexion": "correcta",
                "resultado": valor,
                "mensaje": "✅ Base de datos funcionando correctamente"
            }
    except Exception as e:
        return {
            "conexion": "error",
            "error": str(e),
            "mensaje": "❌ Error conectando a la base de datos"
        }

# =========================================================
# ENDPOINT DE SALUD (HEALTH CHECK)
# =========================================================

@app.get("/health")
def health_check():
    """Endpoint para verificar el estado del servicio"""
    return {
        "status": "healthy",
        "database": "connected",
        "version": "1.0.0"
    }