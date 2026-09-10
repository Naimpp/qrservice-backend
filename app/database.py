from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# =========================================================
# CONEXIÓN - CON VARIABLES DE ENTORNO PARA RAILWAY
# =========================================================

# 🔥 Para Railway: usa SQLite por defecto (se guarda en el disco)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./qr_service.db")

# Si quieres usar MySQL en Railway, descomenta y configura:
# DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://usuario:contraseña@host/nombre_db")

# 🔥 Para desarrollo local con MySQL (si lo prefieres)
# DATABASE_URL = "mysql+pymysql://root:1234@localhost/qr_service"

# =========================================================
# CREAR ENGINE
# =========================================================

# Configuración especial para SQLite
connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False  # Cambiar a True para ver logs SQL
)

# =========================================================
# CREAR SESIONES
# =========================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# =========================================================
# CLASE BASE DE LOS MODELOS
# =========================================================

Base = declarative_base()

# =========================================================
# FUNCIÓN PARA OBTENER LA SESIÓN
# =========================================================

def get_db():
    """Función para obtener una sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================================================
# FUNCIÓN PARA CREAR LAS TABLAS (SI NO EXISTEN)
# =========================================================

def crear_tablas():
    """Crea todas las tablas si no existen"""
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas/verificadas correctamente")

# =========================================================
# FUNCIÓN PARA PROBAR LA CONEXIÓN
# =========================================================

def probar_conexion():
    """Prueba la conexión a la base de datos"""
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Conexión a base de datos exitosa")
            return True
    except Exception as e:
        print(f"❌ Error conectando a base de datos: {e}")
        return False