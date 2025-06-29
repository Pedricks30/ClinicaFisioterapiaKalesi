document.addEventListener('DOMContentLoaded', function() {
    // Actualizar el select de profesionales cuando cambia la especialidad
    const especialidadSelect = document.getElementById('id_especialidad');
    const profesionalSelect = document.getElementById('id_profesional');
    
    if (especialidadSelect && profesionalSelect) {
        especialidadSelect.addEventListener('change', function() {
            const especialidadId = this.value;
            
            if (especialidadId) {
                fetch(`/horarios/filtrar_profesionales/?especialidad=${especialidadId}`)
                    .then(response => response.json())
                    .then(data => {
                        profesionalSelect.innerHTML = '';
                        
                        // Agregar opción por defecto
                        const defaultOption = document.createElement('option');
                        defaultOption.value = '';
                        defaultOption.textContent = '---------';
                        profesionalSelect.appendChild(defaultOption);
                        
                        // Agregar profesionales
                        data.profesionales.forEach(profesional => {
                            const option = document.createElement('option');
                            option.value = profesional.id;
                            option.textContent = profesional.name;
                            profesionalSelect.appendChild(option);
                        });
                    });
            } else {
                profesionalSelect.innerHTML = '';
                const defaultOption = document.createElement('option');
                defaultOption.value = '';
                defaultOption.textContent = '---------';
                profesionalSelect.appendChild(defaultOption);
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    const calendar = new FullCalendar.Calendar(calendarEl, {
        // ... (configuración existente)
        
        selectConstraint: {
            startTime: '06:00',
            endTime: '22:00',
            daysOfWeek: [1, 2, 3, 4, 5] // Lunes a Viernes
        },
        
        selectAllow: function(selectInfo) {
            // Verificar si el horario seleccionado está disponible
            return fetch(`/api/horarios-disponibles/?profesional_id=${profesionalId}&fecha=${selectInfo.startStr}`)
                .then(response => response.json())
                .then(data => {
                    return data.disponible;
                });
        },
        
        eventRender: function(info) {
            // Resaltar citas según estado
            if (info.event.extendedProps.estado === 'P') {
                info.el.style.backgroundColor = '#ffc107'; // Amarillo para pendientes
            } else if (info.event.extendedProps.estado === 'C') {
                info.el.style.backgroundColor = '#28a745'; // Verde para confirmadas
            }
        }
    });
    
    calendar.render();
});