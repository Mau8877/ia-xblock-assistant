(function() {
    window.IA_Components = window.IA_Components || {};
    
    window.IA_Components.obtenerRespuestasCodigo = function(element) {
        var respuestas = [];
        $(element).find('.ia-comp-codigo').each(function() {
            respuestas.push({
                id: $(this).data('id'),
                texto: $(this).find('.code-input').val(),
                tipo: 'codigo'
            });
        });
        return respuestas;
    };

    $(document).on('keydown', '.code-input', function(e) {
        var selStart = this.selectionStart;
        var selEnd = this.selectionEnd;
        var $this = $(this);
        var value = $this.val();

        // --- MANEJO DE TAB (Insertar 4 espacios) ---
        if (e.key === 'Tab') {
            e.preventDefault();
            $this.val(value.substring(0, selStart) + "    " + value.substring(selEnd));
            this.selectionStart = this.selectionEnd = selStart + 4;
        }

        // --- MANEJO DE ENTER (Auto-indentación) ---
        if (e.key === 'Enter') {
            // 1. Encontrar el inicio de la línea actual
            var lineStart = value.lastIndexOf('\n', selStart - 1) + 1;
            var currentLine = value.substring(lineStart, selStart);
            
            // 2. Extraer los espacios o tabs al principio de esa línea (el indent)
            var indent = currentLine.match(/^\s*/)[0];
            
            // 3. Si hay indentación, la replicamos en la nueva línea
            if (indent.length > 0) {
                e.preventDefault(); // Detenemos el enter normal
                
                var splitBefore = value.substring(0, selStart);
                var splitAfter = value.substring(selEnd);
                
                // Insertamos el salto de línea manual + el indent clonado
                $this.val(splitBefore + "\n" + indent + splitAfter);
                
                // Colocamos el cursor después del nuevo indent
                this.selectionStart = this.selectionEnd = selStart + 1 + indent.length;
            }
        }
    });
})();