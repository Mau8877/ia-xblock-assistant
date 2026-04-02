import os
import json
import time
import logging
from openai import OpenAI
from dotenv import load_dotenv
from .prompt_docente_builder import generar_system_prompt

logger = logging.getLogger(__name__)
load_dotenv()

# Lista de modelos gratuitos en orden de prioridad
MODELOS_FALLBACK = [
    "qwen/qwen3.6-plus-preview:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen3.6-plus:free"
]

def generar_contenido_unidad(prompt_usuario):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return {"resultado": "error", "mensaje": "Falta API Key."}

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    system_prompt = generar_system_prompt()

    # Intentamos cada modelo de la lista
    for modelo in MODELOS_FALLBACK:
        try:
            logger.info(f"Intentando generar con modelo: {modelo}")
            
            completion = client.chat.completions.create(
                model=modelo,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt_usuario}
                ],
                response_format={ "type": "json_object" },
                timeout=30 # Evitamos que un modelo lento trabe todo
            )

            respuesta_ia = completion.choices[0].message.content
            # Validar JSON antes de darlo por bueno
            json.loads(respuesta_ia)
            
            logger.info(f"Éxito con modelo: {modelo}")
            return {
                "resultado": "ok", 
                "json_unidad": respuesta_ia
            }

        except Exception as e:
            error_msg = str(e)
            # Si es un error de Rate Limit (429) o de sobrecarga del proveedor (503/500)
            if "429" in error_msg or "provider" in error_msg.lower():
                logger.warning(f"Modelo {modelo} saturado/fallido. Saltando al siguiente...")
                continue # Salta al siguiente modelo en MODELOS_FALLBACK
            else:
                # Si es un error de otro tipo (ej: API Key inválida), mejor parar
                logger.error(f"Error crítico con {modelo}: {error_msg}")
                break 

    return {
        "resultado": "error", 
        "mensaje": "Todos los modelos gratuitos están saturados en este momento. Reintenta en un minuto."
    }