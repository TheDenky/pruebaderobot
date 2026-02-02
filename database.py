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
                INSERT INTO person (name, age, dni, sex, diagnostic_level, actual_level, actual_therapy)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                persona.name, 
                persona.age, 
                persona.dni,
                persona.sex,
                nivel_id, 
                nivel_id, 
                1
            ))
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
        
    def actualizar_datos_persona(
        self, 
        person_id: int,
        name: Optional[str] = None,
        apellido: Optional[str] = None,
        dni: Optional[str] = None,
        age: Optional[int] = None,
        sex: Optional[str] = None
    ) -> bool:
        """
        Actualizar datos generales de una persona
        Solo actualiza los campos que no sean None
        
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        try:
            campos_actualizar = []
            valores = []
            
            # Construir query dinámicamente solo con campos a actualizar
            if name is not None:
                campos_actualizar.append("name = ?")
                valores.append(name)
            
            if apellido is not None:
                campos_actualizar.append("apellido = ?")
                valores.append(apellido)
            
            if dni is not None:
                campos_actualizar.append("dni = ?")
                valores.append(dni)
            
            if age is not None:
                campos_actualizar.append("age = ?")
                valores.append(age)
            
            if sex is not None:
                campos_actualizar.append("sex = ?")
                valores.append(sex)
            
            if not campos_actualizar:
                print("⚠️ No hay campos para actualizar")
                return False
            
            # Agregar person_id al final
            valores.append(person_id)
            
            # Construir y ejecutar query
            query = f"""
                UPDATE person 
                SET {', '.join(campos_actualizar)}
                WHERE personId = ?
            """
            
            cursor = self.conn.cursor()
            cursor.execute(query, valores)
            self.conn.commit()
            
            print(f"✅ Datos actualizados para persona ID {person_id}")
            print(f"   Campos: {', '.join([c.split('=')[0].strip() for c in campos_actualizar])}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al actualizar datos: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def obtener_persona_completa(self, person_id: int) -> Optional[dict]:
        """
        Obtener todos los datos de una persona incluyendo apellido
        
        Returns:
            Diccionario con todos los datos o None
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT p.*, l.name as nivel_nombre
                FROM person p
                LEFT JOIN level l ON p.actual_level = l.levelId
                WHERE p.personId = ?
            """, (person_id,))
            
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return {
                'person_id': row['personId'],
                'name': row['name'],
                'apellido': row['apellido'] if 'apellido' in row.keys() else None,
                'age': row['age'],
                'dni': row['dni'] if 'dni' in row.keys() else None,
                'sex': row['sex'] if 'sex' in row.keys() else None,
                'nivel_id': row['actual_level'],
                'nivel_nombre': row['nivel_nombre'],
                'fecha_registro': row['register_date']
            }
            
        except Exception as e:
            print(f"❌ Error al obtener persona: {e}")
            return None
    
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
                INSERT INTO sesion (
                    personId, levelId, number, 
                    correct_exercise, failed_exercise, 
                    observation, observaciones_terapeuta
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                sesion.person_id,
                nivel_id,
                sesion.numero_sesion,
                sesion.ejercicios_correctos,
                sesion.ejercicios_fallidos,
                sesion.observaciones,
                sesion.observaciones_terapeuta
            ))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"❌ Error al crear sesión: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def obtener_ultima_sesion(self, person_id: int) -> Optional[Sesion]:
        """Obtener última sesión de una persona"""
        try:
            cursor = self.conn.cursor()
            
            # Obtener última sesión de esta persona específica
            cursor.execute('''
                SELECT * FROM sesion 
                WHERE personId = ?
                ORDER BY date DESC 
                LIMIT 1
            ''', (person_id,))
            
            row = cursor.fetchone()
            
            if row:
                return self._row_to_sesion(row, person_id)
            return None
            
        except Exception as e:
            print(f"❌ Error al obtener sesión: {e}")
            return None
            
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
                WHERE personId = ?
                ORDER BY date ASC
            ''', (person_id,))
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
            dni=row['dni'] if 'dni' in row.keys() else None,
            sex=row['sex'] if 'sex' in row.keys() else None,
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
        
        # Obtener personId de la sesión o usar el proporcionado
        session_person_id = row['personId'] if 'personId' in row.keys() and row['personId'] else person_id
        
        # Obtener valores de ejercicios desde BD
        correctos = row['correct_exercise'] if 'correct_exercise' in row.keys() and row['correct_exercise'] else 0
        fallidos = row['failed_exercise'] if 'failed_exercise' in row.keys() and row['failed_exercise'] else 0
        
        return Sesion(
            sesion_id=row['sesionId'],
            person_id=session_person_id,
            nivel=nivel,
            fecha=fecha,
            numero_sesion=row['number'] if row['number'] else 1,
            ejercicios_completados=[],  # Vacío al cargar de BD (no necesario)
            observaciones=row['observation'] if row['observation'] else '',
            observaciones_terapeuta=row['observaciones_terapeuta'] if 'observaciones_terapeuta' in row.keys() else '',
            # NUEVO: Pasar valores de BD para que las propiedades los usen
            _ejercicios_correctos_bd=correctos,
            _ejercicios_fallidos_bd=fallidos
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
    
    # ========== OBSERVACIONES ==========

    def crear_observacion(self, person_id: int, observacion: str, terapeuta: str = None) -> int:
        """Crear nueva observación del terapeuta"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO observaciones (personId, observacion, terapeuta)
                VALUES (?, ?, ?)
            ''', (person_id, observacion, terapeuta))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"❌ Error al crear observación: {e}")
            return None

    def obtener_observaciones_persona(self, person_id: int) -> List[dict]:
        """Obtener observaciones de una persona"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM observaciones 
                WHERE personId = ?
                ORDER BY fecha DESC
            ''', (person_id,))
            rows = cursor.fetchall()
            
            observaciones = []
            for row in rows:
                observaciones.append({
                    'observacion_id': row['observacionId'],
                    'person_id': row['personId'],
                    'fecha': row['fecha'],
                    'observacion': row['observacion'],
                    'terapeuta': row['terapeuta']
                })
            
            return observaciones
        except Exception as e:
            print(f"❌ Error al obtener observaciones: {e}")
            return []

    def actualizar_observaciones_sesion(self, sesion_id: int, observaciones: str):
        """Actualizar observaciones del terapeuta en una sesión"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE sesion 
                SET observaciones_terapeuta = ?
                WHERE sesionId = ?
            ''', (observaciones, sesion_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error al actualizar observaciones: {e}")
            return False
