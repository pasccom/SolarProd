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
                                      .sort((v1, v2) => SolarData.vars.findIndex((e) => (e.code == v1)) -
                                                        SolarData.vars.findIndex((e) => (e.code == v2)));

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

    this.isArray = (a) => (Array.isArray(a) && Array.isArray(a[0]));
    this.sumArray = (a) => d3.transpose(a).map((d) => d3.sum(d));

    this.export = function() {
        var d = this.aggregate(data[this.var]);

        return {headers: this.headLines(data[this.var]),
                data: d3.transpose([data.dates.map(this.dateFormatter)].concat(!Array.isArray(d[0]) ? [d] : !Array.isArray(d[0][0]) ? d : d3.merge(d))), // TODO define merge
        };
    }

    this.update = function() {
        if (this.var !== null) {
            // Update index:
            this.length = 1;
            var d = this.aggregate(data[this.var]);
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
