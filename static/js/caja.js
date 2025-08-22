// static/js/caja.js

$(document).ready(function() {
    function loadContent(contentName) {
        $.ajax({
            url: "/caja/content/" + contentName,
            type: 'GET',
            success: function(response) {
                $('#dynamic-content-area').html(response);
                if (contentName === 'recibos-provisionales') {
                    initializeSignaturePad();
                }
            },
            error: function(error) {
                console.log('Hubo un error al cargar el contenido.', error);
                $('#dynamic-content-area').html('Hubo un error al cargar el contenido.');
            }
        });
    }

    // Cargar el contenido de Recibos Provisionales por defecto al entrar a la página
    loadContent('recibos-provisionales');

    // Manejar los clics en los enlaces del menú lateral para cargar el contenido dinámicamente
    $(document).on('click', '.submenu-link', function(e) {
        e.preventDefault(); // Previene el comportamiento por defecto del enlace
        const contentName = $(this).data('content');
        if(contentName) {
            loadContent(contentName);
        }
    });

    function initializeSignaturePad() {
        const canvas = document.getElementById('firma-canvas');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        let isDrawing = false;
        
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';
        ctx.strokeStyle = '#000';

        canvas.addEventListener('mousedown', (e) => {
            isDrawing = true;
            ctx.beginPath();
            const rect = canvas.getBoundingClientRect();
            ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top);
        });

        canvas.addEventListener('mousemove', (e) => {
            if (isDrawing) {
                const rect = canvas.getBoundingClientRect();
                ctx.lineTo(e.clientX - rect.left, e.clientY - rect.top);
                ctx.stroke();
            }
        });

        canvas.addEventListener('mouseup', () => {
            isDrawing = false;
        });

        // Eventos para dispositivos táctiles
        canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            isDrawing = true;
            ctx.beginPath();
            const rect = canvas.getBoundingClientRect();
            ctx.moveTo(e.touches[0].clientX - rect.left, e.touches[0].clientY - rect.top);
        });

        canvas.addEventListener('touchmove', (e) => {
            e.preventDefault();
            if (isDrawing) {
                const rect = canvas.getBoundingClientRect();
                ctx.lineTo(e.touches[0].clientX - rect.left, e.touches[0].clientY - rect.top);
                ctx.stroke();
            }
        });

        canvas.addEventListener('touchend', () => {
            isDrawing = false;
        });

        // Botones del modal de firma
        $('#limpiar-firma-btn').on('click', () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        });

        $('#aceptar-firma-btn').on('click', () => {
            const firmaDataUrl = canvas.toDataURL();
            $('#firma').val(firmaDataUrl);
            $('#firma-modal').hide();
            
            // Enviar el formulario
            const form = $('#recibo-form');
            const url = form.attr('action');
            const formData = form.serialize();

            $.ajax({
                url: url,
                method: 'POST',
                data: formData,
                success: function(response) {
                    if (response.status === 'success') {
                        swal('Éxito', response.message, 'success');
                        loadContent('recibos-provisionales');
                    } else {
                        swal('Error', response.message, 'error');
                    }
                },
                error: function() {
                    swal('Error', 'Hubo un error de conexión.', 'error');
                }
            });
        });
    }

    // Manejar el clic en el botón "Guardar" para mostrar el modal de firma
    $(document).on('click', '#guardar-recibo-btn', function(e) {
        e.preventDefault();
        
        const form = document.getElementById('recibo-form');
        if (!form.checkValidity()) {
            swal('Información', 'Por favor, complete todos los campos obligatorios.', 'info');
            return;
        }

        $('#firma-modal').show();
    });
});
