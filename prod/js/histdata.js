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
        this.validVars = Object.keys(data[0]).filter((k) => (k != 'date'))
                                             .sort((v1, v2) => SolarData.vars.findIndex((e) => (e.code == v1)) -
                                                               SolarData.vars.findIndex((e) => (e.code == v2)));

    // Parse dates:
    data.forEach((d) => {d.date = this.dateParser(d.date);});

    // Is empty?
    this.isEmpty = () => (data.length == 0);

    // X scale
    this.xScale = d3.scaleBand().domain(data.map((d) => d.date));

    // X axis
    this.xAxis.scale(this.xScale);

    this.export = function() {
        return {headers: this.headLines(data[0][this.var]),
                data: data.map((d) => {
                    var e = this.aggregate(d[this.var]);
                    return [this.dateFormatter(d.date)].concat(!Array.isArray(e) ? [e] : !Array.isArray(e[0]) ? e : d3.merge(e)); // TODO define merge
                }),
        };
    }

    this.update = function() {
        // Clear existing indexes:
        for (var i = 0; i < this.length; i++)
            delete this[i];
        if (this.var !== null) {
            // Create new indexes:
            for (var i = 0; i < data.length; i++) {
                d = this.aggregate(data[i][this.var]);
                this[i] = {date: data[i].date, data: d};
            }
            this.length = data.length;

            // Set scales padding/domain:
            var maxData = d3.max(this, (d) => Array.isArray(d.data) ? d3.max(d.data, (a) => Array.isArray(a) ? d3.max(a) : a) : d.data);
            this.updateDivider(maxData)
            this.xScale.padding((this.agg == 'sum') ? 0 : 0.1);
            this.yScale.domain([0, maxData/this.div]);
        } else {
            this.length = 0;
        }
    };
    this.update();
}
HistData.prototype = SolarData;
