"""
CORRECCIÓN AUTOMÁTICA DE SERVICES.PY
Actualiza services.py para que pase las rutas de imágenes a la interfaz
"""

import os
import shutil
from datetime import datetime


def hacer_backup(archivo):
    """Crea backup del archivo original"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = f"{archivo}.backup_{timestamp}"
    shutil.copy2(archivo, backup)
    print(f"✅ Backup creado: {backup}")
    return backup


def corregir_services():
    """Corrige el archivo services.py"""
    
    print("\n" + "="*70)
    print("🔧 CORRECCIÓN AUTOMÁTICA DE SERVICES.PY")
    print("="*70 + "\n")
    
    archivo = 'services.py'
    
    # Verificar que existe
    if not os.path.exists(archivo):
        print(f"❌ Error: {archivo} no existe en este directorio")
        print("   Asegúrate de ejecutar este script desde la raíz del proyecto")
        return False
    
    # Hacer backup
    print("📦 Creando backup del archivo original...")
    backup = hacer_backup(archivo)
    
    # Leer contenido
    print("📖 Leyendo services.py...")
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Aplicar correcciones
    print("🔧 Aplicando correcciones...\n")
    
    correcciones = 0
    
    # CORRECCIÓN 1: Actualizar llamada a mostrar_ejercicio en _ejecutar_ejercicio_con_ia
    # Buscar: self.interfaz.mostrar_ejercicio(ejercicio.word)
    # Reemplazar con código que incluya la imagen
    
    patron_viejo = "self.interfaz.mostrar_ejercicio(ejercicio.word)"
    
    if patron_viejo in contenido:
        # Código nuevo que incluye la ruta de imagen
        codigo_nuevo = """# NUEVO: Pasar la ruta de la imagen si está disponible
        ruta_imagen = ejercicio.apoyo_visual if ejercicio.apoyo_visual else None
        
        self.interfaz.mostrar_ejercicio(
            palabra=ejercicio.word,
            ruta_imagen=ruta_imagen  # NUEVO parámetro
        )"""
        
        # Reemplazar manteniendo la indentación
        contenido_nuevo = contenido.replace(
            "        self.interfaz.mostrar_ejercicio(ejercicio.word)",
            codigo_nuevo
        )
        
        if contenido_nuevo != contenido:
            contenido = contenido_nuevo
            correcciones += 1
            print("   ✅ Actualizada llamada a mostrar_ejercicio()")
    
    # CORRECCIÓN 2: Actualizar otra posible llamada en realizar_test_diagnostico
    patron_viejo_2 = "self.interfaz.mostrar_ejercicio(palabra_esperada.upper())"
    
    if patron_viejo_2 in contenido:
        # Para el test diagnóstico, probablemente no tenemos imagen, así que None
        codigo_nuevo_2 = """self.interfaz.mostrar_ejercicio(
            palabra=palabra_esperada.upper(),
            ruta_imagen=None
        )"""
        
        contenido_nuevo = contenido.replace(
            "            self.interfaz.mostrar_ejercicio(palabra_esperada.upper())",
            codigo_nuevo_2
        )
        
        if contenido_nuevo != contenido:
            contenido = contenido_nuevo
            correcciones += 1
            print("   ✅ Actualizada llamada en test diagnóstico")
    
    # Verificar si ya está corregido
    if correcciones == 0:
        if 'ruta_imagen=' in contenido and 'mostrar_ejercicio' in contenido:
            print("   ℹ️  services.py ya está actualizado (no se hicieron cambios)")
            print("\n💡 Si las imágenes no se muestran, el problema está en otro lado.")
            print("   Ejecuta: python diagnostico_imagenes.py")
            return True
        else:
            print("   ⚠️  No se encontraron los patrones esperados para corregir")
            print("   Esto puede significar que services.py tiene una estructura diferente")
            print("\n   Ver INSTRUCCIONES_MANUAL.txt para corrección manual")
            return False
    
    # Guardar archivo corregido
    print(f"\n💾 Guardando cambios en {archivo}...")
    with open(archivo, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print(f"✅ {correcciones} corrección(es) aplicada(s)")
    
    print("\n" + "="*70)
    print("✅ CORRECCIÓN COMPLETADA")
    print("="*70)
    print(f"\n📁 Archivo original respaldado en: {backup}")
    print(f"📝 Archivo actualizado: {archivo}")
    print("\n🎯 PRÓXIMO PASO:")
    print("   python main.py")
    print("\n   Las imágenes deberían mostrarse ahora.\n")
    
    return True


def main():
    """Función principal"""
    
    print("\n" + "="*70)
    print("  🔧 CORRECTOR AUTOMÁTICO - SISTEMA DE IMÁGENES")
    print("="*70 + "\n")
    
    print("Este script actualizará services.py para mostrar imágenes.\n")
    
    respuesta = input("¿Continuar con la corrección automática? (s/n): ")
    
    if respuesta.lower() != 's':
        print("\n❌ Operación cancelada")
        print("   Para corrección manual, ver: INSTRUCCIONES_MANUAL.txt\n")
        return
    
    exito = corregir_services()
    
    if exito:
        print("🎉 ¡Listo! Ahora prueba el robot:")
        print("   python main.py\n")
    else:
        print("⚠️  Revisa INSTRUCCIONES_MANUAL.txt para más ayuda\n")


if __name__ == "__main__":
    main()
