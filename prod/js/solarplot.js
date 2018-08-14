var SolarPlot = {
    // Initialize plot data:
    init: function(root, data)
    {   
        this.root = root;
        this.data = data;
    },
    // Plot resize event:
    resize: function(w, h) {
        this.data.xRange(w);
        this.data.yRange(h);
    },
    // Plot width:
    width: function() {
        return this.data.xRange();
    },
    // Plot height:
    height: function() {
        return this.data.yRange();
    },
    // Get d3 selection:
    getD3: function(d) {
        if (d === undefined)
            d = this.legendData;

        if (d[0] === undefined)
            return d;
        else
            return this.getD3(d[0]);
    },
}

function EmptyPlot()
{
    this.legendStyle = null;
    this.remove = () => {};
    this.draw = () => false;
}
EmptyPlot.prototype = SolarPlot;
