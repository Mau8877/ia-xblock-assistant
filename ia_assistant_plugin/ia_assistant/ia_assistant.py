from xblock.core import XBlock
from xblock.fields import Scope, String
from xblock.fragment import Fragment

class IAAssistantXBlock(XBlock):
    """
    Componente XBlock para el Asistente Inteligente.
    """
    
    # Un campo de configuración básico que se guarda en la base de datos
    display_name = String(
        display_name="Nombre a mostrar",
        default="🤖 Asistente IA (FICCT)",
        scope=Scope.settings,
        help="Nombre del bloque en la plataforma"
    )

    def student_view(self, context=None):
        """
        La vista principal que verá el estudiante al entrar al curso.
        """
        # HTML incrustado temporal (luego lo separaremos en archivos .html y .css)
        html = f"""
        <div style="padding: 20px; border: 2px solid #0056D2; border-radius: 8px; background-color: #f9f9f9;">
            <h2 style="color: #0056D2; margin-top: 0;">{self.display_name}</h2>
            <p>¡Hola! El esqueleto estructural de tu XBlock está funcionando perfectamente en el Workbench local.</p>
            <p><i>Siguiente paso: Conectar la lógica del LLM aquí adentro.</i></p>
        </div>
        """
        
        # Fragmento es como Open edX empaqueta el contenido web
        frag = Fragment(html)
        return frag

    @staticmethod
    def workbench_scenarios():
        """
        Un escenario de prueba para que aparezca en el xblock-sdk (Workbench).
        """
        return [
            ("IA Assistant XBlock (Prueba Local)",
             "<ia_assistant/>"),
        ]