const $d = document;
const blur_item = $d.querySelector('.blur-section-item');
const items = $d.querySelector('.items');

const csrf = $d.querySelector('input[name="csrfmiddlewaretoken"]').value;

// MOSTRAR DESCRIPCIÓN DEL PROYECTO -------------------------------------------------------------------------------------------------
function showDescription(element) {
    let item = element.parentElement;

    item.classList.toggle('show-display');
}

// MOSTRAR OPCIONES EN CELULAR ------------------------------------------------------------------------------------------------------
function showOptions(element) {
    const menu_option = element.parentElement;
    const item = menu_option.parentElement.parentElement.parentElement;

    // Añadimos un foco al item seleccionado con resalted
    item.classList.add('resalted');
    blur_item.classList.add('resalted');
    menu_option.style.zIndex = "2";

    // Fijamos la posición de ese item en la pantalla
    scrollToSection('smooth');

    // Mostramos el menu de opciones
    menu_option.classList.toggle('toggle');
    items.style.scroll = 'hidden';


    // Dejamos de hacer foco en el item seleccionado quitandole la clase resalted
    blur_item.addEventListener('click', (e) => {
        removeResalted(item, menu_option);
    });

    // Escuchamos el evento de resize para manejar cambios de orientación
    window.addEventListener('resize', function () {
        // Cada que se cambia, llamamos a la función para desplazarnos al item seleccionad
        if (window.matchMedia("(orientation: portrait)").matches) {
            // Orientación vertical
            scrollToSection();
        } else if (window.matchMedia("(orientation: landscape)").matches) {
            // Orientación horizontal
            scrollToSection();
        }
    });

    // Función para desplazar la página a la item.resalted cuando desplace a horizontal
    function scrollToSection(bhv='instant') {
        const sectionToScroll = $d.querySelector('.item.resalted');

        // Siempre que exista moverse hacia allá
        if (sectionToScroll) {
            sectionToScroll.scrollIntoView({ behavior: bhv });
            items.style.scroll = 'auto';
        }
    }

}


function removeResalted(item, menu_option) {
    item.classList.remove('resalted');
    blur_item.classList.remove('resalted');
    menu_option.style.zIndex = "0";
    menu_option.classList.remove('toggle');
    items.style.scroll = 'auto';
}

// Ocultar menú desplegable cuando se hace clic en otro lugar, si es que quitamos todos los efectos
// $d.addEventListener('click', function(event) {
//     let menus = $d.querySelectorAll('.menu-options');
//     menus.forEach(function(menu) {
//         if (!menu.contains(event.target)) {
//             menu.classList.remove('toggle');
//             menu.style.zIndex = "1";
//         }
//     });
// });


// CREAR UN PROYECTO -------------------------------------------------------------------------------------------------------

function createProject() {
    document.getElementById('submit-btn').click();
}




// ELIMINAR ALGÚN PROYECTO -------------------------------------------------------------------------------------------------------

function showDeleteModal(button) {
    const projectId = button.getAttribute("data-project-id");
    const projectUrl = button.getAttribute("data-project-url");
    // Damos el nombre del proyecto al modal-body
    $d.getElementById("project-name").textContent = $d.querySelector(`[data-project-id="${projectId}"] .title-pj`).textContent;

    // Así mismo le damos al data-project-id el id del button
    $d.getElementById('delete-project-id').dataset.projectId = projectId;
    $d.getElementById('delete-project-id').dataset.projectUrl = projectUrl;
}


// Función para eliminar el proyecto
function deleteProject(element) {
    const projectId = element.dataset.projectId;
    const buttonDelete = $d.querySelector('#delete-project .btn-close');
    const url_view = element.dataset.projectUrl;

    // Mandamos a procesar
    fetch(url_view,{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf,
        },
    })
    .then(response => response.json())
    .then(data => {
        const menu_option = buttonDelete.parentElement.parentElement;
        const item  = menu_option.parentElement.parentElement.parentElement;

        // Removemos el item seleccionado
        $d.querySelector(`[data-project-id="${projectId}"]`).remove();

        $d.getElementById("project-name").textContent = '';
        // Así mismo le damos al data-project-id el id del button
        $d.getElementById('delete-project-id').dataset.projectId = '';

        // Salimos del modal
        buttonDelete.click();

        appendAlert(data.message, "success", 'bodyAlertPlaceholder');


        removeResalted(item, menu_option);
        verificateItems();
    })
    .catch(error => {
        console.log('Error: ', error);
    })

}



// SALVAGUARDAR UN PROYECTO -------------------------------------------------------------------------------------------------
function saveProject(element) {
    const url_view = element.dataset.projectUrl;

     // Mandamos a procesar
    fetch(url_view,{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf,
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            const item = document.querySelector(`[data-project-id="${element.dataset.projectId}"]`);

            item.querySelector('.option-info').remove();
            item.classList.remove('item-False');

            appendAlert(data.message, "success", 'bodyAlertPlaceholder');
        } else if (data.error) {

            console.log(data.error)
            appendAlert(data.error, "danger", 'bodyAlertPlaceholder');
        }
    })

}






$d.addEventListener("DOMContentLoaded", function () {
    const fileList = $d.getElementById("file-list");

    const addFileButton = $d.getElementById("add-file-button");

    const fileInput = $d.getElementById("file-input");
    
    const btnSendFiles = $d.getElementById("btn-send-files");



    let files_upload = {};
    let contDict = 0;
    let currentTotalSize = 0;

    // Si existe algún archivo autoguardado se abrirá esto
    if ($d.querySelector('.info-modal-autosave')) {
        $d.querySelector('.info-modal-autosave').click();
    }

    // Si existe algún proyecto se ocultará la imagen
    verificateItems();


    // FUNCIÓN PARA AGREGAR ARCHIVOS -------------------------------------------------------------------------------------------
    function addFiles(arrayFile) {
        for (let i = 0; i < arrayFile.length; i++) {
            const file = arrayFile[i];
            const len_files_upload = contDict;
    
            contDict += 1;
            
            // Verificar que el archivo tenga la extensión .bib
            if (file.name.endsWith('.bib')) {
                // Calculamos el peso del archivo
                const fileSizeMB = file.size / (1024 * 1024);

                // Sumar el tamaño al peso total
                currentTotalSize += fileSizeMB;

                // Mostrar el peso total actualizado
                updateTotalSizeElement();
    
                // Agregamos el archivo a la variable
                files_upload[len_files_upload] = file;
    
                // CreaciÃ³n del elemento HTML para mostrar cada archivo seleccionado
                const fileElement = $d.createElement("div");
                fileElement.className = "col mt-2";
                
                fileElement.innerHTML = `
                    <div class="square">
                        <div class="img-file">
                            <svg viewBox="91.758 41.85 326.107 413.488" xmlns="http://www.w3.org/2000/svg">
                                <path d="M 168.558 41.973 L 297.076 41.973 L 297.076 41.85 L 417.865 158.612 L 417.796 158.612 L 417.796 381.189 C 417.796 407.526 396.445 428.877 370.108 428.877 L 361.823 428.877 L 361.823 399.525 C 377.291 396.656 389.004 383.093 389.004 366.793 L 389.004 158.612 L 317.053 158.612 C 304.571 156.547 297.912 148.656 297.076 134.938 L 297.076 70.765 L 182.954 70.765 C 164.567 70.765 149.662 85.67 149.662 104.057 L 149.662 309.043 L 120.87 309.043 L 120.87 89.661 C 120.87 63.324 142.221 41.973 168.558 41.973 Z" style="stroke: rgb(0, 0, 0); stroke-width: 0px;" />
                                <text style="font-family: Arial, sans-serif; font-size: 133.8px; font-weight: 700; letter-spacing: 9.6px; white-space: pre;" x="91.758" y="427.338">BIB</text>
                            </svg>
                            <button class="delete-file" data-file="${file.name}/${len_files_upload}">
                                <i class="bi bi-x-lg"></i>
                            </button>
                        </div>
                    </div>
                    <div class="text">${file.name}</div>
                `;
    
                fileList.insertBefore(fileElement, fileList.querySelector(".add-file"));
    
                // Event listener para el botón de eliminar asociado a cada archivo
                fileElement.querySelector(".delete-file").addEventListener("click", function () {
                    // Obtener el key del archivo que se va a eliminar
                    const keyFile = this.getAttribute("data-file").split('/')[1];

                    // Restar el tamaño del archivo eliminado del peso total
                    const fileSize = files_upload[keyFile].size / (1024 * 1024);
                    currentTotalSize -= fileSize;

                    // Mostrar el peso total actualizado
                    updateTotalSizeElement();

                    /// Lo quitamos de la lista a enviar al form
                    delete files_upload[keyFile];
    
    
                    // Eliminar el elemento visualmente
                    this.parentElement.parentElement.parentElement.remove();
                });
            }
            else {
                appendAlert(`Debe ser formato .bib: ${file.name}`, 'danger');
            }

        }


        // Resetear el input de archivos para permitir nuevas selecciones
        fileInput.value = "";
    }

    // Actualizamos el peso de todos los archivos subidos
    function updateTotalSizeElement() {
    const infoFiles = $d.querySelector(".info-files");
    if (infoFiles) {
        infoFiles.querySelector('strong').textContent = `${currentTotalSize.toFixed(2)} MB`;
    }}


    // BOTÓN PARA SUBIR ARCHIVOS DEL MODAL -------------------------------------------------------------------------------------------

    // Cuando hagamos clic en el boton, es como si hicieramos clic en el input file 
    addFileButton.addEventListener("click", function () {
        fileInput.click();
    });

    // Cuando se sube uno o más archivos, habrá un cambio y por ende se irá a subir los archivos
    fileInput.addEventListener("change", function (event) {
        const files = event.target.files;

        addFiles(files);

    });

    // Agregar event listener para los botones de eliminar existentes
    $d.querySelectorAll(".delete-file").forEach(function (button) {
        button.addEventListener("click", function () {
            this.parentElement.parentElement.parentElement.remove();
        });
    });


    // LÓGICA SOLTAR ARCHIVOS EN LA ZONA DE ARRASTRE ----------------------------------------------------------

    let dropZone = $d.getElementById('drop-zone');

    // Eventos de arrastre y soltar en la zona de arrastre
    dropZone.addEventListener('dragover', function(event) {
        event.preventDefault();
        event.stopPropagation();
        dropZone.classList.add('is-active');
    });

    // Eventos de salir de la zona de arrastre
    dropZone.addEventListener('dragleave', function(event) {
        event.preventDefault();
        event.stopPropagation();
        dropZone.classList.remove('is-active');
    });

    // Eventos de soltar el archivo en la zona de arrastre
    dropZone.addEventListener('drop', function(event) {
        event.preventDefault();
        event.stopPropagation();
        dropZone.classList.remove('is-active');

        const filesDropped = event.dataTransfer.files;

        addFiles(filesDropped);

    });

    // ENVIAR ARCHIVOS SELECCIONADOS AL BACKEND PARA PROCESAMIENTO RÁPIDO ----------------------------------------------------------------

    // Botón para enviar archivos al backend a procesar
    btnSendFiles.addEventListener('click', e => {

        if (Object.keys(files_upload).length > 0) {
            let url_view = btnSendFiles.dataset.projectUrl;

            let formData = new FormData();

            // Añadimos el csrf al formData
            formData.append('csrfmiddlewaretoken', csrf);

            // Agregar cada archivo seleccionado al formData
            for (let key in files_upload) {
                formData.append(key, files_upload[key]);
            }

            // Activamos pantalla de carga
            blur_active();

            // Mandamos a procesar
            fetch(url_view,{
                method: 'POST',
                body : formData,
            })
            .then(response => response.json())
            .then(data => {
                if (data.redirect_url) {
                    // Reenviar a la ruta de reportes con los datos del servidor, así mismo,
                    // mandarle una descarga automática del archivo merged.

                    window.location.href = data.redirect_url;
                } else if (data.error) {
                    // Desactivamos pantalla de carga
                    blur_inactive();
                    console.log(data.error_message)
                    appendAlert(data.error, "danger");
                }

            })
            .catch(error => {
                console.log('Error: ', error);
            })



            // Cerramos el modal.. aunque deberíamos dar retroalimentación de carga aquí o directamente en reporte con una animación de carga
            // $d.querySelector('#añadir_manual .btn-close').click();

        } else {
            appendAlert("No haz seleccionado ningún archivo!", "warning");
        }
    })


});

// MOSTRADOR DE ALERTAS DE BOOSTRAP ---------------------------------------------------------------

const appendAlert = (message, type, idAlertDiv='modalAlertPlaceholder') => {
    const alertPlaceholder = $d.getElementById(idAlertDiv);
    const wrapper = $d.createElement('div');
    wrapper.innerHTML = [
    `<div class="alert alert-${type} alert-dismissible" role="alert">`,
    `   <div>${message}</div>`,
    '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
    '</div>'
    ].join('');

    alertPlaceholder.append(wrapper);
};


// Función para verificar si hay items y presentar una imagne
function verificateItems() {
    if ($d.querySelector('.ct-body .item')) {
        $d.querySelector('.non-image').classList.add('n-inactive');
    } else {
        $d.querySelector('.non-image').classList.remove('n-inactive');
    }
}

// Función para activar el blur de carga
function blur_active() {
    $d.querySelector('.blur-shadow').classList.add('shadow-loader');
    $d.querySelector('.modal').style.zIndex = 4;
    $d.querySelector('.modal-backdrop.show').style.zIndex = 2;
}

// Función para desactivar el blur de carga
function blur_inactive() {
    $d.querySelector('.blur-shadow').classList.remove('shadow-loader');
}