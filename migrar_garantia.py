"""
Script de migración: agrega la columna dias_garantia a la tabla intervenciones.
Ejecutar UNA SOLA VEZ.

Uso:
    python migrar_garantia.py
"""

from sqlalchemy import text
from app.database import engine


def migrar():
    with engine.connect() as conn:
        # Ver si la columna ya existe
        try:
            conn.execute(text("SELECT dias_garantia FROM intervenciones LIMIT 1"))
            print("ℹ️  La columna 'dias_garantia' YA EXISTE. No hace falta migrar.")
            return
        except Exception:
            pass  # No existe, seguimos

        print("🔧 Agregando columna 'dias_garantia' a la tabla 'intervenciones'...")

        dialecto = engine.dialect.name
        print(f"   Dialecto detectado: {dialecto}")

        if dialecto == "sqlite":
            conn.execute(text("ALTER TABLE intervenciones ADD COLUMN dias_garantia INTEGER"))
        elif dialecto in ("postgresql", "postgres"):
            conn.execute(text("ALTER TABLE intervenciones ADD COLUMN dias_garantia INTEGER"))
        elif dialecto == "mysql":
            conn.execute(text("ALTER TABLE intervenciones ADD COLUMN dias_garantia INT NULL"))
        else:
            print(f"⚠️  Dialecto desconocido: {dialecto}. Intentando SQL genérico...")
            conn.execute(text("ALTER TABLE intervenciones ADD COLUMN dias_garantia INTEGER"))

        conn.commit()
        print("✅ Columna 'dias_garantia' agregada correctamente.")


if __name__ == "__main__":
    migrar()