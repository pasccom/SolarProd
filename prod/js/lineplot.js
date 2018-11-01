function LinePlot(root) {
    this.lines = undefined;

    this.legendStyle = (function(selection) {
        selection.classed('legenditem', true);
        selection.style('color', (d) => this.getD3(d).style('stroke'));
        selection.style('opacity', (d) => this.getD3(d).style('stroke-opacity'));
    }).bind(this);

    this.remove = function()
    {
        if (this.lines !== undefined)
            this.lines.remove();
    };

    // Set the attributes correctly (draw the chart)
    this.draw = function()
    {
        // Manages all lines:
        if (this.lines === undefined)
            this.lines = root.selectAll('g.nonexistent');
        this.lines = this.lines.data(this.data);
        this.lines.exit().remove();
        this.lines = this.lines.enter().append('g').merge(this.lines);

        // Manages groups of lines (by inverter):
        var linesGroups = this.lines.selectAll('g').data((d) =>
            Array.isArray(d.y[0]) ? d.y.map((a) => {
                return {x: d.x, y: a};
            }) : [d]
        );
        linesGroups.exit().remove();
        linesGroups = linesGroups.enter().append('g').merge(linesGroups);
        linesGroups.attr('stroke', (d, i) => d3.interpolateInferno(0.9 - 0.45*i/linesGroups.size()));

        // Manages individual lines (by string):
        var paths = linesGroups.selectAll('path').data((d) =>
            Array.isArray(d.y[0]) ? d.y.map((a) =>
                a.map((e, i) => {
                    return {x: d.x[i], y:e};
                })
            ) : [d.y.map((e, i) => {
                return {x: d.x[i], y: e};
            })]
        );
        paths.exit().remove();
        paths = paths.enter().append('path').classed('line', true).merge(paths);

        // Draws lines:
        var line = d3.line().x((d) => this.data.xScale(d.x))
                            .y((d) => this.data.yScale(d.y/this.data.div));
        paths.attr('d', line)
             .attr('stroke-opacity', (d, i) => (0.9 - 0.7*i*linesGroups.size()/paths.size()));

        // Data for legend:
        this.legendData = d3.select(this.lines.node()).selectAll('g').nodes().map((g) =>
            d3.select(g).selectAll('path').nodes().map((p) =>
                d3.select(p)
            )
        );


        return true;
    };
}
LinePlot.prototype = SolarPlot;
