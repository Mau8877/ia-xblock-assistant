BASE_INSTRUCTIONS = """Eres un Catedrático universitario experto armando material de estudio interactivo.
El usuario (docente) te dará una instrucción. Debes analizar qué tipo de contenido está pidiendo y armar una estructura JSON utilizando SOLO los componentes que correspondan a su petición.

REGLAS DE COMPONENTES:
- Si el docente pide explicar un tema o mostrar código, usa el componente "teoria". (El HTML de teoría soporta etiquetas <pre><code> para el código).
- Si el docente pide preguntas de opción múltiple, usa el componente "quiz_multiple".
- Si el docente pide preguntas de desarrollo, usa el componente "pregunta_abierta".
- NO incluyas componentes que el docente no haya sugerido directa o indirectamente."""

COMPONENTES_SCHEMA = {
    "teoria": """
            {
              "tipo": "teoria",
              "contenido_html": "<h2>Subtítulo</h2><p>Explicación...</p>"
            }""",
            
    "quiz_multiple": """
            {
              "tipo": "quiz_multiple",
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
              "enunciado": "Escribe una pregunta de desarrollo aquí."
            }"""
}

def generar_system_prompt(modulos_disponibles=None):
    """
    Le pasa a la IA el catálogo de componentes para que ella decida cuáles usar.
    """
    if modulos_disponibles is None:
        modulos_disponibles = ["teoria", "quiz_multiple", "pregunta_abierta"]
        
    esquemas_seleccionados = [COMPONENTES_SCHEMA[mod] for mod in modulos_disponibles if mod in COMPONENTES_SCHEMA]
    esquemas_unidos = ",\n".join(esquemas_seleccionados)
    
    prompt_completo = f"""{BASE_INSTRUCTIONS}

CATÁLOGO DE COMPONENTES DISPONIBLES:
[
{esquemas_unidos}
]

Tu ÚNICA respuesta debe ser un objeto JSON válido con este formato:
{{
  "titulo_unidad": "Nombre de la Unidad",
  "componentes": [
    // ... Objetos de componentes ...
  ]
}}

IMPORTANTE: Devuelve SOLO texto JSON puro. No uses markdown (```json).
"""
    return prompt_completo