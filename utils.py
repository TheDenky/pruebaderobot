"""
UTILS - Funciones de utilidad
"""
import re
from config import Config


def extraer_numero(texto: str) -> int:
    """Extrae número de un texto"""
    # Buscar dígitos
    numeros = re.findall(r'\d+', texto)
    if numeros:
        return int(numeros[0])
    
    # Mapeo de palabras a números
    palabras_numeros = {
        'uno': 1, 'dos': 2, 'tres': 3, 'cuatro': 4, 'cinco': 5,
        'seis': 6, 'siete': 7, 'ocho': 8, 'nueve': 9, 'diez': 10,
        'once': 11, 'doce': 12, 'trece': 13, 'catorce': 14, 'quince': 15,
        'dieciséis': 16, 'diecisiete': 17, 'dieciocho': 18,
        'dieciseis': 16
    }
    
    texto_lower = texto.lower()
    for palabra, numero in palabras_numeros.items():
        if palabra in texto_lower:
            return numero
    
    raise ValueError("No se pudo extraer número")


def mensaje_positivo_aleatorio() -> str:
    """Retorna un mensaje positivo aleatorio"""
    import random
    return random.choice(Config.MENSAJES_POSITIVOS)


def mensaje_animo_aleatorio() -> str:
    """Retorna un mensaje de ánimo aleatorio"""
    import random
    return random.choice(Config.MENSAJES_ANIMO)


def imprimir_encabezado(texto: str, ancho: int = 70):
    """Imprime un encabezado bonito"""
    print("\n" + "="*ancho)
    espacios = (ancho - len(texto)) // 2
    print(" "*espacios + texto)
    print("="*ancho + "\n")


def imprimir_seccion(texto: str, ancho: int = 70):
    """Imprime una sección"""
    print("\n┌" + "─"*(ancho-2) + "┐")
    espacios = (ancho - len(texto) - 2) // 2
    print("│" + " "*espacios + texto + " "*espacios + "│")
    print("└" + "─"*(ancho-2) + "┘\n")