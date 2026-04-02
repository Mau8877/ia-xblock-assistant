import logging
from xblock.core import XBlock
from xblock.fields import Scope, String
from xblock.fragment import Fragment

# --- Importaciones de Capas Refactorizadas ---
from .utils.load_resource import load_resource
from .component_manager import renderizar_unidad
from .ia_docente.ia_docente_client import generar_contenido_unidad
from .ia_alumno.evaluator.calcular_nota import calcular_nota_final

# Configuración de logs para el workbench de Django
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

    # -----------------------------------------------------------------------
    # VISTA STUDIO (Configuración del Docente)
    # -----------------------------------------------------------------------
    def studio_view(self, context=None):
        """ Renderiza la interfaz donde el profesor escribe el prompt. """
        html_str = load_resource("static/core/studio/studio.html")
        html_formateado = html_str.format(prompt_docente=self.prompt_docente)
        
        frag = Fragment(html_formateado)
        frag.add_css(load_resource("static/core/studio/studio.css"))
        frag.add_javascript(load_resource("static/core/studio/studio.js"))
        frag.initialize_js('StudioDocenteInit')
        return frag

    @XBlock.json_handler
    def guardar_prompt(self, data, suffix=''):
        """ 
        Handler Ajax que delega la generación a ia_docente_client. 
        """
        nuevo_prompt = data.get('prompt', '')
        self.prompt_docente = nuevo_prompt 

        logger.info(f"IA Assistant: Iniciando generación para docente...")
        
        # Delegación a la lógica de negocio en ia_docente
        resultado = generar_contenido_unidad(nuevo_prompt)

        if resultado['resultado'] == 'ok':
            self.unidad_json = resultado['json_unidad']
            logger.info("IA Assistant: Unidad generada y persistida exitosamente.")
            return {"resultado": "ok", "mensaje": "Unidad generada correctamente."}
        else:
            # El error ya viene formateado con el mensaje de ia_docente_client
            return resultado

    # -----------------------------------------------------------------------
    # VISTA STUDENT (Interfaz del Alumno)
    # -----------------------------------------------------------------------
    def student_view(self, context=None):
        """ Ensambla dinámicamente los componentes de la unidad. """

        #return self.studio_view(context)
        json_crudo = self.unidad_json if self.unidad_json else "{}"
        
        # El component_manager se encarga de convertir JSON -> HTML y listar recursos
        html_componentes, recursos = renderizar_unidad(json_crudo)

        html_base = load_resource("static/core/student/student.html").format(
            unidad_titulo=recursos.get('titulo', 'Unidad de Aprendizaje'),
            componentes_html=html_componentes,
            unidad_json=json_crudo,
            prompt_debug=self.prompt_docente
        )
        
        frag = Fragment(html_base)
        
        # Inyectar dinámicamente CSS/JS de los componentes usados (Teoría, Código, etc.)
        for css in recursos.get('css', []): frag.add_css(load_resource(css))
        for js in recursos.get('js', []): frag.add_javascript(load_resource(js))
        
        # Recursos base del "Chasis" del estudiante
        frag.add_css(load_resource("static/core/student/student.css"))
        frag.add_javascript(load_resource("static/core/student/student.js"))
        frag.initialize_js('StudentMasterInit')
        
        return frag

    # -----------------------------------------------------------------------
    # HANDLER DE CALIFICACIÓN
    # -----------------------------------------------------------------------
    @XBlock.json_handler
    def calificar_unidad(self, data, suffix=''):
        """ 
        Recibe las respuestas y delega la evaluación a ia_alumno.evaluator.
        """
        logger.info("IA Assistant: Procesando entrega del alumno...")
        
        resultado = calcular_nota_final(data, self.unidad_json)
        
        # Publicar la nota en el runtime de Open edX (Grades)
        # Nota: nota viene en escala 0-100, edX espera 0.0-1.0
        nota_final = resultado.get('nota', 0)
        self.runtime.publish(self, 'grade', {
            'value': nota_final / 100.0, 
            'max_value': 1.0
        })
        
        return resultado

    @staticmethod
    def workbench_scenarios():
        """ Escenario para el SDK de XBlock. """
        return [("IA Assistant XBlock", "<ia_assistant/>")]