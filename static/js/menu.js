const $d = document;
let mainCont = $d.querySelector('.main-container');
const sidebarBtn = $d.querySelector('.sidebar-btn');
const blurSection = $d.querySelector('.blur-section');
const navbarBtn = $d.querySelector('.navbar-btn');

// Función para obtener el estado del sidebar desde localStorage
const getSidebarState = () => localStorage.getItem('sidebarState') === 'visible';

// Función para guardar el estado del sidebar en localStorage
const setSidebarState = (isVisible) => {
    localStorage.setItem('sidebarState', isVisible ? 'visible' : 'hidden');
};

// Inicializar el estado del sidebar
const initializeSidebar = () => {
    if (getSidebarState()) {
        mainCont.classList.remove('hidden-sb');
    } else {
        mainCont.classList.add('hidden-sb');
    }
};

// Llamada inicial para configurar el estado del sidebar
initializeSidebar();

// Botón del sidebar para mostrar y ocultar el sidebar
sidebarBtn.addEventListener('click', function() {
    if (getSidebarState()) {
        mainCont.classList.add('hidden-sb');
        setSidebarState(false);
    } else {
        mainCont.classList.remove('hidden-sb');
        setSidebarState(true);
    }
});

// Pantalla de Blur del sidebar cuando sea en dispositivos smartphone
// Cuando se haga clic en este, el sidebar se repliega, el blur se oculta y se le devuelve el scroll al body
blurSection.addEventListener('click', function() {
    mainCont.classList.add('hidden-sb');
    $d.querySelector('.body').style.overflow = 'scroll';
});

// Botón del Navbar para mostrar el sidebar y por ende el blur
// Mostramos el sidebar
navbarBtn.addEventListener('click', function() {
    mainCont.classList.remove('hidden-sb');
    $d.querySelector('.body').style.overflow = 'hidden';
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

    // Eliminar la alerta después de 3 segundos
    setTimeout(() => {
        wrapper.querySelector('.alert').classList.add('alert-slide-out');

        setTimeout(() => {
            wrapper.remove(); // Elimina el elemento del DOM
        }, 1001); // 1 segundo

    }, 3000); // 3000 milisegundos = 3 segundos
};
