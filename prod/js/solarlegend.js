function SolarLegend(root)
{
    // Recursive forEach function:
    var recForEach = function(a, fun)
    {
        if (!Array.isArray(a))
            fun(a);
        else
            a.forEach((e) => recForEach(e, fun));
    };

    // Update visibility in legend so that it matches the visility of the element:
    var updateVisibility = function()
    {
        // Ensure the checkboxes match the visility of the elements:
        root.selectAll('input').each(function(d) {
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
    };

    // Change the visibility of an element:
    var changeVisibility = function(d)
    {
        // Show/hides elements:
        recForEach(d, (e) => {
            if (d3.select(d3.event.target).property('checked'))
                e.style('display', 'initial');
            else
                e.style('display', 'none');
        });

        updateVisibility();
    };

    // Draw the legend:
    this.draw = function(data, style)
    {
        this.enableCursor = function(enable)
        {
            var legendItemOn = function(event, callback) {
                root.selectAll('.legenditem').on(event, !enable ? null : function(d) {
                    if (d === undefined)
                        d = data;
                    if (!Array.isArray(d))
                        d = [d];

                    d.forEach(callback);
                });
            };

            legendItemOn('mouseenter', (e) => {e.classed('selected', true);});
            legendItemOn('mouseleave', (e) => {e.classed('selected', false);});
        };

        var appendLegendItem = function(d)
        {
            if (d === undefined)
                d = data;

            if (!d.isLeaf)
                return;
            if (!Array.isArray(d))
                d = [d];

            var item = d3.select(this).append('span').classed('legenditem', true)
                                                     .html('&mdash;&mdash;&mdash;&mdash;&mdash;&mdash;')
                                                     .on('mouseenter', null)
                                                     .on('mouseleave', null)
                                                     .call(style);

            var observer = new MutationObserver(function(mutations, observer) {
                mutations.forEach((mutation) => {
                    if (mutation.attributeName != 'class')
                        return;
                    item.classed('selected', d3.select(mutation.target).classed('selected'));
                });
            });
            d.forEach((e) => {observer.observe(e.node(), {attributes: true})});
        };

        var appendVisibilityBox = function()
        {
            d3.select(this).append('span')
                           .classed('input', true).append('input')
                                                  .attr('type', 'checkbox')
                                                  .on('change', changeVisibility);
        };

        root.append('h4').text('Légende');
        // Creates legend (using lists)
        var list = root.selectAll('ul')
                       .data([data]);
        list = list.enter().append('ul');

        var inv = list.selectAll('li')
                        .data((d) => d.isLeaf ? [] : d);
        inv = inv.enter().append('li');
        inv.append('span').classed('label', true);
        inv.select('span').each(appendLegendItem);
        inv.select('span').append('span').text((d, i) => ('Onduleur ' + (i + 1)));
        inv.each(appendVisibilityBox);

        var str = inv.append('ul').selectAll('li')
                                .data((d) => d.isLeaf ? [] : d);
        str = str.enter().append('li');
        str.append('span').classed('label', true);
        str.select('span').each(appendLegendItem);
        str.select('span').append('span').text((d, i) => (' String ' + (i + 1)));
        str.each(appendVisibilityBox);

        if (list.selectAll('li').empty()) {
            root.each(appendLegendItem);
            root.append('span').text(' Total');
        }

        updateVisibility();
    };

    // Crear legend:
    this.clear = function()
    {
        root.selectAll('*').remove();
    };

    this.enableCursor = function(enable, listener) {};
}
