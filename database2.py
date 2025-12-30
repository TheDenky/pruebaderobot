"""
DATABASE - Gestión completa de base de datos
Todo lo relacionado con SQLite en un solo archivo
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
        """Obtener ejercicios de un nivel específico"""
        try:
            cursor = self.conn.cursor()
            nivel_id = nivel.value
            
            # Obtener desde tabla therapy con JOIN a exercise
            cursor.execute('''
                SELECT e.*, t.levelId
                FROM therapy t
                INNER JOIN exercise e ON t.exerciseId = e.exerciseId
                WHERE t.levelId = ?
                ORDER BY t.therapy_number
            ''', (nivel_id,))
            rows = cursor.fetchall()
            
            ejercicios = []
            for row in rows:
                ejercicio = Ejercicio(
                    exercise_id=row['exerciseId'],
                    word=row['word'],
                    nivel=nivel,
                    tipo=row.get('type', 'palabra'),
                    dificultad=row.get('difficulty', 1),
                    apoyo_visual=row.get('image')
                )
                ejercicios.append(ejercicio)
            
            return ejercicios
        except Exception as e:
            print(f"❌ Error al obtener ejercicios: {e}")
            return []
    
    def obtener_todos_ejercicios(self) -> List[Ejercicio]:
        """Obtener todos los ejercicios"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM exercise ORDER BY difficulty')
            rows = cursor.fetchall()
            
            ejercicios = []
            for row in rows:
                ejercicio = Ejercicio(
                    exercise_id=row['exerciseId'],
                    word=row['word'],
                    tipo=row.get('type', 'palabra'),
                    dificultad=row.get('difficulty', 1),
                    apoyo_visual=row.get('image')
                )
                ejercicios.append(ejercicio)
            
            return ejercicios
        except Exception as e:
            print(f"❌ Error al obtener ejercicios: {e}")
            return []
    
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
    
    # ========== MAPEO DE DATOS ==========
    
    def _row_to_persona(self, row) -> Persona:
        """Convertir row de BD a Persona"""
        nivel_id = row.get('actual_level', 1)
        try:
            nivel = NivelTerapia(nivel_id)
        except:
            nivel = NivelTerapia.INICIAL
        
        return Persona(
            person_id=row['personId'],
            name=row['name'],
            age=row['age'],
            nivel_actual=nivel,
            fecha_registro=row.get('register_date')
        )
    
    def _row_to_sesion(self, row, person_id: int) -> Sesion:
        """Convertir row de BD a Sesion"""
        nivel_id = row['levelId']
        try:
            nivel = NivelTerapia(nivel_id)
        except:
            nivel = NivelTerapia.INICIAL
        
        fecha_str = row.get('date')
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
            observaciones=row.get('observation', '')
        )
    
    def cerrar(self):
        """Cerrar conexión"""
        if self.conn:
            self.conn.close()
            print("🔒 Conexión a BD cerrada")