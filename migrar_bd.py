"""
SCRIPT DE MIGRACIÓN DE BASE DE DATOS
Agrega nuevos campos y corrige la estructura
"""
import sqlite3
from datetime import datetime


def migrar_base_datos(db_path='data.db'):
    """Migrar base de datos a nueva estructura"""
    
    print("\n" + "="*70)
    print("🔄 MIGRACIÓN DE BASE DE DATOS")
    print("="*70 + "\n")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # ===== PASO 1: AGREGAR CAMPOS A TABLA PERSON =====
        print("📝 Paso 1: Actualizando tabla PERSON...")
        
        # Verificar si los campos ya existen
        cursor.execute("PRAGMA table_info(person)")
        columnas_existentes = [col[1] for col in cursor.fetchall()]
        
        # Agregar DNI si no existe
        if 'dni' not in columnas_existentes:
            cursor.execute("""
                ALTER TABLE person 
                ADD COLUMN dni TEXT
            """)
            print("   ✅ Campo 'dni' agregado")
        else:
            print("   ⏭️  Campo 'dni' ya existe")
        
        # Agregar sexo si no existe
        if 'sex' not in columnas_existentes:
            cursor.execute("""
                ALTER TABLE person 
                ADD COLUMN sex TEXT
            """)
            print("   ✅ Campo 'sex' agregado")
        else:
            print("   ⏭️  Campo 'sex' ya existe")
        
        conn.commit()
        
        # ===== PASO 2: AGREGAR CAMPOS A TABLA SESION =====
        print("\n📝 Paso 2: Actualizando tabla SESION...")
        
        cursor.execute("PRAGMA table_info(sesion)")
        columnas_sesion = [col[1] for col in cursor.fetchall()]
        
        # Agregar personId si no existe
        if 'personId' not in columnas_sesion:
            cursor.execute("""
                ALTER TABLE sesion 
                ADD COLUMN personId INTEGER
            """)
            print("   ✅ Campo 'personId' agregado")
            
            # Intentar asociar sesiones existentes a personas
            # (esto es un best-effort, puede no ser 100% preciso para datos antiguos)
            cursor.execute("""
                SELECT personId, actual_level FROM person
            """)
            personas = cursor.fetchall()
            
            for person_id, nivel_id in personas:
                # Asociar sesiones de ese nivel a esa persona
                cursor.execute("""
                    UPDATE sesion 
                    SET personId = ? 
                    WHERE levelId = ? AND personId IS NULL
                """, (person_id, nivel_id))
            
            print("   ✅ Sesiones asociadas a personas")
        else:
            print("   ⏭️  Campo 'personId' ya existe")
        
        # Agregar observaciones_terapeuta si no existe
        if 'observaciones_terapeuta' not in columnas_sesion:
            cursor.execute("""
                ALTER TABLE sesion 
                ADD COLUMN observaciones_terapeuta TEXT
            """)
            print("   ✅ Campo 'observaciones_terapeuta' agregado")
        else:
            print("   ⏭️  Campo 'observaciones_terapeuta' ya existe")
        
        conn.commit()
        
        # ===== PASO 3: CREAR TABLA DE OBSERVACIONES (OPCIONAL) =====
        print("\n📝 Paso 3: Creando tabla OBSERVACIONES...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS observaciones (
                observacionId INTEGER PRIMARY KEY AUTOINCREMENT,
                personId INTEGER NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                observacion TEXT NOT NULL,
                terapeuta TEXT,
                FOREIGN KEY(personId) REFERENCES person(personId)
            )
        """)
        print("   ✅ Tabla 'observaciones' creada/verificada")
        
        conn.commit()
        
        # ===== VERIFICACIÓN FINAL =====
        print("\n" + "="*70)
        print("✅ MIGRACIÓN COMPLETADA")
        print("="*70)
        
        # Mostrar nueva estructura
        print("\n📊 NUEVA ESTRUCTURA DE TABLAS:\n")
        
        print("Tabla PERSON:")
        cursor.execute("PRAGMA table_info(person)")
        for col in cursor.fetchall():
            print(f"   - {col[1]} ({col[2]})")
        
        print("\nTabla SESION:")
        cursor.execute("PRAGMA table_info(sesion)")
        for col in cursor.fetchall():
            print(f"   - {col[1]} ({col[2]})")
        
        print("\nTabla OBSERVACIONES:")
        cursor.execute("PRAGMA table_info(observaciones)")
        for col in cursor.fetchall():
            print(f"   - {col[1]} ({col[2]})")
        
        print("\n" + "="*70 + "\n")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    
    print("\n⚠️  IMPORTANTE: Este script modificará la base de datos.")
    print("   Se recomienda hacer un backup antes de continuar.\n")
    
    respuesta = input("¿Continuar con la migración? (s/n): ")
    
    if respuesta.lower() == 's':
        migrar_base_datos()
        print("✅ ¡Migración exitosa!")
        print("   Ahora puedes ejecutar el robot normalmente.\n")
    else:
        print("❌ Migración cancelada\n")