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

var SolarData = {
    shortVars:  ['nrj',     'pwr',       'pac',          'uac',        'pdc',          'udc',        'temp'],
    longVars:   ['Énergie', 'Puissance', 'Puissance AC', 'Tension AC', 'Puissance DC', 'Tension DC', 'Température'],
    units:      ['Wh',      'W',         'W',            'V',          'W',            'V',          '°C'],

    prefixes:   ['p', 'n', 'µ', 'm', '', 'k', 'M', 'G', 'T'],
    minPrefix: -4,
    prefix: function(log1000Div) {
        return this.prefixes[-this.minPrefix + log1000Div];
    },

    isEmpty: () => true,

    init: function(year, month, day)
    {   
        // Type:
        if (year == '')
            this.type = SolarData.Type.ALL;
        else if (month == '')
            this.type = SolarData.Type.YEAR;
        else if (day == '')
            this.type = SolarData.Type.MONTH;
        else
            this.type = SolarData.Type.DAY;
        
        // Available variables:
        if (this[0])
            this.variables = Object.keys(this[0]).filter((k) => !k.startsWith('date'))
                                                 .map((k) => SolarData.shortVars.indexOf(k))
                                                 .sort();
                                             
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
        
        // Ensure year, month and day are defined:
        if ((year === undefined) && (month === undefined) && (day === undefined)) {
            var date;
            if (this[0].date)
                date = d3.isoParse(this[0].date);
            if (this[0].dates)
                date = d3.isoParse(this[0].dates[0]);
            
            year = date.getFullYear();
            month = (date.getMonth() + 1);
            day = date.getDate();
        }

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
    create: function(data, year, month, day)
    {
        // Ensure SolarData inherits an Array:
        if (Array.isArray(data))
            Object.setPrototypeOf(SolarData, data);
        else
            Object.setPrototypeOf(SolarData, [data]);
        
        // Return appropriate child object instance:
        if (!Array.isArray(data))
            return new LineData(year, month, day);
        else if (data.length > 0)
            return new HistData(year, month, day);
        else
            return new EmptyData(year, month, day)
    },
    Type: {
        ALL:   'ALL',
        YEAR:  'YEAR',
        MONTH: 'MONTH',
        DAY:   'DAY',
    },
}

function EmptyData(year, month, day)
{
    this.init(year, month, day);
}
EmptyData.prototype = SolarData;
