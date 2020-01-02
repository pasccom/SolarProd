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

function SolarData()
{
    // Recursive min function:
    var recMin = function(a)
    {
        if (!Array.isArray(a))
            return a;
        else
            return d3.min(a, recMin);
    }

    // Recursive max function:
    var recMax = function(a)
    {
        if (!Array.isArray(a))
            return a;
        else
            return d3.max(a, recMax);
    }

    // Recursive forEach function:
    var recForEach = function(a, fun)
    {
        if (!Array.isArray(a))
            fun(a);
        else
            a.forEach((e) => recForEach(e, fun));
    };

    const Type = {
        ALL:   'ALL',
        YEAR:  'YEAR',
        MONTH: 'MONTH',
        DAY:   'DAY',
    };

    // Data type:
    var type;
    // Current variable and aggregation:
    var variable;
    var agg;

    var updateDivider = function(maxData)
    {
        this.div = 1;
        this.log1000Div = 0;

        while (maxData/this.div >= 1000) {
            this.div *= 1000;
            this.log1000Div += 1;
        }
        while (maxData/this.div < 1) {
            this.div /= 1000;
            this.log1000Div -= 1;
        }
    };

    var aggSum = function(e, s)
    {
        if (!e || !this.isArray(e))
            return e;

        e = e.map((d) => aggSum.call(this, d, s - 1));
        if (s <= 0)
            return this.sumArray(e);
        else
            return e;
    };

    var aggLegend = function(e, s)
    {
        if (!e || !this.isLegendArray(e)) {
            var d = e;
            d.isLeaf = true;
            return d;
        }

        if (s <= 0)
            return aggLegend.call(this, e[0], s - 1);
        else
            return e.map((d) => aggLegend.call(this, d, s - 1));
    };

    var headLine = function(datum, i, format, a, l)
    {
        if (l == 0)
            format = format + ((i !== null) ? (i + 1) : '');

        if ((a == 0) || !datum || !this.isArray(datum))
            return format;

        datum = datum.map((d, j) => headLine.call(this, d, j, format, a - 1, l - 1));
        if (Array.isArray(datum[0]))
            return d3.merge(datum);
        else
            return datum;
    };

    return {
        isEmpty: () => true,
        isArray: Array.isArray,
        isLegendArray: Array.isArray,
        sumArray: d3.sum,

        init: function(year, month, day, today)
        {
            this.length = 0;
            variable = null;
            agg = null;
            type = Type.ALL;

            // Ensure year, month and day are well padded and find type:
            if (year != '') {
                year = SolarData.pad(year, 4, '0');
                type = Type.YEAR;
            }
            if (month != '') {
                month = SolarData.pad(month, 2, '0');
                type = Type.MONTH;
            }
            if (day != '') {
                day = SolarData.pad(day, 2, '0');
                type = Type.DAY;
            }

            this.hasDate = function() {
                if (arguments.length == 0)
                    return today;
                if (arguments.length != 3)
                    return false;
                return (((arguments[0] === year)  || (parseInt(arguments[0]) == parseInt(year))) &&
                        ((arguments[1] === month) || (parseInt(arguments[1]) == parseInt(month))) &&
                        ((arguments[2] === day)   || (parseInt(arguments[2]) == parseInt(day))));
            };

            // Available variables and sums:
            this.validVars = [];
            this.validAggs = [];

            // X label, date parser and date formatter:
            switch (type) {
                case Type.ALL:
                    this.xLabel = 'Année';
                    this.dateParser = ((date) => d3.isoParse(date).getFullYear());
                    this.dateFormatter = ((date) => SolarData.pad('' + date + '', 4, '0'));
                    break;
                case Type.YEAR:
                    this.xLabel = 'Mois';
                    this.dateParser = ((date) => d3.isoParse(date).getMonth() + 1);
                    this.dateFormatter = ((date) => SolarData.pad('' + date + '', 2, '0') + '/' + SolarData.pad(year, 4, '0'));
                    break;
                case Type.MONTH:
                    this.xLabel = 'Jour';
                    this.dateParser = ((date) => d3.isoParse(date).getDate());
                    this.dateFormatter = ((date) => SolarData.pad('' + date + '', 2, '0') + '/' + SolarData.pad(month, 2, '0') + '/' + SolarData.pad(year, 4, '0'));
                    break;
                case Type.DAY:
                    this.xLabel = 'Temps (h)';
                    this.dateParser = d3.isoParse;
                    this.dateFormatter = d3.timeFormat('%d/%m/%Y %H:%M');
                    break;
                default:
                    this.xLabel = '';
                    this.dateParser = ((date) => NaN);
                    this.dateFormatter = ((date) => '');
                    break;
            }

            // Date of data as a string:
            this.dateString = [day, month, year].filter(item => item != '').join('-');

            // Scales
            this.xScale = d3.scaleTime();
            this.yScale = d3.scaleLinear();

            // Axes
            this.xAxis = d3.axisBottom().scale(this.xScale);
            this.yAxis = d3.axisLeft().scale(this.yScale)
                                    .tickSizeOuter(0);

            // Grid
            this.yGrid = d3.axisRight().scale(this.yScale);
        },

        variable: function(v) {
            if (arguments.length > 0) {
                if (this.validVars.includes(v) && (variable != v)) {
                    variable = v;

                    switch (v) {
                    case 'uac':
                    case 'temp':
                        this.validAggs = ['inv'];
                        break;
                    case 'pdc':
                        this.validAggs = ['sum', 'inv', 'str'];
                        break;
                    case 'udc':
                        this.validAggs = ['str'];
                        break;
                    case 'nrj':
                    case 'pwr':
                    case 'pac':
                        this.validAggs = ['sum', 'inv'];
                        break;
                    default:
                        console.warn('Unknown variable: ' + variable);
                    }

                    if ((agg == null) || !this.validAggs.includes(agg))
                        agg = this.validAggs[0];
                    this.update();
                }
            }

            return variable;
        },

        aggregation: function(s) {
            if (arguments.length > 0) {
                if (this.validAggs.includes(s)) {
                    agg = s;
                    this.update();
                }
            }

            return agg;
        },
        aggregate: function(datum)
        {
            return aggSum.call(this, datum, SolarData.aggregations.index(agg));
        },
        aggregateLegend: function(legendData)
        {
            return aggLegend.call(this, legendData, SolarData.aggregations.index(agg));
        },

        headLines: function(datum)
        {
            var headers = [];

            var a = SolarData.aggregations.index(agg);
            var formats = ['Total', 'Onduleur ', 'String '];
            for (var l = 0; l <= a; l++)
                headers.push([''].concat(headLine.call(this, datum, null, formats[l], a, l)));

            if (headers.length > 1)
                headers.shift();
            headers[0][0] = 'Date';

            return headers;
        },

        merge: function(a)
        {
            if (!this.isArray(a))
                return [a];
            else
                return d3.merge(a.map((e) => this.merge(e)));
        },

        exportFilename: function() {
            var dateString = this.dateString;
            if (dateString != '')
                dateString = '_' + dateString;
            return 'export_' + variable + '_' + agg + dateString + '.csv';
        },
        exportCsv: function()
        {
            if (this.isEmpty())
                return;

            var exportData = this.export();
            if (!exportData)
                return;

            // Create CSV from data:
            var csv = new Blob([[
                exportData.headers.map((line) => line.join(',')).join('\r\n'),
                exportData.data.map((line) => line.join(',')).join('\r\n')
            ].join('\r\n')], {type: 'text/csv;charset=utf-8'});
            saveAs(csv, this.exportFilename());
        },

        yLabel: function()
        {
            return SolarData.variables.name(variable) + ' (' + SolarData.prefix(this.log1000Div) + SolarData.variables.unit(variable) + ')';
        },
        yCursor: function(y)
        {
            return Math.round(1000 * y / this.div) / 1000;
        },
        xRange: function(w)
        {
            if ((arguments.length > 0) && w) {
                if (Array.isArray(w))
                    w = w[1];

                this.xScale.range([0, w]);
                if (type == Type.DAY)
                    this.yGrid.tickSize(w/1.025);
                else
                    this.yGrid.tickSize(w);

                // Adapt X axis tick labels:
                if (type == Type.YEAR) {
                    if (w >= 750)
                        this.xAxis.tickFormat(function(d) {return localeLongMonth(new Date(1970, d - 1));});
                    else
                        this.xAxis.tickFormat(function(d) {return localeShortMonth(new Date(1970, d - 1)) + '.';});
                }
            }

            return this.xScale.range();
        },
        yRange: function(h)
        {
            if ((arguments.length > 0) && h) {
                if (Array.isArray(h))
                    h = h[0];

                this.yScale.range([h, 0]);
            }

            return this.yScale.range();
        },
        updateYDomain: function(data) // TODO test and use virtual max function
        {
            var maxData = (data[0] !== undefined) ? d3.max(data, (d) => recMax(d.y)) : recMax(data.y);
            updateDivider.call(this, maxData);
            this.yScale.domain([0, 1.025*maxData/this.div]);
        },
        xTickCenter: function()
        {
            return this.xScale.step()/2;
        },
    };
}

/*!\brief Pad number to reach length
 *
 * Pad the number n to the left using p until it has length l.
 * n is not truncated if it is longer than l.
 * \param n The number to pad
 * \param l The desired text length
 * \param p The character to use for padding
 * \return The number padded
 */
SolarData.pad = function(n, l, p)
{
    if (p == '')
        throw new RangeError('p should not be empty');

    n = '' + n + '';
    while (n.length < l)
        n = p + n;
    return n;
};

SolarData.filePath = function(year, month, day)
{
    var file = '';

    if ((day != undefined) && (day != ''))
        file = "/" + SolarData.pad(day, 2, '0') + file;
    if ((month != undefined) && (month != ''))
        file = "/" + SolarData.pad(month, 2, '0') + file;
    if ((year != undefined) && (year != ''))
        file = "/" + SolarData.pad(year, 4, '0') + file;
    if (file == '')
        file = 'years';

    return file + '.json';
};

SolarData.listFilePath = function(year, month, day)
{
    var folder = '';

    if ((month != undefined) && (month != ''))
        folder = 'days';
    else if ((year != undefined) && (year != ''))
        folder = 'months';

    return 'list/' + folder + SolarData.filePath(year, month, day);
};

SolarData.dataFilePath = function(year, month, day)
{
    var folder = '';

    if ((day != undefined) && (day != ''))
        folder = 'days';
    else if ((month != undefined) && (month != ''))
        folder = 'months';
    else if ((year != undefined) && (year != ''))
        folder = 'years';

    return 'data/' + folder + SolarData.filePath(year, month, day);
};

SolarData.create = function(year, month, day)
{
    var dataPath = ((arguments.length == 0) ? 'data/today.json' : SolarData.dataFilePath(year, month, day));
    console.log("Data file path: ", dataPath);

    // Loads the data:
    return new Promise((resolve, reject) => {
        d3.json(dataPath).on('error', reject)
                            .on('load', (data) => {
            // Return appropriate child object instance:
            if (!Array.isArray(data))
                resolve(new LineData(data, year, month, day));
            else if (data.length > 0)
                resolve(new HistData(data, year, month, day));
            else
                resolve(new EmptyData(data, year, month, day));
        }).get();
    });
};

SolarData.variables = (function() {
    // Variables:
    const vars = [
        {code: 'nrj',  name: 'Énergie',      unit: 'Wh'},
        {code: 'pwr',  name: 'Puissance',    unit: 'W' },
        {code: 'pac',  name: 'Puissance AC', unit: 'W' },
        {code: 'uac',  name: 'Tension AC',   unit: 'V' },
        {code: 'pdc',  name: 'Puissance DC', unit: 'W' },
        {code: 'udc',  name: 'Tension DC',   unit: 'V' },
        {code: 'temp', name: 'Température',  unit: '°C'},
    ];

    return {
        name: function(v) {
            return vars.find((e) => (e.code == v)).name;
        },
        unit: function(v) {
            return vars.find((e) => (e.code == v)).unit;
        },
        sort: function(v1, v2)
        {
            return vars.findIndex((e) => (e.code == v1)) -
                   vars.findIndex((e) => (e.code == v2))
        },
    };
})();

SolarData.aggregations = (function() {
    var aggs = [
        {code: 'sum', name: 'Total'},
        {code: 'inv', name: 'Par onduleur'},
        {code: 'str', name: 'Par string'},
    ];

    return {
        name: function(a) {
            return aggs.find((e) => (e.code == a)).name;
        },
        index: function(agg) {
            return aggs.findIndex((a) => (a.code == agg))
        },
    };
})();

SolarData.prefix = (function() {
    var prefixes  = ['p', 'n', 'µ', 'm', '', 'k', 'M', 'G', 'T'];
    var minPrefix = -4;

    return (log1000Div) => prefixes[-minPrefix + log1000Div];
})();

Object.setPrototypeOf(SolarData, Array.prototype);

function EmptyData(data, year, month, day)
{
    this.init(year, month, day, false);
    this.hasDate = function() {return false};
    this.export = function() {return null};
    this.update = function() {};
}

EmptyData.prototype = {};
Object.setPrototypeOf(EmptyData.prototype, SolarData());
