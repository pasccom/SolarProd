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
        if ((year != '') && (month != '') && (day != ''))
            return this.isFirstDay(year, month, day);
        else if ((year != '') && (month != ''))
            return this.isFirstMonth(year, month);
        else
            return this.isFirstYear(year);
    },
    isLast: function(year, month, day) {
        if ((year != '') && (month != '') && (day != ''))
            return this.isLastDay(year, month, day);
        else if ((year != '') && (month != ''))
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
    this.year = '';
    this.month = '';
    this.day = '';

    // Day and month to select:
    this.selectMonth = 0;
    this.selectDay = 0;
    this.selectDir = 1;

    // Cache:
    this.cache = new SolarCache();

    d3.select('body').append('div');

    var toolbar1 = d3.select('body').select('div').append('div').classed('toolbar', true);
    var toolbar2 = d3.select('body').select('div').append('div').classed('toolbar', true);

    // The selectors:
    this.daySelect = toolbar1.append('select').attr('title', 'Jour')
                                              .attr('disabled', true)
                                              .on('change', () => {
        this.day = this.daySelect.property('value');
        this.updatePrevNext();
    });
    this.monthSelect = toolbar1.append('select').attr('title', 'Mois')
                                                .attr('disabled', true)
                                                .on('change', () => {
        this.month = this.monthSelect.property('value');
        this.updatePrevNext();
        this.updateDays();
    });
    this.yearSelect = toolbar1.append('select').attr('title', 'Année')
                                               .attr('disabled', true)
                                               .on('change', () => {
        this.year = this.yearSelect.property('value');
        this.updatePrevNext();
        this.updateMonths();
    });
    this.varSelect = toolbar1.append('select').attr('title', 'Variable')
                                              .attr('disabled', true)
                                              .on('change', () => {
        this.chart.plot.data.variable(this.varSelect.property('value'));
        this.updateAggs();
        this.chart.draw();
    });
    this.aggSelect = toolbar1.append('select').attr('title', 'Aggrégation')
                                              .attr('disabled', true)
                                              .on('change', () => {
        this.chart.plot.data.aggregation(this.aggSelect.property('value'));
        this.chart.draw();
    });

    // The buttons:
    this.plotButton = toolbar1.append('img').classed('button', true)
                                            .attr('src', 'img/plot.png')
                                            .attr('title', 'Tracer')
                                            .attr('alt', 'Tracer')
                                            .on('click', () => {this.plot();});
    this.prevButton = toolbar2.append('img').classed('button', true)
                                            .classed('disabled', true)
                                            .attr('src', 'img/prev.png')
                                            .attr('title', 'Précédent')
                                            .attr('alt', 'Précédent')
                                            .on('click', () => {this.prevPlot();});
    this.todayButton = toolbar2.append('img').classed('button', true)
                                             .attr('src', 'img/today.png')
                                             .attr('title', 'Aujourd\'hui')
                                             .attr('alt', 'Aujourd\'hui')
                                             .on('click', () => {this.plot(true);});
    this.nextButton = toolbar2.append('img').classed('button', true)
                                            .classed('disabled', true)
                                            .attr('src', 'img/next.png')
                                            .attr('title', 'Suivant')
                                            .attr('alt', 'Suivant')
                                            .on('click', () => {this.nextPlot();});
    this.exportButton = toolbar2.append('img').classed('button', true)
                                              .classed('disabled', true)
                                              .attr('src', 'img/csv.png')
                                              .attr('title', 'Export CSV')
                                              .attr('alt', 'Export CSV')
                                              .on('click', () => {this.chart.plot.data.exportCsv();});

    // TODO remove?
    // WARNING Used by test.py
    this.daySelect.attr('id', 'day');
    this.monthSelect.attr('id', 'month');
    this.yearSelect.attr('id', 'year');
    this.varSelect.attr('id', 'var');
    this.aggSelect.attr('id', 'sum');

    this.plotButton.attr('id', 'plot');
    this.prevButton.attr('id', 'prev');
    this.todayButton.attr('id', 'today');
    this.nextButton.attr('id', 'next');
    this.exportButton.attr('id', 'export');

    this.chart = new SolarChart(d3.select('body'));
    d3.select(window).on('resize', this.windowResize.bind(this));
    this.windowResize();

    this.updateYears(false);
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

    // Update years selector:
    updateYears: function(callPlot) {
        // Fetch available years with AJAX:
        d3.json("list/years.json").on('error', console.warn)
                                  .on('load', (data) => {
            data.unshift('');
            var years = this.yearSelect.attr('disabled', null)
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
        this.monthSelect.attr('disabled', true);
        this.daySelect.attr('disabled', true);

        if (this.year == '') {
            this.month = '';
            this.day = '';
            this.monthSelect.attr('disabled', true)
                            .selectAll('option').remove();
            this.daySelect.attr('disabled', true)
                          .selectAll('option').remove();
            if (callPlot)
                this.plot();
            return;
        }
        console.log("Selected new year: " + pad(this.year, 4, '0'));

        // Fetch available months with AJAX:
        d3.json("list/months/" + pad(this.year, 4, '0') + ".json").on('error', (error) => {
            console.warn(error);

            this.month = '';
            this.day = '';
            this.monthSelect.attr('disabled', true)
                            .selectAll('option').remove();
            this.daySelect.attr('disabled', true)
                          .selectAll('option').remove();
            if (this.selectMonth*this.selectDir < 0)
                this.prevYearPlot(callPlot);
            else if (this.selectMonth*this.selectDir > 0)
                this.nextYearPlot(callPlot);
            if (callPlot)
                this.plot();
            return;
        }).on('load', (data) => {
            data.unshift('');

            var months = this.monthSelect.attr('disabled', null)
                                         .selectAll('option').data(data, (d) => d);
            months.enter().append('option').attr('value', (d) => d)
                                           .text((d) => (d == '' ? '' : localeLongMonth(new Date(this.year, d - 1))));
            months.exit().remove();

            this.monthSelect.selectAll('option')
                               .filter((d) => (d == ''))
                               .lower();

            if (this.selectMonth*this.selectDir > 0)
                this.month = data[this.selectMonth*this.selectDir];
            if (this.selectMonth*this.selectDir < 0)
                this.month = data[data.length + this.selectMonth*this.selectDir];
            this.monthSelect.property('value', this.month);

            if (this.selectMonth != 0)
                this.updatePrevNext();
            if ((this.selectDay == 0) && (this.selectDir == -1))
                this.updateCache();
            this.selectMonth = 0;

            this.updateDays(callPlot);
            if ((callPlot) && (this.day == ''))
                this.plot();
        }).get();
    },
    // Update days selector:
    updateDays: function(callPlot)
    {
        if (this.month == '') {
            this.day = '';
            this.daySelect.attr('disabled', true)
                          .selectAll('option').remove();
            if (callPlot)
                this.plot();
            return;
        }

        console.log("Selected new month: " + pad(this.month, 2, '0') + "/" + pad(this.year, 4, '0'));

        // Fetch available days with AJAX:
        d3.json("list/days/" + pad(this.year, 4, '0') + "/" + pad(this.month, 2, '0')  + ".json").on('error', () => {
            this.day = '';
            this.daySelect.attr('disabled', true)
                          .selectAll('option').remove();
            if (this.selectDay*this.selectDir < 0)
                this.prevMonthPlot(callPlot);
            else if (this.selectDay*this.selectDir > 0)
                this.nextMonthPlot(callPlot);
            if (callPlot)
                this.plot();
            return;
        }).on('load', (data) => {
            data.unshift('');

            var days = this.daySelect.attr('disabled', null)
                                     .selectAll('option')
                                     .data(data, (d) => d);
            days.enter().append('option').attr('value', (d) => d)
                                         .text((d) => d);
            days.exit().remove();

            this.daySelect.selectAll('option')
                          .filter((d) => (d == ''))
                          .lower();

            if (this.selectDay*this.selectDir > 0)
                this.day = data[this.selectDay*this.selectDir];
            if (this.selectDay*this.selectDir < 0)
                this.day = data[data.length + this.selectDay*this.selectDir];
            this.daySelect.property('value', this.day);

            if (this.selectDay != 0)
                this.updatePrevNext();
            if (this.selectDir == -1)
                this.updateCache();
            this.selectDay = 0;

            if (callPlot)
                this.plot();
        }).get();
    },
    // Updates the variable selector:
    updateVars: function()
    {
        var data = (arguments.length >= 1) ?  arguments[0] : this.chart.plot.data;

        // Adds the new variables using a data join:
        var vars = this.varSelect.attr('disabled', null)
                                 .selectAll('option').data(data.validVars, (d) => d);
        vars.enter().append('option').attr('value', (d) => d)
                                     .text(SolarData.variableName);
        vars.exit().remove();
        vars.order();

        // Updates sums if needed:
        if (this.varSelect.property('value') != data.variable()) {
            data.variable(this.varSelect.property('value'));
            this.updateAggs(data);
        }
    },
    // Updates the sum selector:
    updateAggs: function()
    {
        var data = (arguments.length >= 1) ?  arguments[0] : this.chart.plot.data;

        // Adds the new sums using a data join:
        var aggs = this.aggSelect.attr('disabled', (data.validAggs.length < 2) ? true : null)
                                 .selectAll('option').data(data.validAggs, (d) => d);
        aggs.enter().append('option').attr('value', (d) => d)
                                     .text(SolarData.aggregationName);
        aggs.exit().remove();
        aggs.order();
    },
    // Update cache:
    updateCache: function()
    {
        if (this.selectDay == 1)
            this.cache.lastDay = [this.year, this.month, this.day];
        else if (this.selectDay == -1)
            this.cache.firstDay = [this.year, this.month, this.day];
        else if (this.selectMonth == 1)
            this.cache.lastMonth = [this.year, this.month];
        else if (this.selectMonth == -1)
            this.cache.firstMonth = [this.year, this.month];
        else
            return;

        this.selectDir = 1;
        console.log('Updated cache:', this.cache);
        this.updatePrevNext();
    },

    plot: function(today) {
        // Set date of today:
        if (today) {
            this.selectMonth = -1;
            this.selectDay = -1;
            this.selectDir = 1;
            this.year = this.yearSelect.selectAll('option').filter(function() {return (this.nextElementSibling == null);})
                                                           .attr('value');
            this.yearSelect.property('value', this.year);
            this.updateMonths();
            this.updatePrevNext();
        }

        var solarPromise = today ? SolarData.create() : SolarData.create(this.year, this.month, this.day);
        solarPromise.catch(console.warn);
        solarPromise.then((data) => {
            this.updateVars(data);
            this.chart.setData(data);

            // Activate export:
            this.exportButton.classed('disabled', false);
        });
    },

    // Plots data for previous day:
    prevDayPlot: function(callPlot)
    {
        if (this.cache.isFirstDay(this.year, this.month, this.day))
            return;

        var prevDay = this.prevOption(this.daySelect, this.day);
        if (prevDay) {
            this.day =  prevDay.attr('value');
            this.daySelect.property('value', this.day);
            this.updatePrevNext();
            if (callPlot)
                this.plot();
        } else {
            this.selectDay = -this.selectDir;
            this.prevMonthPlot(callPlot);
        }
    },
    // Plots data for previous month:
    prevMonthPlot: function(callPlot)
    {
        if (this.cache.isFirstMonth(this.year, this.month)) {
            if (this.selectDay != 0) {
                this.selectDir = -1;
                this.nextDayPlot(callPlot);
            }
            return;
        }

        var prevMonth = this.prevOption(this.monthSelect, this.month);
        if (prevMonth) {
            this.month = prevMonth.attr('value');
            this.monthSelect.property('value', this.month);
            this.updatePrevNext();
            this.updateDays(callPlot);
        } else {
            this.selectMonth = -this.selectDir;
            this.prevYearPlot(callPlot);
        }
    },
    // Plots data for previous year:
    prevYearPlot: function(callPlot)
    {
        if (this.cache.isFirstYear(this.year)) {
            if (this.selectDay != 0) {
                this.selectDir = -1;
                this.nextDayPlot(callPlot);
            } else if (this.selectMonth != 0) {
                this.selectDir = -1;
                this.nextMonthPlot(callPlot);
            }
            return;
        }

        var prevYear = this.prevOption(this.yearSelect, this.year);
        if (prevYear) {
            this.year = prevYear.attr('value');
            this.yearSelect.property('value', this.year);
            this.updatePrevNext();
            this.updateMonths(callPlot);
        } else {
            this.prevButton.classed('disabled', true);
            this.selectDir = -1;
            if (this.selectDay != 0)
                this.nextDayPlot(callPlot);
            else if (this.selectMonth != 0)
                this.nextMonthPlot(callPlot);
        }
    },
    // Plots data for previous year/month/day:
    prevPlot: function()
    {
        if (this.day != '')
            this.prevDayPlot(true);
        else if (this.month != '')
            this.prevMonthPlot(true);
        else if (this.year != '')
            this.prevYearPlot(true);
    },

    // Plots data for next day:
    nextDayPlot: function(callPlot)
    {
        if (this.cache.isLastDay(this.year, this.month, this.day))
            return;

        var nextDay = this.nextOption(this.daySelect, this.day);
        if (nextDay) {
            this.day = nextDay.attr('value');
            this.daySelect.property('value', this.day);
            this.updatePrevNext();
            if (callPlot)
                this.plot();
        } else {
            this.selectDay = this.selectDir;
            this.nextMonthPlot(callPlot);
        }
    },
    // Plots data for next month:
    nextMonthPlot: function(callPlot)
    {
        if (this.cache.isLastMonth(this.year, this.month)) {
            if (this.selectDay != 0) {
                this.selectDir = -1;
                this.prevDayPlot(callPlot);
            }
            return;
        }

        var nextMonth = this.nextOption(this.monthSelect, this.month);
        if (nextMonth) {
            this.month = nextMonth.attr('value');
            this.monthSelect.property('value', this.month);
            this.updatePrevNext();
            this.updateDays(callPlot);
        } else {
            this.selectMonth = this.selectDir;
            this.nextYearPlot(callPlot);
        }
    },
    // Plots data for next year:
    nextYearPlot: function(callPlot)
    {
        if (this.cache.isLastYear(this.year)) {
            if (this.selectDay != 0) {
                this.selectDir = -1;
                this.prevDayPlot(callPlot);
            } else if (this.selectMonth != 0) {
                this.selectDir = -1;
                this.prevMonthPlot(callPlot);
            }
            return;
        }

        var nextYear = this.nextOption(this.yearSelect, this.year);
        if (nextYear) {
            this.year = nextYear.attr('value');
            this.yearSelect.property('value', this.year);
            this.updatePrevNext();
            this.updateMonths(callPlot);
        } else {
            this.nextButton.classed('disabled', true);
            this.selectDir = -1;
            if (this.selectDay != 0)
                this.prevDayPlot(callPlot);
            else if (this.selectMonth != 0)
                this.prevMonthPlot(callPlot);
        }
    },
    // Plots data for next year/month/day:
    nextPlot: function()
    {
        if (this.day != '')
            this.nextDayPlot(true);
        else if (this.month != '')
            this.nextMonthPlot(true);
        else if (this.year != '')
            this.nextYearPlot(true);
    },

    // Get previous option(s):
    prevOption: function(d3Select, datum)
    {
        if (datum == '')
            return null;

        var p = d3Select.selectAll('option')
                        .filter(function(d) {return d == datum;})
                        .selectAll(function() {return [this.previousElementSibling];});

        if (p.empty() ||  (p.attr('value') == ''))
            return null;
        return p;
    },
    // Get next option(s):
    nextOption: function(d3Select, datum)
    {
        if (datum == '')
            return null;

        var n = d3Select.selectAll('option')
                        .filter(function(d) {return d == datum;})
                        .selectAll(function() {return [this.nextElementSibling];});

        if (n.empty())
            return null;
        return n;
    },
    // Update the states of previous and next buttons:
    updatePrevNext: function()
    {
        var prevDay = (this.year != '') && (this.month != '') ? this.prevOption(this.daySelect, this.day) : null;
        var nextDay = (this.year != '') && (this.month != '') ? this.nextOption(this.daySelect, this.day) : null;

        var prevMonth = (this.year != '') ? this.prevOption(this.monthSelect, this.month) : null;
        var nextMonth = (this.year != '') ? this.nextOption(this.monthSelect, this.month) : null;

        var prevYear = this.prevOption(this.yearSelect, this.year);
        var nextYear = this.nextOption(this.yearSelect, this.year);

        d3.select('#prev').classed('disabled', this.cache.isFirst(this.year, this.month, this.day) || (!prevDay && !prevMonth && !prevYear));
        d3.select('#next').classed('disabled', this.cache.isLast(this.year, this.month, this.day) || (!nextDay && !nextMonth && !nextYear));
    },
}
