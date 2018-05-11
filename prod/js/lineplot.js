function LinePlot(root, data) {
    this.init(root, data);
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
        if (this.lines === undefined)
            this.lines = chart.plotRoot.selectAll('g.nonexistent');
        this.lines = this.lines.data(data);
        this.lines.exit().remove();
        this.lines = this.lines.enter().append('g').merge(this.lines);

        // Get plotted variable:
        var variable = d3.select('#var').property('value');
        if (variable == '')
            variable = 0;
        var v = SolarData.shortVars[variable];

        // Get sum function:
        var sum = d3.select('#sum').property('value');
        if (sum == '')
            sum = 'sum';

        // Groups of lines (by inverter):
        var linesGroups = this.lines.selectAll('g').data(function(d) {
            if (v.endsWith('dc')) {
                if (sum == 'str')
                    return d[v].map(function(a) {return {
                        dates: d.dates,
                        data: a,
                    };});
                else if (sum == 'inv')
                    return d[v].map(function(a) {return {
                        dates: d.dates,
                        data: d3.transpose(a).map(function(e) {return d3.sum(e);}),
                    };});
                else
                    return [{
                        dates: d.dates,
                        data: d[v].map(function(a) {return d3.transpose(a).map(function(e) {return d3.sum(e);});}),
                    }];
            } else {
                if (sum == 'sum')
                    return [{
                        dates: d.dates,
                        data: d3.transpose(d[v]).map(function(a) {return d3.sum(a);}),
                    }];
                else
                    return d[v].map(function(a) {return {
                        dates: d.dates,
                        data: a,
                    };});
            }
        });
        linesGroups.exit().remove();
        linesGroups = linesGroups.enter().append('g').merge(linesGroups);
        linesGroups.attr('stroke', function(d, i) {return d3.interpolateInferno(0.9 - 0.45*i/linesGroups.size());});

        // Paths (by string):
        var paths = linesGroups.selectAll('path').data(function(d) {
            if (v.endsWith('dc')) {
                if (sum == 'str')
                    return d.data.map(function(a) {return d3.zip(d.dates, a);});
                else if (sum == 'inv')
                    return [d3.zip(d.dates, d.data)];
                else
                    return [d3.zip(d.dates, d3.transpose(d.data).map(function(e) {return d3.sum(e);}))];
            } else {
                return [d3.zip(d.dates, d.data)];
            }
        });
        paths.exit().remove();
        paths = paths.enter().append('path').classed('line', true).merge(paths);

        // Compute unit divider (TODO to be moved in data):
        var maxData = d3.max(paths.data(), function(a) {return d3.max(a, function(d) {return d[1];});});
        var div = 1;
        this.log1000Div = 0;
        while (maxData/div >= 1000) {
            div *= 1000;
            this.log1000Div += 1;
        }
        while (maxData/div < 1) {
            div /= 1000;
            this.log1000Div -= 1;
        }

        // Set scale domains:
        data.yScale.domain([0, maxData/div]);

        // Draws lines:
        var line = d3.line().x(function(d) {return data.xScale(d[0]);})
                            .y(function(d) {return data.yScale(d[1]/div);});
        paths.attr('d', line)
            .attr('stroke-opacity', function(d, i) {return 0.9 - 0.7*i*linesGroups.size()/paths.size();});

        // Draw axes and legend:
        //chart.draw(log1000Div);
        this.legendData = paths;
        drawLegend(paths);

        return true;
    };
}
LinePlot.prototype = SolarPlot;
