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
                                             .sort(this.sortVariables);

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
                data: data.map((d) =>  [this.dateFormatter(d.date)].concat(this.merge(this.aggregate(d[this.var])))),
        };
    };

    this.update = function() {
        // Clear existing indexes:
        for (var i = 0; i < this.length; i++)
            delete this[i];
        if (this.var !== null) {
            // Create new indexes:
            for (var i = 0; i < data.length; i++)
                this[i] = {date: data[i].date, data: this.aggregate(data[i][this.var])};
            this.length = data.length;
            this.updateYDomain(this);
            this.xScale.padding((this.agg == 'sum') ? 0 : 0.1);
        } else {
            this.length = 0;
        }
    };
    this.update();
}
HistData.prototype = SolarData;
