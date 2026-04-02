import json
from .utils.load_resource import load_resource

def renderizar_unidad(json_str):
    """
    Toma el JSON de la IA y devuelve el HTML ensamblado con wrappers para las pestañas.
    """
    try:
        if not json_str or json_str == "{}" or json_str == "":
            return "", {"titulo": "Unidad Vacía", "css": set(), "js": set()}
            
        datos = json.loads(json_str)
    except Exception as e:
        return f"<p>Error al parsear unidad: {str(e)}</p>", {"titulo": "Error", "css": set(), "js": set()}

    html_final = ""
    recursos = {
        "titulo": datos.get("titulo_unidad", "Unidad Interactiva"),
        "css": set(),
        "js": set()
    }

    componentes = datos.get("componentes", [])

    for idx, comp in enumerate(componentes):
        tipo = comp.get("tipo")
        # Usamos el ID de la IA si existe, sino generamos uno por índice
        comp_id = comp.get("id", f"{tipo}_{idx}")

        # --- SECCIÓN: TEORÍA ---
        if tipo == "teoria":
            template = load_resource("static/components/teoria/teoria.html")
            contenido = template.format(contenido_html=comp.get("contenido_html", ""))
            # El wrapper 'ia-comp-teoria' permite al JS moverlo a la pestaña 1
            html_final += f'<div class="ia-comp-teoria" id="{comp_id}">{contenido}</div>'
            recursos["css"].add("static/components/teoria/teoria.css")

        # --- SECCIÓN: QUIZ MULTIPLE ---
        elif tipo == "quiz_multiple":
            preguntas_html = ""
            for i, p in enumerate(comp.get("preguntas", [])):
                preguntas_html += f'<div class="ia-pregunta" data-correcta="{p.get("correcta")}">'
                preguntas_html += f'<h4>{i+1}. {p.get("enunciado")}</h4>'
                for j, opt in enumerate(p.get("opciones", [])):
                    # El name incluye el comp_id para que los radios sean independientes
                    preguntas_html += f'<label class="ia-opcion"><input type="radio" name="q_{comp_id}_{i}" value="{j}"> {opt}</label>'
                preguntas_html += '</div>'
            
            template = load_resource("static/components/quiz_multiple/quiz.html")
            contenido = template.format(preguntas_html=preguntas_html)
            html_final += f'<div class="ia-comp-quiz" id="{comp_id}">{contenido}</div>'
            recursos["css"].add("static/components/quiz_multiple/quiz.css")
            recursos["js"].add("static/components/quiz_multiple/quiz.js")

        # --- SECCIÓN: PREGUNTA ABIERTA ---
        elif tipo == "pregunta_abierta":
            template = load_resource("static/components/pregunta_abierta/pregunta_abierta.html")
            contenido = template.format(
                comp_id=comp_id, 
                enunciado=comp.get("enunciado", "")
            )
            # Se clasifican como abiertas para que el JS las mande a la pestaña de ejercicios
            html_final += f'<div class="ia-comp-abierta" id="{comp_id}">{contenido}</div>'
            recursos["css"].add("static/components/pregunta_abierta/pregunta_abierta.css")
            recursos["js"].add("static/components/pregunta_abierta/pregunta_abierta.js")

        # --- SECCIÓN: LABORATORIO DE CÓDIGO ---
        elif tipo == "codigo":
            specs = comp.get('especificaciones', {})
            codigo_limpio = comp.get('codigo_inicial', '').replace('\\n', '\n')
            
            # Calculamos el tamaño del código base (ej. el "def...pass")
            base_len = len(codigo_limpio)

            template = load_resource("static/components/codigo/codigo.html")
            contenido = template.format(
                id=comp_id,
                enunciado=comp.get('enunciado', ''),
                lenguaje=comp.get('lenguaje', 'PYTHON').upper(),
                codigo_inicial=codigo_limpio,
                entrada=specs.get('entrada_esperada', 'N/A'),
                salida=specs.get('salida_esperada', 'N/A')
            )
            # AGREGAMOS data-base-len para que el JS sea inteligente
            html_final += f'<div class="ia-comp-codigo" id="{comp_id}" data-base-len="{base_len}">{contenido}</div>'
            recursos["css"].add("static/components/codigo/codigo.css")
            recursos["js"].add("static/components/codigo/codigo.js")

    return html_final, recursos