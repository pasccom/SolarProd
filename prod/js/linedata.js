function LineData(data, year, month, day) {
    // Ensure year, month and day are defined:
    if ((year === undefined) && (month === undefined) && (day === undefined)) {
        var date = d3.isoParse(data.dates[0]);

        year = date.getFullYear();
        month = (date.getMonth() + 1);
        day = date.getDate();
    }

    this.init(year, month, day);
    
    // Available variables:
    this.validVars = Object.keys(data).filter((k) => (k != 'dates'))
                                      .sort((v1, v2) => SolarData.shortVars.indexOf(v1) - SolarData.shortVars.indexOf(v2));

    // Parse dates:
    data.dates = data.dates.map(this.dateParser);

    // Is empty?
    this.isEmpty = () => (data.dates.length <= 2);

    // X scale
    this.xScale.domain(d3.extent(data.dates));
    
    // X axis
    this.xAxis.tickSizeOuter(0);
    this.xAxis.ticks(d3.timeHour.every(1))
    this.xAxis.tickFormat(locale.format('%_H'));

    this.export = function() {
        var recSum = function(e, s)
        {
            if (!e || !Array.isArray(e[0]))
                return e;

            e = e.map((d) => recSum(d, s - 1));
            if (s <= 0)
                return d3.transpose(e).map((d) => d3.sum(d));
            else
                return e;
        }

        var recFormat = function(e, i, f, s, l)
        {
            if (l == 0)
                f = f + ((i !== null) ? (i + 1) : '');

            if ((s == 0) || !e || !Array.isArray(e[0]))
                return f;

            e = e.map((d, j) => recFormat(d, j, f, s - 1, l - 1));
            if (Array.isArray(e[0]))
                return d3.merge(e);
            else
                return e;
        }


        var exportData = {headers: []};

        // TODO to be moved:
        var formats = ['Total', 'Onduleur ', 'String '];
        for (var s = 0; s <= this.aggregations.findIndex((a) => (a.code == this.agg)); s++)
            exportData.headers.push([''].concat(recFormat(data[this.var], null, formats[s], this.aggregations.findIndex((a) => (a.code == this.agg)), s)));
        if (exportData.headers.length > 1)
            exportData.headers.shift();
        exportData.headers[0][0] = 'Date';

        var d = recSum(data[this.var], this.aggregations.findIndex((a) => (a.code == this.agg))); // TODO should be this.agg.
        exportData.data = d3.transpose([data.dates.map(this.dateFormatter)].concat(!Array.isArray(d[0]) ? [d] : !Array.isArray(d[0][0]) ? d : d3.merge(d)));

        return exportData;
    }

    this.update = function() {
        var recSum = function(e, s)
        {
            if (!e || !Array.isArray(e[0]))
                return e;

            e = e.map((d) => recSum(d, s - 1));
            if (s <= 0)
                return d3.transpose(e).map((d) => d3.sum(d));
            else
                return e;
        };

        if (this.var !== null) {
            this.length = 1;
            var d = recSum(data[this.var], this.aggregations.findIndex((a) => (a.code == this.agg))); // TODO should be this.agg.
            this[0] = {x: data.dates, y: d};

            // Set scale domains:
            var maxData = d3.max(this[0].y, (d) => Array.isArray(d) ? d3.max(d, (e) => Array.isArray(e) ? d3.max(e) : e) : d);
            this.updateDivider(maxData);
            this.yScale.domain([0, maxData/this.div]);
        } else {
            if (this.length > 0)
                delete this[0];
            this.length = 0;
        }
    };
    this.update();
}
LineData.prototype = SolarData;
