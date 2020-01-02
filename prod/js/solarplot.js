/* Copyright 2018-2020 Pascal COMBES <pascom@orange.fr>
 * 
 * This file is part of SolarProd.
 * 
 * SolarProd is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * SolarProd is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with SolarProd. If not, see <http://www.gnu.org/licenses/>
 */

var SolarPlot = {
    // Initialize plot data:
    setData: function(data)
    {   
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

function EmptyPlot(root)
{
    this.legendStyle = null;
    this.remove = () => {};
    this.draw = () => false;
    this.redraw = () => false;
    this.enableCursor = (enable, listener) => false;
}
EmptyPlot.prototype = SolarPlot;
