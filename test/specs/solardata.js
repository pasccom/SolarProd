types.numericString = types.fmap(
    (chars) => chars.join(''),
    types.arrayOf(types.elements('0123456789'.split()))
);

types.lowercaseString = types.fmap(
    (chars) => chars.join(''),
    types.arrayOf(types.elements('abcdefghijklmnopqrstuvwxyz'.split()))
);

types.uppercaseString = types.fmap(
    (chars) => chars.join(''),
    types.arrayOf(types.elements('ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split()))
);

types.alphaString = types.fmap(
    (chars) => chars.join(''),
    types.arrayOf(types.elements('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'.split()))
);

types.alphaNumericString = types.fmap(
    (chars) => chars.join(''),
    types.arrayOf(types.elements('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'.split()))
);

describe('Helpers ', function() {
    describe('pad() ', function() {
        it('should return a string', [
            types.oneOf([types.int.nonNegative, types.string]),
            types.int.nonNegative,
            types.constantly('0'),
        ], function(n, l, p) {
            expect(typeof pad(n, l, p)).toBe('string');
        });
        it('should return a string of length larger or equal to l', [
            types.oneOf([types.int.nonNegative, types.string]),
            types.int.nonNegative,
            types.elements(['0', ' ', ' 0']),
        ], function(n, l, p) {
            expect(pad(n, l, p).length).toBeGreaterThanOrEqual(l);
        });
        it('should start with p and end with n', [
            types.oneOf([types.int.nonNegative, types.alphaNumericString]),
            types.int.nonNegative,
            types.elements(['0', ' ', ' 0']),
        ], function(n, l, p) {
            expect(pad(n, l, p)).toMatch('^(' + p + ')*' + n + '$');
        });

        it('should be parsed as the initial int', [
            types.int.nonNegative,
            types.int.nonNegative,
            types.constantly('0', ' ', '00', '  '),
        ], function(n, l, p) {
            expect(parseInt(pad(n, l, p))).toBe(n);
        });
        it('should throw when called with empty string', [
            types.oneOf([types.int.nonNegative, types.string]),
            types.int.nonNegative,
            types.constantly(''),
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
            types.oneOf([types.choose(0, 9999), types.fmap((year) => pad(year, 4, '0'), types.choose(0, 9999))]),
        ], function(year) {
            var solarData = SolarData.create([], year, '', '');
            expect(solarData.type).toBe(SolarData.Type.YEAR);
        });
        it('should be of type MONTH', [
            types.oneOf([types.choose(0, 9999), types.fmap((year) => pad(year, 4, '0'), types.choose(0, 9999))]),
            types.oneOf([types.choose(1, 12), types.fmap((month) => pad(month, 2, '0'), types.choose(1, 12))]),
        ], function(year, month) {
            var solarData = SolarData.create([], year, month, '');
            expect(solarData.type).toBe(SolarData.Type.MONTH);
        });
        it('should be of type DAY', [
            types.oneOf([types.choose(0, 9999), types.fmap((year) => pad(year, 4, '0'), types.choose(0, 9999))]),
            types.oneOf([types.choose(1, 12), types.fmap((month) => pad(month, 2, '0'), types.choose(1, 12))]),
            types.oneOf([types.choose(1, 31), types.fmap((day) => pad(day, 2, '0'), types.choose(1, 31))]),
        ], function(year, month, day) {
            var solarData = SolarData.create([], year, month, day);
            expect(solarData.type).toBe(SolarData.Type.DAY);
        });
        /* TODO need a date generator based on given format
        it('should be of type DAY', [
            types.oneOf([
                types.arrayOf(types.shape({date: types.date('%Y-%m-%d')})),
                types.shape({dates: types.arrayOf(types.date('%Y-%m-%d %H:%M'))}),
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
            types.oneOf([types.choose(0, 9999), types.fmap((year) => pad(year, 4, '0'), types.choose(0, 9999))]),
        ], function(year) {
            var solarData = SolarData.create([], year, '', '');
            expect(solarData.xLabel).toBe('Mois');
        });
        it('should be of type "Jour"', [
            types.oneOf([types.choose(0, 9999), types.fmap((year) => pad(year, 4, '0'), types.choose(0, 9999))]),
            types.oneOf([types.choose(1, 12), types.fmap((month) => pad(month, 2, '0'), types.choose(1, 12))]),
        ], function(year, month) {
            var solarData = SolarData.create([], year, month, '');
            expect(solarData.xLabel).toBe('Jour');
        });
        it('should be of type "Temps (h)"', [
            types.oneOf([types.choose(0, 9999), types.fmap((year) => pad(year, 4, '0'), types.choose(0, 9999))]),
            types.oneOf([types.choose(1, 12), types.fmap((month) => pad(month, 2, '0'), types.choose(1, 12))]),
            types.oneOf([types.choose(1, 31), types.fmap((day) => pad(day, 2, '0'), types.choose(1, 31))]),
        ], function(year, month, day) {
            var solarData = SolarData.create([], year, month, day);
            expect(solarData.xLabel).toBe('Temps (h)');
        });
        /* TODO need a date generator based on given format
        it('should be of type "Temps (h)"', [
            types.oneOf([
                types.arrayOf(types.shape({date: types.date('%Y-%m-%d')})),
                types.shape({dates: types.arrayOf(types.date('%Y-%m-%d %H:%M'))}),
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
            types.oneOf([types.choose(0, 9999), types.fmap((year) => pad(year, 4, '0'), types.choose(0, 9999))]),
        ], function(year) {
            var solarData = SolarData.create([], year, '', '');
            expect(solarData.dateString).toBe(pad(year, 4, '0'));
        });
        it('should be "%m-%Y"', [
            types.oneOf([types.choose(0, 9999), types.fmap((year) => pad(year, 4, '0'), types.choose(0, 9999))]),
            types.oneOf([types.choose(1, 12), types.fmap((month) => pad(month, 2, '0'), types.choose(1, 12))]),
        ], function(year, month) {
            var solarData = SolarData.create([], year, month, '');
            expect(solarData.dateString).toBe(pad(month, 2, '0') + '-' + pad(year, 4, '0'));
        });
        it('should be "%d-%m-%Y"', [
            types.oneOf([types.choose(0, 9999), types.fmap((year) => pad(year, 4, '0'), types.choose(0, 9999))]),
            types.oneOf([types.choose(1, 12), types.fmap((month) => pad(month, 2, '0'), types.choose(1, 12))]),
            types.oneOf([types.choose(1, 31), types.fmap((day) => pad(day, 2, '0'), types.choose(1, 31))]),
        ], function(year, month, day) {
            var solarData = SolarData.create([], year, month, day);
            expect(solarData.dateString).toBe(pad(day, 2, '0') + '-' + pad(month, 2, '0') + '-' + pad(year, 4, '0'));
        });
        // TODO today
    });
    describe('axes and scales', function() {
        it('X scale should be X axis scale, Y scale should be Y axis scale', types.oneOf([
            types.tuple([
                types.constantly(''),
                types.constantly(''),
                types.constantly(''),
            ]),
            types.tuple([
                types.oneOf([types.choose(0, 9999), types.fmap((year) => pad(year, 4, '0'), types.choose(0, 9999))]),
                types.constantly(''),
                types.constantly(''),
            ]),
            types.tuple([
                types.oneOf([types.choose(0, 9999), types.fmap((year) => pad(year, 4, '0'), types.choose(0, 9999))]),
                types.oneOf([types.choose(1, 12), types.fmap((month) => pad(month, 2, '0'), types.choose(1, 12))]),
                types.constantly(''),
            ]),
            types.tuple([
                types.oneOf([types.choose(0, 9999), types.fmap((year) => pad(year, 4, '0'), types.choose(0, 9999))]),
                types.oneOf([types.choose(1, 12), types.fmap((month) => pad(month, 2, '0'), types.choose(1, 12))]),
                types.oneOf([types.choose(1, 31), types.fmap((day) => pad(day, 2, '0'), types.choose(1, 31))]),
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
