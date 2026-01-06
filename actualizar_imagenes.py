"""
SCRIPT PARA ACTUALIZAR RUTAS DE IMÁGENES EN LA BASE DE DATOS
Actualiza la columna 'image' en la tabla 'exercise' con las rutas correctas
"""

import sqlite3
import os


def verificar_carpeta_imagenes():
    """Verificar que existe la carpeta de imágenes"""
    carpeta = "imagenes"
    
    if not os.path.exists(carpeta):
        print(f"📁 Creando carpeta '{carpeta}'...")
        os.makedirs(carpeta)
        print(f"✅ Carpeta '{carpeta}' creada")
    else:
        print(f"✅ Carpeta '{carpeta}' ya existe")
    
    return carpeta


def obtener_mapeo_imagenes():
    """
    Retorna un diccionario con el mapeo de palabras a nombres de archivo
    """
    # IMPORTANTE: Los nombres de archivo deben coincidir con los que descargas
    # Formato: palabra en la BD -> nombre del archivo de imagen
    
    mapeo = {
        # NIVEL 1 - INICIAL
        'A': 'A.png',
        'E': 'E.png',
        'I': 'I.png',
        'O': 'O.png',
        'U': 'U.png',
        'MAMÁ': 'MAMA.png',
        'PAPÁ': 'PAPA.png',
        'BEBÉ': 'BEBE.png',
        
        # NIVEL 2 - BASICO
        'BOCA': 'BOCA.png',
        'MANO': 'MANO.png',
        'PATO': 'PATO.png',
        'MESA': 'MESA.png',
        'BOLA': 'BOLA.png',
        'POMO': 'POMO.png',
        'BOTE': 'BOTE.png',
        'MIMO': 'MIMO.png',
        'PIPA': 'PIPA.png',
        'MAPA': 'MAPA.png',
        
        # NIVEL 3 - INTERMEDIO
        'CASA': 'CASA.png',
        'GATO': 'GATO.png',
        'DADO': 'DADO.png',
        'TAZA': 'TAZA.png',
        'DEDO': 'DEDO.png',
        'CAMA': 'CAMA.png',
        'GOMA': 'GOMA.png',
        'TODO': 'TODO.png',
        'QUESO': 'QUESO.png',
        'NIDO': 'NIDO.png',
        'SOPA': 'SOPA.png',
        'LUNA': 'LUNA.png',
        
        # NIVEL 4 - AVANZADO (palabras)
        'LORO': 'LORO.png',
        'ROSA': 'ROSA.png',
        'PERRO': 'PERRO.png',
        'CARRO': 'CARRO.png',
        'RORRO': 'RORRO.png',
        'LÁPIZ': 'LAPIZ.png',
        'LÁMPARA': 'LAMPARA.png',
        'GUITARRA': 'GUITARRA.png',
        
        # NIVEL 4 - AVANZADO (frases)
        'MI MAMÁ': 'MI_MAMA.png',
        'MI PAPÁ': 'MI_PAPA.png',
        'LA CASA': 'LA_CASA.png',
        'EL GATO': 'EL_GATO.png',
        'YO COMO PAN': 'YO_COMO_PAN.png',
        'ME GUSTA JUGAR': 'ME_GUSTA_JUGAR.png',
        'MAMÁ ESTÁ AQUÍ': 'MAMA_ESTA_AQUI.png',
    }
    
    return mapeo


def actualizar_rutas_imagenes(db_path='data.db', carpeta_imagenes='imagenes'):
    """
    Actualiza la columna 'image' de la tabla 'exercise' con las rutas correctas
    """
    
    print("\n" + "="*70)
    print("🔄 ACTUALIZANDO RUTAS DE IMÁGENES EN LA BASE DE DATOS")
    print("="*70 + "\n")
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Obtener mapeo de imágenes
        mapeo = obtener_mapeo_imagenes()
        
        # Obtener todos los ejercicios
        cursor.execute("SELECT exerciseId, word FROM exercise")
        ejercicios = cursor.fetchall()
        
        print(f"📋 Total de ejercicios en BD: {len(ejercicios)}\n")
        
        actualizados = 0
        sin_imagen = 0
        no_encontrados = 0
        
        for ejercicio in ejercicios:
            exercise_id = ejercicio['exerciseId']
            word = ejercicio['word']
            
            # Buscar la imagen correspondiente
            if word in mapeo:
                nombre_archivo = mapeo[word]
                ruta_completa = os.path.join(carpeta_imagenes, nombre_archivo)
                
                # Verificar si el archivo existe
                if os.path.exists(ruta_completa):
                    # Actualizar en la BD
                    cursor.execute("""
                        UPDATE exercise 
                        SET image = ? 
                        WHERE exerciseId = ?
                    """, (ruta_completa, exercise_id))
                    
                    print(f"✅ {word:20} → {ruta_completa}")
                    actualizados += 1
                else:
                    # Archivo no existe, pero actualizamos la ruta de todas formas
                    cursor.execute("""
                        UPDATE exercise 
                        SET image = ? 
                        WHERE exerciseId = ?
                    """, (ruta_completa, exercise_id))
                    
                    print(f"⚠️  {word:20} → {ruta_completa} (archivo no encontrado)")
                    no_encontrados += 1
            else:
                print(f"❌ {word:20} → Sin imagen definida en el mapeo")
                sin_imagen += 1
        
        # Guardar cambios
        conn.commit()
        conn.close()
        
        # Resumen
        print("\n" + "="*70)
        print("📊 RESUMEN")
        print("="*70)
        print(f"✅ Rutas actualizadas: {actualizados}")
        print(f"⚠️  Archivos no encontrados: {no_encontrados}")
        print(f"❌ Sin imagen en mapeo: {sin_imagen}")
        print(f"📊 Total procesados: {len(ejercicios)}")
        
        if no_encontrados > 0:
            print("\n⚠️  NOTA: Algunas imágenes no fueron encontradas.")
            print("   Asegúrate de descargar todas las imágenes según LISTA_IMAGENES_NECESARIAS.txt")
            print(f"   y colocarlas en la carpeta '{carpeta_imagenes}/'")
        
        if sin_imagen > 0:
            print("\n❌ ATENCIÓN: Algunos ejercicios no tienen imagen asignada.")
            print("   Actualiza la función obtener_mapeo_imagenes() en este script.")
        
        print("\n✅ Actualización completada\n")
        
    except Exception as e:
        print(f"\n❌ Error al actualizar rutas: {e}")
        import traceback
        traceback.print_exc()


def listar_imagenes_disponibles(carpeta='imagenes'):
    """Lista las imágenes que ya existen en la carpeta"""
    
    print("\n" + "="*70)
    print(f"📁 IMÁGENES DISPONIBLES EN '{carpeta}/'")
    print("="*70 + "\n")
    
    if not os.path.exists(carpeta):
        print(f"❌ La carpeta '{carpeta}' no existe")
        return
    
    archivos = [f for f in os.listdir(carpeta) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    if len(archivos) == 0:
        print("❌ No hay imágenes en la carpeta")
        print("   Descarga las imágenes según LISTA_IMAGENES_NECESARIAS.txt")
    else:
        print(f"✅ {len(archivos)} imágenes encontradas:\n")
        for archivo in sorted(archivos):
            print(f"   • {archivo}")
    
    print()


def main():
    """Función principal"""
    
    print("\n" + "="*70)
    print("  🖼️  CONFIGURACIÓN DE IMÁGENES PARA ROBOT DODO")
    print("="*70 + "\n")
    
    # Verificar/crear carpeta de imágenes
    carpeta = verificar_carpeta_imagenes()
    
    # Listar imágenes disponibles
    listar_imagenes_disponibles(carpeta)
    
    # Preguntar si desea actualizar la BD
    respuesta = input("¿Deseas actualizar las rutas en la base de datos? (s/n): ")
    
    if respuesta.lower() == 's':
        actualizar_rutas_imagenes(carpeta_imagenes=carpeta)
    else:
        print("\n❌ Actualización cancelada")
        print("   Cuando tengas las imágenes listas, ejecuta este script de nuevo\n")


if __name__ == "__main__":
    main()
