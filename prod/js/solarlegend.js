function SolarLegend(legendRoot)
{
    this.root = legendRoot;
}

SolarLegend.prototype = {
    // Update visibility in legend so that it matches the visility of the element:
    updateVisibility: function()
    {
        // Ensure the checkboxes match the visility of the elements:
        this.root.selectAll('input').each(function(d) {
            if (d[0] === undefined) {
                this.checked = (d.style('display') != 'none');
            } else {
                var allSelected = true;
                var anySelected = false;
                d.forEach((e) => {
                    if (Array.isArray(e))
                        e = e[0];
                    allSelected &= (e.style('display') != 'none');
                    anySelected |= (e.style('display') != 'none');
                });
                this.checked = anySelected;
                this.indeterminate = !allSelected && anySelected;
            }
        });
    },
    // Change the visibility of an element:
    changeVisiblilty: function(d)
    {
        // Show/hides elements:
        recForEach(d, (e) => {
            if (d3.select(d3.event.target).property('checked'))
                e.style('display', 'initial');
            else
                e.style('display', 'none');
        });

        this.updateVisibility();
    },
    // Draw the legend:
    draw: function(agg, data, style)
    {
        var appendLegendItem = function(element)
        {
            element.append('span').html('&mdash;&mdash;&mdash;&mdash;&mdash;&mdash;').call(style);
        };

        var appendVisibilityBox = (function(element)
        {
            element.append('span')
                .classed('input', true).append('input')
                                        .attr('type', 'checkbox')
                                        .on('change', this.changeVisiblilty.bind(this));
        }).bind(this);

        this.root.append('h4').text('Légende');
        // Creates legend (using lists)
        if (agg == 'sum') {
            this.root.call(appendLegendItem);
            this.root.append('span').text(' Total');
        } else {
            var inv = this.root.append('ul').selectAll('li')
                                            .data(data);
            inv = inv.enter().append('li');
            inv.append('span').classed('label', true);

            if (agg != 'str')
                inv.select('span').call(appendLegendItem);

            inv.select('span').append('span').text((d, i) => ('Onduleur ' + (i + 1)));
            inv.call(appendVisibilityBox);

            if (agg == 'str') {
                var str = inv.append('ul').selectAll('li')
                                        .data((d) => d);
                str = str.enter().append('li');
                str.append('span').classed('label', true);

                str.select('span').call(appendLegendItem);
                str.select('span').append('span').text((d, i) => (' String ' + (i + 1)));
                str.call(appendVisibilityBox);
            }

            this.updateVisibility();
        }
    },
    // Crear legend:
    clear: function()
    {
        this.root.selectAll('*').remove();
    },
}
