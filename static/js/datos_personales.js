document.getElementById('uploadButton').addEventListener('click', function () {
    document.getElementById('id_profile_picture').click();
});

document.getElementById('id_profile_picture').addEventListener('change', function () {
            var file = this.files[0];
            if (file) {
                // Actualizar el valor del input de texto con el nombre del archivo
                document.getElementById('fileName').value = file.name;

                // Crear un objeto URL para la imagen seleccionada
                var reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('image_profile').src = e.target.result;
                }
                reader.readAsDataURL(file);
            }
        });

function limpiarFormulario() {
    document.getElementById('newPassword').value = '';
    document.getElementById('confirmPassword').value = '';
    document.getElementById('newPassword').style.borderColor = 'white';
    document.getElementById('confirmPassword').style.borderColor = 'white';
    document.getElementById('mensaje_validacion').textContent = ''; // Limpiar también el mensaje de validación
}