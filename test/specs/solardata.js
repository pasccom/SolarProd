describe('Helpers ', function() {
    describe('pad() ', function() {
        it('should return a string', function() {
            expect(pad(0, 1, '0')).toBe('0');
            expect(pad('0', 1, '0')).toBe('0');
        });
        it('should return the number itself', function() {
            expect(pad(1, 1, '0')).toBe('1');
            expect(pad(11, 1, '0')).toBe('11');
            expect(pad(11, 2, '0')).toBe('11');
            expect(pad(111, 2, '0')).toBe('111');
        });
        it('should return a string of length l', function() {
            expect(pad(1, 1, '0').length).toBe(1);
            expect(pad(1, 2, '0').length).toBe(2);
            expect(pad(1, 3, '0').length).toBe(3);
        });
        it('should return a string of length larger or equal to l', function() {
            expect(pad(1, 1, '00').length).toBeGreaterThanOrEqual(1);
            expect(pad(1, 2, '00').length).toBeGreaterThanOrEqual(2);
            expect(pad(1, 3, '00').length).toBeGreaterThanOrEqual(3);
        });
        it('should start with p and end with n', function() {
            expect(pad(1, 1, '0')).toMatch('^0*1$');
            expect(pad(1, 2, '0')).toMatch('^0*1$');
            expect(pad(1, 3, '0')).toMatch('^0*1$');
            expect(pad(11, 1, '0')).toMatch('^0*11$');
            expect(pad(11, 2, '0')).toMatch('^0*11$');
            expect(pad(11, 3, '0')).toMatch('^0*11$');
            expect(pad(1, 1, ' ')).toMatch('^ *1$');
            expect(pad(1, 2, ' ')).toMatch('^ *1$');
            expect(pad(1, 3, ' ')).toMatch('^ *1$');
            expect(pad(1, 1, '0 ')).toMatch('^(0 )*1$');
            expect(pad(1, 2, '0 ')).toMatch('^(0 )*1$');
            expect(pad(1, 3, '0 ')).toMatch('^(0 )*1$');
        });
        it('should be parsed as the initial int', function() {
            expect(parseInt(pad(0, 1, '0'))).toBe(0);
            expect(parseInt(pad(0, 2, '0'))).toBe(0);
            expect(parseInt(pad(0, 3, '0'))).toBe(0);
            expect(parseInt(pad(0, 1, ' '))).toBe(0);
            expect(parseInt(pad(0, 2, ' '))).toBe(0);
            expect(parseInt(pad(0, 3, ' '))).toBe(0);
            expect(parseInt(pad(1, 1, '0'))).toBe(1);
            expect(parseInt(pad(1, 2, '0'))).toBe(1);
            expect(parseInt(pad(1, 3, '0'))).toBe(1);
            expect(parseInt(pad(1, 1, ' '))).toBe(1);
            expect(parseInt(pad(1, 2, ' '))).toBe(1);
            expect(parseInt(pad(1, 3, ' '))).toBe(1);
        });
        it('should throw when called with empty string', function() {
            expect(() => pad(0, 1, '')).toThrowError(RangeError, 'p should not be empty');
            expect(() => pad(1, 1, '')).toThrowError(RangeError, 'p should not be empty');
            expect(() => pad(0, 2, '')).toThrowError(RangeError, 'p should not be empty');
        });
    });
});
