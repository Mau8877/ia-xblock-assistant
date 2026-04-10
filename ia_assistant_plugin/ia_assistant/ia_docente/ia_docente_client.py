import os
import json
import time
import logging
import re  
from openai import OpenAI
from dotenv import load_dotenv
from .prompt_docente_builder import GENERAR_SYSTEM_PROMPT

logger = logging.getLogger(__name__)
load_dotenv()

# Lista de modelos IA
MODELOS_FALLBACK = [
    "nvidia/nemotron-3-super-120b-a12b:free",
    "minimax/minimax-m2.5:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "google/gemini-2.0-flash-lite-preview-02-05:free"
]

def generar_contenido_unidad(prompt_usuario):
    print("\n--- INICIANDO GENERACIÓN DE IA ---") # <-- DEBUG DIRECTO
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("ERROR: Falta API Key en el archivo .env")
        return {"resultado": "error", "mensaje": "Falta API Key."}

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    system_prompt = GENERAR_SYSTEM_PROMPT()

    # Intentamos cada modelo de la lista
    for modelo in MODELOS_FALLBACK:
        try:
            print(f">>> Intentando conectar con: {modelo}...") # <-- DEBUG DIRECTO
            logger.info(f"Intentando generar con modelo: {modelo}")
            
            completion = client.chat.completions.create(
                model=modelo,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt_usuario}
                ],
                response_format={ "type": "json_object" },
                timeout=6  # <-- ¡CORREGIDO A 8 SEGUNDOS!
            )

            # 🛡️ BLINDAJE 1: Prevenir el error "'NoneType' object is not subscriptable"
            if not completion or not hasattr(completion, 'choices') or not completion.choices:
                print(f"XXX Fallo vacío con {modelo}") # <-- DEBUG DIRECTO
                logger.warning(f"Fallo de API con {modelo}: La respuesta vino vacía (sin choices).")
                time.sleep(1)
                continue
                
            respuesta_raw = completion.choices[0].message.content
            
            # 🛡️ BLINDAJE 2: Prevenir que el contenido sea nulo
            if not respuesta_raw:
                print(f"XXX Fallo lógico (texto nulo) con {modelo}") # <-- DEBUG DIRECTO
                logger.warning(f"Fallo lógico con {modelo}: El modelo respondió con texto vacío.")
                continue
            
            match = re.search(r'\{.*\}', respuesta_raw, re.DOTALL)
            
            if match:
                respuesta_ia = match.group(0)
            else:
                print(f"XXX No se encontró JSON en {modelo}") # <-- DEBUG DIRECTO
                logger.warning(f"Modelo {modelo} no devolvió un JSON válido. Reintentando...")
                continue

            # Validar JSON antes de darlo por bueno
            json.loads(respuesta_ia)
            
            print(f"✅ ¡ÉXITO TOTAL con {modelo}!") # <-- DEBUG DIRECTO
            logger.info(f"Éxito con modelo: {modelo}")
            return {
                "resultado": "ok", 
                "json_unidad": respuesta_ia
            }

        except json.JSONDecodeError:
            print(f"XXX JSON Corrupto devuelto por {modelo}") # <-- DEBUG DIRECTO
            logger.warning(f"Error de formato con {modelo}: El JSON devuelto estaba corrupto.")
            continue 

        except Exception as e:
            error_msg = str(e)
            print(f"XXX Error de API/Red con {modelo}: {error_msg[:100]}") # <-- DEBUG DIRECTO
            logger.warning(f"Fallo general/API con {modelo}: {error_msg}. Saltando al siguiente...")
            time.sleep(1)
            continue 

    print("❌ TODOS LOS MODELOS FALLARON.") # <-- DEBUG DIRECTO
    return {
        "resultado": "error", 
        "mensaje": "Todos los modelos gratuitos están saturados en este momento. Reintenta en un minuto."
    }