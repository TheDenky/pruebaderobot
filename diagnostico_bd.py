"""
SCRIPT DE DIAGNÓSTICO
Verifica que la base de datos esté correctamente configurada
"""
import sqlite3
from models import NivelTerapia


def diagnosticar_bd(db_path='data.db'):
    """Diagnóstico completo de la base de datos"""
    
    print("\n" + "="*70)
    print("🔍 DIAGNÓSTICO DE BASE DE DATOS")
    print("="*70 + "\n")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Verificar tablas
        print("📋 Verificando tablas...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = [row['name'] for row in cursor.fetchall()]
        
        tablas_esperadas = ['person', 'exercise', 'level', 'therapy', 'sesion']
        for tabla in tablas_esperadas:
            if tabla in tablas:
                print(f"  ✅ Tabla '{tabla}' existe")
            else:
                print(f"  ❌ Tabla '{tabla}' NO existe")
        
        print()
        
        # 2. Verificar niveles
        print("🎯 Verificando niveles...")
        cursor.execute("SELECT * FROM level ORDER BY levelId")
        niveles = cursor.fetchall()
        
        if len(niveles) == 4:
            print(f"  ✅ 4 niveles encontrados (correcto)")
            for nivel in niveles:
                print(f"     {nivel['levelId']}. {nivel['name']}")
        else:
            print(f"  ⚠️ Se encontraron {len(niveles)} niveles (deberían ser 4)")
        
        print()
        
        # 3. Verificar ejercicios
        print("📝 Verificando ejercicios...")
        cursor.execute("SELECT COUNT(*) as total FROM exercise")
        total_ejercicios = cursor.fetchone()['total']
        print(f"  Total de ejercicios: {total_ejercicios}")
        
        # Ejercicios por dificultad
        cursor.execute("""
            SELECT difficulty, COUNT(*) as cantidad
            FROM exercise
            GROUP BY difficulty
            ORDER BY difficulty
        """)
        print("  Distribución por dificultad:")
        for row in cursor.fetchall():
            print(f"    Dificultad {row['difficulty']}: {row['cantidad']} ejercicios")
        
        print()
        
        # 4. Verificar tabla THERAPY (asignaciones)
        print("🔗 Verificando asignaciones (tabla THERAPY)...")
        cursor.execute("SELECT COUNT(*) as total FROM therapy")
        total_therapy = cursor.fetchone()['total']
        print(f"  Total de asignaciones: {total_therapy}")
        
        # Asignaciones por nivel
        cursor.execute("""
            SELECT levelId, COUNT(*) as cantidad
            FROM therapy
            GROUP BY levelId
            ORDER BY levelId
        """)
        asignaciones = cursor.fetchall()
        
        if len(asignaciones) > 0:
            print("  ✅ Asignaciones por nivel:")
            for row in asignaciones:
                print(f"     Nivel {row['levelId']}: {row['cantidad']} ejercicios")
        else:
            print("  ❌ NO HAY ASIGNACIONES - Este es el problema")
            print("     Solución: Ejecuta inicializar_bd_mejorado.py")
        
        print()
        
        # 5. Verificar integridad de asignaciones
        print("🔍 Verificando integridad de asignaciones...")
        cursor.execute("""
            SELECT t.therapyId, t.levelId, t.exerciseId, e.word
            FROM therapy t
            LEFT JOIN exercise e ON t.exerciseId = e.exerciseId
            WHERE e.word IS NULL
        """)
        huerfanos = cursor.fetchall()
        
        if len(huerfanos) == 0:
            print("  ✅ Todas las asignaciones son válidas")
        else:
            print(f"  ⚠️ {len(huerfanos)} asignaciones inválidas (ejercicios que no existen)")
        
        print()
        
        # 6. Probar obtención de ejercicios por nivel
        print("🧪 Probando obtención de ejercicios por nivel...")
        for nivel in [1, 2, 3, 4]:
            cursor.execute("""
                SELECT COUNT(*) as cantidad
                FROM therapy t
                INNER JOIN exercise e ON t.exerciseId = e.exerciseId
                WHERE t.levelId = ?
            """, (nivel,))
            cantidad = cursor.fetchone()['cantidad']
            
            nivel_enum = NivelTerapia(nivel)
            if cantidad > 0:
                print(f"  ✅ Nivel {nivel} ({nivel_enum.name}): {cantidad} ejercicios")
            else:
                print(f"  ❌ Nivel {nivel} ({nivel_enum.name}): 0 ejercicios - PROBLEMA")
        
        print()
        
        # 7. Verificar personas
        print("👥 Verificando personas...")
        cursor.execute("SELECT COUNT(*) as total FROM person")
        total_personas = cursor.fetchone()['total']
        print(f"  Total de personas: {total_personas}")
        
        if total_personas > 0:
            cursor.execute("""
                SELECT p.name, p.age, l.name as nivel
                FROM person p
                LEFT JOIN level l ON p.actual_level = l.levelId
                LIMIT 5
            """)
            print("  Primeras 5 personas:")
            for row in cursor.fetchall():
                print(f"    • {row['name']} ({row['age']} años) - Nivel: {row['nivel']}")
        
        print()
        
        # 8. Resumen
        print("="*70)
        print("📊 RESUMEN DEL DIAGNÓSTICO")
        print("="*70)
        
        problemas = []
        
        if len(niveles) != 4:
            problemas.append("Número incorrecto de niveles")
        
        if total_ejercicios == 0:
            problemas.append("No hay ejercicios en la BD")
        
        if total_therapy == 0:
            problemas.append("No hay asignaciones ejercicio-nivel (tabla THERAPY vacía)")
        
        if len(problemas) == 0:
            print("\n✅ ¡TODO CORRECTO! La base de datos está bien configurada.\n")
        else:
            print("\n❌ PROBLEMAS ENCONTRADOS:")
            for i, problema in enumerate(problemas, 1):
                print(f"  {i}. {problema}")
            print("\n🔧 SOLUCIÓN:")
            print("  Ejecuta: python inicializar_bd_mejorado.py")
            print("  Esto recreará la base de datos con todos los datos necesarios.\n")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error durante el diagnóstico: {e}")
        import traceback
        traceback.print_exc()


def verificar_ejercicios_nivel(db_path='data.db', nivel: int = 3):
    """Verificar ejercicios específicos de un nivel"""
    
    print(f"\n🔍 Verificando ejercicios del nivel {nivel}...\n")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Obtener ejercicios del nivel
        cursor.execute("""
            SELECT e.exerciseId, e.word, e.type, e.difficulty, t.therapy_number
            FROM therapy t
            INNER JOIN exercise e ON t.exerciseId = e.exerciseId
            WHERE t.levelId = ?
            ORDER BY t.therapy_number
        """, (nivel,))
        
        ejercicios = cursor.fetchall()
        
        if len(ejercicios) == 0:
            print(f"❌ No se encontraron ejercicios para el nivel {nivel}")
            print("   Esto explica el error que estás viendo.\n")
            print("🔧 SOLUCIÓN:")
            print("   1. Ejecuta: python inicializar_bd_mejorado.py")
            print("   2. Responde 'sí' cuando pregunte si quieres limpiar datos")
            print("   3. Esto creará todos los ejercicios y asignaciones necesarias\n")
        else:
            print(f"✅ Encontrados {len(ejercicios)} ejercicios para el nivel {nivel}:\n")
            for ej in ejercicios:
                print(f"  {ej['therapy_number']}. {ej['word']} (ID: {ej['exerciseId']}, Tipo: {ej['type']})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    
    # Diagnóstico completo
    diagnosticar_bd()
    
    # Si hay argumentos, verificar nivel específico
    if len(sys.argv) > 1:
        try:
            nivel = int(sys.argv[1])
            verificar_ejercicios_nivel(nivel=nivel)
        except:
            print("Uso: python diagnostico_bd.py [nivel]")
            print("Ejemplo: python diagnostico_bd.py 3")
