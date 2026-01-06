"""
SCRIPT DE PRUEBA - SISTEMA DE IMÁGENES
Verifica que el sistema de imágenes funciona correctamente
"""

import os
import sys
from PIL import Image
import sqlite3


def verificar_pillow():
    """Verificar que Pillow está instalado"""
    print("\n" + "="*70)
    print("1️⃣  VERIFICANDO PILLOW (PIL)")
    print("="*70)
    
    try:
        from PIL import Image, ImageTk
        print("✅ Pillow está instalado correctamente")
        print(f"   Versión: {Image.__version__}")
        return True
    except ImportError:
        print("❌ Pillow NO está instalado")
        print("   Instalar con: pip install Pillow")
        return False


def verificar_carpeta_imagenes():
    """Verificar que existe la carpeta de imágenes"""
    print("\n" + "="*70)
    print("2️⃣  VERIFICANDO CARPETA DE IMÁGENES")
    print("="*70)
    
    carpeta = "imagenes"
    
    if os.path.exists(carpeta):
        print(f"✅ Carpeta '{carpeta}' existe")
        
        # Contar imágenes
        archivos = [f for f in os.listdir(carpeta) 
                   if f.endswith(('.png', '.jpg', '.jpeg'))]
        
        print(f"📊 Total de imágenes: {len(archivos)}")
        
        if len(archivos) == 0:
            print("⚠️  No hay imágenes en la carpeta")
            print("   Descarga las imágenes según LISTA_IMAGENES_NECESARIAS.txt")
            return False
        else:
            print(f"✅ {len(archivos)} imágenes encontradas")
            return True
    else:
        print(f"❌ Carpeta '{carpeta}' NO existe")
        print(f"   Crear con: mkdir {carpeta}")
        return False


def verificar_base_datos():
    """Verificar que la BD tiene las rutas de imágenes"""
    print("\n" + "="*70)
    print("3️⃣  VERIFICANDO BASE DE DATOS")
    print("="*70)
    
    db_path = "data.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Base de datos '{db_path}' NO existe")
        print("   Ejecuta: python inicializar_bd_mejorado.py")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Contar ejercicios con imagen
        cursor.execute("""
            SELECT COUNT(*) as total 
            FROM exercise 
            WHERE image IS NOT NULL AND image != ''
        """)
        con_imagen = cursor.fetchone()['total']
        
        # Total de ejercicios
        cursor.execute("SELECT COUNT(*) as total FROM exercise")
        total = cursor.fetchone()['total']
        
        print(f"📊 Total ejercicios: {total}")
        print(f"📊 Con ruta de imagen: {con_imagen}")
        
        if con_imagen == 0:
            print("⚠️  Ningún ejercicio tiene ruta de imagen")
            print("   Ejecuta: python actualizar_imagenes.py")
            conn.close()
            return False
        
        # Verificar cuáles imágenes existen físicamente
        cursor.execute("""
            SELECT word, image 
            FROM exercise 
            WHERE image IS NOT NULL AND image != ''
        """)
        
        ejercicios_con_imagen = cursor.fetchall()
        
        existentes = 0
        faltantes = 0
        
        print("\n📋 Verificando archivos de imagen:")
        for ej in ejercicios_con_imagen:
            word = ej['word']
            image_path = ej['image']
            
            if os.path.exists(image_path):
                print(f"   ✅ {word:20} → {image_path}")
                existentes += 1
            else:
                print(f"   ❌ {word:20} → {image_path} (no encontrado)")
                faltantes += 1
        
        print(f"\n📊 Resumen:")
        print(f"   ✅ Imágenes existentes: {existentes}")
        print(f"   ❌ Imágenes faltantes: {faltantes}")
        
        conn.close()
        
        if faltantes > 0:
            print("\n⚠️  Algunas imágenes no se encontraron")
            print("   Descárgalas según LISTA_IMAGENES_NECESARIAS.txt")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error al verificar BD: {e}")
        return False


def probar_carga_imagen():
    """Probar que se puede cargar una imagen"""
    print("\n" + "="*70)
    print("4️⃣  PROBANDO CARGA DE IMAGEN")
    print("="*70)
    
    # Buscar cualquier imagen disponible
    carpeta = "imagenes"
    
    if not os.path.exists(carpeta):
        print("❌ Carpeta de imágenes no existe")
        return False
    
    archivos = [f for f in os.listdir(carpeta) 
               if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    if len(archivos) == 0:
        print("❌ No hay imágenes para probar")
        return False
    
    # Tomar la primera imagen
    imagen_prueba = os.path.join(carpeta, archivos[0])
    
    print(f"📸 Probando con: {imagen_prueba}")
    
    try:
        # Intentar abrir imagen
        img = Image.open(imagen_prueba)
        print(f"✅ Imagen abierta correctamente")
        print(f"   Tamaño: {img.size[0]}x{img.size[1]} píxeles")
        print(f"   Formato: {img.format}")
        print(f"   Modo: {img.mode}")
        
        # Intentar redimensionar
        img.thumbnail((300, 300), Image.Resampling.LANCZOS)
        print(f"✅ Redimensionamiento exitoso")
        print(f"   Nuevo tamaño: {img.size[0]}x{img.size[1]} píxeles")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al cargar imagen: {e}")
        return False


def verificar_ui():
    """Verificar que ui.py tiene soporte de imágenes"""
    print("\n" + "="*70)
    print("5️⃣  VERIFICANDO UI.PY")
    print("="*70)
    
    if not os.path.exists("ui.py"):
        print("❌ Archivo ui.py no encontrado")
        return False
    
    with open("ui.py", "r", encoding="utf-8") as f:
        contenido = f.read()
    
    # Verificar que tiene el método para cargar imágenes
    if "cargar_y_mostrar_imagen" in contenido:
        print("✅ ui.py tiene el método cargar_y_mostrar_imagen")
    else:
        print("❌ ui.py NO tiene el método cargar_y_mostrar_imagen")
        print("   Actualiza ui.py con los cambios de ui_con_imagenes.py")
        return False
    
    # Verificar que tiene label_imagen
    if "self.label_imagen" in contenido:
        print("✅ ui.py tiene label_imagen")
    else:
        print("❌ ui.py NO tiene label_imagen")
        return False
    
    # Verificar import de PIL
    if "from PIL import Image" in contenido or "import PIL" in contenido:
        print("✅ ui.py importa PIL")
    else:
        print("⚠️  ui.py no importa PIL")
        print("   Agrega: from PIL import Image, ImageTk")
        return False
    
    return True


def main():
    """Ejecutar todas las verificaciones"""
    
    print("\n" + "="*70)
    print("  🧪 VERIFICACIÓN DEL SISTEMA DE IMÁGENES - ROBOT DODO")
    print("="*70)
    
    resultados = []
    
    # 1. Verificar Pillow
    resultados.append(("Pillow instalado", verificar_pillow()))
    
    # 2. Verificar carpeta
    resultados.append(("Carpeta de imágenes", verificar_carpeta_imagenes()))
    
    # 3. Verificar BD
    resultados.append(("Base de datos", verificar_base_datos()))
    
    # 4. Probar carga
    resultados.append(("Carga de imágenes", probar_carga_imagen()))
    
    # 5. Verificar UI
    resultados.append(("UI actualizada", verificar_ui()))
    
    # Resumen final
    print("\n" + "="*70)
    print("📊 RESUMEN FINAL")
    print("="*70 + "\n")
    
    todos_ok = True
    for nombre, resultado in resultados:
        if resultado:
            print(f"✅ {nombre}")
        else:
            print(f"❌ {nombre}")
            todos_ok = False
    
    print("\n" + "="*70)
    
    if todos_ok:
        print("✅ ¡TODO CORRECTO! El sistema de imágenes está listo")
        print("   Puedes ejecutar el robot con: python main.py")
    else:
        print("❌ HAY PROBLEMAS QUE RESOLVER")
        print("   Revisa los errores arriba y sigue las instrucciones")
        print("   Consulta GUIA_INSTALACION_IMAGENES.txt para más ayuda")
    
    print("="*70 + "\n")
    
    return 0 if todos_ok else 1


if __name__ == "__main__":
    sys.exit(main())
