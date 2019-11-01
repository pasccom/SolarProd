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

function drawGraphs(selection){
    selection.selectAll('svg').each(function() {
        var graph = d3.select(this);

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

function popup() {
    // Argument processing (contents[, title[, icon]])
    if (arguments.length < 1)
        return;

    var contents = arguments[0];
    var title = null;
    var icon = null;

    if (arguments.length >= 2)
        title = arguments[1];
    if (arguments.length >= 3)
        icon = arguments[2];

    // The overlay:
    var overlay = d3.select('body').append('div').classed('overlay', true);

    // The popup:
    var popup = d3.select('body').append('div').classed('popup', true)
                                 .on('click', () => {d3.event.stopPropagation();});

    // The close button:
    var closeButton = popup.append('img').attr('src', 'img/close.png')
                                         .attr('title', 'Fermer')
                                         .attr('alt', 'X')
                                         .attr('id', 'close');

    // Title and icon:
    if (title) {
        popup.append('h4');

        if (icon)
            popup.select('h4').append('img').attr('src', icon);

        popup.select('h4').append('span').text(title);
    }

    // Contents:
    contents(popup.append('div').attr('id', 'content'));

    // Close function:
    this.close = function() {
        d3.selectAll('.popup').select('#content').dispatch('close');
        d3.selectAll('.overlay').remove();
        d3.selectAll('.popup').remove();
        d3.select(window).on('keydown.popup', null);
        d3.select(window).on('resize.popup', null);
    };
    overlay.on('click', this.close.bind(this));
    closeButton.on('click', this.close.bind(this));
    d3.select(window).on('keydown.popup', () => {
        if ((d3.event.key == 'Escape') && !d3.event.shiftKey && !d3.event.altKey && !d3.event.ctrlKey && !d3.event.metaKey)
            this.close();
    });

    // Resize event:
    this.windowResize = function() {
        // Popup width and height:
        var w = window.innerWidth;
        var h = window.innerHeight;

        var pw = Math.max(0.5*w, Math.min(362, w));
        var ph = Math.max(0.7*h, Math.min(462, h));

        popup.style('width', pw + 'px')
             .style('height', ph + 'px')
             .style('left', ((w - pw) / 2) + 'px')
             .style('top', ((h - ph) / 2) + 'px');
    };

    d3.select(window).on('resize.popup', this.windowResize.bind(this));
    this.windowResize();
}

function tabView(parent, contents) {
    // Parent customization:
    parent.classed('tab-view', true)
          .style('overflow-x', 'hidden');

    // The scroll buttons:
    parent.append('p').attr('id', 'left-button')
                      .classed('scroll', true)
                      .style('display', 'none')
                      .text('<');
    parent.append('p').attr('id', 'right-button')
                      .classed('scroll', true)
                      .style('display', 'none')
                      .text('>');

    // The tabs:
    var tabBar = parent.append('ul');
    var tabElements = tabBar.selectAll('li').data(contents.querySelectorAll('div'));
    tabElements.exit().remove();
    tabElements = tabElements.enter().append('li').text((d) => d.title).merge(tabElements);

    // The pages:
    var page = parent.append('div');
    contents.querySelectorAll('div').forEach(function(d) {
        var newPage = page.append(() => d);
        drawGraphs(newPage);
    });
    page.selectAll('div').style('display', 'none');

    // Tabs and pages binding:
    tabElements.on('click', (d, i) => {
        page.selectAll('div').filter(function() {
            return d3.select(this).style('display') == 'block';
        }).dispatch('hide');
        tabElements.classed('active-tab', false);
        page.selectAll('div').style('display', 'none');
        tabElements.filter((d, j) => (i == j)).classed('active-tab', true);
        page.selectAll('div').filter((d, j) => (i == j)).style('display', 'block')
                                                        .dispatch('show');
        this.windowResize();
    });
    tabElements.filter((d, i) => (i == 0)).classed('active-tab', true);
    page.selectAll('div').filter((d, i) => (i == 0)).style('display', 'block');

    // Scroll:
    this.scroll = function(dir) {
        var curMargin = parseFloat(tabBar.style('margin-left'));
        var pw = tabBar.node().getBoundingClientRect().width + curMargin + 4;

        var tw = -8;
        tabElements.each(function() {
           tw += this.getBoundingClientRect().width;
        });

        //console.log("Scroll: ", pw - 30 - tw, curMargin, 26);

        tabBar.style('margin-left', Math.max(pw - 30 - tw, Math.min(26, curMargin + dir)) + 'px');
    };
    this.autoScroll = (function() {
        var scrollTimer = null;
        return function(start, dir) {
            if (start) {
                this.scroll(dir);
                scrollTimer = window.setInterval(() => this.scroll(dir), 100);
            } else {
                if (scrollTimer !== null)
                    window.clearInterval(scrollTimer);
                scrollTimer = null;
            }
        };
    }).call(this);

    parent.select('#left-button').on('mousedown', () => this.autoScroll(true, +5));
    parent.select('#left-button').on('mouseup', () => this.autoScroll(false));
    parent.select('#right-button').on('mousedown', () => this.autoScroll(true, -5));
    parent.select('#right-button').on('mouseup', () => this.autoScroll(false));

    // Resize event:
    this.windowResize = function() {
        var curMargin = parseFloat(tabBar.style('margin-left'));
        var pw = tabBar.node().getBoundingClientRect().width + curMargin + 4;

        var tw = -8;
        var bw = -8;
        var aw = -8;
        tabElements.each(function() {
           if (d3.select(this).classed('active-tab'))
               bw = tw;
           tw += this.getBoundingClientRect().width;
           if (d3.select(this).classed('active-tab'))
               aw = tw;
        });

        // console.log("Total width:", tw);
        // console.log("Before width:", bw);
        // console.log("After width:", aw);
        // console.log("Parent width:", pw);


        if (pw < tw) {
            parent.selectAll('.scroll').style('display', 'block');

            var maxMargin = Math.min(26, pw - 30 - aw);
            var minMargin = Math.max(pw - 30 - tw, 26 - 8 - bw);

            // console.log("Margins:", minMargin, curMargin, maxMargin);

            tabBar.style('margin-left', Math.max(minMargin, Math.min(maxMargin, curMargin)) + 'px');
        } else {
            parent.selectAll('.scroll').style('display', 'none');
            tabBar.style('margin-left', '-4px');
        }
    };

    d3.select(window).on('resize.tab-view', this.windowResize.bind(this));
    parent.on('close', function() {
        console.log("Tab-view close event");
        page.selectAll('div').dispatch('close');
        d3.select(window).on('resize.tab-view', null);
    });
    this.windowResize();
}

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
    buttons.cursor = toolbar2.append('img').classed('button', true)
                                           .classed('disabled', true)
                                           .attr('src', 'img/cursor.png')
                                           .attr('title', 'Afficher le curseur')
                                           .attr('alt', 'Curseur');
    buttons.export = toolbar2.append('img').classed('button', true)
                                           .classed('disabled', true)
                                           .attr('src', 'img/csv.png')
                                           .attr('title', 'Export CSV')
                                           .attr('alt', 'Export CSV');
    buttons.info = toolbar2.append('img').classed('button', true)
                                         .attr('src', 'img/info.png')
                                         .attr('title', 'Informations')
                                         .attr('alt', 'Info');
    buttons.help = toolbar2.append('img').classed('button', true)
                                         .attr('src', 'img/help.png')
                                         .attr('title', 'Aide')
                                         .attr('alt', 'Aide');

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
    buttons.cursor.attr('id', 'cursor');
    buttons.export.attr('id', 'export');
    buttons.info.attr('id', 'info');
    buttons.help.attr('id', 'help');

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
            this.windowResize();
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
            this.windowResize();
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
            this.windowResize();

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
            } else {
                selects()[level - 1].property('value', date()[level - 1]);
                date.update(level, selects()[level - 1].property('value'));
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
                                         .text(SolarData.variables.name);
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
                                        .text(SolarData.aggregations.name);
            aggs.exit().remove();
            aggs.order();

            // Updates aggs if needed:
            if (selects.agg.property('value') != data.aggregation()) {
                data.aggregation(selects.agg.property('value'));
            }
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

        if (today) {
            if (this.chart.plot.data.hasDate())
                return;
        } else {
            if (this.chart.plot.data.hasDate(... date()))
                return;
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

            // Activate data cursor and export:
            buttons.cursor.classed('checked', false);
            buttons.cursor.classed('disabled', data.isEmpty());
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
        // Compute toolbar total width (defaults to 437):
        var tw = 12;
        d3.selectAll('.toolbar').each(function() {tw += (this.getBoundingClientRect().width + 4);});

        // Plot width and height:
        var w = window.innerWidth - 18;
        var h = window.innerHeight - 56;
        if (window.innerWidth < tw)
            h -= 36;

        this.chart.resize(w, h);
    };

    var toogleCursor = function() {
        buttons.cursor.classed('checked', this.chart.enableCursor(!buttons.cursor.classed('checked')));
    };

    var setupSelectEvents = function(select, callback) {
        var eventsBlocked = false;

        select.on('change', function() {
            if (!eventsBlocked)
                callback.apply(this, arguments);
        });

        select.on('keydown', function() {
            var value = select.property('value');

            if (d3.event.key == 'Control')
                eventsBlocked = true;

            if (eventsBlocked) {
                setTimeout(function() {
                    for (var l = 3; l >= 0; l--) {
                        if ((l !== 0) && (select == selects()[l - 1])) {
                            select.property('value', date()[l - 1]);
                            break;
                        }
                        if (l === 0)
                            select.property('value', value);
                    }
                });
            }
        });

        select.on('keyup', function() {
           if (d3.event.key == 'Control')
                eventsBlocked = false;
        });
    };

    // Change event:
    selects.day.call(setupSelectEvents, () => {
        date.update(3, selects.day.property('value'));
        updatePrevNext();
    });
    selects.month.call(setupSelectEvents, () => {
        date.update(2, selects.month.property('value'));
        updatePrevNext();
        this.update(false, 3);
    });
    selects.year.call(setupSelectEvents, () => {
        date.update(1, selects.year.property('value'));
        updatePrevNext();
        this.update(false, 2);
    });
    selects.var.call(setupSelectEvents, () => {
        chart.plot.data.variable(selects.var.property('value'));
        updateAggs();
        this.chart.draw();
        buttons.cursor.classed('checked', false);
    });
    selects.agg.call(setupSelectEvents, () => {
        this.chart.plot.data.aggregation(selects.agg.property('value'));
        this.chart.draw();
        buttons.cursor.classed('checked', false);
    });

    // Click event:
    buttons.plot.on('click', () => {this.plot();});
    buttons.prev.on('click', () => {this.siblingPlot(-1);});
    buttons.today.on('click', () => {this.plot(true);});
    buttons.next.on('click', () => {this.siblingPlot(1);});
    buttons.cursor.on('click', () => {toogleCursor.call(this);});
    buttons.export.on('click', () => {this.chart.plot.data.exportCsv();});
    buttons.info.on('click', function() {
        popup(function(selection) { // TODO do not show popup when json does not load
            d3.html('info.html', (html) => {
                tabView(selection, html);
            });
        }, 'À propos', 'img/info.png');
    });
    buttons.help.on('click', function() {
        popup(function(selection) { // TODO do not show popup when html does not load
            d3.html('help.html', (html) => {
                selection.classed('help', true).html(html.getElementById('content').innerHTML.trim());
            });
        }, 'Aide', 'img/help.png');
    });

    // Load event:
    buttons.plot.on('load', () => {this.windowResize();});
    buttons.prev.on('load', () => {this.windowResize();});
    buttons.today.on('load', () => {this.windowResize();});
    buttons.next.on('load', () => {this.windowResize();});
    buttons.cursor.on('load', () => {this.windowResize();});
    buttons.export.on('load', () => {this.windowResize();});
    buttons.info.on('load', () => {this.windowResize();});
    buttons.help.on('load', () => {this.windowResize();});

    // Key event:
    d3.select(window).on('keydown', () => {
        if ((d3.event.key == 'Escape') && !d3.event.shiftKey && !d3.event.altKey && !d3.event.ctrlKey && !d3.event.metaKey && buttons.cursor.classed('checked'))
            buttons.cursor.dispatch('click');

        if (d3.event.shiftKey || d3.event.altKey || !d3.event.ctrlKey || d3.event.metaKay)
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

        if ((d3.event.key == 'c') && !buttons.cursor.classed('checked'))
            buttons.cursor.dispatch('click');

        if ((d3.event.key == 'F2') && !d3.event.repeat)
            buttons.info.dispatch('click');

        if ((d3.event.key == 'F1') && !d3.event.repeat)
            buttons.help.dispatch('click');
    });

    // Resize event:
    d3.select(window).on('resize', this.windowResize.bind(this));
    this.windowResize();

    // Update year selector:
    this.update(false, 1);
};
