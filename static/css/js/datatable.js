$(document).ready(function () {
    if ($('#dataTable').length) {
        var table = $('#dataTable').DataTable({
            "language": {
                "decimal": ",",
                "thousands": ".",
                "lengthMenu": "Mostrar _MENU_ entradas",
                "zeroRecords": "No se encontraron resultados",
                "info": "Mostrando _START_ a _END_ de _TOTAL_ registros",
                "infoEmpty": "Mostrando 0 a 0 de 0 registros",
                "infoFiltered": "(filtrado de _MAX_ registros totales)",
                "search": "Buscar:",
                "paginate": {
                    "first": "Primero",
                    "last": "Último",
                    "next": "Sig.",
                    "previous": "Ant."
                }
            },
            responsive: true, // Habilita el plugin Responsive
            "order": [[0, 'desc']], // Ordena por la primera columna en orden descendente (el más reciente primero)
            "columnDefs": [
                {
                    responsivePriority: 1, targets: -1 // Prioridad para la última columna (acciones)
                },
                {
                    targets: 1,  
                    /*className: 'd-flex justify-content-center',*/
                    responsivePriority: 2 // Prioridad para la segunda columna
                }
            ],
            "paging": true,
            "searching": true,
            "info": true,
            "dom": '<"top"B><"clear"><"top-wrapper"lf>rt<"bottom"ip><"clear">',
            "buttons": [
                // Botón personalizado para "Crear"
                {
                    text: '<i class="fas fa-plus-circle"></i> Crear Nuevo',  // Texto del botón
                    className: 'btn btn-success',
                    action: function (e, dt, node, config) {
                        // Redirigir a la URL de "Agregar Usuario"
                        // Verificar si se debe abrir un modal o redirigir
                        if (accionBoton === 'modal') {
                            // Abrir el modal dinámico
                            abrir_modal_edicion(urlBoton);
                        } else {
                            // Redirigir a la URL
                            window.location.href = urlBoton;
                        }
                    }
                },
                {
                    extend: 'csv',
                    text: '<i class="fas fa-file-csv"></i> CSV',
                    className: 'btn btn-success'
                },
                {
                    extend: 'excel',
                    text: '<i class="fas fa-file-excel"></i> Excel',
                    className: 'btn btn-success'
                },
                {
                    extend: 'pdf',
                    text: '<i class="fas fa-file-pdf"></i> PDF',
                    className: 'btn btn-danger'
                },
                {
                    extend: 'print',
                    text: '<i class="fas fa-print"></i> Imprimir',
                    className: 'btn btn-info'
                },
                {
                    extend: 'colvis',
                    text: '<i class="fas fa-eye"></i> Visibilidad de la columna ',
                    className: 'btn btn-primary',
                    collectionLayout: 'fixed two-column',
                    postfixButtons: ['colvisRestore'],
                    attr: {
                        'data-bs-toggle': 'dropdown',
                        'aria-expanded': 'false'
                    }
                }
            ]
        });

        // Forzar la actualización de la información de paginación
        table.on('draw', function () {
            console.log("Info de paginación:", table.page.info());
        });
    }
});
