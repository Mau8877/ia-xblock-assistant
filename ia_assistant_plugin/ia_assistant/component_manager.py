import json
from .utils.load_resource import load_resource

def renderizar_unidad(json_str):
    """
    Toma el JSON de la IA y devuelve el HTML ensamblado y los recursos.
    """
    try:
        if not json_str or json_str == "{}" or json_str == "":
            return "", {"titulo": "Unidad Vacía", "css": set(), "js": set()}
            
        datos = json.loads(json_str)
    except Exception as e:
        return f"<p>Error al parsear unidad: {str(e)}</p>", {"titulo": "Error", "css": set(), "js": set()}

    html_final = ""
    # Inicializamos como SETS para evitar que se cargue el mismo CSS 5 veces 
    # si hay 5 componentes del mismo tipo.
    recursos = {
        "titulo": datos.get("titulo_unidad", "Unidad Interactiva"),
        "css": set(),
        "js": set()
    }

    componentes = datos.get("componentes", [])

    for idx, comp in enumerate(componentes):
        tipo = comp.get("tipo")
        
        if tipo == "teoria":
            template = load_resource("static/components/teoria/teoria.html")
            html_final += template.format(contenido_html=comp.get("contenido_html", ""))
            recursos["css"].add("static/components/teoria/teoria.css")

        elif tipo == "quiz_multiple":
            preguntas_html = ""
            for i, p in enumerate(comp.get("preguntas", [])):
                preguntas_html += f'<div class="ia-pregunta" data-correcta="{p.get("correcta")}">'
                preguntas_html += f'<h4>{i+1}. {p.get("enunciado")}</h4>'
                for j, opt in enumerate(p.get("opciones", [])):
                    preguntas_html += f'<label class="ia-opcion"><input type="radio" name="q_{idx}_{i}" value="{j}"> {opt}</label>'
                preguntas_html += '</div>'
            
            template = load_resource("static/components/quiz_multiple/quiz.html")
            html_final += template.format(preguntas_html=preguntas_html)
            recursos["css"].add("static/components/quiz_multiple/quiz.css")
            recursos["js"].add("static/components/quiz_multiple/quiz.js")

        elif tipo == "pregunta_abierta":
            template = load_resource("static/components/pregunta_abierta/pregunta_abierta.html")
            html_final += template.format(
                comp_id=comp.get("id", f"ab_{idx}"), 
                enunciado=comp.get("enunciado", "")
            )
            recursos["css"].add("static/components/pregunta_abierta/pregunta_abierta.css")
            recursos["js"].add("static/components/pregunta_abierta/pregunta_abierta.js")

        elif tipo == "codigo":
            specs = comp.get('especificaciones', {})
            
            codigo_limpio = comp.get('codigo_inicial', '').replace('\\n', '\n')

            html_comp = load_resource("static/components/codigo/codigo.html").format(
                id=comp.get('id', f'cod_{idx}'),
                enunciado=comp.get('enunciado', ''),
                lenguaje=comp.get('lenguaje', 'PYTHON').upper(),
                codigo_inicial=codigo_limpio,
                entrada=specs.get('entrada_esperada', 'N/A'),
                salida=specs.get('salida_esperada', 'N/A')
            )
            html_final += html_comp
            recursos["css"].add("static/components/codigo/codigo.css")
            recursos["js"].add("static/components/codigo/codigo.js")

    return html_final, recursos