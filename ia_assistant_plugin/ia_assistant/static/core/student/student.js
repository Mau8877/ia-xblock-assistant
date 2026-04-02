function StudentMasterInit(runtime, element) {
    var $el = $(element);
    var startTime = Date.now();
    var handlerUrl = runtime.handlerUrl(element, 'calificar_unidad');

    function obtenerDataRespuestas() {
        var respuestas = {};
        
        // Recolectar Quizzes
        $el.find('.ia-pregunta').each(function() {
            var name = $(this).find('input').attr('name');
            var valor = $(this).find('input:checked').val();
            if (valor !== undefined) respuestas[name] = valor;
        });

        // Recolectar Abiertas
        $el.find('.ia-comp-abierta').each(function() {
            var id = $(this).attr('id');
            var texto = $(this).find('textarea').val();
            respuestas[id] = texto;
        });

        // Recolectar Código
        $el.find('.ia-comp-codigo').each(function() {
            var id = $(this).attr('id');
            var codigo = $(this).find('.code-input').val();
            respuestas[id] = codigo;
        });

        return respuestas;
    }

    function generarResumenRevision() {
        var $summary = $el.find('#revision-summary');
        
        // 1. Quizzes
        var tQuiz = $el.find('.ia-comp-quiz .ia-pregunta').length;
        var rQuiz = $el.find('.ia-comp-quiz .ia-pregunta').filter(function() { 
            return $(this).find('input:checked').length > 0; 
        }).length;

        // 2. Abiertas (Solo busca dentro de su propio contenedor)
        var $contenedorAbiertas = $el.find('.ia-comp-abierta');
        var tAbierta = $contenedorAbiertas.length;
        var rAbierta = $contenedorAbiertas.filter(function() {
            var texto = $(this).find('textarea').val() || "";
            return texto.trim().length > 15; // Consideramos respondida si escribió algo sustancial
        }).length;

        // 3. Código (Solo busca dentro de su propio contenedor y descuenta el base)
        var $contenedorCodigo = $el.find('.ia-comp-codigo');
        var tCodigo = $contenedorCodigo.length;
        var rCodigo = $contenedorCodigo.filter(function() {
            var $area = $(this).find('textarea');
            var actual = $area.val() || "";
            var baseLen = parseInt($(this).data('base-len')) || 0;
            
            // Si el texto actual es al menos 5 caracteres más largo que el inicial, 
            // asumimos que el alumno trabajó.
            return actual.trim().length > (baseLen + 5);
        }).length;

        var html = `
            <div class="summary-results">
                <p>✅ <b>Quizzes:</b> ${rQuiz} de ${tQuiz} preguntas.</p>
                <p>✍️ <b>Abiertas:</b> ${rAbierta} de ${tAbierta} respondidas.</p>
                <p>💻 <b>Código:</b> ${rCodigo} de ${tCodigo} completados.</p>
            </div>`;
        
        $summary.html(html);
    }

    function organizarComponentes() {
        $el.find('.ia-comp-teoria').detach().appendTo($el.find('#tab-teoria'));
        $el.find('.ia-comp-quiz').detach().appendTo($el.find('#tab-quiz'));
        $el.find('.ia-comp-abierta').detach().appendTo($el.find('#tab-abierta'));
        $el.find('.ia-comp-codigo').detach().appendTo($el.find('#tab-codigo'));

        $el.find('.tab-content').each(function() {
            if ($(this).children().not('.empty-state, h3, #revision-summary, .ia-master-actions, p, hr, #master-feedback').length > 0) {
                $(this).find('.empty-state').hide();
            }
        });
        $el.find('.tab-btn[data-target="tab-teoria"]').trigger('click');
    }

    // --- ACCIÓN DE ENVÍO ---
    $el.find('#btn-enviar-master').click(function() {
        var $btn = $(this);
        var $feedback = $el.find('#master-feedback');
        
        $btn.text('Enviando a la IA...').prop('disabled', true);
        $feedback.hide().html('');

        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify(obtenerDataRespuestas()),
            success: function(data) {
                $btn.text('Enviar Evaluación Completa').prop('disabled', false);
                $feedback.fadeIn();
                
                if (data.resultado === 'ok') {
                    var html = `
                        <div class="ia-score-card">
                            <h4>Calificación: ${data.nota}/100</h4>
                            <div class="ia-feedback-text">${data.mensaje_feedback}</div>
                        </div>`;
                    $feedback.html(html).css('border-left', '5px solid #28a745');
                } else {
                    $feedback.html('<p>❌ Error: ' + data.mensaje + '</p>').css('border-left', '5px solid #dc3545');
                }
            }
        });
    });

    $el.find('.tab-btn').on('click', function(e) {
        e.preventDefault();
        var target = $(this).data('target');
        $el.find('.tab-btn').removeClass('active');
        $(this).addClass('active');
        $el.find('.tab-content').hide();
        $el.find('#' + target).show();
        if(target === 'tab-revision') generarResumenRevision();
    });

    setInterval(function() {
        var diff = Math.floor((Date.now() - startTime) / 1000);
        var mins = Math.floor(diff / 60).toString().padStart(2, '0');
        var secs = (diff % 60).toString().padStart(2, '0');
        $el.find('#ia-timer').text(mins + ':' + secs);
    }, 1000);

    setTimeout(organizarComponentes, 1000);
}