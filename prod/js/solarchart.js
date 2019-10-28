function SolarChart(root, data) {
    // Margins around the chart:
    const margins = {
        left: 60,
        right: 20,
        top: 20,
        bottom: 40,
    };

    // Append chart and legend to root element:
    var chartRoot = root.append('svg').attr('id', 'chart')
                                      .classed('framed', true)
                                      .attr('preserveAspectRatio', 'xMidYMid meet');
    var legendRoot = root.append('div').attr('id', 'legend')
                                       .classed('framed', true);

    // Setup marker:
    chartRoot.append('marker').lower()
                              .attr('id', 'arrowhead')
                              .attr('viewBox', "0 0 10 10")
                              .attr('refX', '0')
                              .attr('refY', '5')
                              .attr('markerUnits', 'strokeWidth')
                              .attr('markerWidth', '16')
                              .attr('markerHeight', '8')
                              .attr('preserveAspectRatio', 'none')
                              .attr('orient', 'auto')
                              .append('path').attr('d', 'M 0 0 L 10 5 L 0 10 z')
                                             .style('fill', '#000000');

    // Create label:
    var xLabel = chartRoot.append('g').classed('label', true);
    xLabel.append('text');
    var yLabel = chartRoot.append('g').classed('label', true);
    yLabel.append('text').attr('transform', 'rotate(-90)');

    // Create plot root element:
    var plotRoot = chartRoot.append('g').attr('transform', "translate(" + margins.left + "," + margins.top + ")");

    // Create grid:
    var yGrid = plotRoot.append('g').classed('grid', true);

    // Create axes:
    var xAxis = plotRoot.append('g').classed('axis', true)
                                    .attr('id', 'xaxis');
    var yAxis = plotRoot.append('g').classed('axis', true)
                                    .attr('id', 'yaxis');

    // Create legend:
    var legend = new SolarLegend(legendRoot);

    // Draw an axis:
    var drawAxis = function(selection, axis) {
        // Add axis and get axis domain:
        var domain = selection.raise().call(axis).select('.domain');

        // Remove last tick (even if not visble for marker):
        var d = domain.attr('d');
        if (d.endsWith('0') || d.endsWith('6'))
            d = d.slice(0, -2);
        domain.attr('d', d);

        // Add/remove marker
        domain.attr('marker-end', (axis.tickSizeOuter() == 0) ? 'url(#arrowhead)' : null);

        // Move ticks to the right so that they are at band boundaries:
        if (axis.tickSizeOuter() != 0) {
            var ticks = selection.selectAll('.tick').select('line');
            ticks.attr('x1', this.plot.data.xTickCenter());
            ticks.attr('x2', this.plot.data.xTickCenter());
        }
    };

    // Change data (and update plot):
    this.setData = function(data) {
        var ow = null;
        var oh = null;
        // Remove old plot:
        if (this.plot !== undefined) {
            ow = this.plot.width();
            oh = this.plot.height();
            data.variable(this.plot.data.variable());
            data.aggregation(this.plot.data.aggregation());
            this.plot.remove();
        }
        // Create new plot:
        if ((data instanceof LineData) && !data.isEmpty())
            this.plot = new LinePlot(plotRoot);
        else if ((data instanceof HistData) && !data.isEmpty())
            this.plot = new HistPlot(plotRoot);
        else
            this.plot = new EmptyPlot(plotRoot);
        this.plot.setData(data);
        // Resize new plot to old plot size:
        this.plot.resize(ow, oh);
        // Draw new plot:
        this.draw();
    };

    // Chart resize event:
    var resizeTimer; // Timer to ensure the chart is not updated continuously
    this.resize = function(w, h) {
        // Legend width between 175px and 250px
        var lw = 175 + 75*(w - 6 - 700)/(1000 - 700);
        if (lw > 250)
            lw = 250;
        if (lw < 175)
            lw = 0;
        // Chart width:
        var cw = w - lw - (8*(lw != 0));

        // Manages legend:
        if (lw == 0) {
            legendRoot.style('display', 'none');
        } else {
            legendRoot.style('display', 'inline-block')
                      .style('width', (lw - 10) + 'px')
                      .style('height', h + 'px')
                      .style('margin-left', '8px');
        }

        chartRoot.attr('width', cw)
                 .attr('height', h);

        // Update plot size only after some time:
        if (resizeTimer !== undefined)
            clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            resizeTimer = undefined;

            chartRoot.attr('viewBox', "0 0 " + cw + " " + h);
            this.plot.resize(cw - margins.left - margins.right, h -  margins.top - margins.bottom);
            xLabel.attr('transform', "translate(" + ((cw + margins.left - margins.right) / 2) + "," + (h - 8) + ")");
            yLabel.attr('transform', "translate(20," + ((h + margins.top - margins.bottom) / 2) + ")");

            this.redraw();
        }, 100);
    };

    // Draw the chart: Create the plot elements
    this.draw = function()
    {
        xAxis.selectAll('text').classed('cursor', false);
        chartRoot.on('mousemove', null)
                 .on('click', null);
        chartRoot.selectAll('.cursor').remove();
        chartRoot.selectAll('.selected').classed('selected', false);

        if (this.plot.draw()) {
            legend.clear();
            if (this.plot.legendStyle)
                legend.draw(this.plot.legendData, this.plot.legendStyle);
        } else {
            this.hide();
            return false;
        }

        return this.redraw();
    }

    // Redraw the chart: Position the plot, the axes and the grid
    this.redraw = function()
    {
        // Redraw plot:
        if (!this.plot.redraw())
            return false;

        // Draw axes and grid:
        yGrid.lower().call(this.plot.data.yGrid).select('.domain').remove();
        drawAxis.call(this, xAxis, this.plot.data.xAxis);
        drawAxis.call(this, yAxis, this.plot.data.yAxis);
        xAxis.attr('transform', "translate(0, " + this.plot.data.yScale(0) + ")");

        // Draw labels:
        xLabel.select('text').text(this.plot.data.xLabel);
        yLabel.select('text').text(this.plot.data.yLabel());

        return true;
    };

    // Removes the current axes:
    this.hide = function() {
        legend.clear();

        xLabel.select('text').text('');
        yLabel.select('text').text('');

        yGrid.selectAll('*').remove();
        xAxis.selectAll('*').remove();
        yAxis.selectAll('*').remove();
    };

    this.enableCursor = function(enable) {
        var enabled = this.plot.enableCursor(enable, () => {
            var w = d3.max(this.plot.data.xScale.range());
            var h = d3.max(this.plot.data.yScale.range());

            if (d3.event.type == HistPlot.CURSOR_TYPE) {
                var xAxisLabels = xAxis.selectAll('text');
                xAxisLabels.classed('cursor', false);
                plotRoot.select('.cursor').remove();

                if (d3.event.detail) {
                    xAxisLabels.filter((d) => (d == d3.event.detail.x)).classed('cursor', true);
                    plotRoot.append('text').classed('cursor', true)
                                           .text(d3.event.detail.y/this.plot.data.div)
                                           .attr('y', -5 + this.plot.data.yScale(d3.event.detail.y/this.plot.data.div))
                                           .attr('x', (d, i, n) => {
                        var hw = n[0].getBBox().width/2;
                        var x = this.plot.data.xScale(d3.event.detail.x) + d3.event.detail.xFrac*this.plot.data.xScale.bandwidth();

                        if (x - hw < 5)
                            return 5 + hw;
                        if (x + hw > w)
                            return  w - hw;
                        return x;
                    });
                }
            } else if (d3.event.type == LinePlot.CURSOR_TYPE) {
                var selectedLine = d3.event.detail.line;

                var xCursor = plotRoot.select('#xcursor');
                var yCursor = plotRoot.select('#ycursor');

                if (xCursor.empty()) {
                    xCursor = plotRoot.append('g').classed('cursor', true)
                                                  .attr('id', 'xcursor')
                                                  .style('display', 'none');
                    xCursor.append('line').attr('y2', -h);
                    xCursor.append('line').attr('y2', 6).style('stroke-dasharray', 'none');
                    xCursor.append('rect').attr('fill', 'background');
                    xCursor.append('text').attr('y', 10)
                                        .attr('dy', '0.71em')
                                        .style('text-anchor', 'middle');
                }

                if (yCursor.empty()) {
                    yCursor = plotRoot.append('g').classed('cursor', true)
                                                  .attr('id', 'ycursor')
                                                  .style('display', 'none');
                    yCursor.append('line').attr('x2', w / 1.025);
                    yCursor.append('line').attr('x2', -6).style('stroke-dasharray', 'none');
                    yCursor.append('rect').attr('fill', 'background');
                    yCursor.append('text').attr('x', -9)
                                        .attr('dy', '0.32em')
                                        .style('text-anchor', 'end');
                }

                chartRoot.selectAll('.selected').classed('selected', false);
                selectedLine.classed('selected', true);

                chartRoot.on('mousemove', () => {
                    var data = selectedLine.data()[0];
                    xCursor.style('display', 'none');
                    yCursor.style('display', 'none');

                    var mousePos = d3.mouse(plotRoot.node());

                    if ((mousePos[0] < 0) ||
                        (mousePos[0] > w / 1.025) ||
                        (mousePos[1] < 0) ||
                        (mousePos[1] > h))
                        return;

                    var x = this.plot.data.xScale.invert(mousePos[0]);
                    var bisector = d3.bisector((d) => d.x);
                    var i = bisector.left(data, x);
                    var y = (i == 0) ? data[i].y : data[i].y + (data[i - 1].y - data[i].y) / (data[i - 1].x - data[i].x) * (x - data[i].x);

                    xCursor.style('display', null).attr('transform', 'translate(' + this.plot.data.xScale(x) + ', ' + h + ')');
                    yCursor.style('display', null).attr('transform', 'translate(0, ' + this.plot.data.yScale(y / this.plot.data.div) + ')');

                    xCursor.select('text').text(x.toLocaleTimeString());
                    yCursor.select('text').text(this.plot.data.yCursor(y));

                    plotRoot.selectAll('.cursor text').each(function() {
                        var bBox = this.getBBox();
                        d3.select(this.parentNode).select('rect').attr('x', bBox.x - 3)
                                                                 .attr('y', bBox.y)
                                                                 .attr('width', bBox.width + 6)
                                                                 .attr('height', bBox.height);
                    });
                });

                chartRoot.on('click', () => {
                    console.log('Cursor disabled');
                    chartRoot.on('mousemove', null);
                    chartRoot.on('click', null);

                    selectedLine.classed('selected', false);
                    xCursor.remove();
                    yCursor.remove();
                });
            }
        });

        if (!enabled) {
            chartRoot.on('mousemove', null);
            chartRoot.on('click', null);
            chartRoot.selectAll('.cursor').remove();
            chartRoot.selectAll('.selected').classed('selected', false);
        }
        legend.enableCursor(enabled);
        return enabled;
    };

    this.setData(new EmptyData([], '', '', ''));
}
