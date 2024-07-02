// Añade un event listener al input de tipo file ('fileInput') que se activa cuando cambia su valor
document.getElementById('fileInput').addEventListener('change', function () {
    // Obtiene el elemento <ul> con el ID 'fileList' donde se van a mostrar los archivos seleccionados
    const fileList = document.getElementById('fileList');

    // Itera sobre los archivos seleccionados por el usuario
    for (let i = 0; i < this.files.length; i++) {
        const file = this.files[i]; // Obtiene el archivo actual en el bucle

        // Crea un nuevo elemento <li> para representar un archivo en la lista
        const listItem = document.createElement('li');

        // Agrega clases CSS al <li> recién creado para darle formato
        listItem.classList.add('list-item', 'd-flex', 'justify-content-between', 'm-2');

        // Crea un elemento <h5> para mostrar el nombre del archivo
        const fileName = document.createElement('h5');
        fileName.classList.add('m-2'); // Agrega una clase para darle formato de margen
        fileName.textContent = file.name; // Establece el texto del <h5> con el nombre del archivo

        // Crea un botón para eliminar el archivo de la lista
        const removeButton = document.createElement('button');
        removeButton.classList.add('btn', 'btn_primary'); // Agrega clases CSS para darle formato de botón
        removeButton.innerHTML = '<i class="bi bi-x"></i>'; // Establece un icono 'x' dentro del botón

        // Añade un event listener al botón de eliminar para manejar su clic
        removeButton.addEventListener('click', function () {
            listItem.remove(); // Elimina el <li> completo al hacer clic en el botón de eliminar
        });

        // Añade el <h5> (nombre del archivo) y el botón de eliminar al <li>
        listItem.appendChild(fileName);
        listItem.appendChild(removeButton);

        // Añade el <li> completo (con el nombre del archivo y el botón de eliminar) al <ul> de fileList
        fileList.appendChild(listItem);
    }
});


document.addEventListener('DOMContentLoaded', ev => {
    const listItems = document.querySelectorAll('.list-item');
    const listVariablesSpan = document.querySelectorAll('.data-files tbody .var-form');
    const headerList = document.querySelector('.title-list');

    // Cuando se haga click en un item, se mostrará su tabla correspondiente al fileId
    listItems.forEach((listItem) =>
        listItem.addEventListener('click',function () {
            hiddenListItem();
            hiddenContent();

            listItem.classList.add('active_list');

            // Presento la tabla correspondiente al file seleccionado
            document.getElementById(`table${listItem.dataset.fileId}`).classList.add('table-display');
    }))


    // Botón para mostrar la descripción básica del proyecto (nombre, descripción, archivos)
    headerList.addEventListener('click', function() {
        hiddenContent();
        hiddenListItem();
        headerList.classList.add('active_list');
        document.querySelector('.data-container').classList.add('table-display');
    })

    // Función para quitarle el table-display a los que lo tengan
    function hiddenContent() {
        document.querySelectorAll('.table-display').forEach((tableDisplay) => {
                tableDisplay.classList.remove('table-display');
            });
    }

    // Función para quitarle el active_list a los item's que lo tengan
    function hiddenListItem() {
        document.querySelectorAll('.active_list').forEach((item) => {
                item.classList.remove('active_list');
            });
    }

    // Botón para cerrar las tablas de los files
    document.querySelector('.close-content').addEventListener('click', function () {
        hiddenContent();
        hiddenListItem();
        headerList.classList.add('active_list');
        document.querySelector('.data-container').classList.add('table-display');
    })


    // Cuando se hace click en alguna de las variables
    listVariablesSpan.forEach((content) => {
        const word = content.querySelector('span');
        const formWord = content.querySelector('.td-form');

        word.addEventListener('dblclick', function () {
            word.style.display = 'none';
            formWord.classList.add('form-display');

            const inputVar = formWord.querySelector('input[type="text"]');

            inputVar.value = word.textContent;

            // Le doy focus al hacer doble clic
            inputVar.focus();

            // Cuando se pierde el focus, se oculta el form y se muestra el span de nuevo
            // document.addEventListener('click', eve => {
            //     console.log(eve.target);

            inputVar.addEventListener('blur', function () {
                document.addEventListener('click', eve => {
                    if (formWord.className.includes('form-display')) {
                        word.style.display = 'block';
                        formWord.classList.remove('form-display');
                    }
                })
            })
            // })



        })

    })


    //  Doble click en el titulo o descripción del proyecto
    const spansProject = document.querySelectorAll('.data-container > form span');
    const buttons = document.querySelectorAll('.data-container > form button');
    const titleProject = spansProject[0].textContent;
    const textProject = spansProject[1].textContent;

    spansProject.forEach((span) =>
        span.addEventListener('dblclick', function () {
            const input = span.nextElementSibling;

            span.style.display = 'none';
            input.style.display  = 'block';

            input.value = span.textContent;

            input.focus();

            input.addEventListener('change',function () {

                span.textContent = input.value;

                checkInputs();
            })

            // Cuando se pierde el focus, se oculta el form y se muestra el span de nuevo
            input.addEventListener('blur', function () {
                if (input.style.display === 'block') {
                    span.style.display = 'block';
                    input.style.display  = 'none';
                }
            })

        })
    )

    // Checkeamos si los input's han sido alterados
    function checkInputs() {
        if (spansProject[0].textContent !== titleProject || spansProject[1].textContent !== textProject) {
            buttons.forEach(btn=> {
                btn.classList.remove('disabled');
            })
        } else {
            buttons.forEach(btn=> {
                btn.classList.add('disabled');
            })
        }

    }

    // Botón para deshacer los cambios hechos por el usuario
    buttons[1].addEventListener('click', function () {
        spansProject[0].textContent = titleProject;
        spansProject[1].textContent = textProject;
        checkInputs();
    })

    // Escuchamos cualquier evento submit o de envío de datos para actualizar
    document.addEventListener('submit',eve => {
        eve.preventDefault();
        const formData = new FormData(eve.target);

        if (eve.target.action.includes('update_project')) {
            fetch(eve.target.action,{
                    method: 'POST',
                    body: formData,
                })
                .then(response=> response.json())
                .then(data => {
                    if (data.message) {

                    }
                })
            .catch(error => {
                console.log('Error: ', error);
            })
        } else {
            console.log("No es el form")
        }
    })


})
