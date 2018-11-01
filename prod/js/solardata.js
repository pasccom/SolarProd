/*!\brief Pad number to reach length
 *
 * Pad the number n to the left using p until it has length l.
 * n is not truncated if it is longer than l.
 * \param n The number to pad
 * \param l The desired text length
 * \param p The character to use for padding
 * \return The number padded
 */
function pad(n, l, p)
{
    if (p == '')
        throw new RangeError('p should not be empty');

    n = '' + n + '';
    while (n.length < l)
        n = p + n;
    return n;
}

function recMin(a)
{
    if (!Array.isArray(a))
        return a;
    else
        return d3.min(a, recMin);
}

function recMax(a)
{
    if (!Array.isArray(a))
        return a;
    else
        return d3.max(a, recMax);
}

function recForEach(a, fun)
{
    if (!Array.isArray(a))
        fun(a);
    else
        a.forEach((e) => recForEach(e, fun));
};

var SolarData = {
    // Variables:
    vars: [
        {code: 'nrj',  name: 'Énergie',      unit: 'Wh'},
        {code: 'pwr',  name: 'Puissance',    unit: 'W' },
        {code: 'pac',  name: 'Puissance AC', unit: 'W' },
        {code: 'uac',  name: 'Tension AC',   unit: 'V' },
        {code: 'pdc',  name: 'Puissance DC', unit: 'W' },
        {code: 'udc',  name: 'Tension DC',   unit: 'V' },
        {code: 'temp', name: 'Température',  unit: '°C'},
    ],
    variableName: function(v)
    {
        return SolarData.vars.find((e) => (e.code == v)).name;
    },
    variableUnit: function(v)
    {
        return SolarData.vars.find((e) => (e.code == v)).unit;
    },

    // Aggregation methods:
    aggregations: [
        {code: 'sum', name: 'Total'},
        {code: 'inv', name: 'Par onduleur'},
        {code: 'str', name: 'Par string'},
    ],
    aggregationName: function(a)
    {
        return SolarData.aggregations.find((e) => (e.code == a)).name;
    },

    prefixes:   ['p', 'n', 'µ', 'm', '', 'k', 'M', 'G', 'T'],
    minPrefix: -4,
    prefix: function(log1000Div)
    {
        return this.prefixes[-this.minPrefix + log1000Div];
    },
    updateDivider: function(maxData)
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
    },

    isEmpty: () => true,
    isArray: Array.isArray,
    sumArray: d3.sum,

    variable: function(v) {
        if (arguments.length > 0) {
            if (this.validVars.includes(v) && (this.var != v)) {
                this.var = v;

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
                    console.warn('Unknown variable: ' + this.var);
                }

                if ((this.agg == null) || !this.validAggs.includes(this.agg))
                    this.agg = this.validAggs[0];
                this.update();
            }
        }

        return this.var;
    },
    aggregation: function(s) {
        if (arguments.length > 0) {
            if (this.validAggs.includes(s)) {
                this.agg = s;
                this.update();
            }
        }

        return this.agg;
    },
    aggregate: function(datum)
    {
        return this.aggSum(datum, this.aggregations.findIndex((a) => (a.code == this.agg)));
    },
    aggSum: function(e, s)
    {
        if (!e || !this.isArray(e))
            return e;

        e = e.map((d) => this.aggSum(d, s - 1));
        if (s <= 0)
            return this.sumArray(e);
        else
            return e;
    },
    headLines: function(datum)
    {
        var headers = [];

        var agg = this.aggregations.findIndex((a) => (a.code == this.agg));
        var formats = ['Total', 'Onduleur ', 'String '];
        for (var l = 0; l <= agg; l++)
            headers.push([''].concat(this.headLine(datum, null, formats[l], agg, l)));

        if (headers.length > 1)
            headers.shift();
        headers[0][0] = 'Date';

        return headers;
    },
    headLine: function(datum, i, format, a, l)
    {
        if (l == 0)
            format = format + ((i !== null) ? (i + 1) : '');

        if ((a == 0) || !datum || !this.isArray(datum))
            return format;

        datum = datum.map((d, j) => this.headLine(d, j, format, a - 1, l - 1));
        if (Array.isArray(datum[0]))
            return d3.merge(datum);
        else
            return datum;
    },
    merge: function(a)
    {
        if (!this.isArray(a))
            return [a];
        else
            return d3.merge(a.map((e) => this.merge(e)));
    },

    init: function(year, month, day)
    {
        this.length = 0;

        // Type:
        if (year == '')
            this.type = SolarData.Type.ALL;
        else if (month == '')
            this.type = SolarData.Type.YEAR;
        else if (day == '')
            this.type = SolarData.Type.MONTH;
        else
            this.type = SolarData.Type.DAY;
        
        // Available variables and sums:
        this.validVars = [];
        this.validAggs = [];

        // Current variable and aggregation:
        this.var = null;
        this.agg = null;

        // X label:
        if (year == '')
            this.xLabel = 'Année';
        else if (month == '')
            this.xLabel = 'Mois';
        else if (day == '')
            this.xLabel = 'Jour';
        else
            this.xLabel = 'Temps (h)';
        
        // Date parser:
        if (year == '')
            this.dateParser = ((date) => d3.isoParse(date).getFullYear());
        else if (month == '')
            this.dateParser = ((date) => d3.isoParse(date).getMonth());
        else if (day == '')
            this.dateParser = ((date) => d3.isoParse(date).getDate());
        else
            this.dateParser = d3.isoParse;
        
        // Date formatter:
        if (year == '')
            this.dateFormatter = ((date) => pad('' + date + '', 4, '0'));
        else if (month == '')
            this.dateFormatter = ((date) => pad('' + (date + 1) + '', 2, '0') + '/' + pad(year, 4, '0'));
        else if (day == '')
            this.dateFormatter = ((date) => pad('' + date + '', 2, '0') + '/' + pad(month, 2, '0') + '/' + pad(year, 4, '0'));
        else
            this.dateFormatter = d3.timeFormat('%d/%m/%Y %H:%M');

        // Ensure year, month and day are well padded:
        year = (year == '') ? '' : pad(year, 4, '0');
        month = (month == '') ? '' : pad(month, 2, '0');
        day = (day == '') ? '' : pad(day, 2, '0');
        
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

    exportFilename: function() {
        var dateString = this.dateString;
        if (dateString != '')
            dateString = '_' + dateString;
        return 'export_' + this.var + '_' + this.agg + dateString + '.csv';
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
        return SolarData.variableName(this.var) + ' (' + SolarData.prefix(this.log1000Div) + SolarData.variableUnit(this.var) + ')';
    },
    xRange: function(w)
    {
        if ((arguments.length > 0) && w) {
            if (Array.isArray(w))
                w = w[1];

            this.xScale.range([0, w]);
            this.yGrid.tickSize(w);

            // Adapt X axis tick labels:
            if (this.type == SolarData.Type.YEAR) {
                if (w >= 750)
                    this.xAxis.tickFormat(function(d) {return localeLongMonth(new Date(1970, d));});
                else
                    this.xAxis.tickFormat(function(d) {return localeShortMonth(new Date(1970, d)) + '.';});
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
    updateYDomain: function(data)
    {
        var maxData = (data[0] !== undefined) ? d3.max(data, (d) => recMax(d.data)) : recMax(data.y);
        this.updateDivider(maxData);
        this.yScale.domain([0, maxData/this.div]);
    },
    xTickCenter: function()
    {
        return this.xScale.step()/2;
    },
    filePath: function(year, month, day)
    {
        var file = '';

        if ((day != undefined) && (day != ''))
            file = "/" + pad(day, 2, '0') + file;
        if ((month != undefined) && (month != ''))
            file = "/" + pad(month, 2, '0') + file;
        if ((year != undefined) && (year != ''))
            file = "/" + pad(year, 4, '0') + file;
        if (file == '')
            file = 'years';

        return file + '.json';
    },
    listFilePath: function(year, month, day) {
        var folder = '';

        if ((month != undefined) && (month != ''))
            folder = 'days';
        else if ((year != undefined) && (year != ''))
            folder = 'months';

        return 'list/' + folder + SolarData.filePath(year, month, day);
    },
    dataFilePath: function(year, month, day) {
        var folder = '';

        if ((day != undefined) && (day != ''))
            folder = 'days';
        else if ((month != undefined) && (month != ''))
            folder = 'months';
        else if ((year != undefined) && (year != ''))
            folder = 'years';

        return 'data/' + folder + SolarData.filePath(year, month, day);
    },
    create: function(year, month, day)
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
    },
    Type: {
        ALL:   'ALL',
        YEAR:  'YEAR',
        MONTH: 'MONTH',
        DAY:   'DAY',
    },
}

Object.setPrototypeOf(SolarData, Array.prototype);

function EmptyData(data, year, month, day)
{
    this.init(year, month, day);
    this.export = function() {return null};
    this.update = function() {};
}
EmptyData.prototype = SolarData;
