function SolarProd() {
    // Current date:
    this.year = '';
    this.month = '';
    this.day = '';


    // Day and month to select:
    this.selectMonth = 0;
    this.selectDay = 0;
    this.selectDir = 1;

    d3.select('body').append('div');

    var toolbar1 = d3.select('body').select('div').append('div').classed('toolbar', true);
    var toolbar2 = d3.select('body').select('div').append('div').classed('toolbar', true);

    // The selectors:
    this.daySelect = toolbar1.append('select').attr('title', 'Jour')
                                              .attr('disabled', true)
                                              .on('change', () => {
        this.day = this.daySelect.property('value');
        updatePrevNext();
    });
    this.monthSelect = toolbar1.append('select').attr('title', 'Mois')
                                                .attr('disabled', true)
                                                .on('change', () => {
        this.month = this.monthSelect.property('value');
        updatePrevNext();
        this.updateDays();
    });
    this.yearSelect = toolbar1.append('select').attr('title', 'Année')
                                               .attr('disabled', true)
                                               .on('change', () => {
        this.year = this.yearSelect.property('value');
        updatePrevNext();
        this.updateMonths();
    });
    this.varSelect = toolbar1.append('select').attr('title', 'Variable')
                                              .attr('disabled', true);
    this.aggSelect = toolbar1.append('select').attr('title', 'Aggrégation')
                                              .attr('disabled', true);

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

    this.updateYears(false);
}

SolarProd.prototype = {
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
                updatePrevNext();
            if ((this.selectDay == 0) && (this.selectDir == -1))
                updateCache();
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
                updatePrevNext();
            if (this.selectDir == -1)
                updateCache();
            this.selectDay = 0;

            if (callPlot)
                this.plot();
        }).get();
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
            updatePrevNext();
        }

        var solarPromise = today ? SolarData.create() : SolarData.create(this.year, this.month, this.day);
        solarPromise.catch(console.warn);
        solarPromise.then((data) => {
            updateVariables(data);
            this.chart.setData(data);

            // Activate export:
            this.exportButton.classed('disabled', false);
        });
    },

    // Plots data for previous day:
    prevDayPlot: function(callPlot)
    {
        if ((cache.firstDay !== undefined) && (this.year == cache.firstDay[0]) && (this.month == cache.firstDay[1]) && (this.day == cache.firstDay[2]))
            return;

        var prevDay = prevOption(this.daySelect, this.day);
        if (prevDay) {
            this.day =  prevDay.attr('value');
            this.daySelect.property('value', this.day);
            updatePrevNext();
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
        if ((cache.firstMonth !== undefined) && (this.year == cache.firstMonth[0]) && (this.month == cache.firstMonth[1])) {
            if (this.selectDay != 0) {
                this.selectDir = -1;
                this.nextDayPlot(callPlot);
            }
            return;
        }

        var prevMonth = prevOption(this.monthSelect, this.month);
        if (prevMonth) {
            this.month = prevMonth.attr('value');
            this.monthSelect.property('value', this.month);
            updatePrevNext();
            this.updateDays(callPlot);
        } else {
            this.selectMonth = -this.selectDir;
            this.prevYearPlot(callPlot);
        }
    },
    // Plots data for previous year:
    prevYearPlot: function(callPlot)
    {
        if ((cache.firstYear !== undefined) && (this.year == cache.firstYear[0])) {
            if (this.selectDay != 0) {
                this.selectDir = -1;
                this.nextDayPlot(callPlot);
            } else if (this.selectMonth != 0) {
                this.selectDir = -1;
                this.nextMonthPlot(callPlot);
            }
            return;
        }

        var prevYear = prevOption(this.yearSelect, this.year);
        if (prevYear) {
            this.year = prevYear.attr('value');
            this.yearSelect.property('value', this.year);
            updatePrevNext();
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
        if ((cache.lastDay !== undefined) && (this.year == cache.lastDay[0]) && (this.month == cache.lastDay[1]) && (this.day == cache.lastDay[2]))
            return;

        var nextDay = nextOption(this.daySelect, this.day);
        if (nextDay) {
            this.day = nextDay.attr('value');
            this.daySelect.property('value', this.day);
            updatePrevNext();
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
        if ((cache.lastMonth !== undefined) && (this.year == cache.lastMonth[0]) && (this.month == cache.lastMonth[1])) {
            if (this.selectDay != 0) {
                this.selectDir = -1;
                this.prevDayPlot(callPlot);
            }
            return;
        }

        var nextMonth = nextOption(this.monthSelect, this.month);
        if (nextMonth) {
            this.month = nextMonth.attr('value');
            this.monthSelect.property('value', this.month);
            updatePrevNext();
            this.updateDays(callPlot);
        } else {
            this.selectMonth = this.selectDir;
            this.nextYearPlot(callPlot);
        }
    },
    // Plots data for next year:
    nextYearPlot: function(callPlot)
    {
        if ((cache.lastYear !== undefined) && (this.year == cache.lastYear[0])) {
            if (this.selectDay != 0) {
                this.selectDir = -1;
                this.prevDayPlot(callPlot);
            } else if (this.selectMonth != 0) {
                this.selectDir = -1;
                this.prevMonthPlot(callPlot);
            }
            return;
        }

        var nextYear = nextOption(this.yearSelect, this.year);
        if (nextYear) {
            this.year = nextYear.attr('value');
            this.yearSelect.property('value', this.year);
            updatePrevNext();
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
}
