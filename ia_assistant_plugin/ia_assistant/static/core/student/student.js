function StudentMasterInit(runtime, element) {
    var handlerUrl = runtime.handlerUrl(element, 'calificar_unidad');

    $('#btn-enviar-master', element).click(function() {
        var $btn = $(this);
        var $feedback = $('#master-feedback', element);
        
        $btn.text('Enviando a la plataforma... ⏳').prop('disabled', true);

        // --- 1. RECOLECCIÓN DE DATOS ---
        var resultadosQuiz = {};
        if (window.IA_Components && window.IA_Components.evaluarQuiz) {
            resultadosQuiz = window.IA_Components.evaluarQuiz(element);
        }

        // AGREGAMOS ESTA PARTE QUE FALTABA:
        var respuestasAbiertas = [];
        if (window.IA_Components && window.IA_Components.obtenerRespuestasAbiertas) {
            respuestasAbiertas = window.IA_Components.obtenerRespuestasAbiertas(element);
        }

        var respuestasCodigo = [];
        if (window.IA_Components && window.IA_Components.obtenerRespuestasCodigo) {
            respuestasCodigo = window.IA_Components.obtenerRespuestasCodigo(element);
        }

        // --- 2. ENVÍO AJAX ---
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify({
                "respuestas_quiz": resultadosQuiz,
                "respuestas_abiertas": respuestasAbiertas,
                "respuestas_codigo": respuestasCodigo
            }),
            // Agregamos contentType para ser más precisos con Django
            contentType: "application/json", 
            success: function(data) {
                $btn.text('Evaluación Enviada').prop('disabled', true);
                
                if(data.resultado === 'ok') {
                    var feedbackHTML = '<ul>';
                    data.feedback.forEach(function(item) {
                        feedbackHTML += `<li>${item}</li>`;
                    });
                    feedbackHTML += '</ul>';

                    $('#master-feedback', element).html(`
                        <div style="padding:20px; background:#e3f2fd; border: 2px solid #0056d2; border-radius:10px; margin-top:20px;">
                            <h3 style="margin-top:0; color:#0056d2;">📊 Resultado de la Evaluación</h3>
                            <p style="font-size:18px;">Tu nota final es: <strong>${data.nota}/100</strong></p>
                            <hr style="border: 0; border-top: 1px solid #0056d2; opacity: 0.2;">
                            <div style="font-size:14px; color:#444;">
                                <strong>Comentarios del Profesor IA:</strong>
                                ${feedbackHTML}
                            </div>
                        </div>
                    `).fadeIn();
                } else {
                    alert("Error en la evaluación: " + data.mensaje);
                    $btn.text('Reintentar').prop('disabled', false);
                }
            },
            error: function() {
                $btn.prop('disabled', false).text('Reintentar Envío');
                alert("Error crítico al conectar con el servidor.");
            }
        });
    });
}