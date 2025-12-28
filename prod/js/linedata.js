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

function LineData(data, year, month, day) {
    var today = false;
    var domain;

    // Ensure year, month and day are defined:
    if ((year === undefined) && (month === undefined) && (day === undefined)) {
        var date = d3.isoParse(data.dates[0]);

        year = date.getFullYear();
        month = (date.getMonth() + 1);
        day = date.getDate();
        today = true;
    }

    this.init(year, month, day, today);
    
    // Available variables:
    this.validVars = Object.keys(data).filter((k) => SolarData.variables.codes().includes(k))
                                      .sort(SolarData.variables.sort);

    // Parse dates:
    data.dates = data.dates.map(this.dateParser);

    // Is empty?
    this.isEmpty = () => (data.dates.length <= 2);

    // X scale
    if (data.dates.length > 0) {
        domain = d3.extent(data.dates).map((d) => d.getTime());
        domain[1] += 0.025*(domain[1] - domain[0]);
        this.xScale.domain(domain.map((d) => new Date(d)));
    }
    
    // X axis
    this.xAxis.tickSizeOuter(0);
    this.xAxis.ticks(d3.timeHour.every(1))
    this.xAxis.tickFormat(locale.format('%_H'));

    this.isArray = (a) => (Array.isArray(a) && a.some((e) => Array.isArray(e)));
    this.sumArray = (a) => d3.transpose(a.filter((e) => e !== null)).map((d) => d3.sum(d));

    this.export = function() {
        return {headers: this.headLines(data[this.variable()]),
                data: d3.transpose([data.dates.map(this.dateFormatter)].concat(this.merge(this.aggregate(data[this.variable()])))),
        };
    };

    this.update = function() {
        if (this.variable() !== null) {
            // Update index:
            this[0] = {x: data.dates, y: this.aggregate(data[this.variable()])};
            this.length = 1;
            this.updateYDomain(this[0]);
        } else {
            if (this.length > 0)
                delete this[0];
            this.length = 0;
        }
    };
    this.update();
}

LineData.prototype = {};
Object.setPrototypeOf(LineData.prototype, SolarData());
