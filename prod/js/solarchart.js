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

    // Create plot root element:
    var plotRoot = chartRoot.append('g').attr('transform', "translate(" + margins.left + "," + margins.top + ")");

    // Create grid:
    var yGrid = plotRoot.append('g').classed('grid', true);

    // Create axes:
    var xAxis = plotRoot.append('g').classed('axis', true)
                                    .attr('id', 'xaxis');
    var yAxis = plotRoot.append('g').classed('axis', true)
                                    .attr('id', 'yaxis');

    // Create label:
    var xLabel = chartRoot.append('g').classed('label', true);
    xLabel.append('text');
    var yLabel = chartRoot.append('g').classed('label', true);
    yLabel.append('text').attr('transform', 'rotate(-90)');

    // Create legend:
    legend = new SolarLegend(legendRoot);

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
        if (data.isEmpty())
            this.plot = new EmptyPlot(plotRoot);
        else if (data.type == SolarData.Type.DAY)
            this.plot = new LinePlot(plotRoot);
        else
            this.plot = new HistPlot(plotRoot);
        this.plot.setData(data);
        // Resize new plot to old plot size:
        this.plot.resize(ow, oh);
        // Draw new plot:
        this.draw();
    };

    // Chart resize event:
    this.resize = function(w, h) {
        // Timer to ensure the chart is not updated continuously:
        var resizeTimer;

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

            this.draw();
        }, 100);
    };

    // Draw the axes (and the grid)
    this.draw = function()
    {
        if (this.plot.draw()) {
            legend.clear();
            if (this.plot.legendStyle)
                legend.draw(this.plot.data.aggregation(), this.plot.legendData, this.plot.legendStyle);
        } else {
            this.hide();
            return false;
        }

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

    this.setData(new EmptyData([], '', '', ''));
}
