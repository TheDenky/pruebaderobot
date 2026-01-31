"""
MODELOS - Entidades del dominio
Todas las clases de datos en un solo archivo
ACTUALIZADO: Con DNI, sexo y personId en sesiones
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class NivelTerapia(Enum):
    """Niveles de terapia según RF1.3"""
    INICIAL = 1
    BASICO = 2
    INTERMEDIO = 3
    AVANZADO = 4


@dataclass
class Persona:
    """Entidad que representa al niño en terapia"""
    name: str
    age: int
    person_id: Optional[int] = None
    apellido: Optional[str] = None
    dni: Optional[str] = None  
    sex: Optional[str] = None  # 'M' o 'F'
    nivel_actual: NivelTerapia = NivelTerapia.INICIAL
    fecha_registro: datetime = field(default_factory=datetime.now)
    
    def puede_subir_nivel(self, tasa_exito: float) -> bool:
        """Determina si puede subir de nivel - RF4.3"""
        return tasa_exito >= 0.80
    
    def validar(self) -> tuple[bool, str]:
        """Validar datos de la persona"""
        if not self.name or len(self.name) < 2:
            return False, "Nombre inválido"
        if self.age < 1 or self.age > 18:
            return False, "Edad debe estar entre 1 y 18 años"
        if self.sex and self.sex not in ['M', 'F']:
            return False, "Sexo debe ser 'M' o 'F'"
        if self.dni and len(self.dni) < 8:
            return False, "DNI inválido"
        return True, ""


@dataclass
class Ejercicio:
    """Entidad que representa un ejercicio terapéutico"""
    exercise_id: int
    word: str
    nivel: NivelTerapia = NivelTerapia.INICIAL
    tipo: str = 'palabra'
    dificultad: int = 1
    apoyo_visual: Optional[str] = None
    
    def requiere_apoyo_visual(self) -> bool:
        """Determina si necesita apoyo visual"""
        return self.dificultad >= 5


@dataclass
class ResultadoEjercicio:
    """Resultado de un ejercicio individual"""
    ejercicio_id: int
    respuesta: str
    correcto: bool
    tiempo_respuesta: float
    intentos: int = 1
    audio_path: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Sesion:
    """Entidad que representa una sesión completa"""
    person_id: int  # ACTUALIZADO: Ahora es requerido
    nivel: NivelTerapia
    fecha: datetime
    ejercicios_completados: List[ResultadoEjercicio]
    sesion_id: Optional[int] = None
    numero_sesion: int = 1  # NUEVO: Número de sesión del usuario
    observaciones: str = ""
    observaciones_terapeuta: str = ""  # NUEVO: Observaciones del terapeuta
    
    @property
    def total_ejercicios(self) -> int:
        return len(self.ejercicios_completados)
    
    @property
    def ejercicios_correctos(self) -> int:
        return sum(1 for e in self.ejercicios_completados if e.correcto)
    
    @property
    def ejercicios_fallidos(self) -> int:
        return self.total_ejercicios - self.ejercicios_correctos
    
    @property
    def tasa_exito(self) -> float:
        if self.total_ejercicios == 0:
            return 0.0
        return self.ejercicios_correctos / self.total_ejercicios
    
    def fue_exitosa(self) -> bool:
        """Determina si la sesión fue exitosa"""
        return self.tasa_exito >= 0.70


@dataclass
class Observacion:
    """Observación del terapeuta sobre un paciente"""
    observacion_id: Optional[int]
    person_id: int
    fecha: datetime
    observacion: str
    terapeuta: Optional[str] = None