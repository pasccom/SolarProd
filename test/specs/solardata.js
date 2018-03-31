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
