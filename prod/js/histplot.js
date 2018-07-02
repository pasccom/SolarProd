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
        if (this.groups === undefined)
            this.groups = this.root.selectAll('g.nonexistent');
        this.groups = this.groups.data(data);
        this.groups.exit().remove();
        this.groups = this.groups.enter().append('g').merge(this.groups);

        // Get plotted variable:
        var v = SolarData.shortVars[data.variable()];

        maxFun = function(a) {return d3.max(a, function(d) {return d3.max(d);});};
        if (v.endsWith('dc')) {
            if (data.sum() == 'sum') {
                sumFun = function(a) {return [[d3.sum(a, function(d) {return d3.sum(d);})]];};
                groupsFun = function(d) {return 1;};
                barsFun = function(d) {return 1;};
            } else if (data.sum() == 'inv') {
                sumFun = function(a) {return [a.map(function(d) {return d3.sum(d);})];};
                groupsFun = function(d) {return d[v].length;};
                barsFun = function(d) {return 1;};
            } else {
                sumFun = function(a) {return a;};
                groupsFun = function(d) {return d.length;};
                barsFun = function(d) {return d3.max(d[v], function(a) {return a.length});};
            }
        } else {
            if (data.sum() == 'sum') {
                sumFun = function(a) {return [[d3.sum(a)]];};
                groupsFun = function(d) {return 1;};
                barsFun = function(d) {return 1;};
            } else {
                sumFun = function(a) {return a.map(function(e) {return [e];});};
                groupsFun = function(d) {return d[v].length;};
                barsFun = function(d) {return 1;};
            }
        }

        // Compute unit divider:
        var maxData = d3.max(data, function(d) {return maxFun(sumFun(d[v]));});
        var div = data.divider(maxData);

        // Set scales padding/domain:
        //data.xScale.padding((data.sum() == 'sum') ? 0 : 0.1);
        data.xScale.padding((data.sum() == 'sum') ? 0 : 0.1);
        data.yScale.domain([0, maxData/div]);

        // Manages subGroups:
        var nGroups = d3.max(data, groupsFun);
        var subGroups = this.groups.selectAll('g');
        subGroups = subGroups.data(function(d) {return sumFun(d[v]);});
        subGroups.exit().remove();
        subGroups = subGroups.enter().append('g').merge(subGroups);
        subGroups.attr('transform', function(d, i) {return "translate(" + (data.xScale.bandwidth()*i/nGroups) + ",0)";})
                .attr('fill', function(d, i) {return d3.interpolateInferno(0.9 - 0.45*i/nGroups);})
                .attr('stroke', function(d, i) {return d3.interpolateInferno(0.9 - 0.45*i/nGroups);});

        // Manages bars:
        var nBars = d3.max(data, barsFun);
        var bars = subGroups.selectAll('rect');
        bars = bars.data(function(d) {return d;});
        bars.style('display', 'initial');
        bars.exit().remove();
        bars = bars.enter().append('rect').classed('bar', true).merge(bars);

        // Draw bars:
        bars.attr('x', function(d, i) {return data.xScale.bandwidth()*i/nGroups/nBars;})
            .attr('y', function(d) {return data.yScale(d/div);})
            .attr('width', 0.98*data.xScale.bandwidth()/nGroups/nBars)
            .attr('height', function(d) {return data.yScale(0) - data.yScale(d/div);})
            .attr('fill-opacity', function(d, i) {return 0.25 + 0.5*i/nBars;});

        // Places groups:
        this.groups.attr('transform', function(d) {return "translate(" + (data.xScale(d.date) + 0.01*data.xScale.bandwidth()/nGroups/nBars) + ",0)";});

        // Draw axes and legend:
        //chart.draw(log1000Div);
        this.legendData = this.groups.filter(function(d, i) {return i == 0;}).selectAll('g').selectAll('rect');
        drawLegend(this.groups.filter(function(d, i) {return i == 0;}).selectAll('g').selectAll('rect'));

        return true;
    };
}

HistPlot.prototype = SolarPlot;
