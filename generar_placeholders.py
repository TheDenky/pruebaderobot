"""
GENERADOR DE IMÁGENES PLACEHOLDER
Crea imágenes temporales para probar el sistema mientras descargas las reales
"""

import os
import sqlite3
from PIL import Image, ImageDraw, ImageFont


def generar_imagen_placeholder(palabra, ruta_salida, tamano=400):
    """
    Genera una imagen placeholder simple con la palabra escrita
    
    Args:
        palabra: Texto a mostrar
        ruta_salida: Donde guardar la imagen
        tamano: Tamaño de la imagen (cuadrada)
    """
    
    # Colores alegres para niños
    colores_fondo = [
        (255, 182, 193),  # Rosa claro
        (173, 216, 230),  # Azul claro
        (144, 238, 144),  # Verde claro
        (255, 218, 185),  # Durazno
        (221, 160, 221),  # Púrpura claro
        (255, 255, 153),  # Amarillo claro
    ]
    
    # Elegir color basado en hash de la palabra
    idx_color = hash(palabra) % len(colores_fondo)
    color_fondo = colores_fondo[idx_color]
    
    # Crear imagen
    img = Image.new('RGB', (tamano, tamano), color=color_fondo)
    draw = ImageDraw.Draw(img)
    
    # Dibujar borde
    borde_grosor = 10
    draw.rectangle(
        [(borde_grosor, borde_grosor), 
         (tamano - borde_grosor, tamano - borde_grosor)],
        outline=(100, 100, 100),
        width=borde_grosor
    )
    
    # Intentar usar fuente
    try:
        # Buscar fuentes disponibles
        fuentes_posibles = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "C:\\Windows\\Fonts\\arial.ttf",
        ]
        
        fuente = None
        for ruta_fuente in fuentes_posibles:
            if os.path.exists(ruta_fuente):
                fuente = ImageFont.truetype(ruta_fuente, 60)
                break
        
        if fuente is None:
            fuente = ImageFont.load_default()
    except:
        fuente = ImageFont.load_default()
    
    # Texto de la palabra
    texto = palabra.upper()
    
    # Calcular posición centrada
    bbox = draw.textbbox((0, 0), texto, font=fuente)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (tamano - text_width) / 2
    y = (tamano - text_height) / 2 - 30
    
    # Dibujar texto con sombra
    draw.text((x + 3, y + 3), texto, fill=(0, 0, 0), font=fuente)
    draw.text((x, y), texto, fill=(255, 255, 255), font=fuente)
    
    # Texto "PLACEHOLDER" pequeño
    try:
        fuente_pequena = ImageFont.truetype(fuentes_posibles[0], 20) if os.path.exists(fuentes_posibles[0]) else ImageFont.load_default()
    except:
        fuente_pequena = ImageFont.load_default()
    
    texto_placeholder = "PLACEHOLDER - Descarga la imagen real"
    bbox_p = draw.textbbox((0, 0), texto_placeholder, font=fuente_pequena)
    text_width_p = bbox_p[2] - bbox_p[0]
    
    x_p = (tamano - text_width_p) / 2
    y_p = tamano - 50
    
    draw.text((x_p, y_p), texto_placeholder, fill=(100, 100, 100), font=fuente_pequena)
    
    # Guardar
    img.save(ruta_salida, 'PNG')
    print(f"   ✅ Generada: {os.path.basename(ruta_salida)}")


def generar_todas_faltantes():
    """Genera placeholders para todas las imágenes faltantes"""
    
    print("\n" + "="*70)
    print("🎨 GENERADOR DE IMÁGENES PLACEHOLDER")
    print("="*70 + "\n")
    
    print("⚠️  IMPORTANTE: Estas son imágenes TEMPORALES para probar.")
    print("   Debes reemplazarlas con imágenes reales apropiadas para niños.\n")
    
    respuesta = input("¿Generar placeholders para las imágenes faltantes? (s/n): ")
    
    if respuesta.lower() != 's':
        print("❌ Operación cancelada")
        return
    
    try:
        # Conectar a BD
        conn = sqlite3.connect('data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Obtener ejercicios con imagen configurada
        cursor.execute("""
            SELECT word, image 
            FROM exercise 
            WHERE image IS NOT NULL AND image != ''
        """)
        
        ejercicios = cursor.fetchall()
        conn.close()
        
        # Generar placeholders para las faltantes
        generadas = 0
        ya_existentes = 0
        
        for ej in ejercicios:
            word = ej['word']
            image_path = ej['image']
            
            if not os.path.exists(image_path):
                # Crear directorio si no existe
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                
                # Generar placeholder
                generar_imagen_placeholder(word, image_path)
                generadas += 1
            else:
                ya_existentes += 1
        
        print(f"\n{'='*70}")
        print(f"📊 RESUMEN")
        print(f"{'='*70}")
        print(f"✅ Placeholders generadas: {generadas}")
        print(f"⏭️  Ya existentes: {ya_existentes}")
        print(f"📊 Total: {generadas + ya_existentes}")
        print(f"{'='*70}\n")
        
        if generadas > 0:
            print("✅ ¡Listo! Ahora puedes probar el robot con:")
            print("   python main.py")
            print("\n⚠️  RECUERDA: Reemplaza los placeholders con imágenes reales")
            print("   apropiadas para niños lo antes posible.\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def generar_vocales_especiales():
    """Genera imágenes especiales para las vocales (letras grandes)"""
    
    print("\n🔤 Generando imágenes de vocales...\n")
    
    vocales = ['A', 'E', 'I', 'O', 'U']
    colores = [
        (255, 99, 71),   # Rojo (A)
        (50, 205, 50),   # Verde (E)
        (255, 215, 0),   # Amarillo (I)
        (30, 144, 255),  # Azul (O)
        (238, 130, 238), # Violeta (U)
    ]
    
    for vocal, color in zip(vocales, colores):
        ruta = f"imagenes/{vocal}.png"
        
        if os.path.exists(ruta):
            print(f"   ⏭️  {vocal}.png ya existe")
            continue
        
        # Crear imagen
        img = Image.new('RGB', (400, 400), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Fuente grande
        try:
            fuentes_posibles = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                "C:\\Windows\\Fonts\\arial.ttf",
            ]
            
            fuente = None
            for ruta_fuente in fuentes_posibles:
                if os.path.exists(ruta_fuente):
                    fuente = ImageFont.truetype(ruta_fuente, 250)
                    break
            
            if fuente is None:
                fuente = ImageFont.load_default()
        except:
            fuente = ImageFont.load_default()
        
        # Centrar vocal
        bbox = draw.textbbox((0, 0), vocal, font=fuente)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (400 - text_width) / 2
        y = (400 - text_height) / 2
        
        # Dibujar con sombra
        draw.text((x + 5, y + 5), vocal, fill=(200, 200, 200), font=fuente)
        draw.text((x, y), vocal, fill=color, font=fuente)
        
        img.save(ruta, 'PNG')
        print(f"   ✅ Generada: {vocal}.png (vocal especial)")


def main():
    """Función principal"""
    
    print("\n" + "="*70)
    print("  🎨 GENERADOR DE IMÁGENES TEMPORALES - ROBOT DODO")
    print("="*70 + "\n")
    
    # Verificar que existe la carpeta
    if not os.path.exists('imagenes'):
        os.makedirs('imagenes')
        print("✅ Carpeta 'imagenes/' creada\n")
    
    # Generar vocales primero (son especiales)
    generar_vocales_especiales()
    
    # Generar resto de placeholders
    generar_todas_faltantes()


if __name__ == "__main__":
    main()
