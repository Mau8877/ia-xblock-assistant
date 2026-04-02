import json
import logging
from ..ia_alumno_client import evaluar_respuestas_batch

logger = logging.getLogger(__name__)

def calcular_nota_final(datos_alumno, unidad_json_str):
    """
    Orquestador principal de calificación con validación robusta.
    """
    try:
        if not unidad_json_str:
            return {"resultado": "error", "mensaje": "No hay contenido en la unidad para calificar."}
        unidad_data = json.loads(unidad_json_str)
    except Exception as e:
        logger.error(f"Error parseando unidad_json_str: {str(e)}")
        return {"resultado": "error", "mensaje": "Error crítico: El formato de la unidad es inválido."}

    # Obtenemos las listas de componentes de forma segura
    componentes_unidad = unidad_data.get('componentes', [])
    
    res_quiz = datos_alumno.get('respuestas_quiz', {})
    res_abiertas = datos_alumno.get('respuestas_abiertas', [])
    res_codigo = datos_alumno.get('respuestas_codigo', [])

    total_puntos = 0
    conteo = 0
    feedback_detallado = []
    lista_para_ia = []

    # 1. Quizzes (Cálculo determinístico)
    if res_quiz and 'puntaje' in res_quiz:
        try:
            nota_q = float(res_quiz.get('puntaje', 0))
            total_puntos += nota_q
            conteo += 1
            feedback_detallado.append(f"Quiz: {round(nota_q, 2)}/100")
        except (ValueError, TypeError):
            logger.warning("Puntaje de quiz no es un número válido.")

    # 2. Preparar Respuestas para IA (Unificado)
    respuestas_mixtas = res_abiertas + res_codigo
    
    for resp in respuestas_mixtas:
        resp_id = str(resp.get('id'))
        
        # Búsqueda defensiva del componente original
        comp_orig = next((c for c in componentes_unidad if str(c.get('id')) == resp_id), None)
        
        # IMPORTANTE: Si no lo encuentra por 'id', intentamos por el id_unico generado en v0.1.0
        # Esto es un fallback por si el JSON guardado usa el índice como ID
        if not comp_orig:
             # Buscamos si algún componente coincide con la lógica de id_unico {tipo}_{idx}
             # Esto asume que el frontend envió el ID del DOM
             pass 

        texto_alumno = str(resp.get('texto', '')).strip()
        
        if comp_orig:
            if texto_alumno:
                # Empaquetamos todo lo que la IA necesita para juzgar
                lista_para_ia.append({
                    "id": resp_id,
                    "enunciado": comp_orig.get('enunciado', 'Sin enunciado'),
                    "tipo": comp_orig.get('tipo', 'abierta'),
                    "respuesta": texto_alumno,
                    "lenguaje": comp_orig.get('lenguaje', 'N/A'),
                    "puntos_clave": comp_orig.get('puntos_clave', 'Evaluar coherencia general')
                })
            else:
                # Penalización por respuesta vacía
                total_puntos += 0
                conteo += 1
                feedback_detallado.append(f"Componente {resp_id}: Sin respuesta (0/100)")
        else:
            logger.error(f"No se encontró el componente original para el ID: {resp_id}")

    # 3. Llamada a la IA (Solo si hay contenido que evaluar)
    if lista_para_ia:
        cant_tareas = len(lista_para_ia)
        evaluaciones_ia = evaluar_respuestas_batch(lista_para_ia)
        
        if evaluaciones_ia and 'evaluaciones' in evaluaciones_ia:
            items_evaluados = evaluaciones_ia['evaluaciones']
            
            for eval_item in items_evaluados:
                nota_item = eval_item.get('nota', 0)
                total_puntos += nota_item
                conteo += 1
                feedback_detallado.append(
                    f"Evaluación IA: {eval_item.get('feedback', 'Sin feedback')} ({nota_item}/100)"
                )
            
            # Validación de lógica: ¿La IA evaluó todo lo que enviamos?
            if len(items_evaluados) < cant_tareas:
                logger.warning("La IA devolvió menos evaluaciones de las solicitadas.")
        else:
            return {"resultado": "error", "mensaje": "La IA de evaluación no respondió correctamente."}

    # 4. Verificación final
    if conteo == 0:
        return {"resultado": "error", "mensaje": "No se encontraron actividades completadas para calificar."}

    return {
        "resultado": "ok",
        "nota": round(total_puntos / conteo, 2),
        "feedback": feedback_detallado
    }