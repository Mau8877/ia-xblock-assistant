import os
import json
import logging
from dotenv import load_dotenv
from openai import OpenAI

from xblock.core import XBlock
from xblock.fields import Scope, String
from xblock.fragment import Fragment

# Importaciones locales
from .utils.load_resource import load_resource
from .prompt_builder import generar_system_prompt 
from .component_manager import renderizar_unidad
from .evaluator import calcular_nota_final

# Configuración de logs para ver en la consola de Django
logger = logging.getLogger(__name__)

class IAAssistantXBlock(XBlock):
    
    display_name = String(
        display_name="Nombre a mostrar",
        default="Asistente IA UAGRM",
        scope=Scope.settings,
        help="Nombre del bloque en la plataforma"
    )

    prompt_docente = String(
        default="Genera la unidad sobre...",
        scope=Scope.settings,
        help="El texto que el docente le envía a la IA."
    )

    unidad_json = String(
        default="",
        scope=Scope.content,
        help="JSON estructurado de la unidad."
    )

    def studio_view(self, context=None):
        """ Vista de configuración para el docente. """
        html_str = load_resource("static/core/studio/studio.html")
        # Aseguramos que el prompt actual se cargue en el textarea
        html_formateado = html_str.format(prompt_docente=self.prompt_docente)
        
        frag = Fragment(html_formateado)
        frag.add_css(load_resource("static/core/studio/studio.css"))
        frag.add_javascript(load_resource("static/core/studio/studio.js"))
        frag.initialize_js('StudioDocenteInit')
        return frag

    @XBlock.json_handler
    def guardar_prompt(self, data, suffix=''):
        """ Llama a Qwen y guarda el resultado en unidad_json. """
        nuevo_prompt = data.get('prompt', '')
        self.prompt_docente = nuevo_prompt 

        # 1. Cargar API Key
        load_dotenv()
        api_key = os.getenv("OPENROUTER_API_KEY")
        
        if not api_key:
            logger.error("IA Assistant: No se encontró OPENROUTER_API_KEY en .env")
            return {"resultado": "error", "mensaje": "Falta la API Key en el servidor."}

        # 2. Configurar Cliente
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

        system_prompt = generar_system_prompt()

        try:
            logger.info(f"IA Assistant: Llamando a Qwen con prompt: {nuevo_prompt[:50]}...")
            
            completion = client.chat.completions.create(
                model="qwen/qwen3.6-plus-preview:free",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": nuevo_prompt}
                ]
            )

            respuesta_ia = completion.choices[0].message.content
            
            # Limpieza básica por si la IA ignora las instrucciones y pone markdown
            respuesta_ia = respuesta_ia.replace("```json", "").replace("```", "").strip()
            
            # Intentar parsear para validar que es JSON real antes de guardar
            json.loads(respuesta_ia)
            
            self.unidad_json = respuesta_ia
            logger.info("IA Assistant: Unidad guardada exitosamente en la BD.")
            
            return {"resultado": "ok", "mensaje": "Unidad generada y guardada correctamente."}

        except json.JSONDecodeError:
            logger.error(f"IA Assistant: La IA devolvió un JSON inválido: {respuesta_ia[:100]}")
            return {"resultado": "error", "mensaje": "La IA devolvió un formato inválido. Intenta de nuevo."}
        except Exception as e:
            logger.error(f"IA Assistant Error: {str(e)}")
            return {"resultado": "error", "mensaje": f"Error de conexión: {str(e)}"}

    def student_view(self, context=None):
        """ Ensambla y muestra la unidad al estudiante. """
        # --- TRUCO DE DEBUG ---
        #return self.studio_view(context)

        json_crudo = self.unidad_json if self.unidad_json else "{}"
        prompt_debug = self.prompt_docente if self.prompt_docente else "Sin prompt."

        html_componentes, recursos = renderizar_unidad(json_crudo)

        html_base = load_resource("static/core/student/student.html").format(
            unidad_titulo=recursos['titulo'],
            componentes_html=html_componentes,
            unidad_json=json_crudo,
            prompt_debug=prompt_debug
        )
        
        frag = Fragment(html_base)
        
        # Inyectar recursos CSS/JS de componentes
        for css in recursos['css']: frag.add_css(load_resource(css))
        for js in recursos['js']: frag.add_javascript(load_resource(js))
        
        # Estilos y JS del Chasis
        frag.add_css(load_resource("static/core/student/student.css"))
        frag.add_javascript(load_resource("static/core/student/student.js"))
        frag.initialize_js('StudentMasterInit')
        
        return frag

    @XBlock.json_handler
    def calificar_unidad(self, data, suffix=''):
        """ Maneja la calificación. """
        resultado = calcular_nota_final(data, self.unidad_json)
        self.runtime.publish(self, 'grade', {'value': resultado['nota']/100.0, 'max_value': 1.0})
        return resultado

    @staticmethod
    def workbench_scenarios():
        return [("IA Assistant XBlock", "<ia_assistant/>")]