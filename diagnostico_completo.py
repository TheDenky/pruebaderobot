"""
Diagnóstico completo del sistema
"""
import sqlite3

def diagnosticar():
    print("\n" + "="*70)
    print("🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA")
    print("="*70 + "\n")
    
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Test 1: Sesiones con datos
    print("1️⃣  Verificando datos de sesiones...")
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN correct_exercise > 0 THEN 1 END) as con_datos,
            COUNT(CASE WHEN correct_exercise IS NULL THEN 1 END) as sin_datos
        FROM sesion
    """)
    row = cursor.fetchone()
    print(f"   Total sesiones: {row['total']}")
    print(f"   Con datos: {row['con_datos']}")
    print(f"   Sin datos: {row['sin_datos']}")
    
    if row['sin_datos'] > 0:
        print("   ⚠️ Hay sesiones sin datos de ejercicios")
    else:
        print("   ✅ Todas las sesiones tienen datos")
    
    # Test 2: Sesiones huérfanas
    print("\n2️⃣  Verificando sesiones huérfanas...")
    cursor.execute("SELECT COUNT(*) as total FROM sesion WHERE personId IS NULL")
    huerfanas = cursor.fetchone()['total']
    print(f"   Sesiones sin personId: {huerfanas}")
    
    if huerfanas > 0:
        print("   ⚠️ Hay sesiones huérfanas que deben corregirse")
    else:
        print("   ✅ No hay sesiones huérfanas")
    
    # Test 3: Contador de sesiones por persona
    print("\n3️⃣  Verificando contador de sesiones por persona...")
    cursor.execute("""
        SELECT 
            p.personId,
            p.name,
            COUNT(s.sesionId) as num_sesiones
        FROM person p
        LEFT JOIN sesion s ON p.personId = s.personId
        GROUP BY p.personId
        HAVING num_sesiones > 0
    """)
    
    personas_con_sesiones = cursor.fetchall()
    print(f"   Personas con sesiones: {len(personas_con_sesiones)}")
    
    for p in personas_con_sesiones[:5]:
        print(f"      • {p['name']}: {p['num_sesiones']} sesiones")
    
    # Test 4: Datos de última sesión
    print("\n4️⃣  Verificando última sesión de cada persona...")
    for p in personas_con_sesiones[:3]:
        cursor.execute("""
            SELECT correct_exercise, failed_exercise
            FROM sesion
            WHERE personId = ?
            ORDER BY date DESC
            LIMIT 1
        """, (p['personId'],))
        
        sesion = cursor.fetchone()
        if sesion:
            print(f"   {p['name']}: ✓{sesion['correct_exercise']} ✗{sesion['failed_exercise']}")
    
    # Test 5: Personas sin apellido
    print("\n5️⃣  Verificando personas sin apellido...")
    cursor.execute("""
        SELECT COUNT(*) as total 
        FROM person 
        WHERE apellido IS NULL OR apellido = ''
    """)
    sin_apellido = cursor.fetchone()['total']
    print(f"   Personas sin apellido: {sin_apellido}")
    
    conn.close()
    
    print("\n" + "="*70)
    print("✅ DIAGNÓSTICO COMPLETADO")
    print("="*70 + "\n")

if __name__ == "__main__":
    diagnosticar()