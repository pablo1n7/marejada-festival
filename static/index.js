
  //LABELLA JS
  
  // var data = [
  //   {date: new Date(1970, 4,18), 
  //     name:'Centro Nacional Patagónico (CENPAT) comenzó a funcionar'},
  //   {date: new Date(1991, 4,18), 
  //     name: 'Inauguración edificio actual UNPSBJ sede Madryn'},

  //   {date: new Date(2024, 11,21), 
  //     name: 'Hoy - Festival'},
  // ];

var data_save = null

var init_timeline = function (data) {
  var options =   {
    margin: {left: 20, right: 20, top: 20, bottom: 20},
    initialWidth: 1000,
    initialHeight: 1000,
  };
  
  var innerWidth =  options.initialWidth - options.margin.left - options.margin.right;
  var innerHeight = options.initialHeight - options.margin.top - options.margin.bottom;
  var colorScale = d3.scale.category10();
  //var colorScale = d3.scaleOrdinal(d3.schemeCategory10);

  d3.select('#timeline').html('');  
  var vis = d3.select('#timeline')
    .append('svg')
    .attr('width',  options.initialWidth)
    .attr('height', options.initialHeight)
    .append('g')
    .attr('transform', 'translate('+(options.margin.left)+','+(options.margin.top)+')');
  
  function labelText(d){
    return d.anio + ' - ' + d.name;
  }
  
  
  
  var dummyText = vis.append('text');
  
  var timeScale = d3.time.scale()
    .domain(d3.extent(data, function(d){return d.date;}))
    .range([0, innerHeight])
    .nice();
  
  var nodes = data.map(function(movie){
    var bbox = dummyText.text(labelText(movie))[0][0].getBBox();
    movie.h = bbox.height;
    movie.w = bbox.width;
    return new labella.Node(timeScale(movie.date), movie.h + 4, movie);
  });
  
  dummyText.remove();
  
  vis.append('line')
    .classed('timeline', true)
    .attr('y2', innerHeight);
  
  var linkLayer = vis.append('g');
  var labelLayer = vis.append('g');
  var dotLayer = vis.append('g');
  
  dotLayer.selectAll('circle.dot')
    .data(nodes)
    .enter().append('circle')
    .classed('dot', true)
    .attr('r', 3)
    .attr('cy', function(d){return d.getRoot().idealPos;});
  
  function color(d,i){
    //return '#1D1F20';
    if (d.data.user == 0){
      return '#1D1F20';
    }else{
      return '#6d932a';
    }
    
  }
  
  var renderer = new labella.Renderer({
    layerGap: 60,
    nodeHeight: nodes[0].width,
    direction: 'right'
  });
  
  function draw(nodes){
    renderer.layout(nodes);
  
    var sEnter = labelLayer.selectAll('rect.flag')
      .data(nodes)
      .enter().append('g')
      .attr('transform', function(d){return 'translate('+(d.x)+','+(d.y-d.dy/2)+')';});
  
    sEnter
      .append('rect')
      .classed('flag', true)
      .attr('width', function(d){ return d.data.w +  (d.data.w  * 0.5); })
      .attr('height', function(d){ return d.dy; })
      .attr('rx', 2)
      .attr('ry', 2)
      .style('fill', color);
  
    sEnter
      .append('text')
      .attr('x', 4)
      .attr('y', 15)
      .style('fill', '#D4F6F0')
      .text(function(d){return labelText(d.data);});
  
    linkLayer.selectAll('path.link')
      .data(nodes)
      .enter().append('path')
      .classed('link', true)
      .attr('d', function(d){return renderer.generatePath(d);})
      .style('stroke', color)
      .style('stroke-width',2)
      .style('opacity', 0.6)
      .style('fill', 'none');
  }
  
  var force = new labella.Force({
    minPos: -10
  })
    .nodes(nodes)
    .compute();
  
  draw(force.nodes());
  
}  

const socket = io.connect('http://192.168.1.110:5000');

// // Obtener datos iniciales
// fetch('/data')
//     .then(response => response.json())
//     .then(data => {
//       // Recorre los elementos del array y actualiza la fecha
//       const updatedData = data.map(item => {
//         // Asegúrate de que la propiedad 'date' exista antes de modificarla
        
//           item.date = new Date(item.anio, item.mes, item.dia);  // Cambia el valor de 'date' a un objeto Date
        
//         return item;  // Retorna el elemento actualizado
//       })
//       init_timeline(updatedData);}
//     )
//     // .then(data => init_timeline(data));

// Recibir datos nuevos a través del WebSocket
   socket.on('update_data', function(data) {
    const updatedData = data.map(item => {
              item.date = new Date(item.anio, item.mes, item.dia);  // Cambia el valor de 'date' a un objeto Date
              return item;})
    if (data_save != null){
      data.sort((a, b) => b.hito - a.hito);
      Toastify({
        newWindow: true,
        close: true,
        oldestFirst:false,
        duration: 300000,
        text: data[0].anio + ' - ' + data[0].name + ': ' + data[0].des,
        className: "info",
        style: {
          background: "linear-gradient(to right, #018979, #618425)",
        }
      }).showToast();
    }
    data_save = updatedData
    init_timeline(updatedData)
});

