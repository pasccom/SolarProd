function SolarCache() {
    var cache = {};

    var is = function(member) {
        return function() {
            if (cache[member] === undefined)
                return false;

            for (var i = 0; i < Math.min(cache[member].length, arguments.length); i++)
                if (cache[member][i] != arguments[i])
                    return false;

            return true;
        };
    };

    // Get cache:
    d3.json("list/cache.json").on('error', console.log)
                              .on('load', (data) => {cache = data;}).get();

    this.isFirstDay   = is('firstDay');
    this.isLastDay    = is('lastDay');
    this.isFirstMonth = is('firstMonth');
    this.isLastMonth  = is('lastMonth');
    this.isFirstYear  = is('firstYear');
    this.isLastYear   = is('lastYear');

    this.update = function(dir, data) {
        if (dir > 0) {
            switch (data.length) {
                case 3:
                    cache.lastDay = data;
                    break;
                case 2:
                    cache.lastMonth = data;
                    break;
                default:
                    break;
            }
        } else if (dir < 0) {
            switch (data.length) {
                case 3:
                    cache.firstDay = data;
                    break;
                case 2:
                    cache.firstMonth = data;
                    break;
                default:
                    break;
            }
        }
    };
}

SolarCache.prototype = {
    isFirst: function(year, month, day) {
        if ((year !== undefined) && (year !== '') && (month !== undefined) && (month !== '') && (day !== undefined) && (day !== ''))
            return this.isFirstDay(year, month, day);
        else if ((year !== undefined) && (year !== '') && (month !== undefined) && (month !== ''))
            return this.isFirstMonth(year, month);
        else
            return this.isFirstYear(year);
    },
    isLast: function(year, month, day) {
        if ((year !== undefined) && (year !== '') && (month !== undefined) && (month !== '') && (day !== undefined) && (day !== ''))
            return this.isLastDay(year, month, day);
        else if ((year !== undefined) && (year !== '') && (month !== undefined) && (month !== ''))
            return this.isLastMonth(year, month);
        else
            return this.isLastYear(year);
    },
};

function SolarProd() {
    // Pending requests:
    var pendingListRequests = 0;
    var pendingDataRequests = 0;

    // Current date:
    var date = (function() {
        var data = ['', '', ''];

        var ret = function() {
            var l = (arguments.length > 0) ? arguments[0] : 3;
            return data.slice(0, l);
        };
        ret.update = function(level, value) {
            if (value === null)
                return false;

            console.log('Date.update:', level, value);
            data[level - 1] = value;
            return true;
        };

        return ret;
    })();

    // Date to select:
    var selectDate = (function() {
        var data = [0, 0, 0];

        var ret = function() {
            var l = (arguments.length > 0) ? arguments[0] : 3;
            return data.slice(0, l);
        };

        ret.update = function(level, value) {
            if (value === null)
                return false;

            console.log('selectDate.update:', level, value);
            data[level - 1] += value;
            return true;
        };

        ret.reset = function() {
            var l = arguments.length >= 1 ? arguments[0] : 3;
            while (l >= 1)
                data[--l] = 0;
        };

        ret.dir = 1;
        return ret;
    })();

    // Cache:
    var cache = new SolarCache();

    // Toolbar layout:
    d3.select('body').append('div');
    var toolbar1 = d3.select('body').select('div').append('div').classed('toolbar', true);
    var toolbar2 = d3.select('body').select('div').append('div').classed('toolbar', true);

    // The selectors:
    var selects = function() {
        var l = (arguments.length > 0) ? arguments[0] : 3;
        return [selects.year, selects.month, selects.day].slice(0, l);
    };
    selects.day = toolbar1.append('select').attr('title', 'Jour')
                                           .attr('disabled', true);
    selects.month = toolbar1.append('select').attr('title', 'Mois')
                                             .attr('disabled', true);
    selects.year = toolbar1.append('select').attr('title', 'Année')
                                            .attr('disabled', true);
    selects.var = toolbar1.append('select').attr('title', 'Variable')
                                           .attr('disabled', true);
    selects.agg = toolbar1.append('select').attr('title', 'Aggrégation')
                                           .attr('disabled', true);

    // The buttons:
    var buttons = function(dir) {
        if (dir == 1)
            return buttons.next;
        if (dir == -1)
            return buttons.prev;
    };
    buttons.plot = toolbar1.append('img').classed('button', true)
                                         .attr('src', 'img/plot.png')
                                         .attr('title', 'Tracer')
                                         .attr('alt', 'Tracer');
    buttons.prev = toolbar2.append('img').classed('button', true)
                                         .classed('disabled', true)
                                         .attr('src', 'img/prev.png')
                                         .attr('title', 'Précédent')
                                         .attr('alt', 'Précédent');
    buttons.today = toolbar2.append('img').classed('button', true)
                                          .attr('src', 'img/today.png')
                                          .attr('title', 'Aujourd\'hui')
                                          .attr('alt', 'Aujourd\'hui');
    buttons.next = toolbar2.append('img').classed('button', true)
                                         .classed('disabled', true)
                                         .attr('src', 'img/next.png')
                                         .attr('title', 'Suivant')
                                         .attr('alt', 'Suivant');
    buttons.export = toolbar2.append('img').classed('button', true)
                                           .classed('disabled', true)
                                           .attr('src', 'img/csv.png')
                                           .attr('title', 'Export CSV')
                                           .attr('alt', 'Export CSV');

    // TODO remove?
    // WARNING Used by test.py
    selects.day.attr('id', 'day');
    selects.month.attr('id', 'month');
    selects.year.attr('id', 'year');
    selects.var.attr('id', 'var');
    selects.agg.attr('id', 'sum');

    buttons.plot.attr('id', 'plot');
    buttons.prev.attr('id', 'prev');
    buttons.today.attr('id', 'today');
    buttons.next.attr('id', 'next');
    buttons.export.attr('id', 'export');

    var chart = new SolarChart(d3.select('body'));
    this.chart = chart;

    // Clears selects from level upwads:
    var clearSelect = function(level) {
        for (var l = level; l <= 3; l++) {
            date.update(l, '');
            selects()[l - 1].selectAll('option').remove();
        }
    };

    // Get previous option(s):
    var siblingOption = function(dir)
    {
        var datum = (arguments.length > 1) ? arguments[1] : this.property('value');

        if (datum == '')
            return null;

        var o = this.selectAll('option')
                    .filter((d) => (d == datum))
                    .selectAll(function() {return (dir == 1) ? [this.nextElementSibling] : [this.previousElementSibling];});

        if (o.empty() ||  (o.attr('value') == ''))
            return null;
        return o.attr('value');
    };
    // Update the states of previous and next buttons:
    var updatePrevNext = function()
    {
        buttons.prev.classed('disabled', cache.isFirst(... date()) ||
                                       (!siblingOption.call(selects.day, -1) &&
                                        !siblingOption.call(selects.month, -1) &&
                                        !siblingOption.call(selects.year, -1)));
        buttons.next.classed('disabled', cache.isLast(... date()) ||
                                       (!siblingOption.call(selects.day, 1) &&
                                        !siblingOption.call(selects.month, 1) &&
                                        !siblingOption.call(selects.year, 1)));
    };

    // Update cache:
    var updateCache = function()
    {
        if (selectDate()[2] != 0)
            cache.update(Math.sign(selectDate()[2]), date(3));
        else if (selectDate()[1] != 0)
            cache.update(Math.sign(selectDate()[1]), date(2));
        else
            return;

        selectDate.dir = 1;
        console.log('Updated cache:', cache);
        updatePrevNext();
    };

    // Update year, month and day selector (depending on level):
    this.update = function(callPlot, level) {
        if (level == 4) {
            if (callPlot)
                this.plot();
            return;
        }

        // Disables selects above current level inclusive:
        for (var l = level; l <= 3; l++)
            selects()[l - 1].attr('disabled', true);

        // None selected at previous level:
        if ((level > 1) && (date()[level - 2] == '')) {
            clearSelect(level);
            if (callPlot)
                this.plot();
            return;
        }

        var listPath = SolarData.listFilePath(... date(level - 1));
        console.log("List file path: ", listPath);

        // Load data list:
        pendingListRequests++;
        d3.json(listPath).on('error', (error) => {
            pendingListRequests--;
            console.warn("Could not retrieve list: ", listPath, error);
            clearSelect(level);
            this.siblingPlot(Math.sign(selectDate()[level - 1]*selectDate.dir), callPlot, level - 1);
        }).on('load', (data) => {
            pendingListRequests--;
            if (pendingListRequests > 0)
                return;

            data.unshift('');

            var text = (d) => d;
            if (level == 2)
                text = (d) => (d == '' ? '' : localeLongMonth(new Date(date()[0], d - 1)));

            var opts = selects()[level - 1].attr('disabled', null)
                                           .selectAll('option').data(data, (d) => d);
            opts.enter().append('option').attr('value', (d) => d)
                                         .text(text);
            opts.exit().remove();

            selects()[level - 1].selectAll('option')
                                .filter((d) => (d == ''))
                                .lower();

            var dateOffset = selectDate()[level - 1]*selectDate.dir;
            var selectDateOffset = 0;
            if (dateOffset < 0) {
                dateOffset = Math.max(data.length + dateOffset, 1);
                selectDateOffset = (data.length - dateOffset)*selectDate.dir;
            } else if (dateOffset > 0) {
                dateOffset = Math.min(dateOffset, data.length - 1);
                selectDateOffset = -dateOffset*selectDate.dir;
            }

            if (dateOffset != 0) {
                date.update(level, data[dateOffset]);
                selects()[level - 1].property('value', date()[level - 1]);
                updatePrevNext();
            }

            if (((level == 3) || (selectDate()[level] == 0)) && (selectDate.dir == -1))
                updateCache();
            selectDate.update(level, selectDateOffset);

            if (selectDate()[level - 1] == 0)
                this.update(callPlot, level + 1);
            else if ((selectDate()[level - 1]*selectDate.dir > 0) && !cache.isLast(... date(level)))
                this.siblingPlot(1, callPlot, level - 1);
            else if ((selectDate()[level - 1]*selectDate.dir < 0) && !cache.isFirst(... date(level)))
                this.siblingPlot(-1, callPlot, level - 1);
            else if (callPlot)
                this.plot();
        }).get();
    };

    // Updates the variable selector:
    var updateVars = function()
    {
        var data = (arguments.length >= 1) ?  arguments[0] : chart.plot.data;

        if (data.isEmpty()) {
            // Clears variables:
            selects.var.attr('disabled', true)
                       .selectAll('option').remove();
        } else {
            // Adds the new variables using a data join:
            var vars = selects.var.attr('disabled', null)
                                  .selectAll('option').data(data.validVars, (d) => d);
            vars.enter().append('option').attr('value', (d) => d)
                                        .text(SolarData.variableName);
            vars.exit().remove();
            vars.order();

            // Updates sums if needed:
            if (selects.var.property('value') != data.variable()) {
                data.variable(selects.var.property('value'));
            }
        }

        updateAggs(data);
    };

    // Updates the sum selector:
    var updateAggs = function()
    {
        var data = (arguments.length >= 1) ?  arguments[0] : chart.plot.data;

        if (data.isEmpty()) {
            // Clears sums:
            selects.agg.attr('disabled', true)
                       .selectAll('option').remove();
        } else {
            // Adds the new sums using a data join:
            var aggs = selects.agg.attr('disabled', (data.validAggs.length < 2) ? true : null)
                                  .selectAll('option').data(data.validAggs, (d) => d);
            aggs.enter().append('option').attr('value', (d) => d)
                                        .text(SolarData.aggregationName);
            aggs.exit().remove();
            aggs.order();
        }
    };

    this.plot = function(today) {
        // Do not fetch plot data while there are pending list requests:
        if (pendingListRequests != 0)
            return;

        // Set date of today:
        if (today) {
            selectDate.update(2, -1);
            selectDate.update(3, -1);
            selectDate.dir = 1;
            date.update(1, selects.year.selectAll('option').filter(function() {return (this.nextElementSibling == null);}).attr('value'));
            selects.year.property('value', date()[0]);
            this.update(false, 2);
            updatePrevNext();
        }

        var solarPromise = today ? SolarData.create() : SolarData.create(... date());
        pendingDataRequests++;
        solarPromise.catch((msg) => {
            pendingDataRequests--;
            console.warn(msg);
        });
        solarPromise.then((data) => {
            pendingDataRequests--;
            // Do not plot while there are pending data requests:
            if (pendingDataRequests > 0)
                return;

            updateVars(data);
            this.chart.setData(data);

            // Activate export:
            buttons.export.classed('disabled', data.isEmpty());
        });
    };

    this.siblingPlot = function()
    {
        var l = 3;
        var level;
        var dir = arguments[0];
        var callPlot = (arguments.length > 1) ? arguments[1] : true;

        if (dir == 0) {
            if (callPlot)
                this.plot();
            return;
        }

        if (arguments.length < 3) {
            for (l = 3; l > 0; l--) {
                if ((date()[l - 1] != '') || (selectDate()[l - 1] != 0)) {
                    this.siblingPlot(dir, callPlot, l);
                    break;
                }
            }
            return;
        }

        level = arguments[2];

        if (level == 0) {
            buttons(dir).classed('disabled', true);
            selectDate.dir = -1;

            l = 3;
            while ((l > 1) && (selectDate()[l - 1] == 0))
                l--;

            selectDate.reset(l);
            this.siblingPlot(-dir, callPlot, l);
        } else if (((dir ==  1) && cache.isLast(... date(level))) ||
                   ((dir == -1) && cache.isFirst(... date(level)))) {
            for (l = 3; l > level; l--) {
                if (selectDate()[l - 1] != 0) {
                    selectDate.dir = -1;
                    this.siblingPlot(dir, callPlot, l);
                    break;
                }
            }
        } else if (selectDate()[level - 1]*selectDate.dir*dir > 0) {
            selectDate.update(level, selectDate.dir*dir);
        } else if (date.update(level, siblingOption.call(selects()[level - 1], dir))) {
            selects()[level - 1].property('value', date()[level - 1]);
            updatePrevNext();
            this.update(callPlot, level + 1);
        } else if ((level > 1) || (selectDate().some((x) => x != 0))) {
            selectDate.update(level, selectDate.dir*dir);
            this.siblingPlot(dir, callPlot, level - 1);
        }
    };

    // Window resize event:
    this.windowResize = function()
    {
        // Compute toolbar total width (currently 403):
        //var tw = 20;
        //d3.selectAll('.toolbar').each(function() {tw += this.clientWidth;});

        // Plot width and height:
        var w = window.innerWidth - 18;
        var h = window.innerHeight - 56;
        if (window.innerWidth < 403)
            h -= 38;

        this.chart.resize(w, h);
    };

    // Change event:
    selects.day.on('change', () => {
        date.update(3, selects.day.property('value'));
        updatePrevNext();
    });
    selects.month.on('change', () => {
        date.update(2, selects.month.property('value'));
        updatePrevNext();
        this.update(false, 3);
    });
    selects.year.on('change', () => {
        date.update(1, selects.year.property('value'));
        updatePrevNext();
        this.update(false, 2);
    });
    selects.var.on('change', () => {
        chart.plot.data.variable(selects.var.property('value'));
        updateAggs();
        this.chart.draw();
    });
    selects.agg.on('change', () => {
        this.chart.plot.data.aggregation(selects.agg.property('value'));
        this.chart.draw();
    });

    // Click event:
    buttons.plot.on('click', () => {this.plot();});
    buttons.prev.on('click', () => {this.siblingPlot(-1);});
    buttons.today.on('click', () => {this.plot(true);});
    buttons.next.on('click', () => {this.siblingPlot(1);});
    buttons.export.on('click', () => {this.chart.plot.data.exportCsv();});

    // Key event:
    d3.select(document).on('keydown', () => {
        if (d3.event.shiftKey || d3.event.altKey || d3.event.ctrlKey || d3.event.metaKay)
            return;

        if ((d3.event.key == 'Enter') && !d3.event.repeat)
            buttons.plot.dispatch('click');

        if ((d3.event.key == 'ArrowUp') && !d3.event.repeat)
            buttons.today.dispatch('click');

        if (d3.event.key == 'ArrowLeft')
            buttons.prev.dispatch('click');

        if (d3.event.key == 'ArrowRight')
            buttons.next.dispatch('click');

        if ((d3.event.key == 'ArrowDown') && !d3.event.repeat)
            buttons.export.dispatch('click');
    });

    // Resize event:
    d3.select(window).on('resize', this.windowResize.bind(this));
    this.windowResize();

    // Update year selector:
    this.update(false, 1);
};
