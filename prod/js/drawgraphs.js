/* Copyright 2018-2020 Pascal COMBES <pascom@orange.fr>
 * 
 * This file is part of SolarProd.
 * 
 * SolarProd is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * SolarProd is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with SolarProd. If not, see <http://www.gnu.org/licenses/>
 */

function drawGraphs(selection){
    selection.selectAll('svg').each(function() {
        // NOTE This is a workaround which is required due to incompatibility of
        // XSLTProcessor and SVG (an xmlns declaration may fix it but my attempts
        // were unsuccessful.
        // Here I add a new SVG element, update its attributes so that they match
        // the attributes of the initial SVG element and delete the old one.
        var graph = selection.insert('svg', (d, i, nodes) => (nodes[i] == this));
        for (var i = 0; i < this.attributes.length; i++) {
            var attribute = this.attributes.item(i);
            graph.attr(attribute.nodeName, attribute.nodeValue);
        }
        d3.select(this).remove();

        // Scales:
        var xScale = d3.scaleLinear().domain([0, 24]);
        var yScale = d3.scaleBand().domain(graph.attr('ydata').split(' '))
                                   .padding(0.25);

        // Title:
        var title = null;
        if (graph.attr('title'))
            title = graph.append('g').classed('title', true)
                                      .attr('text-anchor', 'middle')
                                      .append('text').text(graph.attr('title'));

        // X label:
        var xLabel = null;
        if (graph.attr('xlabel'))
            xLabel = graph.append('g').classed('label', true)
                                      .attr('text-anchor', 'middle')
                                      .append('text').text(graph.attr('xlabel'));

        // Axes:
        var xAxis = graph.append('g').classed('axis', true);
        var yAxis = graph.append('g').classed('axis', true);

        // The bars:
        var bars = graph.selectAll('rect').data(d3.transpose([
            graph.attr('ydata').split(' '),
            graph.attr('xstart').split(' '),
            graph.attr('xend').split(' '),
        ]));
        bars.exit().remove();
        bars = bars.enter().append('rect').classed('bar', true)
                                          .attr('stroke', '#F6D746')
                                          .attr('fill', '#F6D746')
                                          .attr('fill-opacity', 0.25)
                                          .merge(bars);

        // The grid:
        var xGrid = graph.append('g').classed('grid', true);

        // The resize event
        var doWindowResize = function() {
            console.log("Graph resize event");

            var h = graph.node().clientHeight;
            var w = graph.node().clientWidth;
            var p = 20;

            graph.attr('viewBox', '0 0 ' + w + ' ' + h);

            xScale.range([p, w - p]);
            yScale.range([title ? 1.5*p : 0, xLabel ? h - 2*p : h - p]);

            if (title)
                title.attr('transform', 'translate(' + (w / 2) + ', ' + p + ')');

            if (xLabel)
                xLabel.attr('transform', 'translate(' + (w / 2) + ', ' + (h - p / 2) + ')');

            xAxis.attr('transform', 'translate(0, ' + d3.max(yScale.range()) + ')')
                 .call(d3.axisBottom().scale(xScale));
            xGrid.call(d3.axisBottom().scale(xScale).tickSize(d3.max(yScale.range()) - d3.min(yScale.range())));
            xGrid.attr('transform', 'translate(0, ' + (1.5 * p) + ')')
                 .select('.domain').remove();
            yAxis.attr('transform', 'translate(' + xScale(12) + ', 0)')
                 .call(d3.axisLeft().scale(yScale))
                 .attr('text-anchor', 'middle');
            yAxis.selectAll('.domain').style('display', 'none');
            yAxis.selectAll('.tick').select('line').style('display', 'none');
            yAxis.selectAll('.tick').select('text').attr('x', 0);

            bars.attr('x', (d) => xScale(d[1]))
                .attr('y', (d) => yScale(d[0]))
                .attr('width', (d) => (xScale(d[2]) - xScale(d[1])))
                .attr('height', yScale.bandwidth());
        };

        var resizeTimer; // Timer to ensure the graph is not updated continuously
        var windowResize = function() {
            if (resizeTimer !== undefined)
                clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                resizeTimer = undefined;
                doWindowResize();
            }, 100);
        };

        d3.select(window).on('resize.' + graph.attr('id'), windowResize);
        doWindowResize();

        // The close event:
        graph.on('close', function() {
            console.log("Graph close event");
            d3.select(window).on('resize.' + graph.attr('id'), null);
        });

        // The show event:
        graph.on('show', function() {
            console.log("Graph show event");
            d3.select(window).on('resize.' + graph.attr('id'), windowResize);
            doWindowResize();
        });

        // The hide event:
        graph.on('hide', function() {
            console.log("Graph hide event");
            d3.select(window).on('resize.' + graph.attr('id'), null);
        });
    });


    if (!selection.selectAll('svg').empty()) {
        selection.on('close', function() {
            console.log("Page close event");
            selection.selectAll('svg').dispatch('close');
        });

        selection.on('show', function() {
            console.log("Page", selection.attr('id'), "show event");
            selection.selectAll('svg').dispatch('show');
        });

        selection.on('hide', function() {
            console.log("Page", selection.attr('id'), "hide event");
            selection.selectAll('svg').dispatch('hide');
        });
    }
}
