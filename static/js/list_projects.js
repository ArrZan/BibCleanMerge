const $d = document;
// MOSTRAR DESCRIPCIÓN DEL PROYECTO -------------------------------------------------------------------------------------------------

function showDescription(element) {
    let item = element.parentElement;
    
    item.classList.toggle('show-display');
}

// MOSTRAR OPCIONES EN CELULAR ------------------------------------------------------------------------------------------------------

function showOptions(element) {
    let item = element.parentElement;

    item.classList.toggle('toggle');
}




// CREAR UN PROYECTO -------------------------------------------------------------------------------------------------------

function createProject() {
    const modalCreate = $d.getElementById('add_project');

    const titleProject = modalCreate.querySelector('#titleProject');
    const textProject = modalCreate.querySelector('#textProject');
    

    // FALTA VALIDAR LOS CAMPOS
    console.log(titleProject.value);
    console.log(textProject.value);
}




// ELIMINAR ALGÚN PROYECTO -------------------------------------------------------------------------------------------------------

function showDeleteModal(button) {
    const projectId = button.getAttribute("data-project-id");
    const projectName = $d.querySelector(`[data-project-id="${projectId}"] .title-pj`).textContent;

    // Damos el nombre del proyecto al modal-body
    $d.getElementById("project-name").textContent = projectName;
    // Así mismo le damos al data-project-id el id del button
    $d.getElementById('delete-project-id').dataset.projectId = projectId;
}

// Función para eliminar el proyecto
function deleteProject(element) {
    const projectId = element.dataset.projectId;
    const buttonDelete = $d.querySelector('#delete-project .btn-close');






    // AQUÍ MANDAREMOS EL FETCH PARA EL BACKEND Y ELIMINAR UN PROYECTO DE LA BASE DE DATOS, PARA LUEGO CON EL RESPONSE
    // LO ELIMINAMOS VISUALMENTE DE ACÁ






    // Removemos el item seleccionado
    $d.querySelector(`[data-project-id="${projectId}"]`).remove();

    $d.getElementById("project-name").textContent = '';
    // Así mismo le damos al data-project-id el id del button
    $d.getElementById('delete-project-id').dataset.projectId = '';

    // Salimos del modal
    buttonDelete.click();

}






$d.addEventListener("DOMContentLoaded", function () {
    const fileList = $d.getElementById("file-list");

    const addFileButton = $d.getElementById("add-file-button");

    const fileInput = $d.getElementById("file-input");
    
    const btnSendFiles = $d.getElementById("btn-send-files");



    let files_upload = {};
    let contDict = 0;


    // FUNCIÓN PARA AGREGAR ARCHIVOS -------------------------------------------------------------------------------------------
    function addFiles(arrayFile) {
        for (let i = 0; i < arrayFile.length; i++) {
            const file = arrayFile[i];
            const len_files_upload = contDict;
    
            contDict += 1;
            
            // Verificar que el archivo tenga la extensión .bib
            if (file.name.endsWith('.bib')) {
    
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



    // MOSTRADOR DE ALERTAS DE BOOSTRAP ---------------------------------------------------------------

    const alertPlaceholder = $d.getElementById('liveAlertPlaceholder')
    const appendAlert = (message, type) => {
        const wrapper = $d.createElement('div');
        wrapper.innerHTML = [
        `<div class="alert alert-${type} alert-dismissible" role="alert">`,
        `   <div>${message}</div>`,
        '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
        '</div>'
        ].join('');

        alertPlaceholder.append(wrapper);
    };




    // ENVIAR ARCHIVOS SELECCIONADOS AL BACKEND PARA PROCESAMIENTO RÁPIDO ----------------------------------------------------------------

    btnSendFiles.addEventListener('click', e => {

        let csrf = document.querySelector('[name=csrfmiddlewaretoken]').value;
        let url_view = "/project/fast_process/";

        let formData = new FormData();

        // Añadimos el csrf al formData
        formData.append('csrfmiddlewaretoken', csrf);

        // Agregar cada archivo seleccionado al formData
        for (let key in files_upload) {
            formData.append(key, files_upload[key]);
        }


        fetch(url_view,{
            method: 'POST',
            body : formData,
        })
        .then(response =>{
            return response.json();

        })
        .then(data => {
            console.log('Respuesta del server: ', data)

            // Reenviar a la ruta de reportes con los datos del servidor, así mismo,
            // mandarle una descarga automática del archivo merged.
            // window.location.href= '/proyecto/revision/';

        })
        .catch(error => {
            console.log('Error: ', error);
        })



        // Cerramos el modal.. aunque deberíamos dar retroalimentación de carga aquí o directamente en reporte con una animación de carga
        // $d.querySelector('#añadir_manual .btn-close').click();
    })


});
