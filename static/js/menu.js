let mainCont = document.querySelector('.main-container');

// Botón sidebar para mostrar y ocultar el sidebar
document.querySelector('.sidebar-btn').addEventListener('click', function() {
    mainCont.classList.toggle('hidden-sb');
})

// Pantalla de Blur del sidebar cuando sea en dispositivos smartphone
// Cuando se haga clic en  este, el sidebar se repliega, el blur se oculta y se le devuelve el scroll al body
document.querySelector('.blur-section').addEventListener('click', function() {
    mainCont.classList.add('hidden-sb');
    document.querySelector('.body').style.overflow = 'scroll';
})

// Botón del Navbar para mostrar el sidebar y por ende el blur
// Mostramos el sidebar
document.querySelector('.navbar-btn').addEventListener('click', function() {
    mainCont.classList.remove('hidden-sb');
    document.querySelector('.body').style.overflow = 'hidden';
})


// document.addEventListener('DOMContentLoaded', function() {
//     // Verificar el estado guardado del sidebar en sessionStorage
//     var sidebar = document.getElementById('sidebar');
//     var toggleButton = document.getElementById('toggleSidebar');
//
//     // Si no hay estado guardado, inicializar con el sidebar visible
//     if (!sessionStorage.getItem('sidebarState')) {
//         sidebar.classList.remove('hidden-sb');
//     } else {
//         // Aplicar el estado guardado
//         var sidebarState = sessionStorage.getItem('sidebarState');
//         if (sidebarState === 'hidden') {
//             sidebar.classList.add('hidden-sb');
//         } else {
//             sidebar.classList.remove('hidden-sb');
//         }
//     }
//
//     // Escuchar clic en el botón de toggle del sidebar
//     toggleButton.addEventListener('click', function() {
//         sidebar.classList.toggle('hidden-sb');
//
//         // Guardar el estado actual en sessionStorage
//         if (sidebar.classList.contains('hidden-sb')) {
//             sessionStorage.setItem('sidebarState', 'hidden');
//         } else {
//             sessionStorage.setItem('sidebarState', 'visible');
//         }
//     });
// });