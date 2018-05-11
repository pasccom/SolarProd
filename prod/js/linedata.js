function LineData(year, month, day) {
    this.init(year, month, day);
    
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
