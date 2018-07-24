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

function setEqualityTester(set1, set2) {
    if ((set1 instanceof Array) && (set2 instanceof Array)) {
        for (s1 of set1) {
            if (!set2.includes(s1))
                return false;
        }
        for (s2 of set2) {
            if (!set1.includes(s2))
                return false
        }
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
            GenTest.types.elementOf(['0', ' ', ' 0']),
        ], function(n, l, p) {
            expect(pad(n, l, p).length).toBeGreaterThanOrEqual(l);
        });
        it('should start with p and end with n', [
            GenTest.types.oneOf([GenTest.types.int.nonNegative, GenTest.types.string.alphanumeric]),
            GenTest.types.int.nonNegative,
            GenTest.types.elementOf(['0', ' ', ' 0']),
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

    generators.histData = GenTest.types.arrayOf(GenTest.types.shape({date: GenTest.types.date('%Y-%m-%d')}), 1);
    generators.emptyHistData = GenTest.types.arrayOf(GenTest.types.shape({date: GenTest.types.date('%Y-%m-%d')}), null, 0);
    generators.lineData = GenTest.types.shape({dates: GenTest.types.arrayOf(GenTest.types.date('%Y-%m-%d %H:%M'), 3)});
    generators.emptyLineData = GenTest.types.shape({dates: GenTest.types.arrayOf(GenTest.types.date('%Y-%m-%d %H:%M'), null, 2)});
    generators.data = GenTest.types.oneOf([generators.histData, generators.lineData]);

    generators.any = GenTest.types.oneOf([
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
    ])

    describe('prefix', function() {
        it('should return "p"', function() {
            expect(SolarData.prefix(-4)).toBe('p');
        });
        it('should return "n"', function() {
            expect(SolarData.prefix(-3)).toBe('n');
        });
        it('should return "µ"', function() {
            expect(SolarData.prefix(-2)).toBe('µ');
        });
        it('should return "m"', function() {
            expect(SolarData.prefix(-1)).toBe('m');
        });
        it('should return ""', function() {
            expect(SolarData.prefix(0)).toBe('');
        });
        it('should return "k"', function() {
            expect(SolarData.prefix(1)).toBe('k');
        });
        it('should return "M"', function() {
            expect(SolarData.prefix(2)).toBe('M');
        });
        it('should return "G"', function() {
            expect(SolarData.prefix(3)).toBe('G');
        });
        it('should return "T"', function() {
            expect(SolarData.prefix(4)).toBe('T');
        });
    });
    describe('divider', function() {
        it('should return previous power of 1000', [GenTest.types.float(-15, 15)], function(N) {
            var powN = Math.pow(10, N);
            var log1000Div = Math.floor(N/3);
            var powD = Math.pow(1000, log1000Div);

            var solarData = SolarData.create([], '', '', '');
            solarData.updateDivider(powN);
            expect(solarData.div).toBeCloseTo(powD);
            expect(solarData.log1000Div).toBe(log1000Div);
        });
    });

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
    describe('isEmpty', function() {
        it('should be empty', function() {
            var solarData = SolarData.create([], '', '', '');
            expect(solarData.isEmpty()).toBeTruthy();
        });
        it('should be empty', [
            generators.year,
        ], function(year) {
            var solarData = SolarData.create([], year, '', '');
            expect(solarData.isEmpty()).toBeTruthy();
        });
        it('should be empty', [
            generators.year,
            generators.month,
        ], function(year, month) {
            var solarData = SolarData.create([], year, month, '');
            expect(solarData.isEmpty()).toBeTruthy();
        });
        it('should be empty', [
            generators.emptyLineData,
            generators.year,
            generators.month,
            generators.day,
        ], function(data, year, month, day) {
            var solarData = SolarData.create(data, year, month, day);
            expect(solarData.isEmpty()).toBeTruthy();
        });
        it('should be non-empty', [
            generators.histData,
        ],function(data) {
            var solarData = SolarData.create(data, '', '', '');
            expect(solarData.isEmpty()).toBeFalsy();
        });
        it('should be non-empty', [
            generators.histData,
            generators.year,
        ], function(data, year) {
            var solarData = SolarData.create(data, year, '', '');
            expect(solarData.isEmpty()).toBeFalsy();
        });
        it('should be non-empty', [
            generators.histData,
            generators.year,
            generators.month,
        ], function(data, year, month) {
            var solarData = SolarData.create(data, year, month, '');
            expect(solarData.isEmpty()).toBeFalsy();
        });
        it('should be non-empty', [
            generators.lineData,
            generators.year,
            generators.month,
            generators.day,
        ], function(data, year, month, day) {
            var solarData = SolarData.create(data, year, month, day);
            expect(solarData.isEmpty()).toBeFalsy();
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
    describe('dateFormatter', function() {
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
            var date = new Date(data.dates[0]);
            expect(solarData.dateString).toBe(pad(date.getDate(), 2, '0') + '-' + pad(date.getMonth() + 1, 2, '0') + '-' + pad(date.getFullYear(), 4, '0'));
        });
        it('should be "%d-%m-%Y"', [
            generators.histData,
        ], function(data) {
            var solarData = SolarData.create(data);
            var date = new Date(data[0].date);
            expect(solarData.dateString).toBe(pad(date.getDate(), 2, '0') + '-' + pad(date.getMonth() + 1, 2, '0') + '-' + pad(date.getFullYear(), 4, '0'));
        });
    });
    describe('exportFilename', function() {
        it('should be "export_var_sum.csv"', [
            generators.year,
            GenTest.types.elementOf(SolarData.shortVars),
            GenTest.types.elementOf(Object.keys(SolarData.sums)),
        ], function(y, v, s) {
            var data = [{date: pad(y, 4, '0') + '-12-31'}];
            data[0][v] = [];
            var solarData = SolarData.create(data, '', '', '');
            expect(solarData.variable(SolarData.shortVars.indexOf(v))).toBe(SolarData.shortVars.indexOf(v));
            if (solarData.sum(s) != s)
                s = solarData.sum();
            expect(solarData.exportFilename()).toBe('export_' + v + '_' + s + '.csv');
        });
        it('should be "export_var_sum_%Y.csv"', [
            generators.year,
            generators.month,
            GenTest.types.elementOf(SolarData.shortVars),
            GenTest.types.elementOf(Object.keys(SolarData.sums)),
        ], function(y, m, v, s) {
            var data = [{date: pad(y, 4, '0') + '-' + pad(m, 2, '0') + '-28'}];
            data[0][v] = [];
            var solarData = SolarData.create(data, y, '', '');
            expect(solarData.variable(SolarData.shortVars.indexOf(v))).toBe(SolarData.shortVars.indexOf(v));
            if (solarData.sum(s) != s)
                s = solarData.sum();
            expect(solarData.exportFilename()).toBe('export_' + v + '_' + s + '_' + pad(y, 4, '0') + '.csv');
        });
        it('should be "export_var_sum_%m-%Y.csv"', [
            generators.year,
            generators.month,
            generators.day,
            GenTest.types.elementOf(SolarData.shortVars),
            GenTest.types.elementOf(Object.keys(SolarData.sums)),
        ], function(y, m, d, v, s) {
            var data = [{date: pad(y, 4, '0') + '-' + pad(m, 2, '0') + '-' + pad(d, 2, '0')}];
            data[0][v] = [];
            var solarData = SolarData.create(data, y, m, '');
            expect(solarData.variable(SolarData.shortVars.indexOf(v))).toBe(SolarData.shortVars.indexOf(v));
            if (solarData.sum(s) != s)
                s = solarData.sum();
            expect(solarData.exportFilename()).toBe('export_' + v + '_' + s + '_' + pad(m, 2, '0') + '-' + pad(y, 4, '0') + '.csv');
        });
        it('should be "export_var_sum_%d-%m-%Y.csv"', [
            generators.lineData,
            GenTest.types.elementOf(SolarData.shortVars),
            GenTest.types.elementOf(Object.keys(SolarData.sums)),
        ], function(data, v, s) {
            data[v] = data.dates.map(() => Math.round(1000*Math.random()));
            var solarData = SolarData.create(data);
            expect(solarData.variable(SolarData.shortVars.indexOf(v))).toBe(SolarData.shortVars.indexOf(v));
            if (solarData.sum(s) != s)
                s = solarData.sum();
            var date = new Date(data.dates[0]);
            expect(solarData.exportFilename()).toBe('export_' + v + '_' + s + '_' + pad(date.getDate(), 2, '0') + '-' + pad(date.getMonth() + 1, 2, '0') + '-' + pad(date.getFullYear(), 4, '0') + '.csv');
        });
        it('should be "export_var_sum_%d-%m-%Y.csv"', [
            generators.histData,
            GenTest.types.elementOf(SolarData.shortVars),
            GenTest.types.elementOf(Object.keys(SolarData.sums)),
        ], function(data, v, s) {
            data.forEach((d) => {d[v] = [];})
            var solarData = SolarData.create(data);
            expect(solarData.variable(SolarData.shortVars.indexOf(v))).toBe(SolarData.shortVars.indexOf(v));
            if (solarData.sum(s) != s)
                s = solarData.sum();
            var date = new Date(data[0].date);
            expect(solarData.exportFilename()).toBe('export_' + v + '_' + s + '_' + pad(date.getDate(), 2, '0') + '-' + pad(date.getMonth() + 1, 2, '0') + '-' + pad(date.getFullYear(), 4, '0') + '.csv');
        });
    });
    describe('axes and scales', function() {
        it('X scale should be X axis scale, Y scale should be Y axis scale', generators.any, function(year, month, day) {
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
            var expectedData = [];
            for (var y = minYear; y <= maxYear; y++) {
                var nrj = Math.round(1000*Math.random());
                data.push({date: pad(y, 4, '0') + '-12-31', nrj: [nrj]});
                expectedData.push(nrj);
            }

            var solarData = SolarData.create(data, '', '', '');
            expect(solarData.variable(0)).toBe(0);
            expect(solarData.sum('sum')).toBe('sum');

            expect(solarData.length).toBe(maxYear - minYear + 1);
            for (var y = 0; y < solarData.length; y++) {
                expect(solarData[y].date).toBe(minYear + y);
                expect(solarData[y].data).toBe(expectedData[y]);
            }
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
            var expectedData = [];
            for (var m = minMonth; m <= maxMonth; m++) {
                var nrj = Math.round(1000*Math.random());
                data.push({date: pad(year, 4, '0') + '-' + pad(m, 2, '0') + '-28', nrj: [nrj]});
                expectedData.push(nrj);
            }

            var solarData = SolarData.create(data, year, '', '');
            expect(solarData.variable(0)).toBe(0);
            expect(solarData.sum('sum')).toBe('sum');

            expect(solarData.length).toBe(maxMonth - minMonth + 1);
            for (var m = 0; m < solarData.length; m++) {
                expect(solarData[m].date).toBe(minMonth + m - 1);
                expect(solarData[m].data).toBe(expectedData[m]);
            }
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
            var expectedData = [];
            for (var d = minDay; d <= maxDay; d++) {
                var nrj = Math.round(1000*Math.random());
                data.push({date: pad(year, 4, '0') + '-' + pad(month, 2, '0') + '-' + pad(d, 2, '0'), nrj: [nrj]});
                expectedData.push(nrj);
            }

            var solarData = SolarData.create(data, year, month, '');
            expect(solarData.variable(0)).toBe(0);
            expect(solarData.sum('sum')).toBe('sum');

            expect(solarData.length).toBe(maxDay - minDay + 1);
            for (var d = 0; d < solarData.length; d++) {
                expect(solarData[d].date).toBe(minDay + d);
                expect(solarData[d].data).toBe(expectedData[d]);
            }
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
            var expectedX = [];
            var expectedY = [];
            for (var hm = minHour * 60 + minMinute; hm <= maxHour * 60 + maxMinute; hm++) {
                var h = Math.floor(hm / 60);
                var m = hm - h * 60;
                dates.push(pad(year, 4, '0') + '-' + pad(month, 2, '0') + '-' + pad(day, 2, '0') + ' ' + pad(h, 2, '0') + ':' + pad(m, 2, '0'));
                expectedX.push(new Date(year, month - 1, day, h, m));
                expectedY.push(Math.round(1000*Math.random()));
            }

            var solarData = SolarData.create({dates: dates, nrj: expectedY}, year, month, day);
            expect(solarData.variable(0)).toBe(0);
            expect(solarData.sum('sum')).toBe('sum');

            expect(solarData.length).toBe(1);
            expect(solarData[0].x.length).toBe(expectedX.length);
            for (var i = 0; i < solarData[0].x.length; i++) {
                expect(solarData[0].x[i]).toEqual(expectedX[i]);
                expect(solarData[0].y[i]).toEqual(expectedY[i]);
            }
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
            var expectedX = [];
            var expectedY = [];
            for (var hm = minHour * 60 + minMinute; hm <= maxHour * 60 + maxMinute; hm++) {
                var h = Math.floor(hm / 60);
                var m = hm - h * 60;
                dates.push(pad(year, 4, '0') + '-' + pad(month, 2, '0') + '-' + pad(day, 2, '0') + ' ' + pad(h, 2, '0') + ':' + pad(m, 2, '0'));
                expectedX.push(new Date(year, month - 1, day, h, m));
                expectedY.push(Math.round(1000*Math.random()));
            }

            var solarData = SolarData.create({dates: dates, nrj: expectedY});
            expect(solarData.variable(0)).toBe(0);
            expect(solarData.sum('sum')).toBe('sum');

            expect(solarData.length).toBe(1);
            expect(solarData[0].x.length).toBe(expectedX.length);
            for (var i = 0; i < solarData[0].x.length; i++) {
                expect(solarData[0].x[i]).toEqual(expectedX[i]);
                expect(solarData[0].y[i]).toEqual(expectedY[i]);
            }
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
    describe('set X range', function() {
        it('should set X range and Y grid', [
            generators.any,
            GenTest.types.int.positive,
        ], function(ymd, w) {
            var solarData1 = SolarData.create([], ...ymd);
            expect(solarData1.xRange(w)).toEqual([0, w]);
            expect(solarData1.xRange()).toEqual([0, w]);
            expect(solarData1.xRange(null)).toEqual([0, w]);
            expect(solarData1.xScale.range()).toEqual([0, w]);
            expect(solarData1.yGrid.tickSize()).toEqual(w);

            var solarData2 = SolarData.create([], ...ymd);
            expect(solarData2.xRange([0, w])).toEqual([0, w]);
            expect(solarData2.xRange()).toEqual([0, w]);
            expect(solarData2.xRange(null)).toEqual([0, w]);
            expect(solarData2.xScale.range()).toEqual([0, w]);
            expect(solarData2.yGrid.tickSize()).toEqual(w);
        });
        it('should set X range and Y grid', [
            generators.data,
            GenTest.types.int.positive,
        ], function(data, w) {
            var solarData1 = SolarData.create(data);
            expect(solarData1.xRange(w)).toEqual([0, w]);
            expect(solarData1.xRange()).toEqual([0, w]);
            expect(solarData1.xRange(null)).toEqual([0, w]);
            expect(solarData1.xScale.range()).toEqual([0, w]);
            expect(solarData1.yGrid.tickSize()).toEqual(w);

            var solarData2 = SolarData.create(data);
            expect(solarData2.xRange([0, w])).toEqual([0, w]);
            expect(solarData2.xRange()).toEqual([0, w]);
            expect(solarData2.xRange(null)).toEqual([0, w]);
            expect(solarData2.xScale.range()).toEqual([0, w]);
            expect(solarData2.yGrid.tickSize()).toEqual(w);
        });
        it('should change X axis ticks to short month format', [
            generators.year,
            GenTest.types.choose(0, 749),
            generators.monthNumber,
        ], function(year, w, m) {
            var solarData1 = SolarData.create([], year, '', '');
            expect(solarData1.xRange(w)).toEqual([0, w]);
            expect(solarData1.xRange()).toEqual([0, w]);
            expect(solarData1.xRange(null)).toEqual([0, w]);
            var tickFormat = solarData1.xAxis.tickFormat();
            expect(tickFormat(m)).toBe(locale.format('%b')(new Date(2000, m)) + '.');

            var solarData2 = SolarData.create([], year, '', '');
            expect(solarData2.xRange([0, w])).toEqual([0, w]);
            expect(solarData2.xRange()).toEqual([0, w]);
            expect(solarData2.xRange(null)).toEqual([0, w]);
            var tickFormat = solarData2.xAxis.tickFormat();
            expect(tickFormat(m)).toBe(locale.format('%b')(new Date(2000, m)) + '.');
        });
        it('should change X axis ticks to long month format', [
            generators.year,
            GenTest.types.choose(750, null),
            generators.monthNumber,
        ], function(year, w, m) {
            var solarData1 = SolarData.create([], year, '', '');
            expect(solarData1.xRange(w)).toEqual([0, w]);
            expect(solarData1.xRange()).toEqual([0, w]);
            expect(solarData1.xRange(null)).toEqual([0, w]);
            var tickFormat = solarData1.xAxis.tickFormat();
            expect(tickFormat(m)).toBe(locale.format('%B')(new Date(2000, m)));

            var solarData2 = SolarData.create([], year, '', '');
            expect(solarData2.xRange([0, w])).toEqual([0, w]);
            expect(solarData2.xRange()).toEqual([0, w]);
            expect(solarData2.xRange(null)).toEqual([0, w]);
            var tickFormat = solarData2.xAxis.tickFormat();
            expect(tickFormat(m)).toBe(locale.format('%B')(new Date(2000, m)));
        });
    });
    describe('set Y range', function() {
        it('should set Y range', [
            generators.any,
            GenTest.types.int.positive,
        ], function(ymd, h) {
            var solarData1 = SolarData.create([], ...ymd);
            expect(solarData1.yRange(h)).toEqual([h, 0]);
            expect(solarData1.yRange()).toEqual([h, 0]);
            expect(solarData1.yRange(null)).toEqual([h, 0]);
            expect(solarData1.yScale.range()).toEqual([h, 0]);

            var solarData2 = SolarData.create([], ...ymd);
            expect(solarData2.yRange([h, 0])).toEqual([h, 0]);
            expect(solarData2.yRange()).toEqual([h, 0]);
            expect(solarData2.yRange(null)).toEqual([h, 0]);
            expect(solarData2.yScale.range()).toEqual([h, 0]);
        });
        it('should set Y range', [
            generators.data,
            GenTest.types.int.positive,
        ], function(data, h) {
            var solarData1 = SolarData.create(data);
            expect(solarData1.yRange(h)).toEqual([h, 0]);
            expect(solarData1.yRange()).toEqual([h, 0]);
            expect(solarData1.yRange(null)).toEqual([h, 0]);
            expect(solarData1.yScale.range()).toEqual([h, 0]);

            var solarData2 = SolarData.create(data);
            expect(solarData2.yRange([h, 0])).toEqual([h, 0]);
            expect(solarData2.yRange()).toEqual([h, 0]);
            expect(solarData2.yRange(null)).toEqual([h, 0]);
            expect(solarData2.yScale.range()).toEqual([h, 0]);
        });
    });

    var createDate = function(year, month, day) {
        year = pad(year, '0', 4);
        if (year === '')
            year = 2017;
        month = pad(month, '0', 2);
        if (month === '')
            month = 12;
        day = pad(day, '0', 2);
        if (day === '')
            day = 28;
        return year + '-' + month + '-' + day;
    }

    describe('variables', function() {
        it('should return available variables', [
            generators.any,
            GenTest.types.arrayOf(GenTest.types.elementOf(SolarData.shortVars), 1),
        ], function(ymd, vars) {
            var datum = {date: createDate(...ymd)};
            for (const v of vars)
                datum[v] = [];
            console.log(datum);

            jasmine.addCustomEqualityTester(setEqualityTester);

            var solarData = SolarData.create([datum], ...ymd);
            expect(solarData.validVariables).toEqual(vars.map((v) => SolarData.shortVars.indexOf(v)));
        });
    });
    describe('variable', function() {
        it('should set variable', [
            generators.any,
            GenTest.types.arrayOf(GenTest.types.elementOf(SolarData.shortVars), 1),
            GenTest.types.elementOf(SolarData.shortVars),
        ], function(ymd, vars, setVar) {
            var datum = {date: createDate(...ymd)};
            datum[setVar] = [];
            for (const v of vars)
                datum[v] = [];
            console.log(datum);

            jasmine.addCustomEqualityTester(setEqualityTester);

            var solarData = SolarData.create([datum], ...ymd);
            expect(solarData.variable()).toBe(null);
            expect(solarData.variable(setVar)).toBe(null);
            expect(solarData.variable(SolarData.shortVars.indexOf(setVar))).toEqual(SolarData.shortVars.indexOf(setVar));
        });
        it('should not set variable', [
            generators.any,
            GenTest.types.arrayOf(GenTest.types.elementOf(SolarData.shortVars), 1),
            GenTest.types.elementOf(SolarData.shortVars),
        ],function(ymd, vars, setVar) {
            var datum = {date: createDate(...ymd)};
            for (const v of vars)
                if (v != setVar)
                    datum[v] = [];
            console.log(datum);

            jasmine.addCustomEqualityTester(setEqualityTester);

            var solarData = SolarData.create([datum], ...ymd);
            expect(solarData.variable()).toBe(null);
            expect(solarData.variable(setVar)).toBe(null);
            expect(solarData.variable(SolarData.shortVars.indexOf(setVar))).not.toEqual(SolarData.shortVars.indexOf(setVar));
            expect(solarData.variable()).toBe(null);
        });
    });
    describe('yLabel', function() {
        it('Should return y label text with p multiplier', [
            generators.any,
            GenTest.types.elementOf(SolarData.shortVars),
            GenTest.types.float(0.000000000001, 0.000000000999),
        ], function(ymd, setVar, maxData) {
            var datum = {date: createDate(...ymd)};
            datum[setVar] = [];
            var v = SolarData.shortVars.indexOf(setVar);

            var solarData = SolarData.create([datum], ...ymd);
            expect(solarData.variable(v)).toEqual(v);
            solarData.updateDivider(maxData)
            expect(solarData.div).toBeCloseTo(0.000000000001);
            expect(solarData.log1000Div).toBe(-4);
            expect(solarData.yLabel()).toBe(SolarData.longVars[v] + ' (p' + SolarData.units[v] + ')');
        });
        it('Should return y label text with n multiplier', [
            generators.any,
            GenTest.types.elementOf(SolarData.shortVars),
            GenTest.types.float(0.000000001, 0.000000999),
        ], function(ymd, setVar, maxData) {
            var datum = {date: createDate(...ymd)};
            datum[setVar] = [];
            var v = SolarData.shortVars.indexOf(setVar);

            var solarData = SolarData.create([datum], ...ymd);
            expect(solarData.variable(v)).toEqual(v);
            solarData.updateDivider(maxData)
            expect(solarData.div).toBeCloseTo(0.000000001);
            expect(solarData.log1000Div).toBe(-3);
            expect(solarData.yLabel()).toBe(SolarData.longVars[v] + ' (n' + SolarData.units[v] + ')');
        });
        it('Should return y label text with µ multiplier', [
            generators.any,
            GenTest.types.elementOf(SolarData.shortVars),
            GenTest.types.float(0.000001, 0.000999),
        ], function(ymd, setVar, maxData) {
            var datum = {date: createDate(...ymd)};
            datum[setVar] = [];
            var v = SolarData.shortVars.indexOf(setVar);

            var solarData = SolarData.create([datum], ...ymd);
            expect(solarData.variable(v)).toEqual(v);
            solarData.updateDivider(maxData)
            expect(solarData.div).toBeCloseTo(0.000001);
            expect(solarData.log1000Div).toBe(-2);
            expect(solarData.yLabel()).toBe(SolarData.longVars[v] + ' (µ' + SolarData.units[v] + ')');
        });
        it('Should return y label text with m multiplier', [
            generators.any,
            GenTest.types.elementOf(SolarData.shortVars),
            GenTest.types.float(0.001, 0.999),
        ], function(ymd, setVar, maxData) {
            var datum = {date: createDate(...ymd)};
            datum[setVar] = [];
            var v = SolarData.shortVars.indexOf(setVar);

            var solarData = SolarData.create([datum], ...ymd);
            expect(solarData.variable(v)).toEqual(v);
            solarData.updateDivider(maxData)
            expect(solarData.div).toBeCloseTo(0.001);
            expect(solarData.log1000Div).toBe(-1);
            expect(solarData.yLabel()).toBe(SolarData.longVars[v] + ' (m' + SolarData.units[v] + ')');
        });
        it('Should return y label text without multiplier', [
            generators.any,
            GenTest.types.elementOf(SolarData.shortVars),
            GenTest.types.float(1, 999),
        ], function(ymd, setVar, maxData) {
            var datum = {date: createDate(...ymd)};
            datum[setVar] = [];
            var v = SolarData.shortVars.indexOf(setVar);

            var solarData = SolarData.create([datum], ...ymd);
            expect(solarData.variable(v)).toEqual(v);
            solarData.updateDivider(maxData)
            expect(solarData.div).toBeCloseTo(1);
            expect(solarData.log1000Div).toBe(0);
            expect(solarData.yLabel()).toBe(SolarData.longVars[v] + ' (' + SolarData.units[v] + ')');
        });
        it('Should return y label text with k multiplier', [
            generators.any,
            GenTest.types.elementOf(SolarData.shortVars),
            GenTest.types.float(1000, 999999),
        ], function(ymd, setVar, maxData) {
            var datum = {date: createDate(...ymd)};
            datum[setVar] = [];
            var v = SolarData.shortVars.indexOf(setVar);

            var solarData = SolarData.create([datum], ...ymd);
            expect(solarData.variable(v)).toEqual(v);
            solarData.updateDivider(maxData)
            expect(solarData.div).toBeCloseTo(1000);
            expect(solarData.log1000Div).toBe(1);
            expect(solarData.yLabel()).toBe(SolarData.longVars[v] + ' (k' + SolarData.units[v] + ')');
        });
        it('Should return y label text with M multiplier', [
            generators.any,
            GenTest.types.elementOf(SolarData.shortVars),
            GenTest.types.float(1000000, 999999999),
        ], function(ymd, setVar, maxData) {
            var datum = {date: createDate(...ymd)};
            datum[setVar] = [];
            var v = SolarData.shortVars.indexOf(setVar);

            var solarData = SolarData.create([datum], ...ymd);
            expect(solarData.variable(v)).toEqual(v);
            solarData.updateDivider(maxData)
            expect(solarData.div).toBeCloseTo(1000000);
            expect(solarData.log1000Div).toBe(2);
            expect(solarData.yLabel()).toBe(SolarData.longVars[v] + ' (M' + SolarData.units[v] + ')');
        });
        it('Should return y label text with G multiplier', [
            generators.any,
            GenTest.types.elementOf(SolarData.shortVars),
            GenTest.types.float(1000000000, 999999999999),
        ], function(ymd, setVar, maxData) {
            var datum = {date: createDate(...ymd)};
            datum[setVar] = [];
            var v = SolarData.shortVars.indexOf(setVar);

            var solarData = SolarData.create([datum], ...ymd);
            expect(solarData.variable(v)).toEqual(v);
            solarData.updateDivider(maxData)
            expect(solarData.div).toBeCloseTo(1000000000);
            expect(solarData.log1000Div).toBe(3);
            expect(solarData.yLabel()).toBe(SolarData.longVars[v] + ' (G' + SolarData.units[v] + ')');
        });
        it('Should return y label text with T multiplier', [
            generators.any,
            GenTest.types.elementOf(SolarData.shortVars),
            GenTest.types.float(1000000000000, 999999999999999),
        ], function(ymd, setVar, maxData) {
            var datum = {date: createDate(...ymd)};
            datum[setVar] = [];
            var v = SolarData.shortVars.indexOf(setVar);

            var solarData = SolarData.create([datum], ...ymd);
            expect(solarData.variable(v)).toEqual(v);
            solarData.updateDivider(maxData)
            expect(solarData.div).toBeCloseTo(1000000000000);
            expect(solarData.log1000Div).toBe(4);
            expect(solarData.yLabel()).toBe(SolarData.longVars[v] + ' (T' + SolarData.units[v] + ')');
        });
    });
    describe('validSums', function() {
        it('should return ["sum", "inv"] (nrj,pwr,pac)', [
            generators.any,
            GenTest.types.elementOf(['nrj', 'pwr', 'pac']),
        ], function(ymd, selectedVar) {
            var datum = {date: createDate(...ymd)};
            datum[selectedVar] = [];

            jasmine.addCustomEqualityTester(setEqualityTester);

            var solarData = SolarData.create([datum], ...ymd);
            expect(solarData.variable(SolarData.shortVars.indexOf(selectedVar))).toEqual(SolarData.shortVars.indexOf(selectedVar));
            expect(solarData.validSums).toEqual(['sum', 'inv']);
        });
        it('should return ["sum", "inv", "str"] (pdc)',  [
            generators.any,
            GenTest.types.constantly('pdc'),
        ], function(ymd, selectedVar) {
            var datum = {date: createDate(...ymd)};
            datum[selectedVar] = [];

            jasmine.addCustomEqualityTester(setEqualityTester);

            var solarData = SolarData.create([datum], ...ymd);
            expect(solarData.variable(SolarData.shortVars.indexOf(selectedVar))).toEqual(SolarData.shortVars.indexOf(selectedVar));
            expect(solarData.validSums).toEqual(['sum', 'inv', 'str']);
        });
        it('should return ["inv"] (uac, temp)', [
            generators.any,
            GenTest.types.elementOf(['uac', 'temp']),
        ], function(ymd, selectedVar) {
            var datum = {date: createDate(...ymd)};
            datum[selectedVar] = [];

            jasmine.addCustomEqualityTester(setEqualityTester);

            var solarData = SolarData.create([datum], ...ymd);
            expect(solarData.variable(SolarData.shortVars.indexOf(selectedVar))).toEqual(SolarData.shortVars.indexOf(selectedVar));
            expect(solarData.validSums).toEqual(['inv']);
        });
        it('should return ["str"] (udc)',  [
            generators.any,
            GenTest.types.constantly('udc'),
        ], function(ymd, selectedVar) {
            var datum = {date: createDate(...ymd)};
            datum[selectedVar] = [];

            jasmine.addCustomEqualityTester(setEqualityTester);

            var solarData = SolarData.create([datum], ...ymd);
            expect(solarData.variable(SolarData.shortVars.indexOf(selectedVar))).toEqual(SolarData.shortVars.indexOf(selectedVar));
            expect(solarData.validSums).toEqual(['str']);
        });
    });
    describe('sum', function() {
        it('should set sum (nrj, pwr, pac)', [
            generators.any,
            GenTest.types.elementOf(['nrj', 'pwr', 'pac']),
            GenTest.types.elementOf(['sum', 'inv']),
        ], function(ymd, selectedVar, selectedSum) {
            var datum = {date: createDate(...ymd)};
            datum[selectedVar] = [];

            jasmine.addCustomEqualityTester(setEqualityTester);

            var solarData = SolarData.create([datum], ...ymd);
            expect(solarData.variable(SolarData.shortVars.indexOf(selectedVar))).toEqual(SolarData.shortVars.indexOf(selectedVar));
            expect(solarData.sum()).toBe('sum');
            expect(solarData.sum(selectedSum)).toEqual(selectedSum);
        });
        it('should set sum (pdc)', [
            generators.any,
            GenTest.types.constantly('pdc'),
            GenTest.types.elementOf(['sum', 'inv', 'str']),
        ], function(ymd, selectedVar, selectedSum) {
            var datum = {date: createDate(...ymd)};
            datum[selectedVar] = [];

            jasmine.addCustomEqualityTester(setEqualityTester);

            var solarData = SolarData.create([datum], ...ymd);
            expect(solarData.variable(SolarData.shortVars.indexOf(selectedVar))).toEqual(SolarData.shortVars.indexOf(selectedVar));
            expect(solarData.sum()).toBe('sum');
            expect(solarData.sum(selectedSum)).toEqual(selectedSum);
        });
        it('should set sum (uac, temp)', [
            generators.any,
            GenTest.types.elementOf(['uac', 'temp']),
            GenTest.types.constantly('inv'),
        ], function(ymd, selectedVar, selectedSum) {
            var datum = {date: createDate(...ymd)};
            datum[selectedVar] = [];

            jasmine.addCustomEqualityTester(setEqualityTester);

            var solarData = SolarData.create([datum], ...ymd);
            expect(solarData.variable(SolarData.shortVars.indexOf(selectedVar))).toEqual(SolarData.shortVars.indexOf(selectedVar));
            expect(solarData.sum()).toBe('inv');
            expect(solarData.sum(selectedSum)).toEqual(selectedSum);
        });
        it('should set sum (udc)', [
            generators.any,
            GenTest.types.constantly('udc'),
            GenTest.types.constantly('str'),
        ], function(ymd, selectedVar, selectedSum) {
            var datum = {date: createDate(...ymd)};
            datum[selectedVar] = [];

            jasmine.addCustomEqualityTester(setEqualityTester);

            var solarData = SolarData.create([datum], ...ymd);
            expect(solarData.variable(SolarData.shortVars.indexOf(selectedVar))).toEqual(SolarData.shortVars.indexOf(selectedVar));
            expect(solarData.sum()).toBe('str');
            expect(solarData.sum(selectedSum)).toEqual(selectedSum);
        });

        it('should not set sum (nrj, pwr, pac)', [
            generators.any,
            GenTest.types.elementOf(['nrj', 'pwr', 'pac']),
            GenTest.types.constantly('str'),
        ], function(ymd, selectedVar, selectedSum) {
            var datum = {date: createDate(...ymd)};
            datum[selectedVar] = [];

            jasmine.addCustomEqualityTester(setEqualityTester);

            var solarData = SolarData.create([datum], ...ymd);
            expect(solarData.variable(SolarData.shortVars.indexOf(selectedVar))).toEqual(SolarData.shortVars.indexOf(selectedVar));
            expect(solarData.sum()).toBe('sum');
            expect(solarData.sum(selectedSum)).not.toEqual(selectedSum);
            expect(solarData.sum()).toBe('sum');
        });
        it('should not set sum (uac, temp)', [
            generators.any,
            GenTest.types.elementOf(['uac', 'temp']),
            GenTest.types.elementOf(['sum', 'str']),
        ], function(ymd, selectedVar, selectedSum) {
            var datum = {date: createDate(...ymd)};
            datum[selectedVar] = [];

            jasmine.addCustomEqualityTester(setEqualityTester);

            var solarData = SolarData.create([datum], ...ymd);
            expect(solarData.variable(SolarData.shortVars.indexOf(selectedVar))).toEqual(SolarData.shortVars.indexOf(selectedVar));
            expect(solarData.sum()).toBe('inv');
            expect(solarData.sum(selectedSum)).not.toEqual(selectedSum);
            expect(solarData.sum()).toBe('inv');
        });
        it('should not set sum (udc)', [
            generators.any,
            GenTest.types.constantly('udc'),
            GenTest.types.elementOf(['sum', 'inv']),
        ], function(ymd, selectedVar, selectedSum) {
            var datum = {date: createDate(...ymd)};
            datum[selectedVar] = [];

            jasmine.addCustomEqualityTester(setEqualityTester);

            var solarData = SolarData.create([datum], ...ymd);
            expect(solarData.variable(SolarData.shortVars.indexOf(selectedVar))).toEqual(SolarData.shortVars.indexOf(selectedVar));
            expect(solarData.sum()).toBe('str');
            expect(solarData.sum(selectedSum)).not.toEqual(selectedSum);
            expect(solarData.sum()).toBe('str');
        });
    });
    describe('export', function() {
        describe('histData', function() {
            it('1 column data, summed', [
                generators.yearNumber,
                generators.yearNumber,
            ], function(minYear, maxYear) {
                if (minYear > maxYear) {
                    var tmp = minYear;
                    minYear = maxYear;
                    maxYear = tmp;
                }

                var data = [];
                var expectedData = [];
                for (var y = maxYear; y >= minYear; y--) {
                    data.unshift({date: pad(y, 4, '0') + '-12-31', pdc: [Math.round(1000*Math.random())]});
                    expectedData.unshift([pad(y, 4, '0'), data[0].pdc[0]]);
                }

                var solarData = SolarData.create(data, '', '', '');
                expect(solarData.variable(SolarData.shortVars.indexOf('pdc'))).toBe(SolarData.shortVars.indexOf('pdc'));
                expect(solarData.sum('sum')).toBe('sum');

                var exportData = solarData.export();
                console.log(exportData);
                expect(exportData.headers).toEqual([['Date', 'Total']]);
                expect(exportData.data).toEqual(expectedData);
            });
            it('2 inverters data, summed', [
                generators.yearNumber,
                generators.yearNumber,
            ], function(minYear, maxYear) {
                if (minYear > maxYear) {
                    var tmp = minYear;
                    minYear = maxYear;
                    maxYear = tmp;
                }

                var data = [];
                var expectedData = [];
                for (var y = maxYear; y >= minYear; y--) {
                    data.unshift({date: pad(y, 4, '0') + '-12-31', pdc: [Math.round(1000*Math.random()), Math.round(1000*Math.random())]});
                    expectedData.unshift([pad(y, 4, '0'), data[0].pdc[0] + data[0].pdc[1]]);
                }

                var solarData = SolarData.create(data, '', '', '');
                expect(solarData.variable(SolarData.shortVars.indexOf('pdc'))).toBe(SolarData.shortVars.indexOf('pdc'));
                expect(solarData.sum('sum')).toBe('sum');

                var exportData = solarData.export();
                console.log(exportData);
                expect(exportData.headers).toEqual([['Date', 'Total']]);
                expect(exportData.data).toEqual(expectedData);
            });
            it('2 inverters data, by inverter', [
                generators.yearNumber,
                generators.yearNumber,
            ], function(minYear, maxYear) {
                if (minYear > maxYear) {
                    var tmp = minYear;
                    minYear = maxYear;
                    maxYear = tmp;
                }

                var data = [];
                var expectedData = [];
                for (var y = maxYear; y >= minYear; y--) {
                    data.unshift({date: pad(y, 4, '0') + '-12-31', pdc: [Math.round(1000*Math.random()), Math.round(1000*Math.random())]});
                    expectedData.unshift([pad(y, 4, '0'), data[0].pdc[0], data[0].pdc[1]]);
                }

                var solarData = SolarData.create(data, '', '', '');
                expect(solarData.variable(SolarData.shortVars.indexOf('pdc'))).toBe(SolarData.shortVars.indexOf('pdc'));
                expect(solarData.sum('inv')).toBe('inv');

                var exportData = solarData.export();
                console.log(exportData);
                expect(exportData.headers).toEqual([['Date', 'Onduleur 1', 'Onduleur 2']]);
                expect(exportData.data).toEqual(expectedData);
            });
            it('2 inverters, 2 strings data, summed', [
                generators.yearNumber,
                generators.yearNumber,
            ], function(minYear, maxYear) {
                if (minYear > maxYear) {
                    var tmp = minYear;
                    minYear = maxYear;
                    maxYear = tmp;
                }

                var data = [];
                var expectedData = [];
                for (var y = maxYear; y >= minYear; y--) {
                    data.unshift({date: pad(y, 4, '0') + '-12-31', pdc: [[Math.round(1000*Math.random()), Math.round(1000*Math.random())], [Math.round(1000*Math.random()), Math.round(1000*Math.random())]]});
                    expectedData.unshift([pad(y, 4, '0'), data[0].pdc[0][0] + data[0].pdc[0][1] + data[0].pdc[1][0] + data[0].pdc[1][1]]);
                }

                var solarData = SolarData.create(data, '', '', '');
                expect(solarData.variable(SolarData.shortVars.indexOf('pdc'))).toBe(SolarData.shortVars.indexOf('pdc'));
                expect(solarData.sum('sum')).toBe('sum');
                var exportData = solarData.export();
                console.log(exportData);
                expect(exportData.headers).toEqual([['Date', 'Total']]);
                expect(exportData.data).toEqual(expectedData);
            });
            it('2 inverters, 2 strings data, by inverter', [
                generators.yearNumber,
                generators.yearNumber,
            ], function(minYear, maxYear) {
                if (minYear > maxYear) {
                    var tmp = minYear;
                    minYear = maxYear;
                    maxYear = tmp;
                }

                var data = [];
                var expectedData = [];
                for (var y = maxYear; y >= minYear; y--) {
                    data.unshift({date: pad(y, 4, '0') + '-12-31', pdc: [[Math.round(1000*Math.random()), Math.round(1000*Math.random())], [Math.round(1000*Math.random()), Math.round(1000*Math.random())]]});
                    expectedData.unshift([pad(y, 4, '0'), data[0].pdc[0][0] + data[0].pdc[0][1], data[0].pdc[1][0] + data[0].pdc[1][1]]);
                }

                var solarData = SolarData.create(data, '', '', '');
                expect(solarData.variable(SolarData.shortVars.indexOf('pdc'))).toBe(SolarData.shortVars.indexOf('pdc'));
                expect(solarData.sum('inv')).toBe('inv');
                var exportData = solarData.export();
                console.log(exportData);
                expect(exportData.headers).toEqual([['Date', 'Onduleur 1', 'Onduleur 2']]);
                expect(exportData.data).toEqual(expectedData);
            });
            it('2 inverters, 2 strings data, by string', [
                generators.yearNumber,
                generators.yearNumber,
            ], function(minYear, maxYear) {
                if (minYear > maxYear) {
                    var tmp = minYear;
                    minYear = maxYear;
                    maxYear = tmp;
                }

                var data = [];
                var expectedData = [];
                for (var y = maxYear; y >= minYear; y--) {
                    data.unshift({date: pad(y, 4, '0') + '-12-31', pdc: [[Math.round(1000*Math.random()), Math.round(1000*Math.random())], [Math.round(1000*Math.random()), Math.round(1000*Math.random())]]});
                    expectedData.unshift([pad(y, 4, '0'), data[0].pdc[0][0], data[0].pdc[0][1], data[0].pdc[1][0], data[0].pdc[1][1]]);
                }

                var solarData = SolarData.create(data, '', '', '');
                expect(solarData.variable(SolarData.shortVars.indexOf('pdc'))).toBe(SolarData.shortVars.indexOf('pdc'));
                expect(solarData.sum('str')).toBe('str');
                var exportData = solarData.export();
                console.log(exportData);
                expect(exportData.headers).toEqual([
                    ['Date', 'Onduleur 1', 'Onduleur 1', 'Onduleur 2', 'Onduleur 2'],
                    ['', 'String 1', 'String 2', 'String 1', 'String 2'],
                ]);
                expect(exportData.data).toEqual(expectedData);
            });
        });
        describe('line data', function() {
            it('1 column data, summed', [generators.lineData], function(data) {
                data.pdc = [[]];
                var expectedData = [];
                var dateFormatter = d3.timeFormat('%d/%m/%Y %H:%M');
                for (var i = 1; i <= data.dates.length; i++) {
                    data.pdc[0].unshift(Math.round(1000*Math.random()));
                    expectedData.unshift([dateFormatter(d3.isoParse(data.dates[data.dates.length - i])), data.pdc[0][0]]);
                }

                var solarData = SolarData.create(data);
                expect(solarData.variable(SolarData.shortVars.indexOf('pdc'))).toBe(SolarData.shortVars.indexOf('pdc'));
                expect(solarData.sum('sum')).toBe('sum');
                var exportData = solarData.export();
                console.log(exportData);
                expect(exportData.headers).toEqual([['Date', 'Total']]);
                expect(exportData.data).toEqual(expectedData);
            });
            it('2 inverters data, summed', [generators.lineData], function(data) {
                data.pdc = [[], []];
                var expectedData = [];
                var dateFormatter = d3.timeFormat('%d/%m/%Y %H:%M');
                for (var i = 1; i <= data.dates.length; i++) {
                    data.pdc[0].unshift(Math.round(1000*Math.random()));
                    data.pdc[1].unshift(Math.round(1000*Math.random()));
                    expectedData.unshift([dateFormatter(d3.isoParse(data.dates[data.dates.length - i])), data.pdc[0][0] + data.pdc[1][0]]);
                }

                var solarData = SolarData.create(data);
                expect(solarData.variable(SolarData.shortVars.indexOf('pdc'))).toBe(SolarData.shortVars.indexOf('pdc'));
                expect(solarData.sum('sum')).toBe('sum');

                var exportData = solarData.export();
                console.log(exportData);
                expect(exportData.headers).toEqual([['Date', 'Total']]);
                expect(exportData.data).toEqual(expectedData);
            });
            it('2 inverters data, by inverter', [generators.lineData], function(data) {
                data.pdc = [[], []];
                var expectedData = [];
                var dateFormatter = d3.timeFormat('%d/%m/%Y %H:%M');
                for (var i = 1; i <= data.dates.length; i++) {
                    data.pdc[0].unshift(Math.round(1000*Math.random()));
                    data.pdc[1].unshift(Math.round(1000*Math.random()));
                    expectedData.unshift([dateFormatter(d3.isoParse(data.dates[data.dates.length - i])), data.pdc[0][0], data.pdc[1][0]]);
                }

                var solarData = SolarData.create(data);
                expect(solarData.variable(SolarData.shortVars.indexOf('pdc'))).toBe(SolarData.shortVars.indexOf('pdc'));
                expect(solarData.sum('inv')).toBe('inv');

                var exportData = solarData.export();
                console.log(exportData);
                expect(exportData.headers).toEqual([['Date', 'Onduleur 1', 'Onduleur 2']]);
                expect(exportData.data).toEqual(expectedData);
            });
            it('2 inverters, 2 strings data, summed', [generators.lineData], function(data) {
                data.pdc = [[[], []], [[], []]];
                var expectedData = [];
                var dateFormatter = d3.timeFormat('%d/%m/%Y %H:%M');
                for (var i = 1; i <= data.dates.length; i++) {
                    data.pdc[0][0].unshift(Math.round(1000*Math.random()));
                    data.pdc[0][1].unshift(Math.round(1000*Math.random()));
                    data.pdc[1][0].unshift(Math.round(1000*Math.random()));
                    data.pdc[1][1].unshift(Math.round(1000*Math.random()));
                    expectedData.unshift([dateFormatter(d3.isoParse(data.dates[data.dates.length - i])), data.pdc[0][0][0] + data.pdc[0][1][0] + data.pdc[1][0][0] + data.pdc[1][1][0]]);
                }

                var solarData = SolarData.create(data);
                expect(solarData.variable(SolarData.shortVars.indexOf('pdc'))).toBe(SolarData.shortVars.indexOf('pdc'));
                expect(solarData.sum('sum')).toBe('sum');

                var exportData = solarData.export();
                console.log(exportData);
                expect(exportData.headers).toEqual([['Date', 'Total']]);
                expect(exportData.data).toEqual(expectedData);
            });
            it('2 inverters, 2 strings data, by inverter', [generators.lineData], function(data) {
                data.pdc = [[[], []], [[], []]];
                var expectedData = [];
                var dateFormatter = d3.timeFormat('%d/%m/%Y %H:%M');
                for (var i = 1; i <= data.dates.length; i++) {
                    data.pdc[0][0].unshift(Math.round(1000*Math.random()));
                    data.pdc[0][1].unshift(Math.round(1000*Math.random()));
                    data.pdc[1][0].unshift(Math.round(1000*Math.random()));
                    data.pdc[1][1].unshift(Math.round(1000*Math.random()));
                    expectedData.unshift([dateFormatter(d3.isoParse(data.dates[data.dates.length - i])), data.pdc[0][0][0] + data.pdc[0][1][0], data.pdc[1][0][0] + data.pdc[1][1][0]]);
                }

                var solarData = SolarData.create(data);
                expect(solarData.variable(SolarData.shortVars.indexOf('pdc'))).toBe(SolarData.shortVars.indexOf('pdc'));
                expect(solarData.sum('inv')).toBe('inv');

                var exportData = solarData.export();
                console.log(exportData);
                expect(exportData.headers).toEqual([['Date', 'Onduleur 1', 'Onduleur 2']]);
                expect(exportData.data).toEqual(expectedData);
            });
            it('2 inverters, 2 strings data, by string', [generators.lineData], function(data) {
                data.pdc = [[[], []], [[], []]];
                var expectedData = [];
                var dateFormatter = d3.timeFormat('%d/%m/%Y %H:%M');
                for (var i = 1; i <= data.dates.length; i++) {
                    data.pdc[0][0].unshift(Math.round(1000*Math.random()));
                    data.pdc[0][1].unshift(Math.round(1000*Math.random()));
                    data.pdc[1][0].unshift(Math.round(1000*Math.random()));
                    data.pdc[1][1].unshift(Math.round(1000*Math.random()));
                    expectedData.unshift([dateFormatter(d3.isoParse(data.dates[data.dates.length - i])), data.pdc[0][0][0], data.pdc[0][1][0], data.pdc[1][0][0], data.pdc[1][1][0]]);
                }

                var solarData = SolarData.create(data);
                expect(solarData.variable(SolarData.shortVars.indexOf('pdc'))).toBe(SolarData.shortVars.indexOf('pdc'));
                expect(solarData.sum('str')).toBe('str');

                var exportData = solarData.export();
                console.log(exportData);
                expect(exportData.headers).toEqual([
                    ['Date', 'Onduleur 1', 'Onduleur 1', 'Onduleur 2', 'Onduleur 2'],
                    ['', 'String 1', 'String 2', 'String 1', 'String 2'],
                ]);
                expect(exportData.data).toEqual(expectedData);
            });
        });
    });
});
