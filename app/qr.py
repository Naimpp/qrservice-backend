import os
import qrcode

CARPETA_QR = "qrcodes"

# Asegurar que la carpeta existe
os.makedirs(CARPETA_QR, exist_ok=True)


def generar_qr(codigo: str):
    """
    Genera un código QR como archivo PNG
    Retorna la ruta del archivo generado
    """
    try:
        # URL que quedará guardada dentro del QR
        url = f"http://192.168.1.176:8000/equipo/{codigo}"
        
        print(f"🔲 Generando QR para: {url}")
        
        # Generar imagen QR
        img = qrcode.make(url)
        
        # Nombre del archivo
        ruta = os.path.join(
            CARPETA_QR,
            f"{codigo}.png"
        )
        
        # Guardar imagen
        img.save(ruta)
        
        print(f"✅ QR guardado en: {ruta}")
        return ruta
        
    except Exception as e:
        print(f"❌ Error generando QR: {e}")
        return None