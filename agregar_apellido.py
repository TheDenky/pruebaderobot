"""
Script para agregar columna apellido a la tabla person
"""
import sqlite3

def agregar_columna_apellido(db_path='data.db'):
    print("\n" + "="*70)
    print("🔄 AGREGANDO COLUMNA APELLIDO A TABLA PERSON")
    print("="*70 + "\n")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(person)")
        columnas = [col[1] for col in cursor.fetchall()]
        
        if 'apellido' in columnas:
            print("⏭️  La columna 'apellido' ya existe")
        else:
            # Agregar columna
            cursor.execute("""
                ALTER TABLE person 
                ADD COLUMN apellido TEXT
            """)
            conn.commit()
            print("✅ Columna 'apellido' agregada exitosamente")
        
        # Mostrar estructura actualizada
        print("\n📊 Estructura actual de tabla PERSON:")
        cursor.execute("PRAGMA table_info(person)")
        for col in cursor.fetchall():
            print(f"   - {col[1]} ({col[2]})")
        
        conn.close()
        print("\n" + "="*70)
        print("✅ MIGRACIÓN COMPLETADA")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    agregar_columna_apellido()