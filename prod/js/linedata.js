function LineData(year, month, day) {
    // Ensure year, month and day are defined:
    if ((year === undefined) && (month === undefined) && (day === undefined)) {
        var date = d3.isoParse(this[0].dates[0]);

        year = date.getFullYear();
        month = (date.getMonth() + 1);
        day = date.getDate();
    }

    this.init(year, month, day);
    
    // Available variables:
    if (this[0])
        this.variables = Object.keys(this[0]).filter((k) => !k.startsWith('date'))
                                             .map((k) => SolarData.shortVars.indexOf(k))
                                             .sort();

    // Parse dates:
    this[0].dates = this[0].dates.map(this.dateParser);

    // Is empty?
    this.isEmpty = () => (this[0].dates.length <= 2);
    
    // X scale
    this.xScale.domain(d3.extent(this[0].dates));
    
    // X axis
    this.xAxis.tickSizeOuter(0);
    this.xAxis.ticks(d3.timeHour.every(1))
    this.xAxis.tickFormat(locale.format('%_H'));
}
LineData.prototype = SolarData;
