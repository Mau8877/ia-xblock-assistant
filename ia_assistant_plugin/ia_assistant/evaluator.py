import json
import os
from openai import OpenAI
from dotenv import load_dotenv

def calificar_con_ia(enunciado, respuesta, puntos_clave):
    """
    Llama a Qwen para analizar semánticamente la respuesta del alumno.
    """
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        return {"nota": 0, "feedback": "Error: API Key no configurada."}

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1", 
        api_key=api_key
    )
    
    # Prompt de corrección pedagógica
    prompt = f"""
    Actúa como un profesor universitario. 
    Pregunta: {enunciado}
    Puntos clave esperados: {puntos_clave}
    Respuesta del alumno: {respuesta}

    Tu tarea es calificar la respuesta del 0 al 100 y dar un feedback constructivo.
    Responde ÚNICAMENTE un objeto JSON con este formato:
    {{
      "nota": numero,
      "feedback": "explicación breve"
    }}
    """
    
    try:
        res = client.chat.completions.create(
            model="qwen/qwen3.6-plus-preview:free",
            messages=[
                {"role": "system", "content": "Responde solo JSON puro, sin markdown."},
                {"role": "user", "content": prompt}
            ]
        )
        # Limpiamos posibles espacios o caracteres extra
        contenido = res.choices[0].message.content.strip()
        return json.loads(contenido)
    except Exception as e:
        return {"nota": 0, "feedback": f"Error en evaluación IA: {str(e)}"}


def calcular_nota_final(datos_alumno, unidad_json_str):
    """
    Función maestra que orquesta la calificación de todos los componentes.
    """
    res_quiz = datos_alumno.get('respuestas_quiz', {})
    res_abiertas = datos_alumno.get('respuestas_abiertas', [])
    
    try:
        unidad_data = json.loads(unidad_json_str)
    except:
        return {"resultado": "error", "mensaje": "Error al leer la unidad original."}

    total_puntos = 0
    conteo_evaluaciones = 0
    feedback_detallado = []

    # 1. Procesar Quiz (Si existe)
    if res_quiz:
        nota_q = res_quiz.get('puntaje', 0)
        total_puntos += nota_q
        conteo_evaluaciones += 1
        feedback_detallado.append(f"Quiz: {round(nota_q, 2)}/100")

    # 2. Procesar Respuestas Abiertas
    for resp in res_abiertas:
        # Buscamos el componente original para saber el enunciado y puntos clave
        comp_orig = next((c for c in unidad_data['componentes'] if c.get('id') == resp['id']), None)
        
        if comp_orig:
            # Si el alumno no escribió nada, no gastamos créditos de API
            if not resp['texto'].strip():
                eval_ia = {"nota": 0, "feedback": "No entregaste respuesta para esta pregunta."}
            else:
                eval_ia = calificar_con_ia(
                    comp_orig['enunciado'], 
                    resp['texto'], 
                    comp_orig.get('puntos_clave', 'Conceptos generales del tema')
                )
            
            total_puntos += eval_ia['nota']
            conteo_evaluaciones += 1
            feedback_detallado.append(f"Abierta ({comp_orig['enunciado'][:30]}...): {eval_ia['feedback']}")

    # 3. Cálculo Final
    if conteo_evaluaciones == 0:
        return {"resultado": "error", "mensaje": "No hay actividades evaluables."}

    nota_final = total_puntos / conteo_evaluaciones

    return {
        "resultado": "ok",
        "nota": round(nota_final, 2),
        "feedback": feedback_detallado
    }