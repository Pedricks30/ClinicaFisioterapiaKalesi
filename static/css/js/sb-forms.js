document.addEventListener("DOMContentLoaded", function () {
    // Selecciona el input de archivo y el campo de texto
    const fileInput = document.getElementById("file-input");
    const fileNameDisplay = document.getElementById("file-name");
    const phoneInput = document.querySelector("#phone");
    const countryInput = document.querySelector("#country");

    // Verifica si el input de archivo y el campo de texto existen
    if (fileInput !== null && fileNameDisplay !== null) {
        fileInput.addEventListener("change", function () {
            if (fileInput.files.length > 0) {
                fileNameDisplay.value = fileInput.files[0].name;
            } else {
                fileNameDisplay.value = "";
            }
        });
    }

    // Inicializa intl-tel-input en el campo de teléfono si existe
    if (phoneInput) {
        var iti = window.intlTelInput(phoneInput, {
            initialCountry: "bo",
            separateDialCode: true,
            utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js",
        });
        phoneInput.addEventListener('blur', function () {
            var fullNumber = iti.getNumber();
            phoneInput.value = fullNumber;
        });
    }

    // Inicializa country-select-js en el campo de país si existe
    if (countryInput) {
        $("#country").countrySelect({
            defaultCountry: "bo",
            responsiveDropdown: true
        });
    }
});

// Script de de calcular la edad

// Cierra las alertas automáticamente después de 3 segundos si existen
setTimeout(function () {
    var alerts = document.querySelectorAll('.alert');
    if (alerts.length) {
        alerts.forEach(function (alert) {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(function () {
                alert.remove();
            }, 500);
        });
    }
}, 3000); // 3000 milisegundos = 3 segundos

