var width = 1000,
    height = 1000;

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);

var force = d3.layout.force()
    .size([width, height]);

var tooltip = d3.select("body")
	.append("div")
	.attr("class", "tooltip")
    .style("opacity", 0);
    
d3.csv("Names_id_friends.csv", function(error, links) {
  if (error) throw error;

  var nodesByName = {};
  var rels = [];
  var linkedByIndex = {};

  // Create nodes for each unique source and target.
  links.forEach(function(link) {
    var id = nodeByName(link.id);
    var friend1 = nodeByName(link.Friend1id);
    var friend2 = nodeByName(link.Friend2id);
    var friend3 = nodeByName(link.Friend3id);
    var friend4 = nodeByName(link.Friend4id);
    var friend5 = nodeByName(link.Friend5id);
    var friend6 = nodeByName(link.Friend6id);

    if(link.Friend1id != ""){
        rels.push({
            source: id,
            target: friend1
        });
    }

    if(link.Friend2id != ""){
        rels.push({
            source: id,
            target: friend2
        });
    }

    if(link.Friend3id != ""){
        rels.push({
            source: id,
            target: friend3
        });
    }

    if(link.Friend4id != ""){
        rels.push({
            source: id,
            target: friend4
        });
    }

    if(link.Friend5id != ""){
        rels.push({
            source: id,
            target: friend5
        });
    }

    if(link.Friend6id != ""){
        rels.push({
            source: id,
            target: friend6
        });
    }

  });

  rels.forEach(function(d) {

    link = {
        source: d.source,
        target: d.target
    };
    linkedByIndex[`${d.source.index},${d.target.index}`] = 1;
  });

  // Extract the array of nodes from the map by name.
  var nodes = d3.values(nodesByName);

  // Create the link lines.
  var link = svg.selectAll(".link")
      .data(rels)
    .enter().append("line")
      .attr("class", "link");

  // Create the node circles.
  var node = svg.selectAll(".node")
      .data(nodes)
    .enter().append("circle")
      .attr("class", "node")
      .attr("r", 4.5)
      .call(force.drag)
      .on('mouseover.tooltip', function(d) {
        tooltip.transition()
          .duration(300)
          .style("opacity", .8);
        tooltip.html("ID:" + d.name)
          .style("left", (d3.event.pageX) + "px")
          .style("top", (d3.event.pageY + 10) + "px");
      })
      .on('mouseover.fade', fade(0.1))
      .on("mouseout.tooltip", function() {
        tooltip.transition()
          .duration(100)
          .style("opacity", 0);
      })
      .on('mouseout.fade', fade(1))
      .on("mousemove", function() {
        tooltip.style("left", (d3.event.pageX) + "px")
          .style("top", (d3.event.pageY + 10) + "px");
      })
      
      
    node.append('text')
        .attr('x', 0)
        .attr('dy', '.35em')
        .text(d => d.name);

  // Start the force layout.
  force
      .nodes(nodes)
      .links(rels)
      .on("tick", tick)
      .start();

  function tick() {
    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })

        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; })

    node.attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });
  }

  function nodeByName(name) {
    return nodesByName[name] || (nodesByName[name] = {name: name});
  }

  function isConnected(a, b) {
    return linkedByIndex[`${a.index},${b.index}`] || linkedByIndex[`${b.index},${a.index}`] || a.index === b.index;
  }

  function fade(opacity) {
    return d => {
      node.style('stroke-opacity', function (o) {
        const thisOpacity = isConnected(d, o) ? 1 : opacity;
        this.setAttribute('fill-opacity', thisOpacity);
        return thisOpacity;
      });

      link.style('stroke-opacity', o => (o.source === d || o.target === d ? 1 : opacity));

    };
  }
});