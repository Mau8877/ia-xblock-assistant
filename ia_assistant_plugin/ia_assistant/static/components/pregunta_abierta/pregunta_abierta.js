window.IA_Components = window.IA_Components || {};

window.IA_Components.obtenerRespuestasAbiertas = function(element) {
    var respuestas = [];
    $('.ia-component-abierta', element).each(function() {
        respuestas.push({
            id: $(this).attr('data-id'),
            texto: $(this).find('.respuesta-alumno').val()
        });
    });
    return respuestas;
};