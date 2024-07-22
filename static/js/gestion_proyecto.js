

const csrf = $d.querySelector('input[name="csrfmiddlewaretoken"]').value;
// Doble clic en el título o descripción del proyecto
const spansProject = $d.querySelectorAll('.position-relative > span');
const submitBtn = $d.getElementById('submit-btn'); // Botón submit del form project
const cancelBtn = $d.querySelector('.data-container > form .btn_warning'); // Botón para cancelar del form project
let titleProject = spansProject[0].textContent; // Titulo del proyecto
let textProject = spansProject[1].textContent; // Descripción del proyecto

$d.addEventListener('DOMContentLoaded', ev => {
    // Añade un event listener al input de tipo file ('fileInput') que se activa cuando cambia su valor
    const btnAddFile = $d.getElementById('fileInput');

    let listItems = $d.querySelectorAll('.list-item');
    let listVariablesSpan = $d.querySelectorAll('.data-files tbody .var-form');
    const headerList = $d.querySelector('.title-list');


    btnAddFile.addEventListener('change', function () {

        // Función para validar la extensión de un archivo de imagen


        // Obtiene el elemento <ul> con el ID 'fileList' donde se van a mostrar los archivos seleccionados
        const fileList = $d.getElementById('fileList');
        let formData = new FormData();

        // Contador de archivos válidos
        let numArchivosValidos = 0;

        // Añadimos el csrf al formData
        formData.append('csrfmiddlewaretoken', csrf);

        // Agregar cada archivo seleccionado al formData
        for (let i = 0; i < this.files.length; i++) {
            const file = this.files[i]; // Obtiene el archivo actual en el bucle
            const fileName = file.name;
            const extPermitidas = /\.(bib)$/i; // extensiones permitidas

            // Verificar si la extensión está permitida
            if (!extPermitidas.test(fileName)) {
                const message = 'Al menos uno o más archivos no tienen el formato adecuado (.bib).';
                appendAlert(message, 'warning', 'bodyAlertPlaceholder');
            } else {
                formData.append('archivo' + i, file);
                numArchivosValidos++;
            }
        }

        if (numArchivosValidos > 0) {

            blur_active(); // Activamos blur de carga
            fetch(this.dataset.action,{
                    method: 'POST',
                    body: formData,
                })
                .then(response=> response.json())
                .then(data => {
                    blur_inactive()
                    if (data.message) {
                        addItems(fileList, data.entries);
                        this.value = "";
                    }  else if (data.error) {
                        // Desactivamos pantalla de carga
                        appendAlert(data.error, "danger");
                    }
                })
            .catch(error => {
                console.log('Error: ', error);
            })
        }
    });


    function addItems(fileList, data) {
        // Obtenemos la url enviada del backend
        const currentUrl = $d.getElementById('fileList').dataset.actionDelete;
        // Agrega los items a la list-item por cada archivo
        data.forEach((item) => {
            // Crea un nuevo elemento <li> para representar un archivo en la lista
            const listItem = $d.createElement('li');

            // Agrega clases CSS al <li> recién creado para darle formato
            listItem.classList.add('list-item');

            // Asignamos el id del item
            listItem.setAttribute('data-file-id', item.key);

            // Asignamos la nueva url
            let newUrl = currentUrl.replace(/\/\d+\/$/, `/${item.key}/`);
            console.log(newUrl);


            const fileNameCont = $d.createElement('div');
            fileNameCont.classList.add('list-item-title');
            const fileNameContDelete = $d.createElement('div');
            fileNameContDelete.classList.add('list-item-delete');

            fileNameContDelete.innerHTML = `
                <button class="btn btn_primary"><i class="bi bi-x"></i></button>
                <div class="box-dialog">
                    <span>Deseas borrar?</span>
                    <div class="box-options">
                        <button data-action="${newUrl}" class="btn btn_primary">Si</button>
                        <button class="btn btn_primary">No</button>
                    </div>
                </div>`

            // Crea un elemento <h5> para mostrar el nombre del archivo
            const fileName = $d.createElement('h5');
            fileName.textContent = item.name; // Establece el texto del <h5> con el nombre del archivo

            // Añade el <h5> (nombre del archivo) y el botón de eliminar al <li>
            fileNameCont.appendChild(fileName);

            listItem.appendChild(fileNameCont);
            listItem.appendChild(fileNameContDelete);

            // Añade el <li> completo (con el nombre del archivo y el botón de eliminar) al <ul> de fileList
            fileList.appendChild(listItem);

            createTable(item.key, item.entries);
            addVariable(item.key, item.name);
            listItemsActions(listItem);


        })
    }


    // Iteramos los listItems
    listItems.forEach((listItem) => {listItemsActions(listItem);})

    function addVariable(key, name) {
        const dataFiles =  $d.querySelector('.data-files');

        const trNode = $d.createElement('tr');
        const action = $d.querySelector('.data-files thead th.var');

        const urlAction = action.dataset.action.replace('1',key);

        trNode.innerHTML = `
          <td>${name}</td>
          <td class="var-form tr-${key}">
              <span>N/A</span>
              <div class="td-form">
                  <form class=" ms-2" action="${urlAction}" method="POST">
                    <input class="form-control me-2" name="pf_search_criteria" type="text" placeholder="N/A" aria-label="N/A">
                    <button class="btn btn_primary me-2 btn-submit" type="submit">
                        <i class="bi bi-check"></i>
                    </button>
                    <button class="btn btn_primary btn-cancel" type="button">
                        <i class="bi bi-x"></i>
                    </button>
                </form>
              </div>
          </td>`

        // Añadimos al tbody el tr recién creado
        dataFiles.querySelector('tbody').appendChild(trNode);
        listVar(trNode.querySelector('.var-form'));
    }

    function createTable(key, entries) {
        const CloseTablebtn = $d.querySelector('.container_content .close-content');

        let tableHTML = `
        <div class="col table_container">            
        </div>`

        let tableDiv = $d.createElement('div');

        tableDiv.classList.add('col', 'table_container');
        tableDiv.setAttribute('id', `table${key}`);

        tableDiv.innerHTML = `
        <table class="table table-striped table-hover">
            <thead>
                <tr>
                    <th scope="col">#</th>
                    <th scope="col">Título</th>
                    <th scope="col">Autores</th>
                    <th scope="col">Año</th>
                    <th scope="col">Keywords</th>
                    <th scope="col">Revista</th>
                    <th scope="col">Volumen</th>
                    <th scope="col">Número</th>
                    <th scope="col">Páginas</th>
                    <th scope="col">DOI</th>
                </tr>
            </thead>
            <tbody class="table-group-divider">
                ${entries.map((entry, index) =>`
                    <tr>
                        <th scope="row">${index + 1}</th>
                        <td>${entry.title}</td>
                        <td>${entry.author}</td>
                        <td>${entry.year}</td>
                        <td>${entry.keywords}</td>
                        <td>${entry.journal}</td>
                        <td>${entry.volume}</td>
                        <td>${entry.number}</td>
                        <td>${entry.pages}</td>
                        <td>${entry.doi}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>`

        // Coloca la nueva tabla antes del botón X
        CloseTablebtn.parentNode.insertBefore(tableDiv, CloseTablebtn);

    }

    // Movimiento de hover para los items cuando la pantalla se achique y oculte el contenido legible
    function listItemsActions(listItem) {
        const title = listItem.querySelector('.list-item-title');
        const h5 = listItem.querySelector('h5');
        const idFile = listItem.dataset.fileId;

        // Si el tamaño de la caja es menor al del texto...
        if (h5.scrollWidth > title.offsetWidth) {
            h5.classList.add('overflowing');
        }

        // Se desplazará en x
        listItem.addEventListener('mouseenter', function() {
            if (h5.scrollWidth > title.offsetWidth) {
                h5.classList.add('overflowing');
            }
        });

        // Se dejará de desplazar en x
        listItem.addEventListener('mouseleave', function() {
            h5.classList.remove('overflowing');
        });

        // Ocultará el list desplazado en dispositivos móviles
        $d.querySelector('.list-group').classList.remove('show-list');

        // Cuando se haga click en un item, se mostrará su tabla correspondiente al fileId
        listItem.addEventListener('click',event => {
            if (event.target.tagName !== 'I' && event.target.tagName !== 'BUTTON') {
                hiddenListItem();
                hiddenContent();

                listItem.classList.add('active_list');

                // Presento la tabla correspondiente al file seleccionado
                $d.getElementById(`table${idFile}`).classList.add('table-display');
            }
        })

        // Crea un botón para eliminar el archivo de la lista
        const questButton = listItem.querySelector('.list-item-delete > button');

        questButton.addEventListener('click', function () {
            questButton.nextElementSibling.classList.add('show-box');
        })

        // Tomamos el primero botón
        const deleteButton = listItem.querySelector('.box-options button')
        const cancelButton = listItem.querySelector('.box-options button:last-child')

        // Añade un event listener al botón de eliminar para manejar su clic
        deleteButton.addEventListener('click', function () {
            fetch(this.dataset.action,{
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrf,
                    },
                })
                .then(response=> response.json())
                .then(data => {
                    if (data.message) {
                        appendAlert(data.message,"success", 'bodyAlertPlaceholder');
                    }  else if (data.error) {
                    // Desactivamos pantalla de carga
                    appendAlert(data.error, "danger");
                }
                })
            .catch(error => {
                console.log('Error: ', error);
            })



            listItem.remove(); // Elimina el <li> completo al hacer clic en el botón de eliminar
            $d.querySelector(`tbody td.tr-${idFile}`).parentElement.remove(); // Eliminamos la variable
            $d.getElementById(`table${idFile}`).remove(); // Eliminamos la tabla
            $d.querySelector('.data-container').classList.add('table-display');
        });

        cancelButton.addEventListener('click', function () {
            questButton.nextElementSibling.classList.remove('show-box');
        })
    }

    // Función para mostrar la lista de archivos en dispositivos
    $d.querySelector('.header-list button').addEventListener('click', function () {
        $d.querySelector('.list-group').classList.toggle('show-list');
    })


    // Botón para mostrar la descripción básica del proyecto (nombre, descripción, archivos)
    headerList.addEventListener('click', function() {
        hiddenContent();
        hiddenListItem();
        headerList.classList.add('active_list');
        $d.querySelector('.data-container').classList.add('table-display');
    })

    // Función para quitarle el table-display a los que lo tengan
    function hiddenContent() {
        $d.querySelectorAll('.table-display').forEach((tableDisplay) => {
                tableDisplay.classList.remove('table-display');
            });
    }

    // Función para quitarle el active_list a los item's que lo tengan
    function hiddenListItem() {
        $d.querySelectorAll('.active_list').forEach((item) => {
                item.classList.remove('active_list');
            });
    }

    // Botón para cerrar las tablas de los files
    $d.querySelector('.close-content').addEventListener('click', function () {
        hiddenContent();
        hiddenListItem();
        headerList.classList.add('active_list');
        $d.querySelector('.data-container').classList.add('table-display');
    })


    // Cuando se hace doble click en alguna de las variables
    listVariablesSpan.forEach((content) => {
        listVar(content);
    })

    function listVar(content) {
        const word = content.querySelector('span');

        word.addEventListener('dblclick', function () {
            // content.classList.add('showing');

            const formWord = content.querySelector('.td-form');
            const btnCancel = formWord.querySelector('.btn-cancel');
            const btnSubmit = formWord.querySelector('.btn-submit');

            word.style.display = 'none';
            formWord.classList.add('form-display');

            // Le doy el texto del span al input
            const inputVar = formWord.querySelector('input[type="text"]');

            btnSubmit.disabled = inputVar.value === word.textContent || word.textContent === 'N/A'; // Deshabilitamos el botón si no hay valor alguno

            resetSpan();

            // Le doy focus al hacer doble clic
            inputVar.focus();

            inputVar.addEventListener('keyup', function () {
                btnSubmit.disabled = inputVar.value === word.textContent || inputVar.value === '';
            })

            // Cancelar el formulario y mostrar nuevamente el texto
            btnCancel.addEventListener('click', function(){
                content.classList.remove('showing');
                hiddenForm();
                resetSpan();
            });

            // Manejar el envío del formulario
            formWord.addEventListener('submit', function(event) {
                event.preventDefault(); // Prevenir el comportamiento por defecto del submit
                const newValue = inputVar.value;

                if (newValue === '') {
                    inputVar.value = 'N/A';
                }

                if (newValue !== word.textContent) {
                    const formData = new FormData(event.target);

                    fetch(event.target.action,{
                            method: 'POST',
                            headers: {
                                'X-CSRFToken': csrf,
                             },
                            body: formData,
                        })
                        .then(response=> response.json())
                        .then(data => {
                            if (data.message) {
                                appendAlert(data.message,"success", 'bodyAlertPlaceholder');
                            }

                            if (data.error) {
                                appendAlert(data.error,"danger", 'bodyAlertPlaceholder');
                            }
                        })
                    .catch(error => {
                        console.log('Error: ', error);
                    })
                }

                // Después de completar el envío, restaurar la visualización original
                word.textContent = inputVar.value;
                hiddenForm();
                content.classList.remove('showing');
            });

            inputVar.addEventListener('blur', function (event) {
                if (!event.relatedTarget ||
                    (event.relatedTarget !== btnCancel && event.relatedTarget !== btnSubmit)) {
                    hiddenForm();
                    resetSpan();
                    content.classList.remove('showing');
                }
            })

            function hiddenForm() {
                word.style.display = 'block';
                formWord.classList.remove('form-display');
            }

            function resetSpan() {
                if (word.textContent !== 'N/A') {
                    inputVar.value = word.textContent;
                } else {
                    inputVar.value = '';
                }
            }

        })


    }

    // Detectamos el doble click en los span del form
    spansProject.forEach(span => {
        span.addEventListener('dblclick', function() {
            validateAtt(this);
            cancelarLongPress();
        });

        // Eventos táctiles para detectar long press
        span.addEventListener('touchstart', function(event) {
            event.preventDefault(); // Evita el comportamiento táctil por defecto
            iniciarLongPress(this);
        });

        span.addEventListener('touchend', function(event) {
            event.preventDefault(); // Evita el comportamiento táctil por defecto
            cancelarLongPress();
        });

        span.addEventListener('touchmove', function(event) {
            event.preventDefault(); // Evita el comportamiento táctil por defecto
            cancelarLongPress();
        });
    });

    cancelBtn.addEventListener('click', resetChanges); // Función para deshacer cambios en el form


    // Función para manejar el long press
    let tiempoLongPress;
    const tiempoLongPressDuracion = 500; // Duración en milisegundos para considerar un long press

    function iniciarLongPress(span) {
        tiempoLongPress = setTimeout(function() {
            // Aquí se ejecuta la acción deseada al detectar un long press
            validateAtt(span);
            // Puedes ejecutar una función o realizar otras acciones aquí
        }, tiempoLongPressDuracion);
    }

    function cancelarLongPress() {
        clearTimeout(tiempoLongPress);
    }




    // Escuchamos evento submit
    $d.addEventListener('submit',eve => {
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
                        titleProject = spansProject[0].textContent;
                        textProject = spansProject[1].textContent;

                        $d.querySelector('.header-c .he-title h2').textContent = titleProject;
                        deactiveBtn();
                    }

                    if (data.errors) {
                        data.errors.prj_name.forEach(item=>{
                            if (item.code === 'unique') {
                                // Manejar el error específico 'unique' para el campo prj_name
                                appendAlert('Ya existe un proyecto con este nombre.', 'danger', 'bodyAlertPlaceholder');
                            }
                        })
                    }
                })
            .catch(error => {
                console.log('Error: ', error);
            })
        }
    })

})

function validateAtt(element) {
    const input = element.nextElementSibling;

    // Mostrar input y ocultar span, asignación del valor del span al input y focus del input
    element.style.display = 'none';
    input.style.display = 'block';
    input.value = element.textContent;
    input.focus();

    // Validar input
    input.addEventListener('keyup', function () {
        element.textContent = input.value;
        if ((input.name === 'prj_name' && input.value.length >= 10) || input.name === 'prj_description') {
            if (existChange()) {
                activeBtn();
                input.classList.remove('is-invalid');
            } else {
                deactiveBtn();
            }
        } else {
            deactiveBtn();
            input.classList.add('is-invalid');
        }
    });

    // Ocultar input y mostrar span al perder el foco
    input.addEventListener('blur', function () {
        if ((input.name === 'prj_name' && input.value.length >= 10) || input.name === 'prj_description' && input.style.display === 'block') {
            if (input.name === 'prj_description' && input.value.length === 0) {
                input.value = 'Sin descripción';
                element.textContent = 'Sin descripción';
                deactiveBtn();
            }
            element.style.display = 'block';
            input.style.display = 'none';
        }
    });
}

function deactiveBtn() {
    submitBtn.classList.add('disabled');
    cancelBtn.classList.add('disabled');
}

function activeBtn() {
    submitBtn.classList.remove('disabled');
    cancelBtn.classList.remove('disabled');
}

function existChange() {
    // Si hay cambios, se le quita el disabled
    return spansProject[0].textContent !== titleProject || spansProject[1].textContent !== textProject;
}

function resetChanges() {
    spansProject[0].textContent = titleProject;
    spansProject[1].textContent = textProject;
    if (existChange()) {
        activeBtn();
    } else {
        deactiveBtn();
    }
}

function resetSpanVar(element) {
    if (element.previousElementSibling !== 'N/A') {

        const form = element.parentElement.querySelector('form');

        form.querySelector('input[type="text"]').value = ''; // Reseteamos el value dle input
        element.previousElementSibling.textContent = 'N/A'; //  Reseteamos el texto del span
        console.log(element.previousElementSibling);
        form.querySelector('button[type="submit"]').click(); // Actualizamos
    }
}