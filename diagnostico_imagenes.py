"""
DIAGNÓSTICO - ¿Por qué no se muestran las imágenes?
Verifica paso a paso qué está fallando
"""

import os
import sys


def diagnostico_completo():
    """Ejecuta diagnóstico completo"""
    
    print("\n" + "="*70)
    print("🔍 DIAGNÓSTICO - SISTEMA DE IMÁGENES")
    print("="*70 + "\n")
    
    problemas = []
    
    # 1. Verificar que existen imágenes
    print("1️⃣  Verificando imágenes generadas...")
    
    if not os.path.exists('imagenes'):
        print("   ❌ La carpeta 'imagenes/' NO existe")
        problemas.append("Carpeta imagenes/ no existe")
    else:
        archivos = [f for f in os.listdir('imagenes') if f.endswith(('.png', '.jpg'))]
        print(f"   ✅ Carpeta 'imagenes/' existe con {len(archivos)} archivos")
        
        if len(archivos) == 0:
            problemas.append("No hay imágenes en la carpeta")
        
        # Mostrar algunas
        print("\n   Ejemplos de imágenes encontradas:")
        for img in archivos[:5]:
            ruta = os.path.join('imagenes', img)
            tamaño = os.path.getsize(ruta)
            print(f"      • {img} ({tamaño} bytes)")
    
    # 2. Verificar ui.py
    print("\n2️⃣  Verificando ui.py...")
    
    if not os.path.exists('ui.py'):
        print("   ❌ ui.py NO existe")
        problemas.append("ui.py no existe")
    else:
        with open('ui.py', 'r', encoding='utf-8') as f:
            contenido_ui = f.read()
        
        # Verificar método clave
        if 'def mostrar_ejercicio(self, palabra: str, ruta_imagen: str = None):' in contenido_ui:
            print("   ✅ ui.py tiene el método actualizado mostrar_ejercicio con parámetro ruta_imagen")
        elif 'def mostrar_ejercicio(self, palabra: str):' in contenido_ui:
            print("   ⚠️  ui.py tiene mostrar_ejercicio pero SIN parámetro ruta_imagen")
            print("   🔧 SOLUCIÓN: Actualiza ui.py con ui_con_imagenes.py")
            problemas.append("ui.py no tiene parámetro ruta_imagen")
        else:
            print("   ❌ No se encuentra mostrar_ejercicio en ui.py")
            problemas.append("mostrar_ejercicio no encontrado en ui.py")
        
        # Verificar método de carga
        if 'def cargar_y_mostrar_imagen' in contenido_ui:
            print("   ✅ ui.py tiene el método cargar_y_mostrar_imagen")
        else:
            print("   ❌ ui.py NO tiene el método cargar_y_mostrar_imagen")
            problemas.append("ui.py no tiene cargar_y_mostrar_imagen")
        
        # Verificar import PIL
        if 'from PIL import Image' in contenido_ui:
            print("   ✅ ui.py importa PIL correctamente")
        else:
            print("   ❌ ui.py NO importa PIL")
            problemas.append("ui.py no importa PIL")
    
    # 3. Verificar services.py
    print("\n3️⃣  Verificando services.py...")
    
    if not os.path.exists('services.py'):
        print("   ❌ services.py NO existe")
        problemas.append("services.py no existe")
    else:
        with open('services.py', 'r', encoding='utf-8') as f:
            contenido_services = f.read()
        
        # Buscar cómo se llama a mostrar_ejercicio
        if 'mostrar_ejercicio(' in contenido_services:
            # Verificar si pasa ruta_imagen
            if 'ruta_imagen=' in contenido_services or 'ruta_imagen =' in contenido_services:
                print("   ✅ services.py llama a mostrar_ejercicio CON ruta_imagen")
            else:
                print("   ❌ services.py llama a mostrar_ejercicio SIN ruta_imagen")
                print("   🔧 ESTE ES EL PROBLEMA PRINCIPAL")
                problemas.append("services.py no pasa ruta_imagen a mostrar_ejercicio")
                
                # Buscar la línea exacta
                lineas = contenido_services.split('\n')
                for i, linea in enumerate(lineas, 1):
                    if 'mostrar_ejercicio(' in linea and 'def ' not in linea:
                        print(f"\n   📍 Línea {i}: {linea.strip()}")
        else:
            print("   ⚠️  No se encontró llamada a mostrar_ejercicio")
        
        # Verificar si usa ejercicio.apoyo_visual
        if 'ejercicio.apoyo_visual' in contenido_services or 'apoyo_visual' in contenido_services:
            print("   ✅ services.py accede a ejercicio.apoyo_visual")
        else:
            print("   ❌ services.py NO accede a ejercicio.apoyo_visual")
            problemas.append("services.py no usa apoyo_visual")
    
    # 4. Verificar database.py
    print("\n4️⃣  Verificando database.py...")
    
    if os.path.exists('database.py'):
        with open('database.py', 'r', encoding='utf-8') as f:
            contenido_db = f.read()
        
        if "apoyo_visual=row['image']" in contenido_db or "apoyo_visual =" in contenido_db:
            print("   ✅ database.py asigna apoyo_visual correctamente")
        else:
            print("   ⚠️  database.py podría no estar asignando apoyo_visual")
    
    # RESUMEN
    print("\n" + "="*70)
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("="*70 + "\n")
    
    if len(problemas) == 0:
        print("✅ ¡TODO CORRECTO! No se detectaron problemas.")
        print("\n💡 Si aún no se muestran imágenes, ejecuta el robot con:")
        print("   python main.py")
        print("\n   Y observa si hay errores en la consola.")
    else:
        print("❌ Se encontraron los siguientes problemas:\n")
        for i, problema in enumerate(problemas, 1):
            print(f"   {i}. {problema}")
        
        print("\n" + "="*70)
        print("🔧 SOLUCIONES")
        print("="*70 + "\n")
        
        if "services.py no pasa ruta_imagen a mostrar_ejercicio" in problemas:
            print("PROBLEMA PRINCIPAL: services.py no está pasando las rutas de imágenes\n")
            print("SOLUCIÓN: Ejecuta el script de corrección:")
            print("   python corregir_services.py")
            print("\nO hazlo manualmente siguiendo INSTRUCCIONES_MANUAL.txt")
        
        if "ui.py no tiene parámetro ruta_imagen" in problemas:
            print("\nPROBLEMA: ui.py no está actualizado\n")
            print("SOLUCIÓN:")
            print("   cp ui_con_imagenes.py ui.py")
        
        if "ui.py no importa PIL" in problemas:
            print("\nPROBLEMA: ui.py no importa PIL\n")
            print("SOLUCIÓN: Agrega al inicio de ui.py:")
            print("   from PIL import Image, ImageTk")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    diagnostico_completo()
