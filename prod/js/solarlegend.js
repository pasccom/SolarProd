function SolarLegend(legendRoot, parent)
{
    this.root = legendRoot;
    this.parent = parent;

    this.appendLegendItem = (function(element)
    {
        element.append('span').html('&mdash;&mdash;&mdash;&mdash;&mdash;&mdash;').call(this.parent.plot.legendStyle);
    }).bind(this);
    this.appendVisibilityBox = (function(element)
    {
        element.append('span')
               .classed('input', true).append('input')
                                      .attr('type', 'checkbox')
                                      .on('change', this.changeVisiblilty.bind(this));
    }).bind(this);
}

SolarLegend.prototype = {
    // Update visibility in legend so that it matches the visility of the element:
    updateVisibility: function()
    {
        // Ensure the checkboxes match the visility of the elements:
        this.root.selectAll('input').each(function(d) {
            if (d[0] === undefined) {
                this.checked = (d3.select(d).style('display') != 'none');
            } else {
                var allSelected = true;
                var anySelected = false;
                d.forEach(function(e) {
                    allSelected &= (d3.select(e).style('display') != 'none');
                    anySelected |= (d3.select(e).style('display') != 'none');
                });
                this.checked = anySelected;
                this.indeterminate = !allSelected && anySelected;
            }
        });
    },
    // Change the visibility of an element:
    changeVisiblilty: function(d)
    {
        var selection;
        if (this.parent.plot.groups !== undefined) {
            var group;
            var elem;

            // Get group number for current element:
            this.parent.plot.groups.filter(function(d, i) {return i == 0;})
                                   .selectAll('g').each(function(e, i) {
                d3.select(this).selectAll('rect').each(function(e, j) {
                    var element = this;
                    if ((d[0] === undefined) && (d == element))
                        group = i;
                    if (d[0] !== undefined)
                        d.forEach(function(e) {if (e == element) group = i;});
                });
            });
            // Get element number for current element (if it is an element):
            this.parent.plot.groups.filter(function(d, i) {return i == 0;})
                                   .selectAll('g').selectAll('rect').each(function(e, i) {
                if (this == d)
                    elem = i;
            });
            console.log('group:', group, 'elem:', elem);

            // Get all element at position elem in group group:
            selection = this.parent.plot.groups.selectAll('g').filter(function(e, i) {return (i == group);});
            selection = selection.selectAll('rect').filter(function(e, i) {return (elem === undefined ? true : (i == elem));});
        } else {
            selection = (d[0] === undefined) ? d3.select(d) : d3.selectAll(d);
        }

        // Show/hides elements:
        if (d3.select(d3.event.target).property('checked'))
            selection.style('display', 'initial');
        else
            selection.style('display', 'none');

        this.updateVisibility();
    },
    // Draw the legend:
    draw: function(sum)
    {
        if (!this.parent.plot.legendStyle)
            return;
        this.root.append('h4').text('Légende');

        // Creates legend (using lists)
        if (sum == 'sum') {
            this.root.call(this.appendLegendItem);
            this.root.append('span').text(' Total');
        } else {
            var inv = this.root.append('ul').selectAll('li')
                                            .data(this.parent.plot.legendData._groups);
            inv = inv.enter().append('li');
            inv.append('span').classed('label', true);

            if (sum != 'str')
                inv.select('span').call(this.appendLegendItem);

            inv.select('span').append('span').text((d, i) => ('Onduleur ' + (i + 1)));
            inv.call(this.appendVisibilityBox);

            if (sum == 'str') {
                var str = inv.append('ul').selectAll('li')
                                        .data((d) => d);
                str = str.enter().append('li');
                str.append('span').classed('label', true);

                str.select('span').call(this.appendLegendItem);
                str.select('span').append('span').text((d, i) => (' String ' + (i + 1)));
                str.call(this.appendVisibilityBox);
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
