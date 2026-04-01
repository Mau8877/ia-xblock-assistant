function StudioDocenteInit(runtime, element) {
    var handlerUrl = runtime.handlerUrl(element, 'guardar_prompt');
    
    $('#btn-generar', element).click(function(eventObject) {
        eventObject.preventDefault();
        var prompt_texto = $('#prompt-input', element).val();
        
        var $btn = $('#btn-generar', element);
        var originalText = $btn.text();
        $btn.text('Generando con IA... ⏳').prop('disabled', true);
        $('#mensaje-error', element).hide();
        
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify({"prompt": prompt_texto}),
            success: function(data) {
                $btn.text(originalText).prop('disabled', false);
                if(data.resultado === 'ok') {
                    $('#mensaje-estado', element).show().fadeOut(5000);
                } else {
                    $('#mensaje-error', element).text('❌ ' + data.mensaje).show();
                }
            },
            error: function() {
                $btn.text(originalText).prop('disabled', false);
                $('#mensaje-error', element).text('❌ Error de conexión.').show();
            }
        });
    });
}