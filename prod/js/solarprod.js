function SolarCache() {
    // Get cache:
    d3.json("list/cache.json").on('error', console.log)
                              .on('load', (data) => {
        Object.keys(data).forEach((k) => {this[k] = data[k];});
    }).get();
}

SolarCache.is = function(member) {
    return function() {
        if (this[member] === undefined)
            return false;

        for (var i = 0; i < Math.min(this[member].length, arguments.length); i++)
            if (this[member][i] != arguments[i])
                return false;

        return true;
    };
};

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
    isFirstDay: SolarCache.is('firstDay'),
    isLastDay: SolarCache.is('lastDay'),
    isFirstMonth: SolarCache.is('firstMonth'),
    isLastMonth: SolarCache.is('lastMonth'),
    isFirstYear: SolarCache.is('firstYear'),
    isLastYear: SolarCache.is('lastYear'),
};

function SolarProd() {
    // Current date:
    this.date = function() {
        var l = (arguments.length > 0) ? arguments[0] : 3;
        return [this.date.year, this.date.month, this.date.day].slice(0, l);
    };
    this.date.year = '';
    this.date.month = '';
    this.date.day = '';
    this.date.update = SolarProd.update;

    // Date to select:
    this.selectDate = function() {
        var l = (arguments.length > 0) ? arguments[0] : 3;
        return [this.selectDate.year, this.selectDate.month, this.selectDate.day].slice(0, l);
    };
    this.selectDate.year = 0;
    this.selectDate.month = 0;
    this.selectDate.day = 0;
    this.selectDate.dir = 1;
    this.selectDate.update = SolarProd.update;

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
        this.updateDays();
    });
    this.selects.year = toolbar1.append('select').attr('title', 'Année')
                                                 .attr('disabled', true)
                                                 .on('change', () => {
        this.date.year = this.selects.year.property('value');
        this.updatePrevNext();
        this.updateMonths();
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

    this.updateYears(false);
}

SolarProd.update = function(level, value) {
    if (!value)
        return false;

    var members = ['', 'year', 'month', 'day'];
    this[members[level]] = value;
    return true;
};

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

    // Update years selector:
    updateYears: function(callPlot) {
        // Fetch available years with AJAX:
        d3.json("list/years.json").on('error', console.warn)
                                  .on('load', (data) => {
            data.unshift('');
            var years = this.selects.year.attr('disabled', null)
                                         .selectAll('option').data(data);

            years.enter().append('option').attr('value', (d) => d)
                                          .text((d) => d);
            years.exit().remove();

            if (callPlot)
                this.plot();
        }).get();
    },
    // Update months selector:
    updateMonths: function(callPlot)
    {
        this.selects.month.attr('disabled', true);
        this.selects.day.attr('disabled', true);

        if (this.date.year == '') {
            this.date.month = '';
            this.date.day = '';
            this.selects.month.attr('disabled', true)
                              .selectAll('option').remove();
            this.selects.day.attr('disabled', true)
                            .selectAll('option').remove();
            if (callPlot)
                this.plot();
            return;
        }
        console.log("Selected new year: " + pad(this.date.year, 4, '0'));

        // Fetch available months with AJAX:
        d3.json("list/months/" + pad(this.date.year, 4, '0') + ".json").on('error', (error) => {
            console.warn(error);

            this.date.month = '';
            this.date.day = '';
            this.selects.month.attr('disabled', true)
                              .selectAll('option').remove();
            this.selects.day.attr('disabled', true)
                            .selectAll('option').remove();
            this.siblingPlot(this.selectDate.month*this.selectDate.dir, callPlot, 1);
        }).on('load', (data) => {
            data.unshift('');

            var months = this.selects.month.attr('disabled', null)
                                           .selectAll('option').data(data, (d) => d);
            months.enter().append('option').attr('value', (d) => d)
                                           .text((d) => (d == '' ? '' : localeLongMonth(new Date(this.date.year, d - 1))));
            months.exit().remove();

            this.selects.month.selectAll('option')
                              .filter((d) => (d == ''))
                              .lower();

            if (this.selectDate.month*this.selectDate.dir > 0)
                this.date.month = data[this.selectDate.month*this.selectDate.dir];
            if (this.selectDate.month*this.selectDate.dir < 0)
                this.date.month = data[data.length + this.selectDate.month*this.selectDate.dir];
            this.selects.month.property('value', this.date.month);

            if (this.selectDate.month != 0)
                this.updatePrevNext();
            if ((this.selectDate.day == 0) && (this.selectDate.dir == -1))
                this.updateCache();
            this.selectDate.month = 0;

            this.updateDays(callPlot);
            if ((callPlot) && (this.date.day == ''))
                this.plot();
        }).get();
    },
    // Update days selector:
    updateDays: function(callPlot)
    {
        if (this.date.month == '') {
            this.date.day = '';
            this.selects.day.attr('disabled', true)
                            .selectAll('option').remove();
            if (callPlot)
                this.plot();
            return;
        }

        console.log("Selected new month: " + pad(this.date.month, 2, '0') + "/" + pad(this.date.year, 4, '0'));

        // Fetch available days with AJAX:
        d3.json("list/days/" + pad(this.date.year, 4, '0') + "/" + pad(this.date.month, 2, '0')  + ".json").on('error', () => {
            this.date.day = '';
            this.selects.day.attr('disabled', true)
                            .selectAll('option').remove();
            this.siblingPlot(this.selectDate.day*this.selectDate.dir, callPlot, 2);
        }).on('load', (data) => {
            data.unshift('');

            var days = this.selects.day.attr('disabled', null)
                                       .selectAll('option')
                                       .data(data, (d) => d);
            days.enter().append('option').attr('value', (d) => d)
                                         .text((d) => d);
            days.exit().remove();

            this.selects.day.selectAll('option')
                            .filter((d) => (d == ''))
                            .lower();

            if (this.selectDate.day*this.selectDate.dir > 0)
                this.date.day = data[this.selectDate.day*this.selectDate.dir];
            if (this.selectDate.day*this.selectDate.dir < 0)
                this.date.day = data[data.length + this.selectDate.day*this.selectDate.dir];
            this.selects.day.property('value', this.date.day);

            if (this.selectDate.day != 0)
                this.updatePrevNext();
            if (this.selectDate.dir == -1)
                this.updateCache();
            this.selectDate.day = 0;

            if (callPlot)
                this.plot();
        }).get();
    },
    // Updates the variable selector:
    updateVars: function()
    {
        var data = (arguments.length >= 1) ?  arguments[0] : this.chart.plot.data;

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
            this.updateAggs(data);
        }
    },
    // Updates the sum selector:
    updateAggs: function()
    {
        var data = (arguments.length >= 1) ?  arguments[0] : this.chart.plot.data;

        // Adds the new sums using a data join:
        var aggs = this.selects.agg.attr('disabled', (data.validAggs.length < 2) ? true : null)
                                   .selectAll('option').data(data.validAggs, (d) => d);
        aggs.enter().append('option').attr('value', (d) => d)
                                     .text(SolarData.aggregationName);
        aggs.exit().remove();
        aggs.order();
    },
    // Update cache:
    updateCache: function()
    {
        if (this.selectDate.day == 1)
            this.cache.lastDay = this.date(3);
        else if (this.selectDate.day == -1)
            this.cache.firstDay = this.date(3);
        else if (this.selectDate.month == 1)
            this.cache.lastMonth = this.date(2);
        else if (this.selectDate.month == -1)
            this.cache.firstMonth = this.date(2);
        else
            return;

        this.selectDate.dir = 1;
        console.log('Updated cache:', this.cache);
        this.updatePrevNext();
    },

    plot: function(today) {
        // Set date of today:
        if (today) {
            this.selectDate.month = -1;
            this.selectDate.day = -1;
            this.selectDate.dir = 1;
            this.date.year = this.selects.year.selectAll('option').filter(function() {return (this.nextElementSibling == null);})
                                                                  .attr('value');
            this.selects.year.property('value', this.date.year);
            this.updateMonths();
            this.updatePrevNext();
        }

        var solarPromise = today ? SolarData.create() : SolarData.create(... this.date());
        solarPromise.catch(console.warn);
        solarPromise.then((data) => {
            this.updateVars(data);
            this.chart.setData(data);

            // Activate export:
            this.buttons.export.classed('disabled', false);
        });
    },

    update: function(callPlot, level) {
        if (level == 1)
            this.updateYears(callPlot);
        else if (level == 2)
            this.updateMonths(callPlot);
        else if (level == 3)
            this.updateDays(callPlot);
        else if (callPlot)
            this.plot();
    },

    siblingPlot: function()
    {
        var dir = arguments[0];
        var callPlot = (arguments.length > 1) ? arguments[1] : true;

        if (dir == 0) {
            if (callPlot)
                this.plot();
            return;
        }

        if (arguments.length < 3) {
            for (var l = 3; l > 0; l--) {
                if (this.date()[l - 1] != '') {
                    this.siblingPlot(dir, callPlot, l);
                    break;
                }
            }
            return;
        }

        var level = arguments[2];

        if (level == 0) {
            this.buttons(dir).classed('disabled', true);
            this.selectDate.dir = -1;
            for (var l = 3; l > 1; l--) {
                if (this.selectDate()[l - 1] != 0) {
                    this.siblingPlot(-dir, callPlot, l);
                    break;
                }
            }
            return;
        }

        if (((dir == 1 ) && this.cache.isLast(... this.date(level))) ||
            ((dir == -1) && this.cache.isFirst(... this.date(level)))) {
            for (var l = 3; l > level; l--) {
                if (this.selectDate()[l - 1] != 0) {
                    this.selectDate.dir = -1;
                    this.siblingPlot(dir, callPlot, l);
                    break;
                }
            }
            return;
        }

        if (this.date.update(level, this.siblingOption.call(this.selects()[level - 1], dir))) {
            this.selects()[level - 1].property('value', this.date()[level - 1]);
            this.updatePrevNext();
            this.update(callPlot, level + 1);
        } else {
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
