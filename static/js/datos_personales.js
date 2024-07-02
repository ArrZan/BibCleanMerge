document.getElementById('uploadButton').addEventListener('click', function () {
    document.getElementById('id_profile_picture').click();
});

document.getElementById('id_profile_picture').addEventListener('change', function () {
    var valor = this.files[0].name;
    document.getElementById('fileName').value = valor;
});

document.getElementById('confirmPassword').addEventListener('input', validatePassword);

function validatePassword() {
    var newPassword = document.getElementById('newPassword').value;
    var confirmPassword = document.getElementById('confirmPassword').value;
    var validationMessage = document.getElementById('mensaje_validacion');

    if (newPassword === confirmPassword && newPassword !== "") {
        document.getElementById('newPassword').style.borderColor = 'green';
        document.getElementById('confirmPassword').style.borderColor = 'green';
        validationMessage.textContent = "Las contraseñas coinciden.";
        validationMessage.style.color = 'green';
    } else {
        document.getElementById('newPassword').style.borderColor = 'red';
        document.getElementById('confirmPassword').style.borderColor = 'red';
        validationMessage.textContent = "Las contraseñas no coinciden.";
        validationMessage.style.color = 'red';
    }
}

document.getElementById('limpiarButton').addEventListener('click', limpiarFormulario);

function limpiarFormulario() {
    document.getElementById('newPassword').value = '';
    document.getElementById('confirmPassword').value = '';
    document.getElementById('newPassword').style.borderColor = 'white';
    document.getElementById('confirmPassword').style.borderColor = 'white';
    document.getElementById('mensaje_validacion').textContent = ''; // Limpiar también el mensaje de validación
}