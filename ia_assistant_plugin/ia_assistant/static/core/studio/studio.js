function STUDIO_DOCENTE_INIT(runtime, element) {
    var HANDLER_LLAMAR_IA = runtime.handlerUrl(element, 'generar_borrador_ia');
    var HANDLER_GUARDAR_UNIDAD = runtime.handlerUrl(element, 'guardar_unidad_editada');
    
    // --- MANEJO DE PESTAÑAS PRINCIPALES (Visual vs JSON) ---
    $('.main-tab-btn', element).click(function() {
        $('.main-tab-btn', element).removeClass('active');
        $('.main-tab-content', element).removeClass('active');
        $(this).addClass('active');
        $('#' + $(this).data('target'), element).addClass('active');
    });

    // --- MANEJO DE SUB-PESTAÑAS (Teoría, Quiz, etc.) ---
    $('.sub-tab-btn', element).click(function(e) {
        e.preventDefault();
        $('.sub-tab-btn', element).removeClass('active');
        $('.sub-tab-content', element).removeClass('active-content').hide();
        
        $(this).addClass('active');
        $('#' + $(this).data('target'), element).show().addClass('active-content');
    });

    // --- PASO 1: LLAMAR A LA IA (CON BLINDAJE ANTI-ZOMBIE Y UX MEJORADA) ---
    $('#btn-generar', element).click(function(eventObject) {
        eventObject.preventDefault();
        var $btn = $(this);
        var prompt_texto = $('#prompt-input', element).val().trim();
        
        if (prompt_texto === '') { MOSTRAR_ERROR('El prompt no puede estar vacío.', element); return; }

        var originalText = $btn.find('.btn-text').text();
        $btn.prop('disabled', true);
        $('#btn-guardar-final', element).prop('disabled', true);
        OCULTAR_MENSAJES(element);
        
        // Simulación de progreso para calmar la ansiedad del usuario
        let PASOS_CARGA = [
            'Conectando con la red neuronal...', 
            'Buscando el modelo más óptimo...', 
            'Redactando teoría a nivel universitario...', 
            'Esto toma tiempo (escribiendo párrafos profundos)...',
            'Diseñando quizzes basados en la teoría...',
            'Estructurando ejercicios prácticos...',
            'Validando la coherencia del JSON...',
            'Casi listo, empaquetando la unidad...',
            'Afinando los últimos detalles...'
        ];
        let PASO_ACTUAL = 0;
        
        $btn.find('.btn-text').text(PASOS_CARGA[0]);
        let INTERVALO_PROGRESO = setInterval(function() {
            PASO_ACTUAL++;
            if(PASO_ACTUAL < PASOS_CARGA.length) {
                $btn.find('.btn-text').text(PASOS_CARGA[PASO_ACTUAL]);
            }
        }, 15000); // Rota el mensaje cada 15 segundos
        
        $.ajax({
            type: "POST",
            url: HANDLER_LLAMAR_IA,
            data: JSON.stringify({"prompt": prompt_texto}),
            timeout: 180000, // REGLA ESTRICTA: 3 MINUTOS MAXIMO
            success: function(data) {
                clearInterval(INTERVALO_PROGRESO); // Aniquilar el timer
                RESTAURAR_BOTON($btn, originalText);
                
                if (data.resultado === 'ok') {
                    $('#contenido-preview', element).val(data.contenido_crudo);
                    
                    try {
                        let jsonData = JSON.parse(data.contenido_crudo);
                        DISTRIBUIR_COMPONENTES_VISUALES(jsonData, element);
                    } catch(e) {
                        console.error("Error crítico parseando JSON:", e);
                        MOSTRAR_ERROR("La IA devolvió contenido, pero el formato visual falló. Usa el Modo Avanzado.", element);
                    }

                    $('#btn-guardar-final', element).prop('disabled', false);
                } else {
                    MOSTRAR_ERROR(data.mensaje, element);
                }
            },
            error: function(xhr, status, error) {
                clearInterval(INTERVALO_PROGRESO); // Aniquilar el timer
                RESTAURAR_BOTON($btn, originalText);
                
                if (status === "timeout") {
                    MOSTRAR_ERROR('TIMEOUT: La IA tardó más de 3 minutos en redactar la unidad. Intenta con un tema más específico.', element);
                } else {
                    MOSTRAR_ERROR('Error de conexión con el servidor: ' + error, element);
                }
            }
        });
    });

    // --- PASO 2: GUARDAR ---
    $('#btn-guardar-final', element).click(function(eventObject) {
        eventObject.preventDefault();
        var $btn = $(this);
        
        var contenido_final = "";
        if ($('#vista-visual', element).hasClass('active')) {
            contenido_final = RECOLECTAR_JSON_DE_PESTANAS(element);
            $('#contenido-preview', element).val(contenido_final); 
        } else {
            contenido_final = $('#contenido-preview', element).val();
        }

        var originalText = $btn.find('.btn-text').text();
        $btn.prop('disabled', true);
        $btn.find('.btn-text').text('Publicando...');
        OCULTAR_MENSAJES(element);

        $.ajax({
            type: "POST",
            url: HANDLER_GUARDAR_UNIDAD,
            data: JSON.stringify({ "contenido_final": contenido_final }),
            success: function(data) {
                RESTAURAR_BOTON($btn, originalText);
                if (data.resultado === 'ok') {
                    $('#mensaje-estado', element).slideDown(300);
                    setTimeout(function() { $('#mensaje-estado', element).slideUp(300); }, 4000);
                } else {
                    MOSTRAR_ERROR(data.mensaje, element);
                }
            },
            error: function() {
                RESTAURAR_BOTON($btn, originalText);
                MOSTRAR_ERROR('Error al guardar en la base de datos.', element);
            }
        });
    });

    // ==========================================
    // DISTRIBUIDOR (JSON -> PESTAÑAS)
    // ==========================================
    function DISTRIBUIR_COMPONENTES_VISUALES(data, el) {
        $('#edit-titulo-unidad', el).val(data.titulo_unidad || '');
        
        $('#edit-teoria, #edit-quiz, #edit-abierta, #edit-codigo', el).empty();

        if(data.componentes) {
            data.componentes.forEach((comp, idx) => {
                let html = `<div class="editor-card comp-block" data-tipo="${comp.tipo}" data-id="${comp.id}">`;
                
                if (comp.tipo === 'teoria') {
                    html += `
                        <div class="form-group">
                            <label>Contenido Teórico</label>
                            <div class="quill-container" style="height: 250px; background: #fff;">${comp.contenido_html || ''}</div>
                        </div>`;
                    $('#edit-teoria', el).append(html + '</div>');
                } 
                else if (comp.tipo === 'quiz_multiple') {
                    html += `<div class="form-group"><label>Preguntas del Quiz</label>`;
                    comp.preguntas.forEach((q, qIdx) => {
                        html += `
                        <div class="editor-card q-block" style="border-left-color: #cbd5e1;">
                            <div class="form-group">
                                <label>Enunciado de la Pregunta ${qIdx + 1}</label>
                                <input type="text" class="form-control d-enunciado" value="${q.enunciado}">
                            </div>
                            <div class="quiz-options">
                                <label>Opciones (Marca el círculo de la correcta):</label>
                                ${q.opciones.map((opt, oIdx) => `
                                    <div style="display:flex; gap:10px; margin-bottom:5px;">
                                        <input type="radio" name="correcta_${idx}_${qIdx}" value="${oIdx}" ${q.correcta === oIdx ? 'checked' : ''}>
                                        <input type="text" class="form-control d-opcion" value="${opt}">
                                    </div>
                                `).join('')}
                            </div>
                        </div>`;
                    });
                    html += `</div>`;
                    $('#edit-quiz', el).append(html + '</div>');
                }
                else if (comp.tipo === 'pregunta_abierta') {
                    html += `
                        <div class="form-group">
                            <label>Pregunta de Análisis</label>
                            <textarea class="form-control d-enunciado-gral" rows="3">${comp.enunciado || ''}</textarea>
                        </div>
                        <div class="form-group">
                            <label>Criterios de Evaluación para la IA Evaluadora</label>
                            <input type="text" class="form-control d-puntos" value="${comp.puntos_clave || ''}">
                        </div>`;
                    $('#edit-abierta', el).append(html + '</div>');
                }
                else if (comp.tipo === 'codigo') {
                    html += `
                        <div class="form-group">
                            <label>Problema de Programación</label>
                            <textarea class="form-control d-enunciado-gral" rows="3">${comp.enunciado || ''}</textarea>
                        </div>
                        <div class="form-group">
                            <label>Criterios de Evaluación (Algoritmo esperado)</label>
                            <input type="text" class="form-control d-puntos" value="${comp.puntos_clave || ''}">
                        </div>`;
                    $('#edit-codigo', el).append(html + '</div>');
                }
            });
        }

        // DESPERTAR A QUILL.JS
        $('.quill-container', el).each(function() {
            var quill = new Quill(this, {
                theme: 'snow',
                modules: {
                    toolbar: [
                        ['bold', 'italic', 'underline', 'strike'],
                        [{ 'header': [1, 2, 3, false] }],
                        [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                        [{ 'color': [] }, { 'background': [] }],
                        ['code-block', 'clean']
                    ]
                }
            });
            $(this).data('quill-instance', quill); 
        });

        // EMPTY STATES
        ['#edit-teoria', '#edit-quiz', '#edit-abierta', '#edit-codigo'].forEach(target => {
            if ($(target, el).is(':empty')) {
                $(target, el).html('<div class="empty-state">No se generaron componentes de este tipo.</div>');
            }
        });
    }

    // ==========================================
    // RECOLECTOR (PESTAÑAS -> JSON)
    // ==========================================
    function RECOLECTAR_JSON_DE_PESTANAS(el) {
        let data = {
            titulo_unidad: $('#edit-titulo-unidad', el).val(),
            componentes: []
        };

        $('.comp-block', el).each(function() {
            let $bloque = $(this);
            let tipo = $bloque.data('tipo');
            let compObj = { tipo: tipo, id: $bloque.data('id') };

            if (tipo === 'teoria') {
                let quillInst = $bloque.find('.quill-container').data('quill-instance');
                if (quillInst) {
                    compObj.contenido_html = quillInst.root.innerHTML; 
                } else {
                    compObj.contenido_html = "";
                }
            } 
            else if (tipo === 'quiz_multiple') {
                compObj.preguntas = [];
                $bloque.find('.q-block').each(function() {
                    let $q = $(this);
                    let opciones = [];
                    let correctaIdx = 0;
                    
                    $q.find('.d-opcion').each(function(index) {
                        opciones.push($(this).val());
                        if ($(this).siblings('input[type="radio"]').is(':checked')) correctaIdx = index;
                    });

                    compObj.preguntas.push({
                        enunciado: $q.find('.d-enunciado').val(),
                        opciones: opciones,
                        correcta: correctaIdx
                    });
                });
            }
            else if (tipo === 'pregunta_abierta' || tipo === 'codigo') {
                compObj.enunciado = $bloque.find('.d-enunciado-gral').val();
                compObj.puntos_clave = $bloque.find('.d-puntos').val() || "";
            }

            data.componentes.push(compObj);
        });

        return JSON.stringify(data, null, 2);
    }

    // ==========================================
    // UTILIDADES
    // ==========================================
    function MOSTRAR_ERROR(mensaje, el) { 
        $('#mensaje-estado', el).hide(); 
        $('#mensaje-error .error-texto', el).text(mensaje); 
        $('#mensaje-error', el).slideDown(200); 
    }
    
    function OCULTAR_MENSAJES(el) { 
        $('#mensaje-error', el).slideUp(200); 
        $('#mensaje-estado', el).slideUp(200); 
    }
    
    function RESTAURAR_BOTON($btn, texto) { 
        $btn.prop('disabled', false); 
        $btn.find('.btn-text').text(texto); 
    }
}