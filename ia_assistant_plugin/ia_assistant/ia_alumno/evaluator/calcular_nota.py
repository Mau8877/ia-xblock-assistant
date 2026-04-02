import json
from ..ia_alumno_client import evaluar_respuestas_batch

def calcular_nota_final(datos_alumno, unidad_json_str):
    """
    Orquestador principal.
    """
    try:
        unidad_data = json.loads(unidad_json_str)
    except:
        return {"resultado": "error", "mensaje": "Error de parseo en unidad."}

    res_quiz = datos_alumno.get('respuestas_quiz', {})
    res_abiertas = datos_alumno.get('respuestas_abiertas', [])
    res_codigo = datos_alumno.get('respuestas_codigo', []) # <-- Nuevo componente

    total_puntos = 0
    conteo = 0
    feedback_detallado = []
    lista_para_ia = []

    # 1. Quizzes (IMPORTANTE: Verifica que 'puntaje' venga en el JSON)
    if res_quiz and 'puntaje' in res_quiz:
        nota_q = float(res_quiz.get('puntaje', 0))
        total_puntos += nota_q
        conteo += 1
        feedback_detallado.append(f"Quiz: {round(nota_q, 2)}/100")

    # 2. Preparar Respuestas para IA
    # Unificamos para iterar
    respuestas_mixtas = res_abiertas + res_codigo
    
    for resp in respuestas_mixtas:
        # Buscamos el componente en el JSON original de la unidad
        comp_orig = next((c for c in unidad_data.get('componentes', []) if str(c.get('id')) == str(resp.get('id'))), None)
        
        texto_alumno = resp.get('texto', '').strip()
        
        if comp_orig:
            if texto_alumno:
                # Si hay texto, va a la IA
                lista_para_ia.append({
                    "id": resp.get('id'),
                    "enunciado": comp_orig.get('enunciado'),
                    "tipo": comp_orig.get('tipo'),
                    "respuesta": texto_alumno,
                    "lenguaje": comp_orig.get('lenguaje', 'python'),
                    "puntos_clave": comp_orig.get('puntos_clave', '')
                })
            else:
                # Si está vacío, sumamos 0 y contamos la evaluación
                total_puntos += 0
                conteo += 1
                feedback_detallado.append(f"Componente {resp.get('id')}: Sin respuesta (0/100)")

    # 3. Llamada a la IA
    if lista_para_ia:
        evaluaciones_ia = evaluar_respuestas_batch(lista_para_ia)
        if evaluaciones_ia and 'evaluaciones' in evaluaciones_ia:
            for eval_item in evaluaciones_ia['evaluaciones']:
                total_puntos += eval_item.get('nota', 0)
                conteo += 1
                feedback_detallado.append(f"Evaluación IA: {eval_item.get('feedback', '')} ({eval_item.get('nota', 0)}/100)")
        else:
            return {"resultado": "error", "mensaje": "La IA no pudo procesar la evaluación."}

    # 4. Verificación de Seguridad
    if conteo == 0:
        # Si llegamos aquí, es que el JS envió arrays vacíos []
        return {"resultado": "error", "mensaje": "No se detectaron respuestas para calificar."}

    return {
        "resultado": "ok",
        "nota": round(total_puntos / conteo, 2),
        "feedback": feedback_detallado
    }