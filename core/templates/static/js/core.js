  document.addEventListener("DOMContentLoaded", function () {
    alert("core.js loaded");
    const zipButton = document.querySelector(".btn-warning");
  $("#zipButton").on("click", function() {
    // Mostrar confirmación antes de ejecutar
    Swal.fire({
        title: '¿Ejecutar proceso ZIP?',
        text: "Esta acción procesará y comprimirá los archivos.",
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí, ejecutar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            ejecutarProcesoZIP();
        }
    });
});

function ejecutarProcesoZIP() {
    const $button = $("#zipButton");
    const originalText = $button.text();
    
    $button.prop('disabled', true).html('<span class="spinner-border spinner-border-sm"></span> Procesando...');
    
    $.ajax({
        url: "{% url 'ejecutar_proceso_zip' %}",
        method: "POST",
        headers: {
            "X-CSRFToken": "{{ csrf_token }}"
        },
        dataType: "json"
    })
    .done(function(data) {
        if (data.success) {
            Swal.fire({
                icon: 'success',
                title: 'Completado',
                text: data.message,
                timer: 2000,
                showConfirmButton: false
            }).then(() => {
                location.reload();
            });
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: data.message || data.error
            });
        }
    })
    .fail(function(xhr, status, error) {
        Swal.fire({
            icon: 'error',
            title: 'Error de conexión',
            text: 'No se pudo completar la operación'
        });
    })
    .always(function() {
        $button.prop('disabled', false).html(originalText);
    });
}
});