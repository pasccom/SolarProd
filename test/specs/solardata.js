describe('Helpers ', function() {
    describe('pad() ', function() {
        it('should return a string', [
            GenTest.types.oneOf([GenTest.types.int.nonNegative]),//, GenTest.types.string]),
            GenTest.types.int.nonNegative,
            GenTest.types.constantly('0'),
        ], function(n, l, p) {
            console.log(n);
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
    describe('type', function() {
        it('should be of type ALL', function() {
            var solarData = SolarData.create([], '', '', '');
            expect(solarData.type).toBe(SolarData.Type.ALL);
        });
        it('should be of type YEAR', [
            GenTest.types.oneOf([GenTest.types.choose(0, 9999), GenTest.types.fmap((year) => pad(year, 4, '0'), GenTest.types.choose(0, 9999))]),
        ], function(year) {
            var solarData = SolarData.create([], year, '', '');
            expect(solarData.type).toBe(SolarData.Type.YEAR);
        });
        it('should be of type MONTH', [
            GenTest.types.oneOf([GenTest.types.choose(0, 9999), GenTest.types.fmap((year) => pad(year, 4, '0'), GenTest.types.choose(0, 9999))]),
            GenTest.types.oneOf([GenTest.types.choose(1, 12), GenTest.types.fmap((month) => pad(month, 2, '0'), GenTest.types.choose(1, 12))]),
        ], function(year, month) {
            var solarData = SolarData.create([], year, month, '');
            expect(solarData.type).toBe(SolarData.Type.MONTH);
        });
        it('should be of type DAY', [
            GenTest.types.oneOf([GenTest.types.choose(0, 9999), GenTest.types.fmap((year) => pad(year, 4, '0'), GenTest.types.choose(0, 9999))]),
            GenTest.types.oneOf([GenTest.types.choose(1, 12), GenTest.types.fmap((month) => pad(month, 2, '0'), GenTest.types.choose(1, 12))]),
            GenTest.types.oneOf([GenTest.types.choose(1, 31), GenTest.types.fmap((day) => pad(day, 2, '0'), GenTest.types.choose(1, 31))]),
        ], function(year, month, day) {
            var solarData = SolarData.create([], year, month, day);
            expect(solarData.type).toBe(SolarData.Type.DAY);
        });
        /* TODO need a date generator based on given format
        it('should be of type DAY', [
            GenTest.types.oneOf([
                GenTest.types.arrayOf(GenTest.types.shape({date: GenTest.types.date('%Y-%m-%d')})),
                GenTest.types.shape({dates: GenTest.types.arrayOf(GenTest.types.date('%Y-%m-%d %H:%M'))}),
            ])
        ],function(data) {
            var solarData = SolarData.create(data);
            expect(solarData.type).toBe(SolarData.Type.DAY);
        });*/
    });
    describe('xLabel', function() {
        it('should be of "Année"', function() {
            var solarData = SolarData.create([], '', '', '');
            expect(solarData.xLabel).toBe('Année');
        });
        it('should be of type "Mois"', [
            GenTest.types.oneOf([GenTest.types.choose(0, 9999), GenTest.types.fmap((year) => pad(year, 4, '0'), GenTest.types.choose(0, 9999))]),
        ], function(year) {
            var solarData = SolarData.create([], year, '', '');
            expect(solarData.xLabel).toBe('Mois');
        });
        it('should be of type "Jour"', [
            GenTest.types.oneOf([GenTest.types.choose(0, 9999), GenTest.types.fmap((year) => pad(year, 4, '0'), GenTest.types.choose(0, 9999))]),
            GenTest.types.oneOf([GenTest.types.choose(1, 12), GenTest.types.fmap((month) => pad(month, 2, '0'), GenTest.types.choose(1, 12))]),
        ], function(year, month) {
            var solarData = SolarData.create([], year, month, '');
            expect(solarData.xLabel).toBe('Jour');
        });
        it('should be of type "Temps (h)"', [
            GenTest.types.oneOf([GenTest.types.choose(0, 9999), GenTest.types.fmap((year) => pad(year, 4, '0'), GenTest.types.choose(0, 9999))]),
            GenTest.types.oneOf([GenTest.types.choose(1, 12), GenTest.types.fmap((month) => pad(month, 2, '0'), GenTest.types.choose(1, 12))]),
            GenTest.types.oneOf([GenTest.types.choose(1, 31), GenTest.types.fmap((day) => pad(day, 2, '0'), GenTest.types.choose(1, 31))]),
        ], function(year, month, day) {
            var solarData = SolarData.create([], year, month, day);
            expect(solarData.xLabel).toBe('Temps (h)');
        });
        /* TODO need a date generator based on given format
        it('should be of type "Temps (h)"', [
            GenTest.types.oneOf([
                GenTest.types.arrayOf(GenTest.types.shape({date: GenTest.types.date('%Y-%m-%d')})),
                GenTest.types.shape({dates: GenTest.types.arrayOf(GenTest.types.date('%Y-%m-%d %H:%M'))}),
            ])
        ],function(data) {
            var solarData = SolarData.create(data);
            expect(solarData.xLabel).toBe('Temps (h)');
        });*/
    });
    // TODO date parser
    // TODO date formatter
    describe('dateString', function() {
        it('should be empty', function() {
            var solarData = SolarData.create([], '', '', '');
            expect(solarData.dateString).toBe('');
        });
        it('should be "%Y"', [
            GenTest.types.oneOf([GenTest.types.choose(0, 9999), GenTest.types.fmap((year) => pad(year, 4, '0'), GenTest.types.choose(0, 9999))]),
        ], function(year) {
            var solarData = SolarData.create([], year, '', '');
            expect(solarData.dateString).toBe(pad(year, 4, '0'));
        });
        it('should be "%m-%Y"', [
            GenTest.types.oneOf([GenTest.types.choose(0, 9999), GenTest.types.fmap((year) => pad(year, 4, '0'), GenTest.types.choose(0, 9999))]),
            GenTest.types.oneOf([GenTest.types.choose(1, 12), GenTest.types.fmap((month) => pad(month, 2, '0'), GenTest.types.choose(1, 12))]),
        ], function(year, month) {
            var solarData = SolarData.create([], year, month, '');
            expect(solarData.dateString).toBe(pad(month, 2, '0') + '-' + pad(year, 4, '0'));
        });
        it('should be "%d-%m-%Y"', [
            GenTest.types.oneOf([GenTest.types.choose(0, 9999), GenTest.types.fmap((year) => pad(year, 4, '0'), GenTest.types.choose(0, 9999))]),
            GenTest.types.oneOf([GenTest.types.choose(1, 12), GenTest.types.fmap((month) => pad(month, 2, '0'), GenTest.types.choose(1, 12))]),
            GenTest.types.oneOf([GenTest.types.choose(1, 31), GenTest.types.fmap((day) => pad(day, 2, '0'), GenTest.types.choose(1, 31))]),
        ], function(year, month, day) {
            var solarData = SolarData.create([], year, month, day);
            expect(solarData.dateString).toBe(pad(day, 2, '0') + '-' + pad(month, 2, '0') + '-' + pad(year, 4, '0'));
        });
        // TODO today
    });
    describe('axes and scales', function() {
        it('X scale should be X axis scale, Y scale should be Y axis scale', GenTest.types.oneOf([
            GenTest.types.tuple([
                GenTest.types.constantly(''),
                GenTest.types.constantly(''),
                GenTest.types.constantly(''),
            ]),
            GenTest.types.tuple([
                GenTest.types.oneOf([GenTest.types.choose(0, 9999), GenTest.types.fmap((year) => pad(year, 4, '0'), GenTest.types.choose(0, 9999))]),
                GenTest.types.constantly(''),
                GenTest.types.constantly(''),
            ]),
            GenTest.types.tuple([
                GenTest.types.oneOf([GenTest.types.choose(0, 9999), GenTest.types.fmap((year) => pad(year, 4, '0'), GenTest.types.choose(0, 9999))]),
                GenTest.types.oneOf([GenTest.types.choose(1, 12), GenTest.types.fmap((month) => pad(month, 2, '0'), GenTest.types.choose(1, 12))]),
                GenTest.types.constantly(''),
            ]),
            GenTest.types.tuple([
                GenTest.types.oneOf([GenTest.types.choose(0, 9999), GenTest.types.fmap((year) => pad(year, 4, '0'), GenTest.types.choose(0, 9999))]),
                GenTest.types.oneOf([GenTest.types.choose(1, 12), GenTest.types.fmap((month) => pad(month, 2, '0'), GenTest.types.choose(1, 12))]),
                GenTest.types.oneOf([GenTest.types.choose(1, 31), GenTest.types.fmap((day) => pad(day, 2, '0'), GenTest.types.choose(1, 31))]),
            ]),
        ]), function(year, month, day) {
            var solarData = new SolarData.create([], year, month, day);
            expect(solarData.xAxis.scale()).toBe(solarData.xScale);
            expect(solarData.yAxis.scale()).toBe(solarData.yScale);
            expect(solarData.yGrid.scale()).toBe(solarData.yScale);
        });
        // TODO today
    });
});
