function HistPlot() {
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
        this.groups = this.groups.data(this.data);
        this.groups.exit().remove();
        this.groups = this.groups.enter().append('g').merge(this.groups);

        // Manages subGroups:
        var nGroups = d3.max(this.data, (d) => Array.isArray(d.data) ? d.data.length : 1); // TODO move
        var subGroups = this.groups.selectAll('g');
        subGroups = subGroups.data((d) => Array.isArray(d.data) ? d.data : [d.data]);
        subGroups.exit().remove();
        subGroups = subGroups.enter().append('g').merge(subGroups);
        subGroups.attr('transform', (d, i) => ("translate(" + (this.data.xScale.bandwidth()*i/nGroups) + ",0)"))
                .attr('fill', (d, i) => d3.interpolateInferno(0.9 - 0.45*i/nGroups))
                .attr('stroke', (d, i) => d3.interpolateInferno(0.9 - 0.45*i/nGroups));

        // Manages bars:
        var nBars = d3.max(this.data, (d) => Array.isArray(d.data) ? d3.max(d.data, (a) => Array.isArray(a) ? a.length : 1) : 1); // TODO move
        var bars = subGroups.selectAll('rect');
        bars = bars.data((d) => Array.isArray(d) ? d : [d]);
        bars.style('display', 'initial');
        bars.exit().remove();
        bars = bars.enter().append('rect').classed('bar', true).merge(bars);

        // Draw bars:
        bars.attr('x', (d, i) => this.data.xScale.bandwidth()*i/nGroups/nBars)
            .attr('y', (d) => this.data.yScale(d/this.data.div))
            .attr('width', 0.98*this.data.xScale.bandwidth()/nGroups/nBars)
            .attr('height', (d) => (this.data.yScale(0) - this.data.yScale(d/this.data.div)))
            .attr('fill-opacity', (d, i) => (0.25 + 0.5*i/nBars));

        // Places groups:
        this.groups.attr('transform', (d) => ("translate(" + (this.data.xScale(d.date) + 0.01*this.data.xScale.bandwidth()/nGroups/nBars) + ",0)"));

        // Data for legend:
        this.legendData = this.groups.filter((d, i) => (i == 0)).selectAll('g').selectAll('rect');

        return true;
    };
}

HistPlot.prototype = SolarPlot;
