function HistData(data, year, month, day) {
    // Ensure year, month and day are defined:
    if ((year === undefined) && (month === undefined) && (day === undefined)) {
        var date = d3.isoParse(data[0].date);
        year = date.getFullYear();
        month = (date.getMonth() + 1);
        day = date.getDate();
    }

    this.init(year, month, day);
    
    // Available variables:
    if (data[0])
        this.validVariables = Object.keys(data[0]).filter((k) => (k != 'date'))
                                                  .sort((v1, v2) => SolarData.shortVars.indexOf(v1) - SolarData.shortVars.indexOf(v2));

    // Parse dates:
    data.forEach((d) => {d.date = this.dateParser(d.date);});

    // Is empty?
    this.isEmpty = () => (data.length == 0);

    // X scale
    this.xScale = d3.scaleBand().domain(data.map((d) => d.date));

    // X axis
    this.xAxis.scale(this.xScale);

    this.export = function() {
        var recSum = function(e, s)
        {
            if (Array.isArray(e) && (s <= 0))
                return d3.sum(e, (d) => recSum(d, s - 1));
            else if (Array.isArray(e))
                return e.map((d) => recSum(d, s - 1));
            else
                return e;
        }

        var recFormat = function(e, i, f, s, l)
        {
            if (l == 0)
                f = f + ((i !== null) ? (i + 1) : '');

            if ((s == 0) || !e || !Array.isArray(e))
                return f;

            e = e.map((d, j) => recFormat(d, j, f, s - 1, l - 1));
            if (Array.isArray(e[0]))
                return d3.merge(e);
            else
                return e;
        }

        // TODO to move away
        var sums = ['sum', 'inv', 'str'];

        var exportData = {headers: []};

        var formats = ['Total', 'Onduleur ', 'String '];
        for (var s = 0; s <= sums.indexOf(this.summation); s++)
            exportData.headers.push([s == 0 ? 'Date' : ''].concat(recFormat(data[0][this.var], null, formats[s], sums.indexOf(this.summation), s))); // TODO should be this.summation
        if (exportData.headers.length > 1)
            exportData.headers.shift();
        exportData.headers[0][0] = 'Date';

        exportData.data = data.map((d) => {
            var e = recSum(d[this.var], sums.indexOf(this.summation)); // TODO should be this.summation.
            return [this.dateFormatter(d.date)].concat(!Array.isArray(e) ? [e] : !Array.isArray(e[0]) ? e : d3.merge(e));
        });

        return exportData;
    }

    this.update = function() {
        var recSum = function(e, s)
        {
            if (Array.isArray(e) && (s <= 0))
                return d3.sum(e, (d) => recSum(d, s - 1));
            else if (Array.isArray(e))
                return e.map((d) => recSum(d, s - 1));
            else
                return e;
        }

        // TODO to move away
        var sums = ['sum', 'inv', 'str'];

        for (var i = 0; i < this.length; i++)
            delete this[i];
        if (this.var !== null) {
            for (var i = 0; i < data.length; i++) {
                var d = data[i][this.var];
                d = recSum(d, sums.indexOf(this.summation)); // TODO should be this.summation.
                this[i] = {date: data[i].date, data: d};
            }
            this.length = data.length;
        } else {
            this.length = 0;
        }

        // Set scales padding/domain:
        var maxData = d3.max(this, (d) => Array.isArray(d.data) ? d3.max(d.data, (a) => Array.isArray(a) ? d3.max(a) : a) : d.data);
        this.updateDivider(maxData)
        this.xScale.padding((this.summation == 'sum') ? 0 : 0.1);
        this.yScale.domain([0, maxData/this.div]);
    };
    this.update();
}
HistData.prototype = SolarData;
