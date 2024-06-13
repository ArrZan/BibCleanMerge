
// Obtener una referencia al elemento canvas del DOM
const $grafica = document.querySelector("#grafica");
// Las etiquetas son las porciones de la gráfica
const etiquetas = ["Articulos", "Conferencias", "Books", "Others"];
// Podemos tener varios conjuntos de datos. Comencemos con uno
const datosIngresos = {
    data: [var_dataReport['count_typeEnt']['article'],
            var_dataReport['count_typeEnt']['conference'],
            var_dataReport['count_typeEnt']['book'],
            var_dataReport['count_typeEnt']['others']], // La data es un arreglo que debe tener la misma cantidad de valores que la cantidad de etiquetas
    // Ahora debería haber tantos background colors como datos, es decir, para este ejemplo, 4
    backgroundColor: [
        'rgba(8,44,80,1)',
        'rgba(37, 99, 151, 1)',
        'rgba(255, 129, 24, 1)',
        'rgba(255,180,20,1)',
    ],// Color de fondo
    borderColor: [
        'rgba(8,44,80,1)',
        'rgba(37, 99, 151, 1)',
        'rgba(255, 129, 24, 1)',
        'rgba(255,180,20,1)',
    ],// Color del borde
    borderWidth: 1,// Ancho del borde
};
new Chart($grafica, {
    type: 'pie',// Tipo de gráfica. Puede ser dougnhut o pie
    data: {
        labels: etiquetas,
        datasets: [
            datosIngresos,
            // Aquí más datos...
        ]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'right', // Cambia la posición de la leyenda a la derecha
            },
        },
    },
});