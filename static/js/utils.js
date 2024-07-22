// Función para activar el blur de carga
function blur_active() {
    $d.querySelector('.blur-shadow').classList.add('shadow-loader');
    if ($d.querySelector('.modal')) {$d.querySelector('.modal').style.zIndex = 4;}
    if ($d.querySelector('.modal-backdrop.show')) {$d.querySelector('.modal-backdrop.show').style.zIndex = 2}
}

// Función para desactivar el blur de carga
function blur_inactive() {
    $d.querySelector('.blur-shadow').classList.remove('shadow-loader');
}