function HistPlot(root) {
    var groups;
    var subGroups;
    var bars;

    var nGroups;
    var nBars;

    this.legendStyle = (function(selection) {
        selection.classed('bar', true);

        var color = function(e) {
            var color = d3.color(e.style('fill'));
            if (arguments[1] !== undefined)
                color.opacity = arguments[1];
            else
                color.opacity = e.style('fill-opacity');
            return color;
        };

        selection.style('color', (d) => color(this.getD3(d), 0));
        selection.style('background-color', (d) => color(this.getD3(d)));
        selection.style('border-width', '1px');
        selection.style('border-style', 'solid');
        selection.style('border-color', (d) => color(this.getD3(d), 1));
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
        groups.on('cursor', null);

        // Manages subGroups:
        nGroups = d3.max(this.data, (d) => Array.isArray(d.y) ? d.y.length : 1);
        subGroups = groups.selectAll('g');
        subGroups = subGroups.data((d) => Array.isArray(d.y) ? d.y : [d.y]);
        subGroups.exit().remove();
        subGroups = subGroups.enter().append('g').merge(subGroups);
        subGroups.attr('fill', (d, i) => d3.interpolateInferno(0.9 - 0.45*i/nGroups))
                 .attr('stroke', (d, i) => d3.interpolateInferno(0.9 - 0.45*i/nGroups))
                 .on('cursor', null);

        // Manages bars:
        nBars = d3.max(this.data, (d) => {
            return Array.isArray(d.y) ? d3.max(d.y, (a) => Array.isArray(a) ? a.length : 1) : 1;
        });
        bars = subGroups.selectAll('rect');
        bars = bars.data((d) => Array.isArray(d) ? d : [d]);
        bars.style('display', 'initial');
        bars.exit().remove();
        bars = bars.enter().append('rect').classed('bar', true).merge(bars);

        // Draw bars:
        bars.attr('fill-opacity', (d, i) => (0.25 + 0.5*i/nBars))
            .on('mouseenter', null)
            .on('mouseleave', null);

        // Data for legend:
        this.legendData = this.data.aggregateLegend(d3.transpose(groups.nodes().map((g1) => {
            return d3.select(g1).selectAll('g').nodes();
        })).map((g1) => {
            return d3.transpose(g1.map((g2) => {
                return d3.select(g2).selectAll('rect').nodes().map((r) => d3.select(r));
            }));
        }));

        return true;
    };

    this.redraw = function() {
        if (groups === undefined)
            return false;

        groups.attr('transform', (d) => ("translate(" + (this.data.xScale(d.x) + 0.01*this.data.xScale.bandwidth()/nGroups/nBars) + ",0)"));

        subGroups.attr('transform', (d, i) => ("translate(" + (this.data.xScale.bandwidth()*i/nGroups) + ",0)"));

        bars.attr('x', (d, i) => this.data.xScale.bandwidth()*i/nGroups/nBars)
            .attr('y', (d) => this.data.yScale(d/this.data.div))
            .attr('width', 0.98*this.data.xScale.bandwidth()/nGroups/nBars)
            .attr('height', (d) => (this.data.yScale(0) - this.data.yScale(d/this.data.div)));

        return true;
    };

    this.enableCursor = function(enable, listener) {
        if (groups === undefined)
            return;

        bars.on('mouseenter', !enable ? null : function(d) {
            var bar = d3.select(this).classed('hovered', true);
            bar.dispatch('cursor', {bubbles: true, detail: {d: d}});
        }).on('mouseleave', !enable ? null : function() {
            d3.select(this).classed('hovered', false);
            d3.customEvent(new Event(HistPlot.CURSOR_TYPE), listener);
        }).on('cursor', !enable ? null : function(d, i) {
            d3.event.detail.frac = i/nGroups/nBars;
        });

        subGroups.on('cursor', !enable ? null : function(d, i) {
            d3.event.detail.frac += i/nGroups;
        });

        groups.on('cursor', !enable ? null : function (d) {
            d3.event.stopPropagation();
            d3.customEvent(new CustomEvent(HistPlot.CURSOR_TYPE, {detail: {x: d.x, xFrac: d3.event.detail.frac + 1/2/nGroups/nBars, y:d3.event.detail.d}}), listener);
        });

        return enable;
    };
}

HistPlot.CURSOR_TYPE = 'HistCursor';
HistPlot.prototype = SolarPlot;
