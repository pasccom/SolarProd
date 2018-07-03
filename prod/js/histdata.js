function HistData(year, month, day) {
    // Ensure year, month and day are defined:
    if ((year === undefined) && (month === undefined) && (day === undefined)) {
        var date = d3.isoParse(this[0].date);
        year = date.getFullYear();
        month = (date.getMonth() + 1);
        day = date.getDate();
    }

    this.init(year, month, day);
    
    // Parse dates:
    this.forEach((d) => {d.date = this.dateParser(d.date);});

    // Is empty?
    this.isEmpty = () => (this.length == 0);

    // X scale
    this.xScale = d3.scaleBand().domain(this.map(function(d) {return d.date}));
    
    // X axis
    this.xAxis.scale(this.xScale);
}
HistData.prototype = SolarData;
