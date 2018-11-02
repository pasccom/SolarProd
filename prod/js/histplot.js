function HistPlot(root) {
    var groups;

    this.legendStyle = (function(selection) {
        selection.classed('legenditem', true);
        selection.style('color', (d) => this.getD3(d).style('fill'));
        selection.style('background-color', (d) => this.getD3(d).style('fill'));
        selection.style('opacity', (d) => this.getD3(d).style('fill-opacity'));
    }).bind(this);

    this.remove = function()
    {
        if (groups !== undefined)
            groups.remove();
    };

    // Set the attributes correctly (draw the plot)
    this.draw = function()
    {
        // Manages groups:
        if (groups === undefined)
            groups = root.selectAll('g.nonexistent');
        groups = groups.data(this.data);
        groups.exit().remove();
        groups = groups.enter().append('g').merge(groups);

        // Manages subGroups:
        var nGroups = d3.max(this.data, (d) => Array.isArray(d.y) ? d.y.length : 1);
        var subGroups = groups.selectAll('g');
        subGroups = subGroups.data((d) => Array.isArray(d.y) ? d.y : [d.y]);
        subGroups.exit().remove();
        subGroups = subGroups.enter().append('g').merge(subGroups);
        subGroups.attr('transform', (d, i) => ("translate(" + (this.data.xScale.bandwidth()*i/nGroups) + ",0)"))
                .attr('fill', (d, i) => d3.interpolateInferno(0.9 - 0.45*i/nGroups))
                .attr('stroke', (d, i) => d3.interpolateInferno(0.9 - 0.45*i/nGroups));

        // Manages bars:
        var nBars = d3.max(this.data, (d) => {
            return Array.isArray(d.y) ? d3.max(d.y, (a) => Array.isArray(a) ? a.length : 1) : 1;
        });
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
        groups.attr('transform', (d) => ("translate(" + (this.data.xScale(d.x) + 0.01*this.data.xScale.bandwidth()/nGroups/nBars) + ",0)"));

        // Data for legend:
        this.legendData = d3.transpose(groups.nodes().map((g1) => {
            return d3.select(g1).selectAll('g').nodes();
        })).map((g1) => {
            return d3.transpose(g1.map((g2) => {
                return d3.select(g2).selectAll('rect').nodes().map((r) => d3.select(r));
            }));
        });

        return true;
    };
}

HistPlot.prototype = SolarPlot;
