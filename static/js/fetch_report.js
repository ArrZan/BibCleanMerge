$d.addEventListener('submit', ev => {
    ev.preventDefault();

    const csrf = $d.querySelector('input[name="csrfmiddlewaretoken"]').value;

    const formData = new FormData(ev.target);

    fetch(ev.target.action,{
        method: 'POST',
        headers: {
            'X-CSRFToken': csrf,
        },
        body: formData,
    })
    .then(response=> response.json())
    .then(data => {
        if (data.message) {
            window.location.href = ev.target.dataset.successUrl;
        }  else if (data.error) {
            // Desactivamos pantalla de carga
            appendAlert(data.error, "danger", 'modalAlertPlaceholder2');
        }
    })
    .catch(error => {
        console.log('Error: ', error);
    })
})

function createProject() {
    $d.getElementById('submit-btn').click();
}


$d.addEventListener('click', function(event) {
    //  Si existe el botón de guardar proyecto...
    if ($d.querySelector('.cont-report > .row button')) {

        const anchor = event.target.closest('a');

        // Verifica si el clic ocurrió dentro de un enlace (<a>) o en el propio enlace
        if (anchor && anchor.tagName === 'A') {
            event.preventDefault();  // Evita la acción por defecto del enlace
            // Aquí puedes mostrar un mensaje al usuario o realizar alguna acción
            $d.querySelector('.card-header .btn-close').click();
        }
    }
});

