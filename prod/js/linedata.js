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
        var exportData = this.aggregate(data[this.var]);

        return {headers: this.headLines(data[this.var]),
                data: d3.transpose([data.dates.map(this.dateFormatter)].concat(this.merge(exportData))),
        };
    };

    this.update = function() {
        if (this.var !== null) {
            // Update index:
            this[0] = {x: data.dates, y: this.aggregate(data[this.var])};
            this.length = 1;

            // Set scale domains:
            var maxData = recMax(this[0].y);
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
