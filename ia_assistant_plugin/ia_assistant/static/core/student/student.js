// archivo: static/core/student/student.js
function StudentMasterInit(runtime, element) {
    var $el = $(element);
    var startTime = Date.now();
    var handlerUrl = runtime.handlerUrl(element, 'calificar_unidad');

    function obtenerDataRespuestas() {
        var quizId = $el.find('.ia-comp-quiz').attr('id');
        var dataFinal = { respuestas_quiz: { puntaje: 0, detalles: {}, id: quizId }, respuestas_abiertas: [], respuestas_codigo: [] };

        var correctas = 0; var totalQ = $el.find('.ia-pregunta').length;
        $el.find('.ia-pregunta').each(function() {
            var correcta = String($(this).attr('data-correcta')); 
            var seleccionada = $(this).find('input:checked').val();
            if (seleccionada !== undefined && String(seleccionada) === correcta) correctas++;
        });
        
        var puntajeCrudo = totalQ > 0 ? (correctas / totalQ) * 100 : 0;
        dataFinal.respuestas_quiz.puntaje = parseFloat(puntajeCrudo.toFixed(2));

        $el.find('.ia-comp-abierta').each(function() {
            var idVal = $(this).attr('id');
            if (idVal) dataFinal.respuestas_abiertas.push({ id: idVal, texto: $(this).find('.respuesta-alumno').val() });
        });

        $el.find('.ia-comp-codigo').each(function() {
            var idVal = $(this).attr('id');
            if (idVal) dataFinal.respuestas_codigo.push({ id: idVal, texto: $(this).find('.code-input').val() });
        });

        return dataFinal;
    }

    function organizarComponentes() {
        $el.find('.ia-comp-teoria').detach().appendTo($el.find('#tab-teoria'));
        $el.find('.ia-comp-quiz').detach().appendTo($el.find('#tab-quiz'));
        $el.find('.ia-comp-abierta').detach().appendTo($el.find('#tab-abierta'));
        $el.find('.ia-comp-codigo').detach().appendTo($el.find('#tab-codigo'));

        $el.find('.tab-content').each(function() {
            if ($(this).children().not('.empty-state, h3, #revision-summary, .ia-master-actions, p, hr, #master-feedback, .ia-revision-container').length > 0) {
                $(this).find('.empty-state').hide();
            }
        });
    }

    // --- ACCIÓN DE ENVÍO ---
    $el.find('#btn-enviar-master').click(function() {
        var $btn = $(this);
        var $feedbackArea = $el.find('#master-feedback');
        
        $btn.text('Evaluando con Afrodita...').prop('disabled', true);
        $feedbackArea.hide();

        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify(obtenerDataRespuestas()),
            success: function(data) {
                $btn.text('Enviar Evaluación Completa').prop('disabled', false);
                
                if (data.resultado === 'ok') {
                    // 1. Limpieza de colores previos en componentes
                    $el.find('.ia-pregunta, .ia-comp-abierta, .ia-comp-codigo, .ia-comp-quiz').removeClass('is-correct is-incorrect');

                    // 2. Aplicar feedback in-situ en las otras pestañas
                    data.feedback.forEach(function(item) {
                        var $target = $el.find('#' + item.id);

                        if ($target.length > 0) {
                            var statusClass = (item.nota >= 51) ? 'is-correct' : 'is-incorrect';
                            $target.addClass(statusClass);

                            // Inyección de feedback in-situ
                            var $fbContainer = $target.find('.feedback-ia');
                            if ($fbContainer.length > 0) {
                                $fbContainer.find('.fb-text').html('<b>Afrodita dice:</b> ' + item.detalle);
                                $fbContainer.removeAttr('style').css({'display': 'block', 'visibility': 'visible', 'opacity': '1'});
                                $fbContainer.hide().fadeIn(600);
                            }

                            // Colorear radios del Quiz
                            if (item.tipo === 'Quiz' || $target.hasClass('ia-comp-quiz')) {
                                $target.find('.ia-pregunta').each(function() {
                                    var $q = $(this);
                                    var correcta = String($q.attr('data-correcta'));
                                    var seleccionada = $q.find('input:checked').val();
                                    $q.removeClass('is-correct is-incorrect');
                                    if (seleccionada !== undefined && String(seleccionada) === correcta) $q.addClass('is-correct');
                                    else $q.addClass('is-incorrect');
                                });
                            }
                        }
                    });

                    // 3. DELEGAR LA PESTAÑA REVISIÓN AL MÓDULO EXTERNO
                    if (window.IA_Components && window.IA_Components.Revision) {
                        window.IA_Components.Revision.pintarFeedbackFinal($el, data);
                    }

                } else {
                    $feedbackArea.html('<p class="error-msg">❌ ' + data.mensaje + '</p>').show();
                }
            },
            error: function(xhr, status, error) {
                $btn.text('Enviar Evaluación Completa').prop('disabled', false);
                $feedbackArea.html('<p class="error-msg">❌ Error de conexión: ' + error + '</p>').show();
            }
        });
    });

    // --- MANEJO DE TABS ---
    $el.find('.tab-btn').on('click', function(e) {
        e.preventDefault();
        var target = $(this).data('target');
        
        $el.find('.tab-btn').removeClass('active');
        $(this).addClass('active');
        
        $el.find('.tab-content').hide();
        $el.find('#' + target).show();
        
        // Llamada al módulo externo para generar el resumen
        if (target === 'tab-revision') {
            if (window.IA_Components && window.IA_Components.Revision) {
                window.IA_Components.Revision.generarResumen($el);
            }
        }
    });

    setInterval(function() {
        var diff = Math.floor((Date.now() - startTime) / 1000);
        var mins = Math.floor(diff / 60).toString().padStart(2, '0');
        var secs = (diff % 60).toString().padStart(2, '0');
        $el.find('#ia-timer').text(mins + ':' + secs);
    }, 1000);

    setTimeout(organizarComponentes, 500);
}