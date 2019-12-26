function LinePlot(root) {
    var lines;
    var xCursor = null;
    var yCursor = null;

    this.legendStyle = (function(selection) {
        selection.classed('line', true);
        selection.style('color', (d) => this.getD3(d).style('stroke'));
        selection.style('opacity', (d) => this.getD3(d).style('stroke-opacity'));
    }).bind(this);

    this.remove = function()
    {
        if (lines !== undefined)
            lines.remove();
    };

    // Set the attributes correctly (draw the chart)
    this.draw = function()
    {
        // Manages all lines:
        if (lines === undefined)
            lines = root.selectAll('g.nonexistent');
        lines = lines.data(this.data);
        lines.exit().remove();
        lines = lines.enter().append('g').merge(lines);

        // Manages groups of lines (by inverter):
        var linesGroups = lines.selectAll('g').data((d) => {
            return Array.isArray(d.y[0]) ? d.y.map((a) => {
                return {x: d.x, y: a};
            }) : [d];
        });
        linesGroups.exit().remove();
        linesGroups = linesGroups.enter().append('g').merge(linesGroups);
        linesGroups.attr('stroke', (d, i) => d3.interpolateInferno(0.9 - 0.45*i/linesGroups.size()));

        // Manages individual lines (by string):
        var paths = linesGroups.selectAll('path').data((d) => {
            return Array.isArray(d.y[0]) ? d.y.map((a) => {
                return a.map((e, i) => {
                    return {x: d.x[i], y:e};
                });
            }) : [d.y.map((e, i) => {
                return {x: d.x[i], y: e};
            })];
        });
        paths.exit().remove();
        paths = paths.enter().append('path').classed('line', true).merge(paths);

        // Draws lines:
        paths.attr('stroke-opacity', (d, i) => (0.9 - 0.7*i*linesGroups.size()/paths.size()))
             .on('mouseenter', null)
             .on('mouseleave', null)
             .on('click', null);

        // Data for legend:
        this.legendData = this.data.aggregateLegend(d3.selectAll(lines.nodes()).selectAll('g').nodes().map((g) => {
            return d3.select(g).selectAll('path').nodes().map((p) => d3.select(p));
        }));

        return d3.select();
    };

    this.redraw = function() {
        if (lines === undefined)
            return false;

        var linesGroups = lines.selectAll('g');
        var paths = linesGroups.selectAll('path');

        var line = d3.line().x((d) => this.data.xScale(d.x))
                            .y((d) => this.data.yScale(d.y/this.data.div));
        paths.attr('d', line);

        return true;
    };

    this.enableCursor = function(enable, svg) {
        if (lines === undefined)
            return;

        lines.selectAll('path').on('mouseenter', !enable ? null : function() {d3.select(this).classed('hovered', true);})
                               .on('mouseleave', !enable ? null : function() {d3.select(this).classed('hovered', false);})
                               .on('click', !enable ? null : (d, i, nodes) => {
            var selectedLine = d3.select(nodes[i]);

            d3.event.stopPropagation();

            if (xCursor === null) {
                xCursor = root.append('g').classed('cursor', true)
                                          .attr('id', 'xcursor')
                                          .style('display', 'none');
                xCursor.append('line').attr('y2', 0);
                xCursor.append('line').attr('y2', 6).style('stroke-dasharray', 'none');
                xCursor.append('rect').style('fill', '-moz-default-background-color');
                xCursor.append('text').attr('y', 10)
                                      .attr('dy', '0.71em')
                                      .style('text-anchor', 'middle');
            }

            if (yCursor === null) {
                yCursor = root.append('g').classed('cursor', true)
                                          .attr('id', 'ycursor')
                                          .style('display', 'none');
                yCursor.append('line').attr('x2', 0);
                yCursor.append('line').attr('x2', -6).style('stroke-dasharray', 'none');
                yCursor.append('rect').style('fill', '-moz-default-background-color');
                yCursor.append('text').attr('x', -9)
                                      .attr('dy', '0.32em')
                                      .style('text-anchor', 'end');
            }

            root.selectAll('.selected').classed('selected', false);
            selectedLine.classed('selected', true);

            svg.on('mousemove', () => {
                console.log('Cursor mouse move');

                var w = d3.max(this.data.xScale.range());
                var h = d3.max(this.data.yScale.range());
                var data = selectedLine.data()[0];

                xCursor.style('display', 'none');
                yCursor.style('display', 'none');

                var mousePos = d3.mouse(root.node());

                if ((mousePos[0] < 0) ||
                    (mousePos[0] > w / 1.025) ||
                    (mousePos[1] < 0) ||
                    (mousePos[1] > h))
                    return;

                var x = this.data.xScale.invert(mousePos[0]);
                var bisector = d3.bisector((d) => d.x);
                var i = bisector.left(data, x);
                var y = (i == 0) ? data[i].y : data[i].y + (data[i - 1].y - data[i].y) / (data[i - 1].x - data[i].x) * (x - data[i].x);

                xCursor.selectAll('line').filter(function() {return d3.select(this).attr('y2') <= 0;}).attr('y2', -h);
                yCursor.select('line').filter(function() {return d3.select(this).attr('x2') >= 0;}).attr('x2', w / 1.025);

                xCursor.style('display', null).attr('transform', 'translate(' + this.data.xScale(x) + ', ' + h + ')');
                yCursor.style('display', null).attr('transform', 'translate(0, ' + this.data.yScale(y / this.data.div) + ')');

                xCursor.select('text').text(x.toLocaleTimeString());
                yCursor.select('text').text(this.data.yCursor(y));

                root.selectAll('.cursor text').each(function() {
                    var bBox = this.getBBox();
                    d3.select(this.parentNode).select('rect').attr('x', bBox.x - 3)
                                                             .attr('y', bBox.y)
                                                             .attr('width', bBox.width + 6)
                                                             .attr('height', bBox.height);
                });
            });

            svg.on('click', () => {
                svg.on('mousemove', null);
                svg.on('click', null);

                selectedLine.classed('selected', false);
                xCursor.remove();
                yCursor.remove();
                xCursor = null;
                yCursor = null;
            });
        });

        if (!enable) {
            svg.on('mousemove', null);
            svg.on('click', null);

            root.selectAll('.selected').classed('selected', false);
            xCursor.remove();
            yCursor.remove();
            xCursor = null;
            yCursor = null;
        }

        return enable;
    };
}

LinePlot.prototype = SolarPlot;
