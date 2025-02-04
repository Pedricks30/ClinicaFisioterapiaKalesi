document.addEventListener("DOMContentLoaded", function () {
    // Selecciona el input de archivo y el campo de texto
    const fileInput = document.getElementById("file-input");
    const fileNameDisplay = document.getElementById("file-name");

    // Escucha el evento change del input de archivo
    fileInput.addEventListener("change", function () {
        if (fileInput.files.length > 0) {
            // Actualiza el campo de texto con el nombre del archivo seleccionado
            fileNameDisplay.value = fileInput.files[0].name;
        } else {
            // Si no se selecciona ningún archivo, limpia el campo de texto
            fileNameDisplay.value = "";
        }
    });
});