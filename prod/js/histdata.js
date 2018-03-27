function HistData(year, month, day) {
    this.init(year, month, day);
    
    // Parse dates:
    this.forEach((d) => {d.date = this.dateParser(d.date);});
    
    // X scale
    this.xScale = d3.scaleBand().domain(this.map(function(d) {return d.date}));
    
    // X axis
    this.xAxis.scale(this.xScale);
    
    this.initRanges();
}
HistData.prototype = SolarData;
