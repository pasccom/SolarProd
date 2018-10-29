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
    // pending requests:
    this.pendingListRequests = 0;
    this.pendingDataRequests = 0;

    // Current date:
    this.date = function() {
        var l = (arguments.length > 0) ? arguments[0] : 3;
        return [this.date.year, this.date.month, this.date.day].slice(0, l);
    };
    this.date.year = '';
    this.date.month = '';
    this.date.day = '';
    this.date.update = function(level, value) {
        if (value === null)
            return false;

        var members = ['', 'year', 'month', 'day'];
        console.log('Date.update:', level, members[level], value);
        this[members[level]] = value;
        return true;
    };

    // Date to select:
    this.selectDate = function() {
        var l = (arguments.length > 0) ? arguments[0] : 3;
        return [this.selectDate.year, this.selectDate.month, this.selectDate.day].slice(0, l);
    };
    this.selectDate.year = 0;
    this.selectDate.month = 0;
    this.selectDate.day = 0;
    this.selectDate.dir = 1;
    this.selectDate.update = function(level, value) {
        if (value === null)
            return false;

        var members = ['', 'year', 'month', 'day'];
        console.log('SelectDate.update:', level, members[level], value);
        this[members[level]] += value;
        return true;
    };
    this.selectDate.reset = function() {
        var l = arguments.length >= 1 ? arguments[0] : 3;

        var members = ['', 'year', 'month', 'day'];
        while (l >= 1)
            this[members[l--]] = 0;
    };

    // Cache:
    this.cache = new SolarCache();

    d3.select('body').append('div');

    var toolbar1 = d3.select('body').select('div').append('div').classed('toolbar', true);
    var toolbar2 = d3.select('body').select('div').append('div').classed('toolbar', true);

    // The selectors:
    this.selects = function() {
        var l = (arguments.length > 0) ? arguments[0] : 3;
        return [this.selects.year, this.selects.month, this.selects.day].slice(0, l);
    };
    this.selects.day = toolbar1.append('select').attr('title', 'Jour')
                                                .attr('disabled', true)
                                                .on('change', () => {
        this.date.day = this.selects.day.property('value');
        this.updatePrevNext();
    });
    this.selects.month = toolbar1.append('select').attr('title', 'Mois')
                                                  .attr('disabled', true)
                                                  .on('change', () => {
        this.date.month = this.selects.month.property('value');
        this.updatePrevNext();
        this.update(false, 3);
    });
    this.selects.year = toolbar1.append('select').attr('title', 'Année')
                                                 .attr('disabled', true)
                                                 .on('change', () => {
        this.date.year = this.selects.year.property('value');
        this.updatePrevNext();
        this.update(false, 2);
    });
    this.selects.var = toolbar1.append('select').attr('title', 'Variable')
                                                .attr('disabled', true)
                                                .on('change', () => {
        this.chart.plot.data.variable(this.selects.var.property('value'));
        this.updateAggs();
        this.chart.draw();
    });
    this.selects.agg = toolbar1.append('select').attr('title', 'Aggrégation')
                                                .attr('disabled', true)
                                                .on('change', () => {
        this.chart.plot.data.aggregation(this.selects.agg.property('value'));
        this.chart.draw();
    });

    // The buttons:
    this.buttons = function(dir) {
        if (dir == 1)
            return this.buttons.next;
        if (dir == -1)
            return this.buttons.prev;
    };

    this.buttons.plot = toolbar1.append('img').classed('button', true)
                                              .attr('src', 'img/plot.png')
                                              .attr('title', 'Tracer')
                                              .attr('alt', 'Tracer')
                                              .on('click', () => {this.plot();});
    this.buttons.prev = toolbar2.append('img').classed('button', true)
                                              .classed('disabled', true)
                                              .attr('src', 'img/prev.png')
                                              .attr('title', 'Précédent')
                                              .attr('alt', 'Précédent')
                                              .on('click', () => {this.siblingPlot(-1);});
    this.buttons.today = toolbar2.append('img').classed('button', true)
                                               .attr('src', 'img/today.png')
                                               .attr('title', 'Aujourd\'hui')
                                               .attr('alt', 'Aujourd\'hui')
                                               .on('click', () => {this.plot(true);});
    this.buttons.next = toolbar2.append('img').classed('button', true)
                                              .classed('disabled', true)
                                              .attr('src', 'img/next.png')
                                              .attr('title', 'Suivant')
                                              .attr('alt', 'Suivant')
                                              .on('click', () => {this.siblingPlot(1);});
    this.buttons.export = toolbar2.append('img').classed('button', true)
                                                .classed('disabled', true)
                                                .attr('src', 'img/csv.png')
                                                .attr('title', 'Export CSV')
                                                .attr('alt', 'Export CSV')
                                                .on('click', () => {this.chart.plot.data.exportCsv();});

    d3.select(document).on('keydown', () => {
        console.log(d3.event);

        if (d3.event.shiftKey || d3.event.altKey || d3.event.ctrlKey || d3.event.metaKay)
            return;

        if ((d3.event.key == 'Enter') && !d3.event.repeat)
            this.buttons.plot.dispatch('click');

        if ((d3.event.key == 'ArrowUp') && !d3.event.repeat)
            this.buttons.today.dispatch('click');

        if (d3.event.key == 'ArrowLeft')
            this.buttons.prev.dispatch('click');

        if (d3.event.key == 'ArrowRight')
            this.buttons.next.dispatch('click');

        if ((d3.event.key == 'ArrowDown') && !d3.event.repeat)
            this.buttons.export.dispatch('click');
    });

    // TODO remove?
    // WARNING Used by test.py
    this.selects.day.attr('id', 'day');
    this.selects.month.attr('id', 'month');
    this.selects.year.attr('id', 'year');
    this.selects.var.attr('id', 'var');
    this.selects.agg.attr('id', 'sum');

    this.buttons.plot.attr('id', 'plot');
    this.buttons.prev.attr('id', 'prev');
    this.buttons.today.attr('id', 'today');
    this.buttons.next.attr('id', 'next');
    this.buttons.export.attr('id', 'export');

    this.chart = new SolarChart(d3.select('body'));
    d3.select(window).on('resize', this.windowResize.bind(this));
    this.windowResize();

    this.update(false, 1);
}

SolarProd.prototype = {
    // Window resize event:
    windowResize: function()
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
    },

    clearSelect: function(level) {
        for (var l = level; l <= 3; l++) {
            this.date.update(l, '');
            this.selects()[l - 1].selectAll('option').remove();
        }
    },
    // Update year, month and day selector (depending on level)
    update: function(callPlot, level) {
        if (level == 4) {
            if (callPlot)
                this.plot();
            return;
        }

        // Disables selects above current level inclusive:
        for (var l = level; l <= 3; l++)
            this.selects()[l - 1].attr('disabled', true);

        // None selected at previous level:
        if ((level > 1) && (this.date()[level - 2] == '')) {
            this.clearSelect(level);
            if (callPlot)
                this.plot();
            return;
        }

        var listPath = SolarData.listFilePath(... this.date(level - 1));
        console.log("List file path: ", listPath);

        // Load data list:
        this.pendingListRequests++;
        d3.json(listPath).on('error', (error) => {
            this.pendingListRequests--;
            console.warn("Could not retrieve list: ", listPath, error);
            this.clearSelect(level);
            this.siblingPlot(Math.sign(this.selectDate()[level - 1]*this.selectDate.dir), callPlot, level - 1);
        }).on('load', (data) => {
            this.pendingListRequests--;
            if (this.pendingListRequests > 0)
                return;

            data.unshift('');

            var text = (d) => d;
            if (level == 2)
                text = (d) => (d == '' ? '' : localeLongMonth(new Date(this.date.year, d - 1)));

            var opts = this.selects()[level - 1].attr('disabled', null)
                                                .selectAll('option').data(data, (d) => d);
            opts.enter().append('option').attr('value', (d) => d)
                                         .text(text);
            opts.exit().remove();

            this.selects()[level - 1].selectAll('option')
                                     .filter((d) => (d == ''))
                                     .lower();

            var dateOffset = this.selectDate()[level - 1]*this.selectDate.dir;
            var selectDateOffset = 0;
            if (dateOffset < 0) {
                dateOffset = Math.max(data.length + dateOffset, 1);
                selectDateOffset = (data.length - dateOffset)*this.selectDate.dir;
            } else if (dateOffset > 0) {
                dateOffset = Math.min(dateOffset, data.length - 1);
                selectDateOffset = -dateOffset*this.selectDate.dir;
            }

            if (dateOffset != 0) {
                this.date.update(level, data[dateOffset]);
                this.selects()[level - 1].property('value', this.date()[level - 1]);
                this.updatePrevNext();
            }

            if (((level == 3) || (this.selectDate()[level] == 0)) && (this.selectDate.dir == -1))
                this.updateCache();
            this.selectDate.update(level, selectDateOffset);

            if (this.selectDate()[level - 1] == 0)
                this.update(callPlot, level + 1);
            else if ((this.selectDate()[level - 1]*this.selectDate.dir > 0) && !this.cache.isLast(... this.date(level)))
                this.siblingPlot(1, callPlot, level - 1);
            else if ((this.selectDate()[level - 1]*this.selectDate.dir < 0) && !this.cache.isFirst(... this.date(level)))
                this.siblingPlot(-1, callPlot, level - 1);
            else if (callPlot)
                this.plot();
        }).get();
    },
    // Update cache:
    updateCache: function()
    {
        if (this.selectDate.day != 0)
            this.cache.update(Math.sign(this.selectDate.day), this.date(3));
        else if (this.selectDate.month != 0)
            this.cache.update(Math.sign(this.selectDate.month), this.date(2));
        else
            return;

        this.selectDate.dir = 1;
        console.log('Updated cache:', this.cache);
        this.updatePrevNext();
    },

    // Updates the variable selector:
    updateVars: function()
    {
        var data = (arguments.length >= 1) ?  arguments[0] : this.chart.plot.data;

        if (data.isEmpty()) {
            // Clears variables:
            this.selects.var.attr('disabled', true)
                            .selectAll('option').remove();
        } else {
            // Adds the new variables using a data join:
            var vars = this.selects.var.attr('disabled', null)
                                    .selectAll('option').data(data.validVars, (d) => d);
            vars.enter().append('option').attr('value', (d) => d)
                                        .text(SolarData.variableName);
            vars.exit().remove();
            vars.order();

            // Updates sums if needed:
            if (this.selects.var.property('value') != data.variable()) {
                data.variable(this.selects.var.property('value'));
            }
        }

        this.updateAggs(data);
    },
    // Updates the sum selector:
    updateAggs: function()
    {
        var data = (arguments.length >= 1) ?  arguments[0] : this.chart.plot.data;

        if (data.isEmpty()) {
            // Clears sums:
            this.selects.agg.attr('disabled', true)
                            .selectAll('option').remove();
        } else {
            // Adds the new sums using a data join:
            var aggs = this.selects.agg.attr('disabled', (data.validAggs.length < 2) ? true : null)
                                    .selectAll('option').data(data.validAggs, (d) => d);
            aggs.enter().append('option').attr('value', (d) => d)
                                        .text(SolarData.aggregationName);
            aggs.exit().remove();
            aggs.order();
        }
    },

    plot: function(today) {
        // Do not fetch plot data while there are pending list requests:
        if (this.pendingListRequests != 0)
            return;

        // Set date of today:
        if (today) {
            this.selectDate.month = -1;
            this.selectDate.day = -1;
            this.selectDate.dir = 1;
            this.date.year = this.selects.year.selectAll('option').filter(function() {return (this.nextElementSibling == null);})
                                                                  .attr('value');
            this.selects.year.property('value', this.date.year);
            this.update(false, 2);
            this.updatePrevNext();
        }

        var solarPromise = today ? SolarData.create() : SolarData.create(... this.date());
        this.pendingDataRequests++;
        solarPromise.catch((msg) => {
            this.pendingDataRequests--;
            console.warn(msg);
        });
        solarPromise.then((data) => {
            this.pendingDataRequests--;
            // Do not plot while there are pending data requests:
            if (this.pendingDataRequests > 0)
                return;

            this.updateVars(data);
            this.chart.setData(data);

            // Activate export:
            this.buttons.export.classed('disabled', data.isEmpty());
        });
    },

    siblingPlot: function()
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
                if ((this.date()[l - 1] != '') || (this.selectDate()[l - 1] != 0)) {
                    this.siblingPlot(dir, callPlot, l);
                    break;
                }
            }
            return;
        }

        level = arguments[2];

        if (level == 0) {
            this.buttons(dir).classed('disabled', true);
            this.selectDate.dir = -1;

            l = 3;
            while ((l > 1) && (this.selectDate()[l - 1] == 0))
                l--;

            this.selectDate.reset(l);
            this.siblingPlot(-dir, callPlot, l);
        } else if (((dir ==  1) && this.cache.isLast(... this.date(level))) ||
                   ((dir == -1) && this.cache.isFirst(... this.date(level)))) {
            for (l = 3; l > level; l--) {
                if (this.selectDate()[l - 1] != 0) {
                    this.selectDate.dir = -1;
                    this.siblingPlot(dir, callPlot, l);
                    break;
                }
            }
        } else if (this.selectDate()[level - 1]*this.selectDate.dir*dir > 0) {
            this.selectDate.update(level, this.selectDate.dir*dir);
        } else if (this.date.update(level, this.siblingOption.call(this.selects()[level - 1], dir))) {
            this.selects()[level - 1].property('value', this.date()[level - 1]);
            this.updatePrevNext();
            this.update(callPlot, level + 1);
        } else if ((level > 1) || (this.selectDate().some((x) => x != 0))) {
            this.selectDate.update(level, this.selectDate.dir*dir);
            this.siblingPlot(dir, callPlot, level - 1);
        }
    },
    // Get previous option(s):
    siblingOption: function(dir)
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
    },
    // Update the states of previous and next buttons:
    updatePrevNext: function()
    {
        this.buttons.prev.classed('disabled', this.cache.isFirst(... this.date()) ||
                                            (!this.siblingOption.call(this.selects.day, -1) &&
                                             !this.siblingOption.call(this.selects.month, -1) &&
                                             !this.siblingOption.call(this.selects.year, -1)));
        this.buttons.next.classed('disabled', this.cache.isLast(... this.date()) ||
                                            (!this.siblingOption.call(this.selects.day, 1) &&
                                             !this.siblingOption.call(this.selects.month, 1) &&
                                             !this.siblingOption.call(this.selects.year, 1)));
    },
};
