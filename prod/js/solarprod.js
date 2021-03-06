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

        ret.push = function(value) {
            if (value === null)
                return false;

            var l = 0;
            while(++l <= 4) {
                if (data[l - 1] == '') {
                    data[l - 1] = value;
                    return l;
                }
            }

            return false;
        };

        ret.pop = function() {
            var l = 4;
            while(--l >= 0) {
                if (data[l - 1] != '') {
                    data[l - 1] = '';
                    return l;
                }
            }

            return false;
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

    var selectVar = null;
    var selectSum = null;

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
    buttons.today = toolbar2.append('img').classed('button', true)
                                          .attr('src', 'img/today.png')
                                          .attr('title', 'Aujourd\'hui')
                                          .attr('alt', 'Aujourd\'hui');
    buttons.plot = toolbar2.append('img').classed('button', true)
                                         .attr('src', 'img/plot.png')
                                         .attr('title', 'Tracer')
                                         .attr('alt', 'Tracer');
    buttons.prev = toolbar2.append('img').classed('button', true)
                                         .classed('disabled', true)
                                         .attr('src', 'img/prev.png')
                                         .attr('title', 'Précédent')
                                         .attr('alt', 'Précédent');
    buttons.up = toolbar2.append('img').classed('button', true)
                                       .classed('disabled', true)
                                       .attr('src', 'img/up.png')
                                       .attr('alt', 'Élargir');
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
    buttons.config = toolbar2.append('img').classed('button', true)
                                           .attr('src', 'img/config.png')
                                           .attr('title', 'Configuration')
                                           .attr('alt', 'Config');
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

    buttons.today.attr('id', 'today');
    buttons.plot.attr('id', 'plot');
    buttons.prev.attr('id', 'prev');
    buttons.up.attr('id', 'up');
    buttons.next.attr('id', 'next');
    buttons.cursor.attr('id', 'cursor');
    buttons.export.attr('id', 'export');
    buttons.config.attr('id', 'config');
    buttons.info.attr('id', 'info');
    buttons.help.attr('id', 'help');

    var chart = new SolarChart(d3.select('body'));
    this.chart = chart;

    // Get the value of a cookie:
    var getCookie = function(name, defaultValue)
    {
        var cookies = decodeURIComponent(document.cookie).split(';');
        for(var c = 0; c < cookies.length; c++) {
            if (!cookies[c].trim().startsWith(name + '='))
                continue;
            return cookies[c].trim().substring(name.length + 1);
        }

        return defaultValue;
    };

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

        if (selects.year.property('value') == '')
            buttons.up.attr('title', '');
        else if (selects.month.property('value') == '')
            buttons.up.attr('title', "Afficher toutes les années");
        else if (selects.day.property('value') == '')
            buttons.up.attr('title', "Afficher toute l'année");
        else
            buttons.up.attr('title', "Afficher tout le mois");
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
            updatePrevNext();
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
            updatePrevNext();
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
            } else {
                selects()[level - 1].property('value', date()[level - 1]);
                date.update(level, selects()[level - 1].property('value'));
            }

            if (((level == 3) || (selectDate()[level] == 0)) && (selectDate.dir == -1))
                updateCache();
            selectDate.update(level, selectDateOffset);

            if (selectDate()[level - 1] == 0) {
                this.update(callPlot, level + 1);
            } else if ((selectDate()[level - 1]*selectDate.dir > 0) && !cache.isLast(... date(level))) {
                this.siblingPlot(1, callPlot, level - 1);
            } else if ((selectDate()[level - 1]*selectDate.dir < 0) && !cache.isFirst(... date(level))) {
                this.siblingPlot(-1, callPlot, level - 1);
            } else {
                updatePrevNext();
                if (callPlot)
                    this.plot();
            }
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

        if (selectVar !== null) {
            selects.var.property('value', selectVar);
            if (data.variable() != selectVar) {
                data.variable(selectVar);
                chart.draw();
            }
        }
        selectVar = null;

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

        if (selectSum !== null) {
            selects.agg.property('value', selectSum);
            if (data.aggregation() != selectSum) {
                data.aggregation(selectSum);
                chart.draw();
            }
        }
        selectSum = null;
    };

    this.plot = function(currentLevel) {
        // Do not fetch plot data while there are pending list requests:
        if (pendingListRequests != 0)
            return;

        // Set date of current year/month/day:
        if (currentLevel !== undefined) {
            var titles = ["", "Afficher toutes les années", "Afficher toute l'année", "Afficher tout le mois"]; // TODO locale

            clearSelect(Math.max(currentLevel, 1));

            for (var l = 1; l <= currentLevel; l++)
                selectDate.update(l, -1);
            if (currentLevel >= 1)
                selectDate.dir = 1;

            buttons.cursor.classed('disabled', currentLevel < 0);
            buttons.up.classed('disabled', currentLevel <= 0);
            buttons.up.attr('title', titles[Math.max(currentLevel, 0)]);

            this.update((currentLevel < 3) && (currentLevel >= 0), 1);
            if (currentLevel < 3)
                return;
        }

        if (currentLevel == 3) {
            if (this.chart.plot.data.hasDate())
                return;
        } else {
            if (this.chart.plot.data.hasDate(... date()))
                return;
        }

        var solarPromise = currentLevel == 3 ? SolarData.create() : SolarData.create(... date());
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

            var parentElements = this.chart.setData(data);
            if (parentElements) {
                parentElements.each((d, i, nodes) => {
                    d3.select(nodes[i]).on('click', (d) => this.childPlot(d.x));
                });
            }

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
            updatePrevNext();
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
            this.update(callPlot, level + 1);
        } else if ((level > 1) || (selectDate().some((x) => x != 0))) {
            selectDate.update(level, selectDate.dir*dir);
            this.siblingPlot(dir, callPlot, level - 1);
        }
    };

    this.childPlot = function()
    {
        var titles = ["", "Afficher toutes les années", "Afficher toute l'année", "Afficher tout le mois"]; // TODO centralize in locale
        var child = arguments[0];
        var callPlot = (arguments.length > 1) ? arguments[1] : true;
        var level = child == '' ? date.pop() : date.push('' + child + '');

        if (level === false)
            return;

        buttons.up.classed('disabled', (child == '') && (level == 1));
        buttons.up.attr('title', titles[level - (child == '')])
        this.update(callPlot, level);
    };

    this.configure = function() {
        new Popup(function(selection) {
            d3.html('config.html').on('error', (error) => {
                console.warn('Could not load "config.html"', error);
                this.close();
            }).on('load', (html) => {
                this.show();

                //new TabView(selection, html);
                selection.classed('config', true).html(html.getElementById('home').innerHTML.trim());

                var dataSources = selection.selectAll('select').filter(function() {
                    return d3.select(this).attr('data-src') != null;
                });
                dataSources.each(function() {
                    var dataSink = d3.select(this);
                    var dataValues = JSON.parse(dataSink.attr('data-values').replace(/'/g, '"'));
                    selection.select(dataSink.attr('data-src')).on('change', function() {
                        var dataOptions = dataSink.selectAll('option').data(Object.getOwnPropertyNames(dataValues[d3.select(d3.event.target).property('value')]));
                        dataOptions.exit().remove();
                        dataOptions = dataOptions.enter().append('option').merge(dataOptions);
                        dataOptions.attr('value', (d) => d)
                                   .text((d) => dataValues[d3.select(d3.event.target).property('value')][d]);
                        dataSink.attr('disabled', dataSink.selectAll('option').empty() ? true : null);
                        dataSink.select(function() {
                            return this.parentElement.previousElementSibling;
                        }).classed('disabled', dataSink.attr('disabled') != null);
                        dataSink.dispatch('change');
                    });
                });

                selection.selectAll('select').each(function() {
                    var select = d3.select(this);
                    select.property('value', getCookie(select.attr('id'), ''));
                    select.dispatch('change');
                });

                /*selection.selectAll('input[name="configScale"]').filter(function() {
                    return d3.select(this).attr('value') == getCookie('configScale', '');
                }).property('checked', true);*/
            }).get();
        }, 'Configuration', 'img/config.png', [{
            'title': 'Valider',
            'callback': function(selection) {
                selection.selectAll('select').each(function() {
                    var select = d3.select(this);
                    if (select.property('value') == '')
                        document.cookie = select.attr('id') + '=; expires=Thu, 01 Jan 1970 00:00:00 UTC';
                    else
                        document.cookie = select.attr('id') + '=' + select.property('value') + '; expires=Fri, 31 Dec 9999 23:59:59';
                });
                selection.selectAll('input[name="configScale"]').filter(function() {
                    return d3.select(this).property('checked');
                }).each(function() {
                    document.cookie = 'configScale=' + this.value + '; expires=Fri, 31 Dec 9999 23:59:59';
                });

                this.close();
            },
        }, {
            'title': 'Annuler',
            'callback': function(selection) {
                this.close();
            },
        }]);
    };

    // Window resize event:
    this.windowResize = function()
    {
        var wait = 100;
        if (arguments.length >= 1)
            wait = arguments[0];

        // Compute toolbar total width (defaults to 437):
        var tw = 12;
        d3.selectAll('.toolbar').each(function() {tw += (this.getBoundingClientRect().width + 4);});

        // Plot width and height:
        var w = window.innerWidth - 18;
        var h = window.innerHeight - 56;
        if (window.innerWidth < tw)
            h -= 36;

        this.chart.resize(w, h, wait);
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
        buttons.up.classed('disabled', selects.year.property('value') == '');
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
    buttons.today.on('click', () => {this.plot(3);});
    buttons.plot.on('click', () => {this.plot();});
    buttons.prev.on('click', () => {this.siblingPlot(-1);});
    buttons.up.on('click', () => {this.childPlot('');});
    buttons.next.on('click', () => {this.siblingPlot(1);});
    buttons.cursor.on('click', () => {toogleCursor.call(this);});
    buttons.export.on('click', () => {this.chart.plot.data.exportCsv();});
    buttons.config.on('click', () => {this.configure();});
    buttons.info.on('click', function() {
        new Popup(function(selection) {
            d3.xml('info.xml').on('error', (error) => {
                console.warn('Could not load "info.xml"', error);
                this.close();
            }).on('load', (xml) => {
                d3.xml('info_fr.xsl').on('error', (error) => {
                    console.warn('Could not load "info_fr.xsl"', error);
                    this.close();
                }).on('load', (xsl) => {
                    this.show();

                    var xslProc = new XSLTProcessor();
                    xslProc.importStylesheet(xsl);
                    var html = xslProc.transformToDocument(xml);
                    new TabView(selection, html);
                }).get();
            }).get();
        }, 'À propos', 'img/info.png');
    });
    buttons.help.on('click', function() {
        new Popup(function(selection) {
            d3.html('help.html').on('error', (error) => {
                console.warn('Could not load "help.html"', error);
                this.close();
            }).on('load', (html) => {
                selection.classed('help', true).html(html.getElementById('content').innerHTML.trim());
                this.show();
            }).get();
        }, 'Aide', 'img/help.png');
    });

    // Load event:
    buttons.today.on('load', () => {this.windowResize();});
    buttons.plot.on('load', () => {this.windowResize();});
    buttons.prev.on('load', () => {this.windowResize();});
    buttons.up.on('load', () => {this.windowResize();});
    buttons.next.on('load', () => {this.windowResize();});
    buttons.cursor.on('load', () => {this.windowResize();});
    buttons.export.on('load', () => {this.windowResize();});
    buttons.config.on('load', () => {this.windowResize();});
    buttons.info.on('load', () => {this.windowResize();});
    buttons.help.on('load', () => {this.windowResize();});

    // Key event:
    d3.select(window).on('keydown', () => {
        if ((d3.event.key == 'Escape') && !d3.event.shiftKey && !d3.event.altKey && !d3.event.ctrlKey && !d3.event.metaKey && buttons.cursor.classed('checked'))
            buttons.cursor.dispatch('click');

        if (d3.event.shiftKey || d3.event.altKey || !d3.event.ctrlKey || d3.event.metaKay)
            return;

        if ((d3.event.key == 'Home') && !d3.event.repeat)
            buttons.today.dispatch('click');

        if ((d3.event.key == 'Enter') && !d3.event.repeat)
            buttons.plot.dispatch('click');

        if ((d3.event.key == 'ArrowUp') && !d3.event.repeat)
            buttons.up.dispatch('click');

        if (d3.event.key == 'ArrowLeft')
            buttons.prev.dispatch('click');

        if (d3.event.key == 'ArrowRight')
            buttons.next.dispatch('click');

        if ((d3.event.key == 'ArrowDown') && !d3.event.repeat)
            buttons.export.dispatch('click');

        if ((d3.event.key == 'c') && !buttons.cursor.classed('checked'))
            buttons.cursor.dispatch('click');

        if ((d3.event.key == 'F3') && !d3.event.repeat)
            buttons.config.dispatch('click');

        if ((d3.event.key == 'F2') && !d3.event.repeat)
            buttons.info.dispatch('click');

        if ((d3.event.key == 'F1') && !d3.event.repeat)
            buttons.help.dispatch('click');
    });

    // Resize event:
    d3.select(window).on('resize', () => {this.windowResize();});
    this.windowResize(0);

    // Plot default:
    selectVar = getCookie('defaultVar', null);
    selectSum = getCookie('defaultSum', null);
    this.plot(parseInt(getCookie('defaultDate', -1)));
};
