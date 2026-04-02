import json
import os
import time
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Mantenemos la lista para failover
MODELOS_FALLBACK = [
    "qwen/qwen3.6-plus-preview:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen3.6-plus:free"
]

def evaluar_respuestas_batch(lista_tareas):
    """
    Envía todas las respuestas en un solo prompt con lógica de conmutación por error.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("Evaluador: API Key no encontrada.")
        return None

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    # 1. Construcción del Cuerpo del Mensaje
    prompt_tareas = ""
    for idx, tarea in enumerate(lista_tareas):
        tipo = tarea.get('tipo', 'abierta').upper()
        lang = f"({tarea.get('lenguaje', '')})" if tipo == 'CODIGO' else ""
        prompt_tareas += f"\n--- Tarea {idx} [{tipo} {lang}] ---\n"
        prompt_tareas += f"Enunciado: {tarea['enunciado']}\n"
        prompt_tareas += f"Puntos Clave: {tarea.get('puntos_clave', 'N/A')}\n"
        prompt_tareas += f"Respuesta Alumno: {tarea['respuesta']}\n"

    system_prompt = """
    Actúa como un Ingeniero de Software Senior y Arquitecto. Califica de 0 a 100.
    
    PARA CÓDIGO (Python, SQL, Delphi, C++, etc.):
    - Valora SINTAXIS y si la LÓGICA resuelve el enunciado.
    - Evalúa BUENAS PRÁCTICAS (indentación, nombres).
    - Sé estricto con Begin/End en Delphi/Pascal y con indentación en Python.

    PARA PREGUNTAS ABIERTAS:
    - Valora semántica y puntos clave.

    Responde ESTRICTAMENTE un JSON: 
    {"evaluaciones": [{"id": "id_del_componente", "nota": 80, "feedback": "..."}]}
    """

    # 2. Bucle de Failover entre modelos
    for modelo in MODELOS_FALLBACK:
        # Intentaremos 2 veces por cada modelo antes de saltar al siguiente (por si es un glitch temporal)
        for intento in range(2):
            try:
                logger.info(f"Evaluando con {modelo} (Intento {intento+1})...")
                
                res = client.chat.completions.create(
                    model=modelo,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt_tareas}
                    ],
                    response_format={ "type": "json_object" },
                    timeout=45 # Más tiempo para el alumno, la evaluación es pesada
                )
                
                contenido = res.choices[0].message.content
                return json.loads(contenido)

            except Exception as e:
                error_str = str(e)
                # Si es Rate Limit (429), esperamos un poco y reintentamos o saltamos
                if "429" in error_str:
                    logger.warning(f"Rate limit en {modelo}. Esperando...")
                    time.sleep(2)
                    continue 
                
                logger.error(f"Fallo con modelo {modelo}: {error_str}")
                break # Salta al siguiente modelo de la lista MODELOS_FALLBACK

    logger.critical("Todos los modelos de evaluación fallaron.")
    return None