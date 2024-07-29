// Define el mapeo de traducción
const translations = {
    'article': 'Artículo',
    'book': 'Libro',
    'conference': 'Conferencia',
    'others': 'Otros'
};

// Mapeamos los datos con las traducciones
const data = Object.keys(var_dataReport).map(function(key) {
    return {
        label: translations[key] || key, // Usar la traducción si existe, de lo contrario usar la clave original
        value: var_dataReport[key]
    };
});

// Especificamos las dimensiones del chart y que sea responsive.
const svg = d3.select("svg"),
      width = 500,
      height = Math.min(width, 275),
      radius = Math.min(width, height) / 2,
      legendWidth = 150,
      legendSpacing = 50;


const g = svg.append("g")
    .attr("transform", "translate(" + (width / 2 - legendWidth / 2) + "," + height / 2 + ")");


// Especificamos el color del pastel.
const color = d3.scaleOrdinal(["rgba(8,44,80,1)", "rgba(37, 99, 151, 1)", "rgba(255, 129, 24, 1)", "rgba(255,180,20,1)"]);


// Crear el diseño del pastel
const pie = d3.pie()
    .sort(null)
    .value(d => d.value)
    .padAngle(0);  // Espaciado entre los fragmentos del pastel


//  Especificamos el radio interno y externo del arco del pastel
const path = d3.arc()
    .innerRadius(0) // Radio interno
    .outerRadius(Math.min(width, height) / 2.45); // Radio externo


const label = d3.arc()
    .outerRadius(radius - 10) // Radio de las leyendas externo
    .innerRadius(radius - 10); // Radio de las leyendas interna







//Mando a crear el gráfico con los datos
function drawChart() {
    svg.attr("viewBox", "0 0 " + width + " " + height)
       .attr("preserveAspectRatio", "xMidYMid meet");

    const arc = g.selectAll(".arc")
        .data(pie(data));

    const arcEnter = arc.enter().append("g")
        .attr("class", "arc");

    arcEnter.append("path")
        .attr("d", path)
        .attr("fill", d => color(d.data.label))
        .on("mouseover", function(event, d) {
            d3.select(this.parentNode).raise();
        });

    // Agregar texto con fondo usando foreignObject
    arcEnter.append("foreignObject")
        .attr("transform", d => {
            // Ajustamos la posición vertical del texto de cada fragmento
            let centroid = label.centroid(d);
            return "translate(" + centroid[0] + "," + (centroid[1] - 15) + ")";
        })
        .attr("width", 40) // Ajusta el ancho según sea necesario
        .attr("height", 20) // Ajusta la altura según sea necesario
        .html(d => `<div class="text-background">${d.data.value}</div>`); // Valor numérico
        // .html(d => `<div class="text-background">${((d.data.value / d3.sum(data, d => d.value)) * 100).toFixed(1)}</div>`); // Porcentaje del valaor numérico

    arc.select("path")
        .attr("d", path);

    arc.select("text")
        .attr("transform", d => "translate(" + label.centroid(d) + ")");

    // Create legend
    const legend = svg.append("g")
        .attr("class", "legend")
        .attr("transform", "translate(" + (width - 150) + "," + 50 + ")") // Aquí muevo en x a la leyenda

    legend.selectAll("rect")
        .data(data)
        .enter().append("rect")
        .attr("x", 0)
        .attr("y", function(d, i) { return i * legendSpacing; })
        .attr("width", 18)
        .attr("height", 18)
        .style("fill", d => color(d.label));

    legend.selectAll("text")
        .data(data)
        .enter().append("text")
        .attr("x", 24)
        .attr("y", function(d, i) { return i * legendSpacing + 5; })
        .attr("dy", "0.35em")
        .text(function(d) { return d.label; });

}


drawChart();