"""
DATABASE MEJORADO - Gestión completa de base de datos
Versión corregida que maneja correctamente sqlite3.Row
"""
import sqlite3
from typing import Optional, List, Dict, Any
from models import Persona, Ejercicio, Sesion, NivelTerapia, ResultadoEjercicio
from datetime import datetime


class Database:
    """Gestor de base de datos con todas las operaciones"""
    
    def __init__(self, db_path: str = 'data.db'):
        self.db_path = db_path
        self.conn = None
        self.conectar()
    
    def conectar(self):
        """Conectar a la base de datos"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            print(f"✅ Conectado a BD: {self.db_path}")
        except Exception as e:
            print(f"❌ Error al conectar BD: {e}")
    
    # ========== PERSONAS ==========
    
    def crear_persona(self, persona: Persona) -> int:
        """Crear nueva persona"""
        try:
            cursor = self.conn.cursor()
            nivel_id = persona.nivel_actual.value
            cursor.execute('''
                INSERT INTO person (name, age, diagnostic_level, actual_level, actual_therapy)
                VALUES (?, ?, ?, ?, ?)
            ''', (persona.name, persona.age, nivel_id, nivel_id, 1))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"❌ Error al crear persona: {e}")
            return None
    
    def buscar_persona_por_nombre(self, nombre: str) -> Optional[Persona]:
        """Buscar persona por nombre"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM person 
                WHERE name LIKE ? 
                ORDER BY register_date DESC 
                LIMIT 1
            ''', (f'%{nombre}%',))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_persona(row)
            return None
        except Exception as e:
            print(f"❌ Error al buscar persona: {e}")
            return None
    
    def actualizar_nivel_persona(self, person_id: int, nivel: NivelTerapia):
        """Actualizar nivel de la persona"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE person 
                SET actual_level = ? 
                WHERE personId = ?
            ''', (nivel.value, person_id))
            self.conn.commit()
        except Exception as e:
            print(f"❌ Error al actualizar nivel: {e}")
    
    def contar_personas(self) -> int:
        """Contar total de personas"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT COUNT(*) as total FROM person')
            row = cursor.fetchone()
            return row['total'] if row else 0
        except:
            return 0
    
    # ========== EJERCICIOS ==========
    
    def obtener_ejercicios_por_nivel(self, nivel: NivelTerapia) -> List[Ejercicio]:
        """Obtener ejercicios de un nivel específico - VERSIÓN CORREGIDA"""
        try:
            cursor = self.conn.cursor()
            nivel_id = nivel.value
            
            print(f"🔍 Buscando ejercicios para nivel {nivel_id} ({nivel.name})")
            
            # Obtener desde tabla therapy con JOIN a exercise
            cursor.execute('''
                SELECT e.exerciseId, e.word, e.type, e.difficulty, e.image
                FROM therapy t
                INNER JOIN exercise e ON t.exerciseId = e.exerciseId
                WHERE t.levelId = ?
                ORDER BY t.therapy_number
            ''', (nivel_id,))
            rows = cursor.fetchall()
            
            print(f"📋 Encontrados {len(rows)} ejercicios")
            
            ejercicios = []
            for row in rows:
                # CORRECCIÓN: Acceder a columnas usando corchetes en lugar de .get()
                ejercicio = Ejercicio(
                    exercise_id=row['exerciseId'],
                    word=row['word'],
                    nivel=nivel,
                    tipo=row['type'] if row['type'] else 'palabra',
                    dificultad=row['difficulty'] if row['difficulty'] else nivel_id,
                    apoyo_visual=row['image'] if row['image'] else None
                )
                ejercicios.append(ejercicio)
                print(f"  • {ejercicio.word} (ID: {ejercicio.exercise_id})")
            
            return ejercicios
        except Exception as e:
            print(f"❌ Error al obtener ejercicios: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def obtener_todos_ejercicios(self) -> List[Ejercicio]:
        """Obtener todos los ejercicios - VERSIÓN CORREGIDA"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT exerciseId, word, type, difficulty, image FROM exercise ORDER BY difficulty')
            rows = cursor.fetchall()
            
            print(f"📋 Encontrados {len(rows)} ejercicios totales")
            
            ejercicios = []
            for row in rows:
                # CORRECCIÓN: Acceder a columnas correctamente
                difficulty = row['difficulty'] if row['difficulty'] else 1
                
                # Determinar nivel según dificultad
                if difficulty == 1:
                    nivel = NivelTerapia.INICIAL
                elif difficulty == 2:
                    nivel = NivelTerapia.BASICO
                elif difficulty == 3:
                    nivel = NivelTerapia.INTERMEDIO
                else:
                    nivel = NivelTerapia.AVANZADO
                
                ejercicio = Ejercicio(
                    exercise_id=row['exerciseId'],
                    word=row['word'],
                    nivel=nivel,
                    tipo=row['type'] if row['type'] else 'palabra',
                    dificultad=difficulty,
                    apoyo_visual=row['image'] if row['image'] else None
                )
                ejercicios.append(ejercicio)
            
            return ejercicios
        except Exception as e:
            print(f"❌ Error al obtener ejercicios: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def obtener_ejercicio_por_id(self, exercise_id: int) -> Optional[Ejercicio]:
        """Obtener un ejercicio específico por ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT exerciseId, word, type, difficulty, image 
                FROM exercise 
                WHERE exerciseId = ?
            ''', (exercise_id,))
            row = cursor.fetchone()
            
            if row:
                difficulty = row['difficulty'] if row['difficulty'] else 1
                
                if difficulty == 1:
                    nivel = NivelTerapia.INICIAL
                elif difficulty == 2:
                    nivel = NivelTerapia.BASICO
                elif difficulty == 3:
                    nivel = NivelTerapia.INTERMEDIO
                else:
                    nivel = NivelTerapia.AVANZADO
                
                return Ejercicio(
                    exercise_id=row['exerciseId'],
                    word=row['word'],
                    nivel=nivel,
                    tipo=row['type'] if row['type'] else 'palabra',
                    dificultad=difficulty,
                    apoyo_visual=row['image'] if row['image'] else None
                )
            return None
        except Exception as e:
            print(f"❌ Error al obtener ejercicio: {e}")
            return None
    
    # ========== SESIONES ==========
    
    def crear_sesion(self, sesion: Sesion) -> int:
        """Crear nueva sesión"""
        try:
            cursor = self.conn.cursor()
            nivel_id = sesion.nivel.value
            
            cursor.execute('''
                INSERT INTO sesion (levelId, correct_exercise, failed_exercise, observation, number)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                nivel_id,
                sesion.ejercicios_correctos,
                sesion.ejercicios_fallidos,
                sesion.observaciones,
                1
            ))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"❌ Error al crear sesión: {e}")
            return None
    
    def obtener_ultima_sesion(self, person_id: int) -> Optional[Sesion]:
        """Obtener última sesión de una persona"""
        try:
            # Obtener persona para saber su nivel actual
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM person WHERE personId = ?', (person_id,))
            persona_row = cursor.fetchone()
            
            if not persona_row:
                return None
            
            nivel_actual = persona_row['actual_level']
            
            # Obtener última sesión de ese nivel
            cursor.execute('''
                SELECT * FROM sesion 
                WHERE levelId = ?
                ORDER BY date DESC 
                LIMIT 1
            ''', (nivel_actual,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_sesion(row, person_id)
            return None
        except Exception as e:
            print(f"❌ Error al obtener sesión: {e}")
            return None
    
    def obtener_sesiones_por_persona(self, person_id: int) -> List[Sesion]:
        """Obtener todas las sesiones de una persona"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM sesion 
                ORDER BY date DESC
            ''')
            rows = cursor.fetchall()
            
            sesiones = []
            for row in rows:
                sesion = self._row_to_sesion(row, person_id)
                if sesion:
                    sesiones.append(sesion)
            
            return sesiones
        except Exception as e:
            print(f"❌ Error al obtener sesiones: {e}")
            return []
    
    # ========== NIVELES ==========
    
    def obtener_nivel_por_id(self, level_id: int) -> Optional[dict]:
        """Obtener información de un nivel"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM level WHERE levelId = ?', (level_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'levelId': row['levelId'],
                    'name': row['name'],
                    'description': row['description'] if row['description'] else ''
                }
            return None
        except Exception as e:
            print(f"❌ Error al obtener nivel: {e}")
            return None
    
    def obtener_todos_niveles(self) -> List[dict]:
        """Obtener todos los niveles"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM level ORDER BY levelId')
            rows = cursor.fetchall()
            
            niveles = []
            for row in rows:
                niveles.append({
                    'levelId': row['levelId'],
                    'name': row['name'],
                    'description': row['description'] if row['description'] else ''
                })
            
            return niveles
        except Exception as e:
            print(f"❌ Error al obtener niveles: {e}")
            return []
    
    # ========== MAPEO DE DATOS ==========
    
    def _row_to_persona(self, row) -> Persona:
        """Convertir row de BD a Persona"""
        nivel_id = row['actual_level'] if row['actual_level'] else 1
        
        try:
            nivel = NivelTerapia(nivel_id)
        except:
            nivel = NivelTerapia.INICIAL
        
        return Persona(
            person_id=row['personId'],
            name=row['name'],
            age=row['age'],
            nivel_actual=nivel,
            fecha_registro=row['register_date'] if row['register_date'] else datetime.now()
        )
    
    def _row_to_sesion(self, row, person_id: int) -> Sesion:
        """Convertir row de BD a Sesion"""
        nivel_id = row['levelId']
        
        try:
            nivel = NivelTerapia(nivel_id)
        except:
            nivel = NivelTerapia.INICIAL
        
        fecha_str = row['date'] if row['date'] else None
        if fecha_str:
            try:
                fecha = datetime.fromisoformat(fecha_str)
            except:
                fecha = datetime.now()
        else:
            fecha = datetime.now()
        
        return Sesion(
            sesion_id=row['sesionId'],
            person_id=person_id,
            nivel=nivel,
            fecha=fecha,
            ejercicios_completados=[],
            observaciones=row['observation'] if row['observation'] else ''
        )
    
    # ========== UTILIDADES ==========
    
    def verificar_integridad(self) -> dict:
        """Verificar integridad de la base de datos"""
        try:
            cursor = self.conn.cursor()
            
            # Contar registros en cada tabla
            cursor.execute('SELECT COUNT(*) FROM person')
            personas = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM exercise')
            ejercicios = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM level')
            niveles = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM therapy')
            terapias = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM sesion')
            sesiones = cursor.fetchone()[0]
            
            return {
                'personas': personas,
                'ejercicios': ejercicios,
                'niveles': niveles,
                'terapias': terapias,
                'sesiones': sesiones
            }
        except Exception as e:
            print(f"❌ Error al verificar integridad: {e}")
            return {}
    
    def limpiar_datos(self):
        """Limpiar todos los datos (usar con cuidado)"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM therapy')
            cursor.execute('DELETE FROM sesion')
            cursor.execute('DELETE FROM person')
            cursor.execute('DELETE FROM exercise')
            cursor.execute('DELETE FROM level')
            cursor.execute('DELETE FROM sqlite_sequence')
            self.conn.commit()
            print("✅ Datos limpiados")
        except Exception as e:
            print(f"❌ Error al limpiar datos: {e}")
    
    def cerrar(self):
        """Cerrar conexión"""
        if self.conn:
            self.conn.close()
            print("🔒 Conexión a BD cerrada")
