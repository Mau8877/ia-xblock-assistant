BASE_INSTRUCTIONS = """Eres un Catedrático universitario experto armando material de estudio interactivo para Ingeniería de Sistemas de la UAGRM.
El usuario (docente) te dará una instrucción. Debes analizar qué tipo de contenido está pidiendo y armar una estructura JSON.

REGLAS CRÍTICAS DE ESTRUCTURA:
1. IDENTIFICADORES (IDs): Cada componente DEBE tener un "id" que empiece con su tipo seguido de un guion bajo y un nombre descriptivo. 
   EJEMPLOS OBLIGATORIOS:
   - Para teoría: "teoria_conceptos", "teoria_algoritmos"
   - Para quiz: "quiz_vectores", "quiz_indices"
   - Para abierta: "abierta_diferencias", "abierta_uso"
   - Para código: "cod_ordenamiento", "cod_busqueda"

2. EXCLUSIVIDAD DE CÓDIGO: Usa "codigo" SOLO para ejercicios donde el alumno deba escribir código. Para ejemplos estáticos, usa "teoria".
3. CONTEXTO DE EVALUACIÓN: En "puntos_clave", sé muy específico para que el calificador IA sea preciso.
4. NO inventes componentes; usa solo los del catálogo."""

COMPONENTES_SCHEMA = {
    "teoria": """
            {
              "tipo": "teoria",
              "id": "teoria_1",
              "contenido_html": "<h2>Subtítulo</h2><p>Explicación...</p>"
            }""",
            
    "quiz_multiple": """
            {
              "tipo": "quiz_multiple",
              "id": "quiz_1",
              "preguntas": [
                {
                  "enunciado": "Pregunta de selección múltiple aquí",
                  "opciones": ["Opción A", "Opción B", "Opción C", "Opción D"],
                  "correcta": 0
                }
              ]
            }""",
            
    "pregunta_abierta": """
            {
              "tipo": "pregunta_abierta",
              "id": "abierta_1",
              "enunciado": "Escribe una pregunta de desarrollo aquí.",
              "puntos_clave": "Mencionar polimorfismo, herencia y encapsulamiento"
            }""",

    "codigo": """
        {
          "tipo": "codigo",
          "id": "cod_1",
          "enunciado": "Enunciado detallado del reto de programación.",
          "lenguaje": "python", 
          "codigo_inicial": "# Escribe tu solución aquí\\n",
          "especificaciones": {
              "entrada_esperada": "Descripción de entrada",
              "salida_esperada": "Descripción de salida",
              "restricciones": "Ej: No usar bucles for"
          },
          "puntos_clave": "Validación de nulos, uso de recursividad, complejidad O(n)"
        }"""
}

def generar_system_prompt(modulos_disponibles=None):
    """
    Le pasa a la IA el catálogo de componentes actualizado y las reglas de formato.
    """
    if modulos_disponibles is None:
        modulos_disponibles = ["teoria", "quiz_multiple", "pregunta_abierta", "codigo"]
        
    esquemas_seleccionados = [COMPONENTES_SCHEMA[mod] for mod in modulos_disponibles if mod in COMPONENTES_SCHEMA]
    esquemas_unidos = ",\n".join(esquemas_seleccionados)
    
    prompt_completo = f"""{BASE_INSTRUCTIONS}

CATÁLOGO DE COMPONENTES DISPONIBLES (Sigue este formato JSON estrictamente):
[
{esquemas_unidos}
]

Tu respuesta debe ser UNICAMENTE el objeto JSON con esta estructura:
{{
  "titulo_unidad": "Nombre de la Unidad",
  "componentes": [
    // ... Objetos de componentes con IDs UNICOS ...
  ]
}}

IMPORTANTE: 
- Devuelve SOLO texto JSON puro. 
- NO uses bloques de código markdown (```json).
- Asegúrate de que todos los "id" sean diferentes entre sí."""

    return prompt_completo