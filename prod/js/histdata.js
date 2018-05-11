function HistData(year, month, day) {
    this.init(year, month, day);
    
    // Parse dates:
    this.forEach((d) => {d.date = this.dateParser(d.date);});

    // Is empty?
    this.isEmpty = () => (this.length == 0);

    // X scale
    this.xScale = d3.scaleBand().domain(this.map(function(d) {return d.date}));
    
    // X axis
    this.xAxis.scale(this.xScale);
    
    this.initRanges();
}
HistData.prototype = SolarData;
