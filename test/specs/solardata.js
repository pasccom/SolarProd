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

function fileForDate(year, month, day)
{
    if (year === undefined)
        return 'today.json';
    if (month === undefined)
        month = '';
    if (day === undefined)
        day = '';

    var folder;
    if (day != '')
        folder = 'days';
    else if (month != '')
        folder = 'months';
    else
        folder = 'years';

    var file = '';
    if (year != '')
        file += '/' + pad(year, 4, '0');
    if (month != '')
        file += '/' + pad(month, 2, '0');
    if (day != '')
        file += '/' + pad(day, 2, '0');

    return folder + file + '.json';
}

function createSolarData()
{
    jasmine.Ajax.install(); //console.log('install');

    var fileName = fileForDate(...arguments)
    var solarPromise = SolarData.create(...arguments);

    return {
        using: function(data) {
            var request = jasmine.Ajax.requests.mostRecent();
            expect(request.method).toBe('GET');
            expect(request.params).toBe(null);
            expect(request.username).toBe(null);
            expect(request.password).toBe(null);
            expect(request.url).toBe('data/' + fileName);
            request.respondWith({
                status: 200,
                responseJSON: data,
            });

            return {
                then: function(test) {
                    jasmine.Ajax.uninstall(); //console.log('uninstall');
                    return solarPromise.then(test);
                },
            };
        },
        then: function() {
            return this.using([]).then(...arguments);
        },
    };
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
    ]);

    generators.variable = (function() {
        const vars = [
            {code: 'nrj',  name: 'Énergie',      unit: 'Wh'},
            {code: 'pwr',  name: 'Puissance',    unit: 'W' },
            {code: 'pac',  name: 'Puissance AC', unit: 'W' },
            {code: 'uac',  name: 'Tension AC',   unit: 'V' },
            {code: 'pdc',  name: 'Puissance DC', unit: 'W' },
            {code: 'udc',  name: 'Tension DC',   unit: 'V' },
            {code: 'temp', name: 'Température',  unit: '°C'},
        ];

        var ret = GenTest.types.elementOf(vars);
        ret.code = GenTest.types.elementOf(vars.map((e) => e.code));
        ret.codes = function() {
            return GenTest.types.arrayOf(ret.code, ...arguments);
        }
        return ret;
    })();

    generators.aggregation = (function() {
        const aggregations = [
            {code: 'sum', name: 'Total'},
            {code: 'inv', name: 'Par onduleur'},
            {code: 'str', name: 'Par string'},
        ];

        return GenTest.types.elementOf(aggregations.map((e) => e.code));
    })();

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
        it('should return previous power of 1000', [GenTest.types.float(-15, 15, 0)], function(N) {
            var powN = Math.pow(10, N);
            var log1000Div = Math.floor(N/3);
            var powD = Math.pow(1000, log1000Div);

            return createSolarData('', '', '').then(function(solarData) {
                solarData.updateDivider(powN);
                expect(solarData.div).toBeCloseTo(powD);
                expect(solarData.log1000Div).toBe(log1000Div);
            });
        });
    });

    describe('type', function() {
        it('should be of type ALL', function() {
            return createSolarData('', '', '').then(function(solarData) {
                expect(solarData.type).toBe(SolarData.Type.ALL);
            });
        });
        it('should be of type YEAR', [
            generators.year,
        ], function(year) {
            return createSolarData(year, '', '').then(function(solarData) {
                expect(solarData.type).toBe(SolarData.Type.YEAR);
            });
        });
        it('should be of type MONTH', [
            generators.year,
            generators.month,
        ], function(year, month) {
            return createSolarData(year, month, '').then(function(solarData) {
                expect(solarData.type).toBe(SolarData.Type.MONTH);
            });
        });
        it('should be of type DAY', [
            generators.year,
            generators.month,
            generators.day,
        ], function(year, month, day) {
            return createSolarData(year, month, day).then(function(solarData) {
                expect(solarData.type).toBe(SolarData.Type.DAY);
            });
        });
        it('should be of type DAY', [
            generators.data,
        ], function(data) {
            return createSolarData().then(function(solarData) {
                expect(solarData.type).toBe(SolarData.Type.DAY);
            });
        });
    });
    describe('isEmpty', function() {
        it('should be empty', function() {
            return createSolarData('', '', '').then(function(solarData) {
                expect(solarData.isEmpty()).toBeTruthy();
            });
        });
        it('should be empty', [
            generators.year,
        ], function(year) {
            return createSolarData(year, '', '').then(function(solarData) {
                expect(solarData.isEmpty()).toBeTruthy();
            });
        });
        it('should be empty', [
            generators.year,
            generators.month,
        ], function(year, month) {
            return createSolarData(year, month, '').then(function(solarData) {
                expect(solarData.isEmpty()).toBeTruthy();
            });
        });
        it('should be empty', [
            generators.emptyLineData,
            generators.year,
            generators.month,
            generators.day,
        ], function(data, year, month, day) {
            return createSolarData(year, month, day).using(data).then(function(solarData) {
                expect(solarData.isEmpty()).toBeTruthy();
            });
        });
        it('should be non-empty', [
            generators.histData,
        ],function(data) {
            return createSolarData('', '', '').using(data).then(function(solarData) {
                expect(solarData.isEmpty()).toBeFalsy();
            });
        });
        it('should be non-empty', [
            generators.histData,
            generators.year,
        ], function(data, year) {
            return createSolarData(year, '', '').using(data).then(function(solarData) {
                expect(solarData.isEmpty()).toBeFalsy();
            });
        });
        it('should be non-empty', [
            generators.histData,
            generators.year,
            generators.month,
        ], function(data, year, month) {
            return createSolarData(year, month, '').using(data).then(function(solarData) {
                expect(solarData.isEmpty()).toBeFalsy();
            });
        });
        it('should be non-empty', [
            generators.lineData,
            generators.year,
            generators.month,
            generators.day,
        ], function(data, year, month, day) {
            return createSolarData(year, month, day).using(data).then(function(solarData) {
                expect(solarData.isEmpty()).toBeFalsy();
            });
        });
    });
    describe('xLabel', function() {
        it('should be "Année"', function() {
            return createSolarData('', '', '').then(function(solarData) {
                expect(solarData.xLabel).toBe('Année');
            });
        });
        it('should "Mois"', [
            generators.year,
        ], function(year) {
            return createSolarData(year, '', '').then(function(solarData) {
                expect(solarData.xLabel).toBe('Mois');
            });
        });
        it('should be "Jour"', [
            generators.year,
            generators.month,
        ], function(year, month) {
            return createSolarData(year, month, '').then(function(solarData) {
                expect(solarData.xLabel).toBe('Jour');
            });
        });
        it('should be "Temps (h)"', [
            generators.year,
            generators.month,
            generators.day,
        ], function(year, month, day) {
            return createSolarData(year, month, day).then(function(solarData) {
                expect(solarData.xLabel).toBe('Temps (h)');
            });
        });
        it('should be "Temps (h)"', [
            generators.data,
        ],function(data) {
            return createSolarData().using(data).then(function(solarData) {
                expect(solarData.xLabel).toBe('Temps (h)');
            });
        });
    });
    describe('dateParser', function() {
        it('should return year', [
            GenTest.types.date('%Y-12-31')
        ], function(dateStr) {
            var date = new Date(dateStr);

            return createSolarData('', '', '').then(function(solarData) {
                var parsedDate = solarData.dateParser(dateStr);
                expect(typeof parsedDate).toBe('number');
                expect(parsedDate).toBe(date.getFullYear());
            });
        });
        it('should return month', [
            generators.year,
            GenTest.types.date('%Y-%m-01'),
        ], function(year, dateStr) {
            var date = new Date(dateStr);

            return createSolarData(year, '', '').then(function(solarData) {
                var parsedDate = solarData.dateParser(dateStr);
                expect(typeof parsedDate).toBe('number');
                expect(parsedDate).toBe(date.getMonth());
            });
        });
        it('should return day', [
            generators.year,
            generators.month,
            GenTest.types.date('%Y-%m-%d'),
        ], function(year, month, dateStr) {
            var date = new Date(dateStr);

            return createSolarData(year, month, '').then(function(solarData) {
                var parsedDate = solarData.dateParser(dateStr);
                expect(typeof parsedDate).toBe('number');
                expect(parsedDate).toBe(date.getDate());
            });
        });
        it('should return Date object', [
            generators.year,
            generators.month,
            generators.day,
            GenTest.types.date('%Y-%m-%d %H:%M'),
        ], function(year, month, day, dateStr) {
            jasmine.addCustomEqualityTester(dateEqualityTester);

            var date = new Date(dateStr);

            return createSolarData(year, month, day).then(function(solarData) {
                var parsedDate = solarData.dateParser(dateStr);
                expect(typeof parsedDate).toBe('object');
                expect(parsedDate instanceof Date).toBeTruthy();
                expect(parsedDate).toEqual(date);
            });
        });
        it('should return Date object', [
            generators.data,
            GenTest.types.date('%Y-%m-%d %H:%M'),
        ],function(data, dateStr) {
            jasmine.addCustomEqualityTester(dateEqualityTester);

            var date = new Date(dateStr);

            return createSolarData().using(data).then(function(solarData) {
                var parsedDate = solarData.dateParser(dateStr);
                expect(typeof parsedDate).toBe('object');
                expect(parsedDate instanceof Date).toBeTruthy();
                expect(parsedDate).toEqual(date);
            });
        });
    });
    describe('dateFormatter', function() {
        it('should return "%Y"', [
            GenTest.types.choose(1900, 9999)
        ], function(year) {
            return createSolarData('', '', '').then(function(solarData) {
                var formattedDate = solarData.dateFormatter(year);
                expect(typeof formattedDate).toBe('string');
                expect(formattedDate.length).toBe(4);
                expect(formattedDate).toBe(pad(year, 4, '0'));
            });
        });
        it('should return "%m/%Y"', [
            generators.year,
            GenTest.types.choose(0, 11),
        ], function(year, month) {
            return createSolarData(year, '', '').then(function(solarData) {
                var formattedDate = solarData.dateFormatter(month);
                expect(typeof formattedDate).toBe('string');
                expect(formattedDate.length).toBe(7);
                expect(formattedDate).toBe(pad(month + 1, 2, '0') + '/' + pad(year, 4, '0'));
            });
        });
        it('should return "%d/%m/%Y"', [
            generators.year,
            generators.month,
            GenTest.types.choose(1, 31),
        ], function(year, month, day) {
            return createSolarData(year, month, '').then(function(solarData) {
                var formattedDate = solarData.dateFormatter(day);
                expect(typeof formattedDate).toBe('string');
                expect(formattedDate.length).toBe(10);
                expect(formattedDate).toBe(pad(day, 2, '0') + '/' + pad(month, 2, '0') + '/' + pad(year, 4, '0'));
            });
        });
        it('should return "%d/%m/%Y %H:%M"', [
            generators.year,
            generators.month,
            generators.day,
            GenTest.types.date(),
        ], function(year, month, day, date) {
            return createSolarData(year, month, day).then(function(solarData) {
                var formattedDate = solarData.dateFormatter(date);
                expect(typeof formattedDate).toBe('string');
                expect(formattedDate.length).toBe(16);
                expect(formattedDate).toEqual(
                    pad(date.getDate(), 2, '0') + '/' +
                    pad(date.getMonth() + 1, 2, '0') + '/' +
                    pad(date.getFullYear(), 4, '0') + ' ' +
                    pad(date.getHours(), 2, '0') + ':' +
                    pad(date.getMinutes(), 2, '0')
                );
            });
        });
        it('should return "%d/%m/%Y %H:%M"', [
            generators.data,
            GenTest.types.date(),
        ],function(data, date) {
            return createSolarData().using(data).then(function(solarData) {
                var formattedDate = solarData.dateFormatter(date);
                expect(typeof formattedDate).toBe('string');
                expect(formattedDate.length).toBe(16);
                expect(formattedDate).toEqual(
                    pad(date.getDate(), 2, '0') + '/' +
                    pad(date.getMonth() + 1, 2, '0') + '/' +
                    pad(date.getFullYear(), 4, '0') + ' ' +
                    pad(date.getHours(), 2, '0') + ':' +
                    pad(date.getMinutes(), 2, '0')
                );
            });
        });
    });
    describe('filePath', function() {
        it('years.json', function() {
            expect(SolarData.filePath('', '', '')).toBe('years.json');
        });
        it('/YYYY.json', [
            generators.year,
        ], function(year) {
            expect(SolarData.filePath(year, '', '')).toBe('/' + pad(year, 4, '0') + '.json');
        });
        it('/YYYY/mm.json', [
            generators.year,
            generators.month,
        ], function(year, month) {
            expect(SolarData.filePath(year, month, '')).toBe('/' + pad(year, 4, '0') + '/' + pad(month, 2, '0') + '.json');
        });
        it('/YYYY/mm/dd.json', [
            generators.emptyLineData,
            generators.year,
            generators.month,
            generators.day,
        ], function(data, year, month, day) {
            expect(SolarData.filePath(year, month, day)).toBe('/' + pad(year, 4, '0') + '/' + pad(month, 2, '0') + '/' + pad(day, 2, '0') + '.json');
        });
    });
    describe('dataFilePath', function() {
        it('data/years.json', function() {
            expect(SolarData.dataFilePath('', '', '')).toBe('data/years.json');
        });
        it('data/years/YYYY.json', [
            generators.year,
        ], function(year) {
            expect(SolarData.dataFilePath(year, '', '')).toBe('data/years/' + pad(year, 4, '0') + '.json');
        });
        it('data/months/YYYY/mm.json', [
            generators.year,
            generators.month,
        ], function(year, month) {
            expect(SolarData.dataFilePath(year, month, '')).toBe('data/months/' + pad(year, 4, '0') + '/' + pad(month, 2, '0') + '.json');
        });
        it('data/days/YYYY/mm/dd.json', [
            generators.emptyLineData,
            generators.year,
            generators.month,
            generators.day,
        ], function(data, year, month, day) {
            expect(SolarData.dataFilePath(year, month, day)).toBe('data/days/' + pad(year, 4, '0') + '/' + pad(month, 2, '0') + '/' + pad(day, 2, '0') + '.json');
        });
    });
    describe('listFilePath', function() {
        it('list/years.json', function() {
            expect(SolarData.listFilePath('', '', '')).toBe('list/years.json');
        });
        it('list/months/YYYY.json', [
            generators.year,
        ], function(year) {
            expect(SolarData.listFilePath(year, '', '')).toBe('list/months/' + pad(year, 4, '0') + '.json');
        });
        it('list/days/YYYY/mm.json', [
            generators.year,
            generators.month,
        ], function(year, month) {
            expect(SolarData.listFilePath(year, month, '')).toBe('list/days/' + pad(year, 4, '0') + '/' + pad(month, 2, '0') + '.json');
        });
    });
    describe('dateString', function() {
        it('should be empty', function() {
            return createSolarData('', '', '').then(function(solarData) {
                expect(solarData.dateString).toBe('');
            });
        });
        it('should be "%Y"', [
            generators.year,
        ], function(year) {
            return createSolarData(year, '', '').then(function(solarData) {
                expect(solarData.dateString).toBe(pad(year, 4, '0'));
            });
        });
        it('should be "%m-%Y"', [
            generators.year,
            generators.month,
        ], function(year, month) {
            return createSolarData(year, month, '').then(function(solarData) {
                expect(solarData.dateString).toBe(pad(month, 2, '0') + '-' + pad(year, 4, '0'));
            });
        });
        it('should be "%d-%m-%Y"', [
            generators.year,
            generators.month,
            generators.day,
        ], function(year, month, day) {
            return createSolarData(year, month, day).then(function(solarData) {
                expect(solarData.dateString).toBe(pad(day, 2, '0') + '-' + pad(month, 2, '0') + '-' + pad(year, 4, '0'));
            });
        });
        it('should be "%d-%m-%Y"', [
            generators.lineData,
        ], function(data) {
            var date = new Date(data.dates[0]);

            return createSolarData().using(data).then(function(solarData) {
                expect(solarData.dateString).toBe(
                    pad(date.getDate(), 2, '0') + '-' +
                    pad(date.getMonth() + 1, 2, '0') + '-' +
                    pad(date.getFullYear(), 4, '0')
                );
            });
        });
        it('should be "%d-%m-%Y"', [
            generators.histData,
        ], function(data) {
            var date = new Date(data[0].date);

            return createSolarData().using(data).then(function(solarData) {
                expect(solarData.dateString).toBe(
                    pad(date.getDate(), 2, '0') + '-' +
                    pad(date.getMonth() + 1, 2, '0') + '-' +
                    pad(date.getFullYear(), 4, '0')
                );
            });
        });
    });
    describe('exportFilename', function() {
        it('should be "export_var_sum.csv"', [
            generators.year,
            generators.variable.code,
            generators.aggregation,
        ], function(year, v, s) {
            var data = [{date: pad(year, 4, '0') + '-12-31'}];
            data[0][v] = [];

            return createSolarData('', '', '').using(data).then(function(solarData) {
                expect(solarData.variable(v)).toBe(v);
                if (solarData.aggregation(s) != s)
                    s = solarData.aggregation();
                expect(solarData.exportFilename()).toBe('export_' + v + '_' + s + '.csv');
            });
        });
        it('should be "export_var_sum_%Y.csv"', [
            generators.year,
            generators.month,
            generators.variable.code,
            generators.aggregation,
        ], function(year, month, v, s) {
            var data = [{date: pad(year, 4, '0') + '-' + pad(month, 2, '0') + '-28'}];
            data[0][v] = [];

            return createSolarData(year, '', '').using(data).then(function(solarData) {
                expect(solarData.variable(v)).toBe(v);
                if (solarData.aggregation(s) != s)
                    s = solarData.aggregation();
                expect(solarData.exportFilename()).toBe('export_' + v + '_' + s + '_' + pad(year, 4, '0') + '.csv');
            });
        });
        it('should be "export_var_sum_%m-%Y.csv"', [
            generators.year,
            generators.month,
            generators.day,
            generators.variable.code,
            generators.aggregation,
        ], function(year, month, day, v, s) {
            var data = [{date: pad(year, 4, '0') + '-' + pad(month, 2, '0') + '-' + pad(day, 2, '0')}];
            data[0][v] = [];

            return createSolarData(year, month, '').using(data).then(function(solarData) {
                expect(solarData.variable(v)).toBe(v);
                if (solarData.aggregation(s) != s)
                    s = solarData.aggregation();
                expect(solarData.exportFilename()).toBe('export_' + v + '_' + s + '_' + pad(month, 2, '0') + '-' + pad(year, 4, '0') + '.csv');
            });
        });
        it('should be "export_var_sum_%d-%m-%Y.csv"', [
            generators.year,
            generators.month,
            generators.day,
            GenTest.types.date('%H:%M'),
            generators.variable.code,
            generators.aggregation,
        ], function(year, month, day, time, v, s) {
            var data = {dates: [pad(year, 4, '0') + '-' + pad(month, 2, '0') + '-' + pad(day, 2, '0') + time]};
            data[v] = [Math.round(1000*Math.random())];

            return createSolarData(year, month, day).using(data).then(function(solarData) {
                expect(solarData.variable(v)).toBe(v);
                if (solarData.aggregation(s) != s)
                    s = solarData.aggregation();
                expect(solarData.exportFilename()).toBe('export_' + v + '_' + s + '_' + pad(day, 2, '0') + '-' + pad(month, 2, '0') + '-' + pad(year, 4, '0') + '.csv');
            });

        });
        it('should be "export_var_sum_%d-%m-%Y.csv" (lineData)', [
            generators.lineData,
            generators.variable.code,
            generators.aggregation,
        ], function(data, v, s) {
            var date = new Date(data.dates[0]);
            data[v] = data.dates.map(() => Math.round(1000*Math.random()));

            return createSolarData().using(data).then(function(solarData) {
                expect(solarData.variable(v)).toBe(v);
                if (solarData.aggregation(s) != s)
                    s = solarData.aggregation();
                expect(solarData.exportFilename()).toBe('export_' + v + '_' + s + '_' + pad(date.getDate(), 2, '0') + '-' + pad(date.getMonth() + 1, 2, '0') + '-' + pad(date.getFullYear(), 4, '0') + '.csv');
            });
        });
        it('should be "export_var_sum_%d-%m-%Y.csv" (histData)', [
            generators.histData,
            generators.variable.code,
            generators.aggregation,
        ], function(data, v, s) {
            var date = new Date(data[0].date);
            data.forEach((d) => {d[v] = [];});

            return createSolarData().using(data).then(function(solarData) {
                expect(solarData.variable(v)).toBe(v);
                if (solarData.aggregation(s) != s)
                    s = solarData.aggregation();
                expect(solarData.exportFilename()).toBe('export_' + v + '_' + s + '_' + pad(date.getDate(), 2, '0') + '-' + pad(date.getMonth() + 1, 2, '0') + '-' + pad(date.getFullYear(), 4, '0') + '.csv');
            });
        });
    });
    describe('axes and scales', function() {
        it('X scale should be X axis scale, Y scale should be Y axis scale', generators.any, function(year, month, day) {
            return createSolarData(year, month, day).then(function(solarData) {
                expect(solarData.xAxis.scale()).toBe(solarData.xScale);
                expect(solarData.yAxis.scale()).toBe(solarData.yScale);
                expect(solarData.yGrid.scale()).toBe(solarData.yScale);
            });
        });
        it('X scale should be X axis scale, Y scale should be Y axis scale', [
            generators.data,
        ],function(data) {
            return createSolarData().using(data).then(function(solarData) {
                expect(solarData.xAxis.scale()).toBe(solarData.xScale);
                expect(solarData.yAxis.scale()).toBe(solarData.yScale);
                expect(solarData.yGrid.scale()).toBe(solarData.yScale);
            });
        });
        it('X axis inner and outer tick size to be 6 and Y axis inner and outer tick size to be 6 and 0 respectively', function() {
            return createSolarData('', '', '').then(function(solarData) {
                expect(solarData.xAxis.tickSizeOuter()).toBe(6);
                expect(solarData.xAxis.tickSizeInner()).toBe(6);
                expect(solarData.yAxis.tickSizeOuter()).toBe(0);
                expect(solarData.yAxis.tickSizeInner()).toBe(6);
            });
        });
        it('X axis inner and outer tick size to be 6 and Y axis inner and outer tick size to be 6 and 0 respectively', [
            generators.histData,
        ], function(data) {
            return createSolarData().using(data).then(function(solarData) {
                expect(solarData.xAxis.tickSizeOuter()).toBe(6);
                expect(solarData.xAxis.tickSizeInner()).toBe(6);
                expect(solarData.yAxis.tickSizeOuter()).toBe(0);
                expect(solarData.yAxis.tickSizeInner()).toBe(6);
            });
        });
        it('X axis inner and outer tick size to be 6 and 0 respectively and Y axis inner and outer tick size to be 6 and 0 respectively', [
            generators.lineData,
        ], function(data) {
            return createSolarData().using(data).then(function(solarData) {
                expect(solarData.xAxis.tickSizeOuter()).toBe(0);
                expect(solarData.xAxis.tickSizeInner()).toBe(6);
                expect(solarData.yAxis.tickSizeOuter()).toBe(0);
                expect(solarData.yAxis.tickSizeInner()).toBe(6);
            });
        });
        it('X axis tick format to be "%_H"', [
            generators.lineData,
            GenTest.types.choose(0, 23),
        ], function(data, hour) {
            var date = new Date();
            date.setHours(hour);

            return createSolarData().using(data).then(function(solarData) {
                expect(solarData.xAxis.tickFormat()(date)).toBe(pad(hour, 2, ' '));
            });
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

            return createSolarData('', '', '').using(data).then(function(solarData) {
                expect(solarData.variable('nrj')).toBe('nrj');
                expect(solarData.aggregation('sum')).toBe('sum');

                expect(solarData.length).toBe(maxYear - minYear + 1);
                for (var y = 0; y < solarData.length; y++) {
                    expect(solarData[y].date).toBe(minYear + y);
                    expect(solarData[y].data).toBe(expectedData[y]);
                }
            });
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

            return createSolarData(year, '', '').using(data).then(function(solarData) {
                expect(solarData.variable('nrj')).toBe('nrj');
                expect(solarData.aggregation('sum')).toBe('sum');

                expect(solarData.length).toBe(maxMonth - minMonth + 1);
                for (var m = 0; m < solarData.length; m++) {
                    expect(solarData[m].date).toBe(minMonth + m - 1);
                    expect(solarData[m].data).toBe(expectedData[m]);
                }
            });
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

            return createSolarData(year, month, '').using(data).then(function(solarData) {
                expect(solarData.variable('nrj')).toBe('nrj');
                expect(solarData.aggregation('sum')).toBe('sum');

                expect(solarData.length).toBe(maxDay - minDay + 1);
                for (var d = 0; d < solarData.length; d++) {
                    expect(solarData[d].date).toBe(minDay + d);
                    expect(solarData[d].data).toBe(expectedData[d]);
                }
            });
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

            return createSolarData(year, month, day).using({dates: dates, nrj: expectedY}).then(function(solarData) {
                expect(solarData.variable('nrj')).toBe('nrj');
                expect(solarData.aggregation('sum')).toBe('sum');

                expect(solarData.length).toBe(1);
                expect(solarData[0].x.length).toBe(expectedX.length);
                for (var i = 0; i < solarData[0].x.length; i++) {
                    expect(solarData[0].x[i]).toEqual(expectedX[i]);
                    expect(solarData[0].y[i]).toEqual(expectedY[i]);
                }
            });
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

            return createSolarData().using({dates: dates, nrj: expectedY}).then(function(solarData) {
                expect(solarData.variable('nrj')).toBe('nrj');
                expect(solarData.aggregation('sum')).toBe('sum');

                expect(solarData.length).toBe(1);
                expect(solarData[0].x.length).toBe(expectedX.length);
                for (var i = 0; i < solarData[0].x.length; i++) {
                    expect(solarData[0].x[i]).toEqual(expectedX[i]);
                    expect(solarData[0].y[i]).toEqual(expectedY[i]);
                }
            });
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

            return createSolarData('', '', '').using(data).then(function(solarData) {
                var domain = solarData.xScale.domain();
                expect(domain.length).toBe(maxYear - minYear + 1);
                for (var y = 0; y < domain.length; y++)
                    expect(domain[y]).toBe(minYear + y);
            });
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

            return createSolarData(year, '', '').using(data).then(function(solarData) {
                var domain = solarData.xScale.domain();
                expect(domain.length).toBe(maxMonth - minMonth + 1);
                for (var m = 0; m < domain.length; m++)
                    expect(domain[m]).toBe(minMonth + m - 1);
            });
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

            return createSolarData(year, month, '').using(data).then(function(solarData) {
                var domain = solarData.xScale.domain();
                expect(domain.length).toBe(maxDay - minDay + 1);
                for (var d = 0; d < domain.length; d++)
                    expect(domain[d]).toBe(minDay + d);
            });
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

            return createSolarData(year, month, day).using({dates: dates}).then(function(solarData) {
                var domain = solarData.xScale.domain();
                expect(domain.length).toBe(2);
                expect(domain[0]).toEqual(new Date(year, month - 1, day, minHour, minMinute));
                expect(domain[1]).toEqual(new Date(year, month - 1, day, maxHour, maxMinute));
            });
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

            return createSolarData().using({dates: dates}).then(function(solarData) {
                var domain = solarData.xScale.domain();
                expect(domain.length).toBe(2);
                expect(domain[0]).toEqual(new Date(year, month - 1, day, minHour, minMinute));
                expect(domain[1]).toEqual(new Date(year, month - 1, day, maxHour, maxMinute));
            });
        });
    });
    describe('set X range', function() {
        it('should set X range and Y grid', [
            generators.any,
            GenTest.types.int.positive,
        ], function(ymd, w) {
            return Promise.all([
                createSolarData(...ymd).then(function(solarData) {
                    expect(solarData.xRange(w)).toEqual([0, w]);
                    expect(solarData.xRange()).toEqual([0, w]);
                    expect(solarData.xRange(null)).toEqual([0, w]);
                    expect(solarData.xScale.range()).toEqual([0, w]);
                    expect(solarData.yGrid.tickSize()).toEqual(w);
                }),
                createSolarData(...ymd).then(function(solarData) {
                    expect(solarData.xRange([0, w])).toEqual([0, w]);
                    expect(solarData.xRange()).toEqual([0, w]);
                    expect(solarData.xRange(null)).toEqual([0, w]);
                    expect(solarData.xScale.range()).toEqual([0, w]);
                    expect(solarData.yGrid.tickSize()).toEqual(w);
                }),
            ]);
        });
        it('should set X range and Y grid', [
            generators.data,
            GenTest.types.int.positive,
        ], function(data, w) {
            return Promise.all([
                createSolarData().using(data).then(function(solarData) {
                    expect(solarData.xRange(w)).toEqual([0, w]);
                    expect(solarData.xRange()).toEqual([0, w]);
                    expect(solarData.xRange(null)).toEqual([0, w]);
                    expect(solarData.xScale.range()).toEqual([0, w]);
                    expect(solarData.yGrid.tickSize()).toEqual(w);
                }),
                createSolarData().using(data).then(function(solarData) {
                    expect(solarData.xRange([0, w])).toEqual([0, w]);
                    expect(solarData.xRange()).toEqual([0, w]);
                    expect(solarData.xRange(null)).toEqual([0, w]);
                    expect(solarData.xScale.range()).toEqual([0, w]);
                    expect(solarData.yGrid.tickSize()).toEqual(w);
                }),
            ]);
        });
        it('should change X axis ticks to short month format', [
            generators.year,
            GenTest.types.choose(0, 749),
            generators.monthNumber,
        ], function(year, w, m) {
            return Promise.all([
                createSolarData(year, '', '').then(function(solarData) {
                    expect(solarData.xRange(w)).toEqual([0, w]);
                    expect(solarData.xRange()).toEqual([0, w]);
                    expect(solarData.xRange(null)).toEqual([0, w]);
                    var tickFormat = solarData.xAxis.tickFormat();
                    expect(tickFormat(m)).toBe(locale.format('%b')(new Date(2000, m)) + '.');
                }),
                createSolarData(year, '', '').then(function(solarData) {
                    expect(solarData.xRange([0, w])).toEqual([0, w]);
                    expect(solarData.xRange()).toEqual([0, w]);
                    expect(solarData.xRange(null)).toEqual([0, w]);
                    var tickFormat = solarData.xAxis.tickFormat();
                    expect(tickFormat(m)).toBe(locale.format('%b')(new Date(2000, m)) + '.');
                }),
            ]);
        });
        it('should change X axis ticks to long month format', [
            generators.year,
            GenTest.types.choose(750, null),
            generators.monthNumber,
        ], function(year, w, m) {
            return Promise.all([
                createSolarData(year, '', '').then(function(solarData) {
                    expect(solarData.xRange(w)).toEqual([0, w]);
                    expect(solarData.xRange()).toEqual([0, w]);
                    expect(solarData.xRange(null)).toEqual([0, w]);
                    var tickFormat = solarData.xAxis.tickFormat();
                    expect(tickFormat(m)).toBe(locale.format('%B')(new Date(2000, m)));
                }),
                createSolarData(year, '', '').then(function(solarData) {
                    expect(solarData.xRange([0, w])).toEqual([0, w]);
                    expect(solarData.xRange()).toEqual([0, w]);
                    expect(solarData.xRange(null)).toEqual([0, w]);
                    var tickFormat = solarData.xAxis.tickFormat();
                    expect(tickFormat(m)).toBe(locale.format('%B')(new Date(2000, m)));
                }),
            ]);
        });
    });
    describe('set Y range', function() {
        it('should set Y range', [
            generators.any,
            GenTest.types.int.positive,
        ], function(ymd, h) {
            return Promise.all([
                createSolarData(...ymd).then(function(solarData) {
                    expect(solarData.yRange(h)).toEqual([h, 0]);
                    expect(solarData.yRange()).toEqual([h, 0]);
                    expect(solarData.yRange(null)).toEqual([h, 0]);
                    expect(solarData.yScale.range()).toEqual([h, 0]);
                }),
                createSolarData(...ymd).then(function(solarData) {
                    expect(solarData.yRange([h, 0])).toEqual([h, 0]);
                    expect(solarData.yRange()).toEqual([h, 0]);
                    expect(solarData.yRange(null)).toEqual([h, 0]);
                    expect(solarData.yScale.range()).toEqual([h, 0]);
                }),
            ]);
        });
        it('should set Y range', [
            generators.data,
            GenTest.types.int.positive,
        ], function(data, h) {
            return Promise.all([
                createSolarData().using(data).then(function(solarData) {
                    expect(solarData.yRange(h)).toEqual([h, 0]);
                    expect(solarData.yRange()).toEqual([h, 0]);
                    expect(solarData.yRange(null)).toEqual([h, 0]);
                    expect(solarData.yScale.range()).toEqual([h, 0]);
                }),
                createSolarData().using(data).then(function(solarData) {
                    expect(solarData.yRange([h, 0])).toEqual([h, 0]);
                    expect(solarData.yRange()).toEqual([h, 0]);
                    expect(solarData.yRange(null)).toEqual([h, 0]);
                    expect(solarData.yScale.range()).toEqual([h, 0]);
                }),
            ]);
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

    describe('variables.name', function() {
        it('should return "Énergie"', function() {
            expect(SolarData.variables.name('nrj')).toBe('Énergie');
        });
        it('should return "Puissance"', function() {
            expect(SolarData.variables.name('pwr')).toBe('Puissance');
        });
        it('should return "Puissance AC"', function() {
            expect(SolarData.variables.name('pac')).toBe('Puissance AC');
        });
        it('should return "Puissance DC"', function() {
            expect(SolarData.variables.name('pdc')).toBe('Puissance DC');
        });
        it('should return "Tension AC"', function() {
            expect(SolarData.variables.name('uac')).toBe('Tension AC');
        });
        it('should return "Tension DC"', function() {
            expect(SolarData.variables.name('udc')).toBe('Tension DC');
        });
        it('should return "Température"', function() {
            expect(SolarData.variables.name('temp')).toBe('Température');
        });
    });
    describe('variables.unit', function() {
        it('should return "Wh"', function() {
            expect(SolarData.variables.unit('nrj')).toBe('Wh');
        });
        it('should return "W"', [GenTest.types.elementOf(['pwr', 'pac', 'pdc'])], function(v) {
            expect(SolarData.variables.unit(v)).toBe('W');
        });
        it('should return "V"', [GenTest.types.elementOf(['uac', 'udc'])], function(v) {
            expect(SolarData.variables.unit(v)).toBe('V');
        });
        it('should return "°C"', function() {
            expect(SolarData.variables.unit('temp')).toBe('°C');
        });
    });
    describe('validVars', function() {
        it('should return available variables', [
            generators.any,
            generators.variable.codes(1),
        ], function(ymd, vars) {
            jasmine.addCustomEqualityTester(setEqualityTester);

            var datum = {date: createDate(...ymd)};
            for (const v of vars)
                datum[v] = [];

            return createSolarData(...ymd).using([datum]).then(function(solarData) {
                expect(solarData.validVars).toEqual(vars);
            });
        });
    });
    describe('variable', function() {
        it('should set variable', [
            generators.any,
            generators.variable.codes(1),
            generators.variable.code,
        ], function(ymd, vars, setVar) {
            var datum = {date: createDate(...ymd)};
            datum[setVar] = [];
            for (const v of vars)
                datum[v] = [];

            return createSolarData(...ymd).using([datum]).then(function(solarData) {
                expect(solarData.variable()).toBe(null);
                expect(solarData.variable(setVar)).toBe(setVar);
            });
        });
        it('should not set variable', [
            generators.any,
            generators.variable.codes(1),
            generators.variable.code,
        ],function(ymd, vars, setVar) {
            var datum = {date: createDate(...ymd)};
            for (const v of vars)
                if (v != setVar)
                    datum[v] = [];

            return createSolarData(...ymd).using([datum]).then(function(solarData) {
                expect(solarData.variable()).toBe(null);
                expect(solarData.variable(setVar)).not.toBe(setVar);
                expect(solarData.variable()).toBe(null);
            });
        });
    });
    describe('yLabel', function() {
        it('Should return y label text with p multiplier', [
            generators.any,
            generators.variable,
            GenTest.types.float(0.000000000001, 0.000000000999),
        ], function(ymd, varData, maxData) {
            var datum = {date: createDate(...ymd)};
            datum[varData.code] = [maxData];

            return createSolarData(...ymd).using([datum]).then(function(solarData) {
                expect(solarData.variable(varData.code)).toBe(varData.code);
                //solarData.update();
                expect(solarData.div).toBeCloseTo(0.000000000001);
                expect(solarData.log1000Div).toBe(-4);
                expect(solarData.yLabel()).toBe(varData.name + ' (p' + varData.unit + ')');
            });
        });
        it('Should return y label text with n multiplier', [
            generators.any,
            generators.variable,
            GenTest.types.float(0.000000001, 0.000000999),
        ], function(ymd, varData, maxData) {
            var datum = {date: createDate(...ymd)};
            datum[varData.code] = [maxData];

            return createSolarData(...ymd).using([datum]).then(function(solarData) {
                expect(solarData.variable(varData.code)).toBe(varData.code);
                expect(solarData.div).toBeCloseTo(0.000000001);
                expect(solarData.log1000Div).toBe(-3);
                expect(solarData.yLabel()).toBe(varData.name + ' (n' + varData.unit + ')');
            });
        });
        it('Should return y label text with µ multiplier', [
            generators.any,
            generators.variable,
            GenTest.types.float(0.000001, 0.000999),
        ], function(ymd, varData, maxData) {
            var datum = {date: createDate(...ymd)};
            datum[varData.code] = [maxData];

            return createSolarData(...ymd).using([datum]).then(function(solarData) {
                expect(solarData.variable(varData.code)).toBe(varData.code);
                expect(solarData.div).toBeCloseTo(0.000001);
                expect(solarData.log1000Div).toBe(-2);
                expect(solarData.yLabel()).toBe(varData.name + ' (µ' + varData.unit + ')');
            });
        });
        it('Should return y label text with m multiplier', [
            generators.any,
            generators.variable,
            GenTest.types.float(0.001, 0.999),
        ], function(ymd, varData, maxData) {
            var datum = {date: createDate(...ymd)};
            datum[varData.code] = [maxData];

            return createSolarData(...ymd).using([datum]).then(function(solarData) {
                expect(solarData.variable(varData.code)).toBe(varData.code);
                expect(solarData.div).toBeCloseTo(0.001);
                expect(solarData.log1000Div).toBe(-1);
                expect(solarData.yLabel()).toBe(varData.name + ' (m' + varData.unit + ')');
            });
        });
        it('Should return y label text without multiplier', [
            generators.any,
            generators.variable,
            GenTest.types.float(1, 999),
        ], function(ymd, varData, maxData) {
            var datum = {date: createDate(...ymd)};
            datum[varData.code] = [maxData];

            return createSolarData(...ymd).using([datum]).then(function(solarData) {
                expect(solarData.variable(varData.code)).toBe(varData.code);
                expect(solarData.div).toBeCloseTo(1);
                expect(solarData.log1000Div).toBe(0);
                expect(solarData.yLabel()).toBe(varData.name + ' (' + varData.unit + ')');
            });
        });
        it('Should return y label text with k multiplier', [
            generators.any,
            generators.variable,
            GenTest.types.float(1000, 999999),
        ], function(ymd, varData, maxData) {
            var datum = {date: createDate(...ymd)};
            datum[varData.code] = [maxData];

            return createSolarData(...ymd).using([datum]).then(function(solarData) {
                expect(solarData.variable(varData.code)).toBe(varData.code);
                expect(solarData.div).toBeCloseTo(1000);
                expect(solarData.log1000Div).toBe(1);
                expect(solarData.yLabel()).toBe(varData.name + ' (k' + varData.unit + ')');
            });
        });
        it('Should return y label text with M multiplier', [
            generators.any,
            generators.variable,
            GenTest.types.float(1000000, 999999999),
        ], function(ymd, varData, maxData) {
            var datum = {date: createDate(...ymd)};
            datum[varData.code] = [maxData];

            return createSolarData(...ymd).using([datum]).then(function(solarData) {
                expect(solarData.variable(varData.code)).toBe(varData.code);
                expect(solarData.div).toBeCloseTo(1000000);
                expect(solarData.log1000Div).toBe(2);
                expect(solarData.yLabel()).toBe(varData.name + ' (M' + varData.unit + ')');
            });
        });
        it('Should return y label text with G multiplier', [
            generators.any,
            generators.variable,
            GenTest.types.float(1000000000, 999999999999),
        ], function(ymd, varData, maxData) {
            var datum = {date: createDate(...ymd)};
            datum[varData.code] = [maxData];

            return createSolarData(...ymd).using([datum]).then(function(solarData) {
                expect(solarData.variable(varData.code)).toBe(varData.code);
                expect(solarData.div).toBeCloseTo(1000000000);
                expect(solarData.log1000Div).toBe(3);
                expect(solarData.yLabel()).toBe(varData.name + ' (G' + varData.unit + ')');
            });
        });
        it('Should return y label text with T multiplier', [
            generators.any,
            generators.variable,
            GenTest.types.float(1000000000000, 999999999999999),
        ], function(ymd, varData, maxData) {
            var datum = {date: createDate(...ymd)};
            datum[varData.code] = [maxData];

            return createSolarData(...ymd).using([datum]).then(function(solarData) {
                expect(solarData.variable(varData.code)).toBe(varData.code);
                expect(solarData.div).toBeCloseTo(1000000000000);
                expect(solarData.log1000Div).toBe(4);
                expect(solarData.yLabel()).toBe(varData.name + ' (T' + varData.unit + ')');
            });
        });
    });

    describe('aggregations.name', function() {
        it('should return "Total"', function() {
            expect(SolarData.aggregations.name('sum')).toBe('Total');
        });
        it('should return "Par onduleur"', function() {
            expect(SolarData.aggregations.name('inv')).toBe('Par onduleur');
        });
        it('should return "Par string"', function() {
            expect(SolarData.aggregations.name('str')).toBe('Par string');
        });
    });
    describe('aggregations.index', function() {
        it('should return 0', function() {
            expect(SolarData.aggregations.index('sum')).toBe(0);
        });
        it('should return 1', function() {
            expect(SolarData.aggregations.index('inv')).toBe(1);
        });
        it('should return 2', function() {
            expect(SolarData.aggregations.index('str')).toBe(2);
        });
    });
    describe('validAggs', function() {
        it('should return ["sum", "inv"] (nrj,pwr,pac)', [
            generators.any,
            GenTest.types.elementOf(['nrj', 'pwr', 'pac']),
        ], function(ymd, selectedVar) {
            jasmine.addCustomEqualityTester(setEqualityTester);

            var datum = {date: createDate(...ymd)};
            datum[selectedVar] = [];

            return createSolarData(...ymd).using([datum]).then(function(solarData) {
                expect(solarData.variable(selectedVar)).toBe(selectedVar);
                expect(solarData.validAggs).toEqual(['sum', 'inv']);
            });
        });
        it('should return ["sum", "inv", "str"] (pdc)',  [
            generators.any,
            GenTest.types.constantly('pdc'),
        ], function(ymd, selectedVar) {
            jasmine.addCustomEqualityTester(setEqualityTester);

            var datum = {date: createDate(...ymd)};
            datum[selectedVar] = [];

            return createSolarData(...ymd).using([datum]).then(function(solarData) {
                expect(solarData.variable(selectedVar)).toBe(selectedVar);
                expect(solarData.validAggs).toEqual(['sum', 'inv', 'str']);
            });
        });
        it('should return ["inv"] (uac, temp)', [
            generators.any,
            GenTest.types.elementOf(['uac', 'temp']),
        ], function(ymd, selectedVar) {
            jasmine.addCustomEqualityTester(setEqualityTester);

            var datum = {date: createDate(...ymd)};
            datum[selectedVar] = [];

            return createSolarData(...ymd).using([datum]).then(function(solarData) {
                expect(solarData.variable(selectedVar)).toBe(selectedVar);
                expect(solarData.validAggs).toEqual(['inv']);
            });
        });
        it('should return ["str"] (udc)',  [
            generators.any,
            GenTest.types.constantly('udc'),
        ], function(ymd, selectedVar) {
            jasmine.addCustomEqualityTester(setEqualityTester);

            var datum = {date: createDate(...ymd)};
            datum[selectedVar] = [];

            return createSolarData(...ymd).using([datum]).then(function(solarData) {
                expect(solarData.variable(selectedVar)).toBe(selectedVar);
                expect(solarData.validAggs).toEqual(['str']);
            });
        });
    });
    describe('aggregation', function() {
        it('should set aggregation (nrj, pwr, pac)', [
            generators.any,
            GenTest.types.elementOf(['nrj', 'pwr', 'pac']),
            GenTest.types.elementOf(['sum', 'inv']),
        ], function(ymd, selectedVar, selectedSum) {
            var datum = {date: createDate(...ymd)};
            datum[selectedVar] = [];

            return createSolarData(...ymd).using([datum]).then(function(solarData) {
                expect(solarData.variable(selectedVar)).toBe(selectedVar);
                expect(solarData.aggregation()).toBe('sum');
                expect(solarData.aggregation(selectedSum)).toBe(selectedSum);
            });
        });
        it('should set aggregation (pdc)', [
            generators.any,
            GenTest.types.constantly('pdc'),
            GenTest.types.elementOf(['sum', 'inv', 'str']),
        ], function(ymd, selectedVar, selectedSum) {
            var datum = {date: createDate(...ymd)};
            datum[selectedVar] = [];

            return createSolarData(...ymd).using([datum]).then(function(solarData) {
                expect(solarData.variable(selectedVar)).toBe(selectedVar);
                expect(solarData.aggregation()).toBe('sum');
                expect(solarData.aggregation(selectedSum)).toBe(selectedSum);
            });
        });
        it('should set aggregation (uac, temp)', [
            generators.any,
            GenTest.types.elementOf(['uac', 'temp']),
            GenTest.types.constantly('inv'),
        ], function(ymd, selectedVar, selectedSum) {
            var datum = {date: createDate(...ymd)};
            datum[selectedVar] = [];

            return createSolarData(...ymd).using([datum]).then(function(solarData) {
                expect(solarData.variable(selectedVar)).toBe(selectedVar);
                expect(solarData.aggregation()).toBe('inv');
                expect(solarData.aggregation(selectedSum)).toBe(selectedSum);
            });
        });
        it('should set aggregation (udc)', [
            generators.any,
            GenTest.types.constantly('udc'),
            GenTest.types.constantly('str'),
        ], function(ymd, selectedVar, selectedSum) {
            var datum = {date: createDate(...ymd)};
            datum[selectedVar] = [];

            return createSolarData(...ymd).using([datum]).then(function(solarData) {
                expect(solarData.variable(selectedVar)).toEqual(selectedVar);
                expect(solarData.aggregation()).toBe('str');
                expect(solarData.aggregation(selectedSum)).toEqual(selectedSum);
            });
        });

        it('should not set aggregation (nrj, pwr, pac)', [
            generators.any,
            GenTest.types.elementOf(['nrj', 'pwr', 'pac']),
            GenTest.types.constantly('str'),
        ], function(ymd, selectedVar, selectedSum) {
            var datum = {date: createDate(...ymd)};
            datum[selectedVar] = [];

            return createSolarData(...ymd).using([datum]).then(function(solarData) {
                expect(solarData.variable(selectedVar)).toEqual(selectedVar);
                expect(solarData.aggregation()).toBe('sum');
                expect(solarData.aggregation(selectedSum)).not.toEqual(selectedSum);
                expect(solarData.aggregation()).toBe('sum');
            });
        });
        it('should not set aggregation (uac, temp)', [
            generators.any,
            GenTest.types.elementOf(['uac', 'temp']),
            GenTest.types.elementOf(['sum', 'str']),
        ], function(ymd, selectedVar, selectedSum) {
            var datum = {date: createDate(...ymd)};
            datum[selectedVar] = [];

            return createSolarData(...ymd).using([datum]).then(function(solarData) {
                expect(solarData.variable(selectedVar)).toEqual(selectedVar);
                expect(solarData.aggregation()).toBe('inv');
                expect(solarData.aggregation(selectedSum)).not.toEqual(selectedSum);
                expect(solarData.aggregation()).toBe('inv');
            });
        });
        it('should not set aggregation (udc)', [
            generators.any,
            GenTest.types.constantly('udc'),
            GenTest.types.elementOf(['sum', 'inv']),
        ], function(ymd, selectedVar, selectedSum) {
            var datum = {date: createDate(...ymd)};
            datum[selectedVar] = [];

            return createSolarData(...ymd).using([datum]).then(function(solarData) {
                expect(solarData.variable(selectedVar)).toEqual(selectedVar);
                expect(solarData.aggregation()).toBe('str');
                expect(solarData.aggregation(selectedSum)).not.toEqual(selectedSum);
                expect(solarData.aggregation()).toBe('str');
            });
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

                return createSolarData('', '', '').using(data).then(function(solarData) {
                    expect(solarData.variable('pdc')).toBe('pdc');
                    expect(solarData.aggregation('sum')).toBe('sum');

                    var exportData = solarData.export();
                    expect(exportData.headers).toEqual([['Date', 'Total']]);
                    expect(exportData.data).toEqual(expectedData);
                });
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

                return createSolarData('', '', '').using(data).then(function(solarData) {
                    expect(solarData.variable('pdc')).toBe('pdc');
                    expect(solarData.aggregation('sum')).toBe('sum');

                    var exportData = solarData.export();
                    console.log(exportData);
                    expect(exportData.headers).toEqual([['Date', 'Total']]);
                    expect(exportData.data).toEqual(expectedData);
                });
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

                return createSolarData('', '', '').using(data).then(function(solarData) {
                    expect(solarData.variable('pdc')).toBe('pdc');
                    expect(solarData.aggregation('inv')).toBe('inv');

                    var exportData = solarData.export();
                    console.log(exportData);
                    expect(exportData.headers).toEqual([['Date', 'Onduleur 1', 'Onduleur 2']]);
                    expect(exportData.data).toEqual(expectedData);
                });
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

                return createSolarData('', '', '').using(data).then(function(solarData) {
                    expect(solarData.variable('pdc')).toBe('pdc');
                    expect(solarData.aggregation('sum')).toBe('sum');

                    var exportData = solarData.export();
                    console.log(exportData);
                    expect(exportData.headers).toEqual([['Date', 'Total']]);
                    expect(exportData.data).toEqual(expectedData);
                });
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

                return createSolarData('', '', '').using(data).then(function(solarData) {
                    expect(solarData.variable('pdc')).toBe('pdc');
                    expect(solarData.aggregation('inv')).toBe('inv');

                    var exportData = solarData.export();
                    console.log(exportData);
                    expect(exportData.headers).toEqual([['Date', 'Onduleur 1', 'Onduleur 2']]);
                    expect(exportData.data).toEqual(expectedData);
                });
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

                return createSolarData('', '', '').using(data).then(function(solarData) {
                    expect(solarData.variable('pdc')).toBe('pdc');
                    expect(solarData.aggregation('str')).toBe('str');

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
        describe('line data', function() {
            it('1 column data, summed', [generators.lineData], function(data) {
                data.pdc = [[]];
                var expectedData = [];
                var dateFormatter = d3.timeFormat('%d/%m/%Y %H:%M');
                for (var i = 1; i <= data.dates.length; i++) {
                    data.pdc[0].unshift(Math.round(1000*Math.random()));
                    expectedData.unshift([dateFormatter(d3.isoParse(data.dates[data.dates.length - i])), data.pdc[0][0]]);
                }

                return createSolarData().using(data).then(function(solarData) {
                    expect(solarData.variable('pdc')).toBe('pdc');
                    expect(solarData.aggregation('sum')).toBe('sum');

                    var exportData = solarData.export();
                    console.log(exportData);
                    expect(exportData.headers).toEqual([['Date', 'Total']]);
                    expect(exportData.data).toEqual(expectedData);
                });
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

                return createSolarData().using(data).then(function(solarData) {
                    expect(solarData.variable('pdc')).toBe('pdc');
                    expect(solarData.aggregation('sum')).toBe('sum');

                    var exportData = solarData.export();
                    console.log(exportData);
                    expect(exportData.headers).toEqual([['Date', 'Total']]);
                    expect(exportData.data).toEqual(expectedData);
                });
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

                return createSolarData().using(data).then(function(solarData) {
                    expect(solarData.variable('pdc')).toBe('pdc');
                    expect(solarData.aggregation('inv')).toBe('inv');

                    var exportData = solarData.export();
                    console.log(exportData);
                    expect(exportData.headers).toEqual([['Date', 'Onduleur 1', 'Onduleur 2']]);
                    expect(exportData.data).toEqual(expectedData);
                });
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

                return createSolarData().using(data).then(function(solarData) {
                    expect(solarData.variable('pdc')).toBe('pdc');
                    expect(solarData.aggregation('sum')).toBe('sum');

                    var exportData = solarData.export();
                    console.log(exportData);
                    expect(exportData.headers).toEqual([['Date', 'Total']]);
                    expect(exportData.data).toEqual(expectedData);
                });
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

                return createSolarData().using(data).then(function(solarData) {
                    expect(solarData.variable('pdc')).toBe('pdc');
                    expect(solarData.aggregation('inv')).toBe('inv');

                    var exportData = solarData.export();
                    console.log(exportData);
                    expect(exportData.headers).toEqual([['Date', 'Onduleur 1', 'Onduleur 2']]);
                    expect(exportData.data).toEqual(expectedData);
                });
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

                return createSolarData().using(data).then(function(solarData) {
                    expect(solarData.variable('pdc')).toBe('pdc');
                    expect(solarData.aggregation('str')).toBe('str');

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
});
