function SolarChart(root, data) {
    // Append chart and legend to root element:
    this.chartRoot = root.append('svg').attr('id', 'chart')
                                       .classed('framed', true)
                                       .attr('preserveAspectRatio', 'xMidYMid meet');
    this.legendRoot = root.append('div').attr('id', 'legend')
                                        .classed('framed', true);

    // Setup marker:
    this.chartRoot.append('marker').lower()
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
    this.plotRoot = this.chartRoot.append('g').attr('transform', "translate(" + this.margins.left + "," + this.margins.top + ")");

    // Create grid:
    this.yGrid = this.plotRoot.append('g').classed('grid', true);

    // Create axes:
    this.xAxis = this.plotRoot.append('g').classed('axis', true)
                                          .attr('id', 'xaxis');
    this.yAxis = this.plotRoot.append('g').classed('axis', true)
                                          .attr('id', 'yaxis');

    // Create label:
    this.xLabel = this.chartRoot.append('g').classed('label', true);
    this.xLabel.append('text');
    this.yLabel = this.chartRoot.append('g').classed('label', true);
    this.yLabel.append('text').attr('transform', 'rotate(-90)');

    this.setData(data);
}

SolarChart.prototype = {
    // Margins around the chart:
    margins: {
        left: 60,
        right: 20,
        top: 20,
        bottom: 40,
    },
    // Change data (and update plot):
    setData: function(data) {
        var ow = null;
        var oh = null;
        // Remove old plot:
        if (this.plot !== undefined) {
            ow = this.plot.width();
            oh = this.plot.height();
            data.variable(this.plot.data.variable());
            data.sum(this.plot.data.sum());
            this.plot.remove();
        }
        // Create new plot:
        if (data.isEmpty())
            this.plot = new EmptyPlot(this.plotRoot, data);
        else if (data.type == SolarData.Type.DAY)
            this.plot = new LinePlot(this.plotRoot, data);
        else
            this.plot = new HistPlot(this.plotRoot, data);
        // Resize new plot to old plot size:
        this.plot.resize(ow, oh);
        // Draw new plot:
        this.draw();
    },
    // Chart resize event:
    resize: function(w, h) {
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
            this.legendRoot.style('display', 'none');
        } else {
            this.legendRoot.style('display', 'inline-block')
                           .style('width', (lw - 10) + 'px')
                           .style('height', h + 'px')
                           .style('margin-left', '8px');
        }

        this.chartRoot.attr('width', cw)
                      .attr('height', h);

        // Update plot size only after some time:
        if (this.resizeTimer !== undefined)
            clearTimeout(this.resizeTimer);
        this.resizeTimer = setTimeout(() => {
            this.resizeTimer = undefined;

            this.chartRoot.attr('viewBox', "0 0 " + cw + " " + h);
            this.plot.resize(cw - this.margins.left - this.margins.right, h -  this.margins.top - this.margins.bottom);
            this.xLabel.attr('transform', "translate(" + ((cw + this.margins.left - this.margins.right) / 2) + "," + (h - 8) + ")");
            this.yLabel.attr('transform', "translate(20," + ((h + this.margins.top - this.margins.bottom) / 2) + ")");

            this.draw();
        }, 100);
    },
    // Draw the axes (and the grid)
    draw: function()
    {
        if (!this.plot.draw()) {
            this.hide();
            return false;
        }

        // Draw axes and grid:
        this.yGrid.lower().call(this.plot.data.yGrid).select('.domain').remove();
        this.drawAxis(this.xAxis, this.plot.data.xAxis);
        this.drawAxis(this.yAxis, this.plot.data.yAxis);
        this.xAxis.attr('transform', "translate(0, " + this.plot.data.yScale(0) + ")");

        // Draw labels:
        this.xLabel.select('text').text(this.plot.data.xLabel);
        this.yLabel.select('text').text(this.plot.data.yLabel());

        return true;
    },
    // Removes the current axes:
    hide: function() {
        this.xLabel.select('text').text('');
        this.yLabel.select('text').text('');

        this.yGrid.selectAll('*').remove();
        this.xAxis.selectAll('*').remove();
        this.yAxis.selectAll('*').remove();
    },
    // Draw an axis:
    drawAxis: function(selection, axis) {
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
    },
}
