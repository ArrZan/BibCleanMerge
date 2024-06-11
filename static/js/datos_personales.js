document.getElementById('uploadButton').addEventListener('click', function () {
    document.getElementById('formFile').click();
});

document.getElementById('formFile').addEventListener('change', function () {
    var fileName = this.files[0].name;
    document.getElementById('fileName').value = fileName;
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