// Este objeto global guardará las funciones de evaluación de todos los componentes
window.IA_Components = window.IA_Components || {};

window.IA_Components.evaluarQuiz = function(element) {
    var correctas = 0;
    var total = 0;
    
    $('.ia-pregunta', element).each(function() {
        total++;
        var qElem = $(this);
        var correctaIdx = qElem.attr('data-correcta');
        var seleccionadaIdx = qElem.find('input[type="radio"]:checked').val();
        
        if (seleccionadaIdx === correctaIdx) {
            correctas++;
            qElem.css('border-left-color', '#28a745'); // Verde si está bien
        } else {
            qElem.css('border-left-color', '#dc3545'); // Rojo si está mal
        }
    });
    
    return {
        total: total,
        correctas: correctas,
        puntaje: total > 0 ? (correctas / total) * 100 : 0
    };
};