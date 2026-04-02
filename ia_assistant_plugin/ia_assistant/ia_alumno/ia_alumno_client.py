import json
import os
import time
import logging
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Mantenemos la lista para failover - Priorizando estabilidad
MODELOS_FALLBACK = [
    "qwen/qwen3.6-plus-preview:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemini-2.0-flash-lite-preview-02-05:free"
]

def evaluar_respuestas_batch(lista_tareas):
    """
    Evalúa un lote de tareas con máxima resiliencia.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("Evaluador: API Key no encontrada en el entorno.")
        return None

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    # 1. Construcción del Prompt de Usuario
    prompt_tareas = ""
    for idx, tarea in enumerate(lista_tareas):
        tipo = tarea.get('tipo', 'abierta').upper()
        lang = f"({tarea.get('lenguaje', '')})" if tipo == 'CODIGO' else ""
        prompt_tareas += f"\n--- Tarea ID: {tarea.get('id')} [{tipo} {lang}] ---\n"
        prompt_tareas += f"Enunciado: {tarea['enunciado']}\n"
        prompt_tareas += f"Criterios/Puntos Clave: {tarea.get('puntos_clave', 'N/A')}\n"
        prompt_tareas += f"Respuesta del Estudiante: {tarea['respuesta']}\n"

    system_prompt = """
    Actúa como un Evaluador Académico Senior de Ingeniería de Sistemas. 
    Tu objetivo es calificar respuestas de estudiantes del 0 al 100.
    
    INSTRUCCIONES:
    1. Sé justo pero riguroso con la sintaxis en componentes de CÓDIGO.
    2. En PREGUNTAS ABIERTAS, busca la presencia de los 'Puntos Clave'.
    3. Tu respuesta debe ser exclusivamente un objeto JSON.
    4. USA LOS MISMOS 'id' que se te proporcionan en cada tarea.

    FORMATO DE RESPUESTA:
    {
      "evaluaciones": [
        {"id": "id_recibido", "nota": 0-100, "feedback": "Breve explicación técnica"}
      ]
    }
    """

    # 2. Bucle de Failover entre modelos
    for modelo in MODELOS_FALLBACK:
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
                    timeout=50 # Un poco más de tiempo para evaluaciones complejas
                )
                
                respuesta_raw = res.choices[0].message.content

                # --- LIMPIEZA Y VALIDACIÓN ---
                match = re.search(r'\{.*\}', respuesta_raw, re.DOTALL)
                
                if match:
                    respuesta_ia = match.group(0)
                    try:
                        data_eval = json.loads(respuesta_ia)
                        # Verificamos que tenga la estructura mínima requerida
                        if "evaluaciones" in data_eval:
                            logger.info(f"Evaluación exitosa con {modelo}")
                            return data_eval
                    except json.JSONDecodeError:
                        logger.warning(f"JSON incompleto de {modelo}. Intentando de nuevo...")
                        continue
                else:
                    logger.warning(f"No se detectó estructura JSON en la respuesta de {modelo}.")
                    continue

            except Exception as e:
                error_str = str(e)
                # Manejo de errores de red o cuotas
                if any(err in error_str for err in ["429", "provider", "timeout"]):
                    logger.warning(f"Fallo temporal en {modelo}: {error_str}. Reintentando...")
                    time.sleep(2)
                    continue 
                
                logger.error(f"Fallo crítico en {modelo}: {error_str}")
                break # Pasar al siguiente modelo de la lista

    logger.critical("Error: Todos los modelos del Fallback fallaron.")
    return None