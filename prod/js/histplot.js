function HistPlot(root, data) {
    this.init(root, data);
    this.groups = undefined;

    this.legendStyle = (function(selection) {
        selection.classed('legenditem', true);
        selection.style('color', (d) => this.getD3(d).style('fill'));
        selection.style('background-color', (d) => this.getD3(d).style('fill'));
        selection.style('opacity', (d) => this.getD3(d).style('fill-opacity'));
    }).bind(this);

    this.remove = function()
    {
        if (this.groups !== undefined)
            this.groups.remove();
    };

    // Set the attributes correctly (draw the plot)
    this.draw = function()
    {
        // Manages groups:
        if (this.groups === undefined)
            this.groups = this.root.selectAll('g.nonexistent');
        this.groups = this.groups.data(data);
        this.groups.exit().remove();
        this.groups = this.groups.enter().append('g').merge(this.groups);

        // Manages subGroups:
        var nGroups = d3.max(data, (d) => Array.isArray(d.data) ? d.data.length : 1); // TODO move
        var subGroups = this.groups.selectAll('g');
        subGroups = subGroups.data((d) => Array.isArray(d.data) ? d.data : [d.data]);
        subGroups.exit().remove();
        subGroups = subGroups.enter().append('g').merge(subGroups);
        subGroups.attr('transform', function(d, i) {return "translate(" + (data.xScale.bandwidth()*i/nGroups) + ",0)";})
                .attr('fill', function(d, i) {return d3.interpolateInferno(0.9 - 0.45*i/nGroups);})
                .attr('stroke', function(d, i) {return d3.interpolateInferno(0.9 - 0.45*i/nGroups);});

        // Manages bars:
        var nBars = d3.max(data, (d) => Array.isArray(d.data) ? d3.max(d.data, (a) => Array.isArray(a) ? a.length : 1) : 1); // TODO move
        var bars = subGroups.selectAll('rect');
        bars = bars.data((d) => Array.isArray(d) ? d : [d]);
        bars.style('display', 'initial');
        bars.exit().remove();
        bars = bars.enter().append('rect').classed('bar', true).merge(bars);

        // Draw bars:
        bars.attr('x', function(d, i) {return data.xScale.bandwidth()*i/nGroups/nBars;})
            .attr('y', function(d) {return data.yScale(d/data.div);})
            .attr('width', 0.98*data.xScale.bandwidth()/nGroups/nBars)
            .attr('height', function(d) {return data.yScale(0) - data.yScale(d/data.div);})
            .attr('fill-opacity', function(d, i) {return 0.25 + 0.5*i/nBars;});

        // Places groups:
        this.groups.attr('transform', function(d) {return "translate(" + (data.xScale(d.date) + 0.01*data.xScale.bandwidth()/nGroups/nBars) + ",0)";});

        // Draw axes and legend:
        this.legendData = this.groups.filter(function(d, i) {return i == 0;}).selectAll('g').selectAll('rect');
        drawLegend(this.groups.filter(function(d, i) {return i == 0;}).selectAll('g').selectAll('rect'));

        return true;
    };
}

HistPlot.prototype = SolarPlot;
