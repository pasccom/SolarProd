function HistData(data, year, month, day) {
    var today = false;

    // Ensure year, month and day are defined:
    if ((year === undefined) && (month === undefined) && (day === undefined)) {
        var date = d3.isoParse(data[0].date);
        year = date.getFullYear();
        month = (date.getMonth() + 1);
        day = date.getDate();
        today = true;
    }

    this.init(year, month, day, today);
    
    // Available variables:
    if (data[0])
        this.validVars = Object.keys(data[0]).filter((k) => (k != 'date'))
                                             .sort(SolarData.variables.sort);

    // Parse dates:
    data.forEach((d) => {d.date = this.dateParser(d.date);});

    // Is empty?
    this.isEmpty = () => (data.length == 0);

    // X scale
    this.xScale = d3.scaleBand().domain(data.map((d) => d.date));

    // X axis
    this.xAxis.scale(this.xScale);

    this.export = function() {
        return {headers: this.headLines(data[0][this.variable()]),
                data: data.map((d) =>  [this.dateFormatter(d.date)].concat(this.merge(this.aggregate(d[this.variable()])))),
        };
    };

    this.update = function() {
        // Clear existing indexes:
        for (var i = 0; i < this.length; i++)
            delete this[i];
        if (this.variable() !== null) {
            // Create new indexes:
            for (var i = 0; i < data.length; i++)
                this[i] = {x: data[i].date, y: this.aggregate(data[i][this.variable()])};
            this.length = data.length;
            this.updateYDomain(this);
            this.xScale.padding((this.aggregation() == 'sum') ? 0 : 0.1);
        } else {
            this.length = 0;
        }
    };
    this.update();
}

HistData.prototype = {};
Object.setPrototypeOf(HistData.prototype, SolarData());
