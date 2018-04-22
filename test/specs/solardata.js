function dateEqualityTester(date1, date2) {
    if ((date1 instanceof Date) && (date2 instanceof Date)) {
        if (date1.getFullYear() != date2.getFullYear())
            return false;
        if (date1.getMonth() != date2.getMonth())
            return false;
        if (date1.getDate() != date2.getDate())
            return false;
        if (date1.getHours() != date2.getHours())
            return false;
        if (date1.getMinutes() != date2.getMinutes())
            return false;
        if (date1.getSeconds() != date2.getSeconds())
            return false;
        return true;
    }
}

describe('Helpers ', function() {
    describe('pad() ', function() {
        it('should return a string', [
            GenTest.types.oneOf([GenTest.types.int.nonNegative, GenTest.types.string]),
            GenTest.types.int.nonNegative,
            GenTest.types.constantly('0'),
        ], function(n, l, p) {
            expect(typeof pad(n, l, p)).toBe('string');
        });
        it('should return a string of length larger or equal to l', [
            GenTest.types.oneOf([GenTest.types.int.nonNegative, GenTest.types.string]),
            GenTest.types.int.nonNegative,
            GenTest.types.elements(['0', ' ', ' 0']),
        ], function(n, l, p) {
            expect(pad(n, l, p).length).toBeGreaterThanOrEqual(l);
        });
        it('should start with p and end with n', [
            GenTest.types.oneOf([GenTest.types.int.nonNegative, GenTest.types.string.alphanumeric]),
            GenTest.types.int.nonNegative,
            GenTest.types.elements(['0', ' ', ' 0']),
        ], function(n, l, p) {
            expect(pad(n, l, p)).toMatch('^(' + p + ')*' + n + '$');
        });

        it('should be parsed as the initial int', [
            GenTest.types.int.nonNegative,
            GenTest.types.int.nonNegative,
            GenTest.types.constantly('0', ' ', '00', '  '),
        ], function(n, l, p) {
            expect(parseInt(pad(n, l, p))).toBe(n);
        });
        it('should throw when called with empty string', [
            GenTest.types.oneOf([GenTest.types.int.nonNegative, GenTest.types.string]),
            GenTest.types.int.nonNegative,
            GenTest.types.constantly(''),
        ], function(n, l, p) {
            expect(() => pad(n, l, p)).toThrowError(RangeError, 'p should not be empty');
        });
    });
});

describe('SolarData', function() {
    var generators = {};

    generators.yearNumber = GenTest.types.choose(1900, 9999, 2000);
    generators.yearString = GenTest.types.fmap((year) => pad(year, 4, '0'), generators.yearNumber);
    generators.year = GenTest.types.oneOf([generators.yearNumber, generators.yearString]);

    generators.monthNumber = GenTest.types.choose(1, 12);
    generators.monthString = GenTest.types.fmap((month) => pad(month, 2, '0'), generators.monthNumber);
    generators.month = GenTest.types.oneOf([generators.monthNumber, generators.monthString]);

    generators.dayNumber = GenTest.types.choose(1, 28);
    generators.dayString = GenTest.types.fmap((day) => pad(day, 2, '0'), generators.dayNumber);
    generators.day = GenTest.types.oneOf([generators.dayNumber, generators.dayString]);

    generators.histData = GenTest.types.nonEmptyArrayOf(GenTest.types.shape({date: GenTest.types.date('%Y-%m-%d')}));
    generators.lineData = GenTest.types.shape({dates: GenTest.types.nonEmptyArrayOf(GenTest.types.date('%Y-%m-%d %H:%M'))});
    generators.data = GenTest.types.oneOf([generators.histData, generators.lineData]);

    describe('type', function() {
        it('should be of type ALL', function() {
            var solarData = SolarData.create([], '', '', '');
            expect(solarData.type).toBe(SolarData.Type.ALL);
        });
        it('should be of type YEAR', [
            generators.year,
        ], function(year) {
            var solarData = SolarData.create([], year, '', '');
            expect(solarData.type).toBe(SolarData.Type.YEAR);
        });
        it('should be of type MONTH', [
            generators.year,
            generators.month,
        ], function(year, month) {
            var solarData = SolarData.create([], year, month, '');
            expect(solarData.type).toBe(SolarData.Type.MONTH);
        });
        it('should be of type DAY', [
            generators.year,
            generators.month,
            generators.day,
        ], function(year, month, day) {
            var solarData = SolarData.create([], year, month, day);
            expect(solarData.type).toBe(SolarData.Type.DAY);
        });
        it('should be of type DAY', [
            generators.data,
        ], function(data) {
            var solarData = SolarData.create(data);
            expect(solarData.type).toBe(SolarData.Type.DAY);
        });
    });
    describe('xLabel', function() {
        it('should be "Année"', function() {
            var solarData = SolarData.create([], '', '', '');
            expect(solarData.xLabel).toBe('Année');
        });
        it('should "Mois"', [
            generators.year,
        ], function(year) {
            var solarData = SolarData.create([], year, '', '');
            expect(solarData.xLabel).toBe('Mois');
        });
        it('should be "Jour"', [
            generators.year,
            generators.month,
        ], function(year, month) {
            var solarData = SolarData.create([], year, month, '');
            expect(solarData.xLabel).toBe('Jour');
        });
        it('should be "Temps (h)"', [
            generators.year,
            generators.month,
            generators.day,
        ], function(year, month, day) {
            var solarData = SolarData.create([], year, month, day);
            expect(solarData.xLabel).toBe('Temps (h)');
        });
        it('should be "Temps (h)"', [
            generators.data,
        ],function(data) {
            var solarData = SolarData.create(data);
            expect(solarData.xLabel).toBe('Temps (h)');
        });
    });
    describe('dateParser', function() {
        it('should return year', [
            GenTest.types.date('%Y-12-31')
        ], function(dateStr) {
            var date = new Date(dateStr);
            var solarData = SolarData.create([], '', '', '');
            var parsedDate = solarData.dateParser(dateStr);

            expect(typeof parsedDate).toBe('number');
            expect(parsedDate).toBe(date.getFullYear());
        });
        it('should return month', [
            generators.year,
            GenTest.types.date('%Y-%m-01'),
        ], function(year, dateStr) {
            var date = new Date(dateStr);
            var solarData = SolarData.create([], year, '', '');
            var parsedDate = solarData.dateParser(dateStr);

            expect(typeof parsedDate).toBe('number');
            expect(parsedDate).toBe(date.getMonth());
        });
        it('should return day', [
            generators.year,
            generators.month,
            GenTest.types.date('%Y-%m-%d'),
        ], function(year, month, dateStr) {
            var date = new Date(dateStr);
            var solarData = SolarData.create([], year, month, '');
            var parsedDate = solarData.dateParser(dateStr);

            expect(typeof parsedDate).toBe('number');
            expect(parsedDate).toBe(date.getDate());
        });
        it('should return Date object', [
            generators.year,
            generators.month,
            generators.day,
            GenTest.types.date('%Y-%m-%d %H:%M'),
        ], function(year, month, day, dateStr) {
            jasmine.addCustomEqualityTester(dateEqualityTester);

            var date = new Date(dateStr);
            var solarData = SolarData.create([], year, month, day);
            var parsedDate = solarData.dateParser(dateStr);

            expect(typeof parsedDate).toBe('object');
            expect(parsedDate instanceof Date).toBeTruthy();
            expect(parsedDate).toEqual(date);
        });
        it('should return Date object', [
            generators.data,
            GenTest.types.date('%Y-%m-%d %H:%M'),
        ],function(data, dateStr) {
            jasmine.addCustomEqualityTester(dateEqualityTester);

            var date = new Date(dateStr);
            var solarData = SolarData.create(data);
            var parsedDate = solarData.dateParser(dateStr);

            expect(typeof parsedDate).toBe('object');
            expect(parsedDate instanceof Date).toBeTruthy();
            expect(parsedDate).toEqual(date);
        });
    });
    describe('dateParser', function() {
        it('should return "%Y"', [
            GenTest.types.choose(1900, 9999)
        ], function(year) {
            var solarData = SolarData.create([], '', '', '');
            var formattedDate = solarData.dateFormatter(year);

            expect(typeof formattedDate).toBe('string');
            expect(formattedDate.length).toBe(4);
            expect(formattedDate).toBe(pad(year, 4, '0'));
        });
        it('should return "%m/%Y"', [
            generators.year,
            GenTest.types.choose(0, 11),
        ], function(year, month) {
            var solarData = SolarData.create([], year, '', '');
            var formattedDate = solarData.dateFormatter(month);

            expect(typeof formattedDate).toBe('string');
            expect(formattedDate.length).toBe(7);
            expect(formattedDate).toBe(pad(month + 1, 2, '0') + '/' + pad(year, 4, '0'));
        });
        it('should return "%d/%m/%Y"', [
            generators.year,
            generators.month,
            GenTest.types.choose(1, 31),
        ], function(year, month, day) {
            var solarData = SolarData.create([], year, month, '');
            var formattedDate = solarData.dateFormatter(day);

            expect(typeof formattedDate).toBe('string');
            expect(formattedDate.length).toBe(10);
            expect(formattedDate).toBe(pad(day, 2, '0') + '/' + pad(month, 2, '0') + '/' + pad(year, 4, '0'));
        });
        it('should return "%d/%m/%Y %H:%M"', [
            generators.year,
            generators.month,
            generators.day,
            GenTest.types.date(),
        ], function(year, month, day, date) {
            var solarData = SolarData.create([], year, month, day);
            var formattedDate = solarData.dateFormatter(date);

            expect(typeof formattedDate).toBe('string');
            expect(formattedDate).toEqual(
                pad(date.getDate(), 2, '0') + '/' +
                pad(date.getMonth() + 1, 2, '0') + '/' +
                pad(date.getFullYear(), 4, '0') + ' ' +
                pad(date.getHours(), 2, '0') + ':' +
                pad(date.getMinutes(), 2, '0')
            );
        });
        it('should return "%d/%m/%Y %H:%M"', [
            generators.data,
            GenTest.types.date(),
        ],function(data, date) {
            var solarData = SolarData.create(data);
            var formattedDate = solarData.dateFormatter(date);

            expect(typeof formattedDate).toBe('string');
            expect(formattedDate).toEqual(
                pad(date.getDate(), 2, '0') + '/' +
                pad(date.getMonth() + 1, 2, '0') + '/' +
                pad(date.getFullYear(), 4, '0') + ' ' +
                pad(date.getHours(), 2, '0') + ':' +
                pad(date.getMinutes(), 2, '0')
            );
        });
    });
    describe('dateString', function() {
        it('should be empty', function() {
            var solarData = SolarData.create([], '', '', '');
            expect(solarData.dateString).toBe('');
        });
        it('should be "%Y"', [
            generators.year,
        ], function(year) {
            var solarData = SolarData.create([], year, '', '');
            expect(solarData.dateString).toBe(pad(year, 4, '0'));
        });
        it('should be "%m-%Y"', [
            generators.year,
            generators.month,
        ], function(year, month) {
            var solarData = SolarData.create([], year, month, '');
            expect(solarData.dateString).toBe(pad(month, 2, '0') + '-' + pad(year, 4, '0'));
        });
        it('should be "%d-%m-%Y"', [
            generators.year,
            generators.month,
            generators.day,
        ], function(year, month, day) {
            var solarData = SolarData.create([], year, month, day);
            expect(solarData.dateString).toBe(pad(day, 2, '0') + '-' + pad(month, 2, '0') + '-' + pad(year, 4, '0'));
        });
        it('should be "%d-%m-%Y"', [
            generators.lineData,
        ], function(data) {
            var solarData = SolarData.create(data);
            var date = new Date(data.dates[0])
            expect(solarData.dateString).toBe(pad(date.getDate(), 2, '0') + '-' + pad(date.getMonth() + 1, 2, '0') + '-' + pad(date.getFullYear(), 4, '0'));
        });
        it('should be "%d-%m-%Y"', [
            generators.histData,
        ], function(data) {
            var solarData = SolarData.create(data);
            var date = new Date(data[0].date)
            expect(solarData.dateString).toBe(pad(date.getDate(), 2, '0') + '-' + pad(date.getMonth() + 1, 2, '0') + '-' + pad(date.getFullYear(), 4, '0'));
        });
    });
    describe('axes and scales', function() {
        it('X scale should be X axis scale, Y scale should be Y axis scale', GenTest.types.oneOf([
            GenTest.types.tuple([
                GenTest.types.constantly(''),
                GenTest.types.constantly(''),
                GenTest.types.constantly(''),
            ]),
            GenTest.types.tuple([
                generators.year,
                GenTest.types.constantly(''),
                GenTest.types.constantly(''),
            ]),
            GenTest.types.tuple([
                generators.year,
                generators.month,
                GenTest.types.constantly(''),
            ]),
            GenTest.types.tuple([
                generators.year,
                generators.month,
                generators.day,
            ]),
        ]), function(year, month, day) {
            var solarData = new SolarData.create([], year, month, day);
            expect(solarData.xAxis.scale()).toBe(solarData.xScale);
            expect(solarData.yAxis.scale()).toBe(solarData.yScale);
            expect(solarData.yGrid.scale()).toBe(solarData.yScale);
        });
        it('X scale should be X axis scale, Y scale should be Y axis scale', [
            generators.data,
        ],function(data) {
            var solarData = SolarData.create(data);
            expect(solarData.xAxis.scale()).toBe(solarData.xScale);
            expect(solarData.yAxis.scale()).toBe(solarData.yScale);
            expect(solarData.yGrid.scale()).toBe(solarData.yScale);
        });
        it('X axis inner and outer tick size to be 6 and Y axis inner and outer tick size to be 6 and 0 respectively', function() {
            var solarData = new SolarData.create([], '', '', '');
            expect(solarData.xAxis.tickSizeOuter()).toBe(6);
            expect(solarData.xAxis.tickSizeInner()).toBe(6);
            expect(solarData.yAxis.tickSizeOuter()).toBe(0);
            expect(solarData.yAxis.tickSizeInner()).toBe(6);
        });
        it('X axis inner and outer tick size to be 6 and Y axis inner and outer tick size to be 6 and 0 respectively', [
            generators.histData,
        ],
           function(data) {
            var solarData = SolarData.create(data);
            expect(solarData.xAxis.tickSizeOuter()).toBe(6);
            expect(solarData.xAxis.tickSizeInner()).toBe(6);
            expect(solarData.yAxis.tickSizeOuter()).toBe(0);
            expect(solarData.yAxis.tickSizeInner()).toBe(6);
        });
        it('X axis inner and outer tick size to be 6 and 0 respectively and Y axis inner and outer tick size to be 6 and 0 respectively', [
            generators.lineData,
        ],
           function(data) {
            var solarData = new SolarData.create(data);
            expect(solarData.xAxis.tickSizeOuter()).toBe(0);
            expect(solarData.xAxis.tickSizeInner()).toBe(6);
            expect(solarData.yAxis.tickSizeOuter()).toBe(0);
            expect(solarData.yAxis.tickSizeInner()).toBe(6);
        });
        it('X axis tick format to be "%_H"', [
            generators.lineData,
            GenTest.types.choose(0, 23),
        ], function(data, hour) {
            var solarData = new SolarData.create(data);
            var date = new Date();
            date.setHours(hour);
            expect(solarData.xAxis.tickFormat()(date)).toBe(pad(hour, 2, ' '));
        });
    });
    describe('data', function() {
        it('should be years', [
            generators.yearNumber,
            generators.yearNumber,
        ], function(minYear, maxYear) {
            if (minYear > maxYear) {
                var tmp = minYear;
                minYear = maxYear;
                maxYear = tmp;
            }

            var data = [];
            for (var y = minYear; y <= maxYear; y++)
                data.push({date: pad(y, 4, '0') + '-12-31'});

            var solarData = SolarData.create(data, '', '', '');
            expect(solarData.length).toBe(maxYear - minYear + 1);
            for (var y = 0; y < solarData.length; y++)
                expect(solarData[y].date).toBe(minYear + y);
        });
        it('should be months', [
            generators.year,
            generators.monthNumber,
            generators.monthNumber,
        ], function(year, minMonth, maxMonth) {
            if (minMonth > maxMonth) {
                var tmp = minMonth;
                minMonth = maxMonth;
                maxMonth = tmp;
            }

            var data = [];
            for (var m = minMonth; m <= maxMonth; m++)
                data.push({date: pad(year, 4, '0') + '-' + pad(m, 2, '0') + '-28'});

            var solarData = SolarData.create(data, year, '', '');
            expect(solarData.length).toBe(maxMonth - minMonth + 1);
            for (var m = 0; m < solarData.length; m++)
                expect(solarData[m].date).toBe(minMonth + m - 1);
        });
        it('should be days', [
            generators.year,
            generators.month,
            generators.dayNumber,
            generators.dayNumber,
        ], function(year, month, minDay, maxDay) {
            if (minDay > maxDay) {
                var tmp = minDay;
                minDay = maxDay;
                maxDay = tmp;
            }

            var data = [];
            for (var d = minDay; d <= maxDay; d++)
                data.push({date: pad(year, 4, '0') + '-' + pad(month, 2, '0') + '-' + pad(d, 2, '0')});

            var solarData = SolarData.create(data, year, month, '');
            expect(solarData.length).toBe(maxDay - minDay + 1);
            for (var d = 0; d < solarData.length; d++)
                expect(solarData[d].date).toBe(minDay + d);
        });
        it('should be dates', [
            generators.year,
            generators.month,
            generators.day,
            GenTest.types.choose(0, 23),
            GenTest.types.choose(0, 23),
            GenTest.types.fmap((m) => 5*m, GenTest.types.choose(0, 11)),
            GenTest.types.fmap((m) => 5*m, GenTest.types.choose(0, 11)),
        ], function(year, month, day, minHour, maxHour, minMinute, maxMinute) {
            jasmine.addCustomEqualityTester(dateEqualityTester);

            if (minHour > maxHour) {
                var tmp = minHour;
                minHour = maxHour;
                maxHour = tmp;
            }
            if ((minHour == maxHour) && (minMinute > maxMinute)) {
                var tmp = minMinute;
                minMinute = maxMinute;
                maxMinute = tmp;
            }

            var dates = [];
            var expectedDates = [];
            for (var hm = minHour * 60 + minMinute; hm <= maxHour * 60 + maxMinute; hm++) {
                var h = Math.floor(hm / 60);
                var m = hm - h * 60;
                dates.push(pad(year, 4, '0') + '-' + pad(month, 2, '0') + '-' + pad(day, 2, '0') + ' ' + pad(h, 2, '0') + ':' + pad(m, 2, '0'));
                expectedDates.push(new Date(year, month - 1, day, h, m));
            }

            var solarData = SolarData.create({dates: dates}, year, month, day);
            expect(solarData.length).toBe(1);
            expect(solarData[0].dates.length).toBe(expectedDates.length);
            for (var i = 0; i < solarData.length; i++)
                expect(solarData[0].dates[i]).toEqual(expectedDates[i]);
        });
        it('should be dates (today)', [
            generators.year,
            generators.month,
            generators.day,
            GenTest.types.choose(0, 23),
            GenTest.types.choose(0, 23),
            GenTest.types.fmap((m) => 5*m, GenTest.types.choose(0, 11)),
            GenTest.types.fmap((m) => 5*m, GenTest.types.choose(0, 11)),
        ], function(year, month, day, minHour, maxHour, minMinute, maxMinute) {
            jasmine.addCustomEqualityTester(dateEqualityTester);

            if (minHour > maxHour) {
                var tmp = minHour;
                minHour = maxHour;
                maxHour = tmp;
            }
            if ((minHour == maxHour) && (minMinute > maxMinute)) {
                var tmp = minMinute;
                minMinute = maxMinute;
                maxMinute = tmp;
            }

            var dates = [];
            var expectedDates = [];
            for (var hm = minHour * 60 + minMinute; hm <= maxHour * 60 + maxMinute; hm++) {
                var h = Math.floor(hm / 60);
                var m = hm - h * 60;
                dates.push(pad(year, 4, '0') + '-' + pad(month, 2, '0') + '-' + pad(day, 2, '0') + ' ' + pad(h, 2, '0') + ':' + pad(m, 2, '0'));
                expectedDates.push(new Date(year, month - 1, day, h, m));
            }

            var solarData = SolarData.create({dates: dates});
            expect(solarData.length).toBe(1);
            expect(solarData[0].dates.length).toBe(expectedDates.length);
            for (var i = 0; i < solarData.length; i++)
                expect(solarData[0].dates[i]).toEqual(expectedDates[i]);
        });
    });
    describe('X domain', function() {
        it('should be years', [
            generators.yearNumber,
            generators.yearNumber,
        ], function(minYear, maxYear) {
            if (minYear > maxYear) {
                var tmp = minYear;
                minYear = maxYear;
                maxYear = tmp;
            }

            var data = [];
            for (var y = minYear; y <= maxYear; y++)
                data.push({date: pad(y, 4, '0') + '-12-31'});

            var solarData = SolarData.create(data, '', '', '');
            var domain = solarData.xScale.domain();
            expect(domain.length).toBe(maxYear - minYear + 1);
            for (var y = 0; y < domain.length; y++)
                expect(domain[y]).toBe(minYear + y);
        });
        it('should be months', [
            generators.year,
            generators.monthNumber,
            generators.monthNumber,
        ], function(year, minMonth, maxMonth) {
            if (minMonth > maxMonth) {
                var tmp = minMonth;
                minMonth = maxMonth;
                maxMonth = tmp;
            }

            var data = [];
            for (var m = minMonth; m <= maxMonth; m++)
                data.push({date: pad(year, 4, '0') + '-' + pad(m, 2, '0') + '-28'});

            var solarData = SolarData.create(data, year, '', '');
            var domain = solarData.xScale.domain();
            expect(domain.length).toBe(maxMonth - minMonth + 1);
            for (var m = 0; m < domain.length; m++)
                expect(domain[m]).toBe(minMonth + m - 1);
        });
        it('should be days', [
            generators.year,
            generators.month,
            generators.dayNumber,
            generators.dayNumber,
        ], function(year, month, minDay, maxDay) {
            if (minDay > maxDay) {
                var tmp = minDay;
                minDay = maxDay;
                maxDay = tmp;
            }

            var data = [];
            for (var d = minDay; d <= maxDay; d++)
                data.push({date: pad(year, 4, '0') + '-' + pad(month, 2, '0') + '-' + pad(d, 2, '0')});

            var solarData = SolarData.create(data, year, month, '');
            var domain = solarData.xScale.domain();
            expect(domain.length).toBe(maxDay - minDay + 1);
            for (var d = 0; d < domain.length; d++)
                expect(domain[d]).toBe(minDay + d);
        });
        it('should be extent of dates', [
            generators.year,
            generators.month,
            generators.day,
            GenTest.types.choose(0, 23),
            GenTest.types.choose(0, 23),
            GenTest.types.fmap((m) => 5*m, GenTest.types.choose(0, 11)),
            GenTest.types.fmap((m) => 5*m, GenTest.types.choose(0, 11)),
        ], function(year, month, day, minHour, maxHour, minMinute, maxMinute) {
            jasmine.addCustomEqualityTester(dateEqualityTester);

            if (minHour > maxHour) {
                var tmp = minHour;
                minHour = maxHour;
                maxHour = tmp;
            }
            if ((minHour == maxHour) && (minMinute > maxMinute)) {
                var tmp = minMinute;
                minMinute = maxMinute;
                maxMinute = tmp;
            }

            var dates = [];
            for (var hm = minHour * 60 + minMinute; hm <= maxHour * 60 + maxMinute; hm++) {
                var h = Math.floor(hm / 60);
                var m = hm - h * 60;
                dates.push(pad(year, 4, '0') + '-' + pad(month, 2, '0') + '-' + pad(day, 2, '0') + ' ' + pad(h, 2, '0') + ':' + pad(m, 2, '0'));
            }

            var solarData = SolarData.create({dates: dates}, year, month, day);
            var domain = solarData.xScale.domain();
            expect(domain.length).toBe(2);
            expect(domain[0]).toEqual(new Date(year, month - 1, day, minHour, minMinute));
            expect(domain[1]).toEqual(new Date(year, month - 1, day, maxHour, maxMinute));
        });
        it('should be dates (today)', [
            generators.year,
            generators.month,
            generators.day,
            GenTest.types.choose(0, 23),
            GenTest.types.choose(0, 23),
            GenTest.types.fmap((m) => 5*m, GenTest.types.choose(0, 11)),
            GenTest.types.fmap((m) => 5*m, GenTest.types.choose(0, 11)),
        ], function(year, month, day, minHour, maxHour, minMinute, maxMinute) {
            jasmine.addCustomEqualityTester(dateEqualityTester);

            if (minHour > maxHour) {
                var tmp = minHour;
                minHour = maxHour;
                maxHour = tmp;
            }
            if ((minHour == maxHour) && (minMinute > maxMinute)) {
                var tmp = minMinute;
                minMinute = maxMinute;
                maxMinute = tmp;
            }

            var dates = [];
            for (var hm = minHour * 60 + minMinute; hm <= maxHour * 60 + maxMinute; hm++) {
                var h = Math.floor(hm / 60);
                var m = hm - h * 60;
                dates.push(pad(year, 4, '0') + '-' + pad(month, 2, '0') + '-' + pad(day, 2, '0') + ' ' + pad(h, 2, '0') + ':' + pad(m, 2, '0'));
            }

            var solarData = SolarData.create({dates: dates});
            var domain = solarData.xScale.domain();
            expect(domain.length).toBe(2);
            expect(domain[0]).toEqual(new Date(year, month - 1, day, minHour, minMinute));
            expect(domain[1]).toEqual(new Date(year, month - 1, day, maxHour, maxMinute));
        });
    });
});
