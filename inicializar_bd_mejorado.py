"""
SCRIPT DE INICIALIZACIÓN DE BASE DE DATOS - VERSIÓN MEJORADA
Crea las tablas y agrega datos de prueba completos para el Robot DODO
Sistema de 4 niveles: INICIAL, BASICO, INTERMEDIO, AVANZADO
"""

import sqlite3
from datetime import datetime, timedelta
import random

def crear_tablas(db_name='data.db'):
    """Crear todas las tablas necesarias"""
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    print("📦 Creando tablas en la base de datos...")
    
    # Tabla PERSON
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "person" (
            "personId" INTEGER NOT NULL UNIQUE,
            "name" TEXT NOT NULL,
            "age" INTEGER NOT NULL,
            "register_date" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            "diagnostic_level" INTEGER,
            "actual_level" INTEGER,
            "actual_therapy" INTEGER,
            PRIMARY KEY("personId" AUTOINCREMENT)
        )
    """)
    print("✅ Tabla 'person' creada")
    
    # Tabla EXERCISE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "exercise" (
            "exerciseId" INTEGER NOT NULL UNIQUE,
            "type" TEXT,
            "word" TEXT,
            "image" TEXT,
            "difficulty" INTEGER,
            PRIMARY KEY("exerciseId" AUTOINCREMENT)
        )
    """)
    print("✅ Tabla 'exercise' creada")
    
    # Tabla LEVEL
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "level" (
            "levelId" INTEGER NOT NULL UNIQUE,
            "name" TEXT,
            "description" TEXT,
            PRIMARY KEY("levelId" AUTOINCREMENT)
        )
    """)
    print("✅ Tabla 'level' creada")
    
    # Tabla SESION
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "sesion" (
            "sesionId" INTEGER NOT NULL UNIQUE,
            "date" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "number" INTEGER,
            "levelId" INTEGER NOT NULL,
            "observation" TEXT,
            "correct_exercise" INTEGER,
            "failed_exercise" INTEGER,
            PRIMARY KEY("sesionId" AUTOINCREMENT)
        )
    """)
    print("✅ Tabla 'sesion' creada")
    
    # Tabla THERAPY
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "therapy" (
            "therapyId" INTEGER NOT NULL UNIQUE,
            "levelId" INTEGER NOT NULL,
            "exerciseId" INTEGER NOT NULL,
            "therapy_number" INTEGER NOT NULL,
            PRIMARY KEY("therapyId" AUTOINCREMENT),
            FOREIGN KEY("levelId") REFERENCES "level"("levelId"),
            FOREIGN KEY("exerciseId") REFERENCES "exercise"("exerciseId")
        )
    """)
    print("✅ Tabla 'therapy' creada")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Todas las tablas creadas correctamente\n")


def limpiar_base_datos(db_name='data.db'):
    """Limpiar todos los datos existentes"""
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    print("🗑️  Limpiando datos existentes...")
    
    cursor.execute("DELETE FROM therapy")
    cursor.execute("DELETE FROM sesion")
    cursor.execute("DELETE FROM person")
    cursor.execute("DELETE FROM exercise")
    cursor.execute("DELETE FROM level")
    
    # Resetear autoincrement
    cursor.execute("DELETE FROM sqlite_sequence")
    
    conn.commit()
    conn.close()
    
    print("✅ Base de datos limpiada\n")


def insertar_niveles(db_name='data.db'):
    """Insertar los 4 niveles de terapia"""
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    print("🎯 Insertando 4 niveles de terapia...")
    
    # Los 4 niveles según NivelTerapia enum
    niveles = [
        (1, 'INICIAL', 'Sonidos básicos y palabras muy simples. Ideal para comenzar la terapia.'),
        (2, 'BASICO', 'Palabras simples con sonidos bilabiales (P, B, M). Construcción de vocabulario básico.'),
        (3, 'INTERMEDIO', 'Palabras más complejas y combinaciones de sonidos. Desarrollo del lenguaje.'),
        (4, 'AVANZADO', 'Frases completas y sonidos difíciles (R, RR, L). Dominio del habla.')
    ]
    
    cursor.executemany("""
        INSERT INTO level (levelId, name, description)
        VALUES (?, ?, ?)
    """, niveles)
    
    conn.commit()
    conn.close()
    
    print(f"✅ {len(niveles)} niveles insertados correctamente\n")


def insertar_ejercicios(db_name='data.db'):
    """Insertar ejercicios organizados por nivel"""
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    print("📝 Insertando ejercicios por nivel...")
    
    # NIVEL 1 - INICIAL: Vocales y palabras muy simples (8 ejercicios)
    ejercicios_nivel1 = [
        ('vocal', 'A', None, 1),
        ('vocal', 'E', None, 1),
        ('vocal', 'I', None, 1),
        ('vocal', 'O', None, 1),
        ('vocal', 'U', None, 1),
        ('palabra', 'MAMÁ', None, 1),
        ('palabra', 'PAPÁ', None, 1),
        ('palabra', 'BEBÉ', None, 1),
    ]
    
    # NIVEL 2 - BASICO: Palabras simples con sonidos bilabiales (10 ejercicios)
    ejercicios_nivel2 = [
        ('palabra', 'BOCA', None, 2),
        ('palabra', 'MANO', None, 2),
        ('palabra', 'PATO', None, 2),
        ('palabra', 'MESA', None, 2),
        ('palabra', 'BOLA', None, 2),
        ('palabra', 'POMO', None, 2),
        ('palabra', 'BOTE', None, 2),
        ('palabra', 'MIMO', None, 2),
        ('palabra', 'PIPA', None, 2),
        ('palabra', 'MAPA', None, 2),
    ]
    
    # NIVEL 3 - INTERMEDIO: Palabras más complejas (12 ejercicios)
    ejercicios_nivel3 = [
        ('palabra', 'CASA', None, 3),
        ('palabra', 'GATO', None, 3),
        ('palabra', 'DADO', None, 3),
        ('palabra', 'TAZA', None, 3),
        ('palabra', 'DEDO', None, 3),
        ('palabra', 'CAMA', None, 3),
        ('palabra', 'GOMA', None, 3),
        ('palabra', 'TODO', None, 3),
        ('palabra', 'QUESO', None, 3),
        ('palabra', 'NIDO', None, 3),
        ('palabra', 'SOPA', None, 3),
        ('palabra', 'LUNA', None, 3),
    ]
    
    # NIVEL 4 - AVANZADO: Palabras difíciles y frases (15 ejercicios)
    ejercicios_nivel4 = [
        ('palabra', 'LORO', None, 4),
        ('palabra', 'ROSA', None, 4),
        ('palabra', 'PERRO', None, 4),
        ('palabra', 'CARRO', None, 4),
        ('palabra', 'RORRO', None, 4),
        ('palabra', 'LÁPIZ', None, 4),
        ('palabra', 'LÁMPARA', None, 4),
        ('palabra', 'GUITARRA', None, 4),
        ('frase', 'MI MAMÁ', None, 4),
        ('frase', 'MI PAPÁ', None, 4),
        ('frase', 'LA CASA', None, 4),
        ('frase', 'EL GATO', None, 4),
        ('frase', 'YO COMO PAN', None, 4),
        ('frase', 'ME GUSTA JUGAR', None, 4),
        ('frase', 'MAMÁ ESTÁ AQUÍ', None, 4),
    ]
    
    # Insertar todos los ejercicios
    todos_ejercicios = ejercicios_nivel1 + ejercicios_nivel2 + ejercicios_nivel3 + ejercicios_nivel4
    
    cursor.executemany("""
        INSERT INTO exercise (type, word, image, difficulty)
        VALUES (?, ?, ?, ?)
    """, todos_ejercicios)
    
    conn.commit()
    
    print(f"✅ {len(todos_ejercicios)} ejercicios insertados")
    print(f"   - Nivel 1 (INICIAL): {len(ejercicios_nivel1)} ejercicios")
    print(f"   - Nivel 2 (BASICO): {len(ejercicios_nivel2)} ejercicios")
    print(f"   - Nivel 3 (INTERMEDIO): {len(ejercicios_nivel3)} ejercicios")
    print(f"   - Nivel 4 (AVANZADO): {len(ejercicios_nivel4)} ejercicios\n")
    
    conn.close()


def asignar_ejercicios_a_niveles(db_name='data.db'):
    """Crear las relaciones en la tabla THERAPY"""
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    print("🔗 Asignando ejercicios a niveles (tabla THERAPY)...")
    
    # Obtener ejercicios por dificultad
    cursor.execute("SELECT exerciseId, difficulty FROM exercise ORDER BY exerciseId")
    ejercicios = cursor.fetchall()
    
    terapias = []
    therapy_number = 1
    
    for exercise_id, difficulty in ejercicios:
        # La dificultad corresponde al levelId
        level_id = difficulty
        terapias.append((level_id, exercise_id, therapy_number))
        therapy_number += 1
    
    cursor.executemany("""
        INSERT INTO therapy (levelId, exerciseId, therapy_number)
        VALUES (?, ?, ?)
    """, terapias)
    
    conn.commit()
    conn.close()
    
    print(f"✅ {len(terapias)} relaciones creadas en tabla THERAPY\n")


def insertar_datos_prueba(db_name='data.db'):
    """Insertar personas y sesiones de prueba para todos los casos"""
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    print("👥 Insertando datos de prueba...")
    
    # Fecha base para las pruebas
    fecha_base = datetime.now()
    
    # ========== CASO 1: Usuario nuevo que empezará desde cero ==========
    # No insertamos nada, este caso se prueba al registrar un nuevo usuario
    
    # ========== CASO 2: Usuario en NIVEL INICIAL (recién empezando) ==========
    cursor.execute("""
        INSERT INTO person (name, age, register_date, diagnostic_level, actual_level, actual_therapy)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ('Ana Martínez', 6, fecha_base - timedelta(days=5), 1, 1, 1))
    ana_id = cursor.lastrowid
    
    # 1 sesión con bajo rendimiento
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=4), 1, 1, 'Primera sesión, mostrando progreso', 3, 5))
    
    print("✅ Ana Martínez - Nivel INICIAL (recién empezando)")
    
    # ========== CASO 3: Usuario en NIVEL BASICO (progreso moderado) ==========
    cursor.execute("""
        INSERT INTO person (name, age, register_date, diagnostic_level, actual_level, actual_therapy)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ('Carlos Pérez', 7, fecha_base - timedelta(days=15), 1, 2, 1))
    carlos_id = cursor.lastrowid
    
    # 3 sesiones mostrando progreso
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=14), 1, 1, 'Completó nivel inicial', 7, 1))
    
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=10), 2, 2, 'Avanzando en nivel básico', 6, 4))
    
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=5), 3, 2, 'Mejorando consistentemente', 7, 3))
    
    print("✅ Carlos Pérez - Nivel BASICO (progreso moderado)")
    
    # ========== CASO 4: Usuario en NIVEL INTERMEDIO (buen progreso) ==========
    cursor.execute("""
        INSERT INTO person (name, age, register_date, diagnostic_level, actual_level, actual_therapy)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ('María López', 8, fecha_base - timedelta(days=30), 2, 3, 1))
    maria_id = cursor.lastrowid
    
    # 5 sesiones mostrando excelente progreso
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=28), 1, 2, 'Inicio en nivel básico', 7, 3))
    
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=25), 2, 2, 'Dominando nivel básico', 9, 1))
    
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=20), 3, 3, 'Subió a nivel intermedio', 8, 4))
    
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=15), 4, 3, 'Progreso constante', 9, 3))
    
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=10), 5, 3, 'Excelente desempeño', 10, 2))
    
    print("✅ María López - Nivel INTERMEDIO (buen progreso)")
    
    # ========== CASO 5: Usuario en NIVEL AVANZADO (casi completando) ==========
    cursor.execute("""
        INSERT INTO person (name, age, register_date, diagnostic_level, actual_level, actual_therapy)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ('Juan García', 9, fecha_base - timedelta(days=60), 2, 4, 1))
    juan_id = cursor.lastrowid
    
    # 8 sesiones mostrando dominio completo
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=55), 1, 2, 'Inicio en básico', 8, 2))
    
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=50), 2, 3, 'Avance a intermedio', 10, 2))
    
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=45), 3, 3, 'Dominando intermedio', 11, 1))
    
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=40), 4, 4, 'Subió a avanzado', 10, 5))
    
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=30), 5, 4, 'Adaptándose al nivel avanzado', 11, 4))
    
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=20), 6, 4, 'Mejorando significativamente', 12, 3))
    
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=10), 7, 4, 'Excelente control del habla', 13, 2))
    
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=3), 8, 4, 'Dominando nivel avanzado', 14, 1))
    
    print("✅ Juan García - Nivel AVANZADO (casi completando)")
    
    # ========== CASO 6: Usuario con dificultades (múltiples intentos en mismo nivel) ==========
    cursor.execute("""
        INSERT INTO person (name, age, register_date, diagnostic_level, actual_level, actual_therapy)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ('Sofía Torres', 5, fecha_base - timedelta(days=20), 1, 1, 1))
    sofia_id = cursor.lastrowid
    
    # 4 sesiones en nivel inicial con dificultades
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=18), 1, 1, 'Presenta dificultad con vocales', 2, 6))
    
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=14), 2, 1, 'Ligera mejora, necesita refuerzo', 3, 5))
    
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=10), 3, 1, 'Avance lento pero constante', 4, 4))
    
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=5), 4, 1, 'Mostrando mejora gradual', 5, 3))
    
    print("✅ Sofía Torres - Nivel INICIAL (con dificultades)")
    
    # ========== CASO 7: Usuario que regresa después de tiempo sin asistir ==========
    cursor.execute("""
        INSERT INTO person (name, age, register_date, diagnostic_level, actual_level, actual_therapy)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ('Luis Ramírez', 8, fecha_base - timedelta(days=90), 1, 2, 1))
    luis_id = cursor.lastrowid
    
    # 2 sesiones antiguas y una reciente
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=88), 1, 1, 'Primera sesión exitosa', 7, 1))
    
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=85), 2, 2, 'Subió a nivel básico', 8, 2))
    
    # Última sesión reciente (regresó después de mucho tiempo)
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=2), 3, 2, 'Regresó después de ausencia, mantiene nivel', 6, 4))
    
    print("✅ Luis Ramírez - Nivel BASICO (regresó después de ausencia)")
    
    # ========== CASO 8: Hermanos en diferentes niveles ==========
    cursor.execute("""
        INSERT INTO person (name, age, register_date, diagnostic_level, actual_level, actual_therapy)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ('Diego Morales', 7, fecha_base - timedelta(days=25), 1, 2, 1))
    
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=20), 1, 1, 'Hermano mayor, buen inicio', 7, 1))
    
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=15), 2, 2, 'Avance rápido', 8, 2))
    
    cursor.execute("""
        INSERT INTO person (name, age, register_date, diagnostic_level, actual_level, actual_therapy)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ('Elena Morales', 5, fecha_base - timedelta(days=10), 1, 1, 1))
    
    cursor.execute("""
        INSERT INTO sesion (date, number, levelId, observation, correct_exercise, failed_exercise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_base - timedelta(days=8), 1, 1, 'Hermana menor, primera sesión', 4, 4))
    
    print("✅ Diego y Elena Morales - Hermanos en diferentes niveles")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ {8} personas de prueba insertadas con sus sesiones\n")


def mostrar_estadisticas_completas(db_name='data.db'):
    """Mostrar estadísticas detalladas de la base de datos"""
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("📊 ESTADÍSTICAS COMPLETAS DE LA BASE DE DATOS")
    print("="*70 + "\n")
    
    # Niveles y sus ejercicios
    print("🎯 NIVELES DE TERAPIA:")
    cursor.execute("""
        SELECT l.levelId, l.name, l.description, COUNT(t.therapyId) as num_ejercicios
        FROM level l
        LEFT JOIN therapy t ON l.levelId = t.levelId
        GROUP BY l.levelId
        ORDER BY l.levelId
    """)
    
    for row in cursor.fetchall():
        print(f"\n   Nivel {row[0]}: {row[1]}")
        print(f"   📝 {row[3]} ejercicios asignados")
        print(f"   📋 {row[2]}")
    
    # Personas por nivel
    print("\n\n👥 PERSONAS REGISTRADAS POR NIVEL:")
    cursor.execute("""
        SELECT l.name, COUNT(p.personId) as cantidad
        FROM level l
        LEFT JOIN person p ON l.levelId = p.actual_level
        GROUP BY l.levelId
        ORDER BY l.levelId
    """)
    
    total_personas = 0
    for row in cursor.fetchall():
        cantidad = row[1]
        total_personas += cantidad
        print(f"   {row[0]}: {cantidad} persona(s)")
    
    print(f"\n   TOTAL: {total_personas} personas registradas")
    
    # Sesiones totales
    cursor.execute("SELECT COUNT(*) FROM sesion")
    sesiones = cursor.fetchone()[0]
    print(f"\n📅 SESIONES REALIZADAS: {sesiones}")
    
    # Promedio de sesiones por persona
    if total_personas > 0:
        promedio = sesiones / total_personas
        print(f"📊 Promedio de sesiones por persona: {promedio:.1f}")
    
    # Ejercicios por tipo
    print("\n\n📝 EJERCICIOS POR TIPO:")
    cursor.execute("""
        SELECT type, COUNT(*) as cantidad
        FROM exercise
        GROUP BY type
    """)
    
    for row in cursor.fetchall():
        print(f"   {row[0].capitalize()}: {row[1]} ejercicios")
    
    # Total de ejercicios
    cursor.execute("SELECT COUNT(*) FROM exercise")
    total_ejercicios = cursor.fetchone()[0]
    print(f"\n   TOTAL: {total_ejercicios} ejercicios")
    
    # Lista de todas las personas con su información
    print("\n\n👤 DETALLE DE PERSONAS REGISTRADAS:")
    cursor.execute("""
        SELECT 
            p.name, 
            p.age, 
            l.name as nivel,
            COUNT(s.sesionId) as num_sesiones,
            ROUND(AVG(CAST(s.correct_exercise AS FLOAT) / 
                      (s.correct_exercise + s.failed_exercise) * 100), 1) as tasa_exito
        FROM person p
        LEFT JOIN level l ON p.actual_level = l.levelId
        LEFT JOIN sesion s ON l.levelId = s.levelId
        GROUP BY p.personId
        ORDER BY p.personId
    """)
    
    print()
    for row in cursor.fetchall():
        nombre, edad, nivel, sesiones, tasa = row
        tasa_str = f"{tasa}%" if tasa else "N/A"
        print(f"   • {nombre} ({edad} años)")
        print(f"     Nivel: {nivel} | Sesiones: {sesiones} | Tasa éxito: {tasa_str}")
    
    print("\n" + "="*70 + "\n")
    
    conn.close()


def main():
    """Función principal"""
    
    print("\n" + "="*70)
    print("  🤖 ROBOT DODO - INICIALIZACIÓN DE BASE DE DATOS MEJORADA")
    print("  Sistema de 4 niveles con datos de prueba completos")
    print("="*70 + "\n")
    
    db_name = 'data.db'
    
    # Preguntar si desea limpiar datos existentes
    import os
    if os.path.exists(db_name):
        print("⚠️  La base de datos ya existe.")
        respuesta = input("¿Deseas limpiar todos los datos y empezar de cero? (s/n): ")
        if respuesta.lower() == 's':
            limpiar_base_datos(db_name)
        else:
            print("❌ Operación cancelada. No se modificó la base de datos.\n")
            return
    
    # Crear estructura
    crear_tablas(db_name)
    
    # Insertar datos
    insertar_niveles(db_name)
    insertar_ejercicios(db_name)
    asignar_ejercicios_a_niveles(db_name)
    insertar_datos_prueba(db_name)
    
    # Mostrar estadísticas
    mostrar_estadisticas_completas(db_name)
    
    print("✅ Base de datos inicializada correctamente")
    print(f"📁 Archivo: {db_name}")
    print(f"\n💡 CASOS DE PRUEBA INCLUIDOS:")
    print("   1. Usuario nuevo (sin registrar) - Para probar registro inicial")
    print("   2. Ana Martínez - Nivel INICIAL (recién empezando)")
    print("   3. Carlos Pérez - Nivel BASICO (progreso moderado)")
    print("   4. María López - Nivel INTERMEDIO (buen progreso)")
    print("   5. Juan García - Nivel AVANZADO (casi completando)")
    print("   6. Sofía Torres - Con dificultades (múltiples intentos)")
    print("   7. Luis Ramírez - Regresó después de ausencia")
    print("   8. Diego y Elena Morales - Hermanos en diferentes niveles")
    print(f"\n🚀 Ahora puedes ejecutar: python main.py\n")


if __name__ == "__main__":
    main()
