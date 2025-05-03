"""
Módulo bot para generar y enviar respuestas automáticas a Google Forms.
Utiliza datos aleatorios con sesgos definidos para simular respuestas realistas.

NOTA IMPORTANTE:
    Este es el módulo que debes ajustar en función de:
      - La estructura y URL del formulario (entry IDs y formResponse URL).
      - Las preguntas del formulario: modify generate_survey_data() para 
        añadir, eliminar o cambiar opciones y pesos.
      - Cualquier nueva lógica de generación (enteros, decimales, sesgos).

    Cada vez que cambien las preguntas o quieras ajustar probabilidades,
    es aquí donde debes actualizar:
      1. La constante URL.
      2. El diccionario de opciones y probabilidades en generate_survey_data().
      3. Las funciones auxiliares de generación (si necesitas nuevos patrones).
"""
import requests
import random
import time

# URL del formulario (debe terminar en 'formResponse')
URL = (
    "https://docs.google.com/forms/d/e/"
    "1FAIpQLScv3Za4RNUn9QMNVDmgTdp3AuPTjyW0iV5BNjIQ2v93_zl3NA/"
    "formResponse"
)


def weighted_choice(choices):
    """
    Selecciona un elemento de 'choices' basado en sus pesos.

    choices: lista de tuplas (opción, peso).
    Devuelve: la opción seleccionada.
    """
    total = sum(weight for option, weight in choices)
    r = random.uniform(0, total)
    upto = 0
    for option, weight in choices:
        if upto + weight >= r:
            return option
        upto += weight


def generate_integer_with_bias(min_val, max_val, primary_vals, primary_weight, secondary_weight):
    """
    Genera un número entero entre min_val y max_val.
    - primary_vals: lista de valores con mayor peso.
    - primary_weight: peso asignado a valores primarios.
    - secondary_weight: peso para otros valores.

    Devuelve: entero seleccionado.
    """
    choices = [
        (val, primary_weight if val in primary_vals else secondary_weight)
        for val in range(min_val, max_val + 1)
    ]
    return weighted_choice(choices)


def generate_decimal_with_bias(min_val, max_val, primary_vals, primary_weight, secondary_weight):
    """
    Genera un número decimal (dos decimales) entre min_val y max_val.
    - primary_vals: lista de valores enteros con mayor peso.
    - primary_weight: peso asignado a valores primarios.
    - secondary_weight: peso para otros decimales.

    Devuelve: decimal seleccionado.
    """
    choices = []
    for x in range(int(min_val), int(max_val) + 1):
        for y in range(0, 100):  # decimales .00 a .99
            val = round(x + y / 100, 2)
            weight = primary_weight if x in primary_vals and y == 0 else secondary_weight
            choices.append((val, weight))
    return weighted_choice(choices)


def generate_multiple_of_5_or_10(min_val, max_val, primary_vals, primary_weight, secondary_weight):
    """
    Genera un múltiplo de 5 entre min_val y max_val.
    Da preferencia a múltiplos de 10 con pesos primarios si aplican.

    Devuelve: múltiplo seleccionado.
    """
    choices = []
    for val in range(min_val, max_val + 1):
        if val % 10 == 0:
            weight = primary_weight if val in primary_vals else secondary_weight
            choices.append((val, weight))
        elif val % 5 == 0:
            choices.append((val, secondary_weight))
    return weighted_choice(choices)


def generate_survey_data():
    """
    Construye un diccionario con respuestas simuladas para cada campo del formulario.
    Los valores se generan según distribuciones definidas.

    Devuelve: dict con clave 'entry.X' y valor generado.
    """
    # Opciones y probabilidades para cada pregunta
    study_area_choices = [
        ("Ingeniería", 0.56), ("Ciencias de la Salud", 0.08),
        ("Ciencias Sociales y Humanidades", 0.04),
        ("Ciencias Económicas y Administrativas", 0.18), ("Otra", 0.14)
    ]
    ai_usage_frequency_choices = [
        ("Siempre", 0.1), ("Regularmente", 0.42),
        ("Algunas veces", 0.34), ("Muy raro", 0.1), ("Nunca", 0.04)
    ]
    ai_knowledge_choices = [
        ("Muy alto", 0.04), ("Alto", 0.14), ("Moderado", 0.68),
        ("Bajo", 0.1), ("Muy bajo", 0.04)
    ]
    ai_tool_choices = [
        ("Asistentes virtuales (ChatGPT, Meta AI)", 0.79),
        ("Plataformas de aprendizaje adaptativo (Duolingo, Coursera)", 0.04),
        ("Herramientas de productividad (Grammarly, Copilot)", 0.01),
        ("Generación de contenidos (DALL-E, Canva)", 0.08),
        ("Otra", 0.08)
    ]
    num_of_tools_choices = [(str(i), p) for i, p in [(1,0.22),(2,0.59),(3,0.1),(4,0.08),(5,0.01)]]
    current_courses_choices = [(str(i), p) for i, p in [(4,0.16),(5,0.22),(6,0.32),(7,0.18),(8,0.12)]]
    satisfaction_choices = [
        ("Muy satisfecho", 0.18), ("Satisfecho", 0.36), ("Neutral", 0.4),
        ("Insatisfecho", 0.02), ("Muy insatisfecho", 0.04)
    ]

    # Ensamblaje de datos con distribuciones definidas
    data = {
        "entry.6101266": weighted_choice(study_area_choices),
        "entry.1224679196": weighted_choice(ai_usage_frequency_choices),
        "entry.708996618": weighted_choice(ai_knowledge_choices),
        "entry.292856958": weighted_choice(ai_tool_choices),
        "entry.223930022": weighted_choice(num_of_tools_choices),
        "entry.2058855424": generate_integer_with_bias(
            1, 24, list(range(1, 13)), primary_weight=0.6, secondary_weight=0.2
        ),
        "entry.1885909055": generate_multiple_of_5_or_10(
            5, 400, [15, 30, 90, 120], primary_weight=0.4, secondary_weight=0.2
        ),
        "entry.1720291759": weighted_choice(current_courses_choices),
        "entry.704058276": weighted_choice([
            (i, 0.4) for i in (16, 17)
        ] + [
            (i, 0.1) for i in (13, 14, 15)
        ] + [
            (round(i + y/100, 2), 0.05)
            for i in (16,) for y in range(0,100)
        ] + [
            (round(i + y/100, 2), 0.02)
            for i in (13,14,15) for y in range(0,100)
        ]),
        "entry.1159776684": weighted_choice(satisfaction_choices)
    }
    print(data, flush=True)
    return data


def submit(url, data):
    """
    Envía el diccionario 'data' al formulario indicado por 'url'.

    Devuelve: True si el envío fue exitoso, False en caso contrario.
    """
    try:
        res = requests.post(url, data=data, timeout=5)
        if res.status_code != 200:
            raise Exception(f"Error al enviar formulario: {res.status_code}")
        return True
    except Exception as e:
        print("Error de envío:", e)
        return False


if __name__ == "__main__":
    """
    Punto de entrada: ejecuta el envío repetido de respuestas simuladas.
    """
    print("Iniciando bot de encuestas...", flush=True)
    for _ in range(334):
        submit(URL, generate_survey_data())
        time.sleep(random.uniform(2, 5))  # Espera aleatoria entre envíos
