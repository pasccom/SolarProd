# Copyright 2018 Pascal COMBES <pascom@orange.fr>
#
# This file is part of SolarProd.
#
# SolarProd is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SolarProd is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SolarProd. If not, see <http://www.gnu.org/licenses/>

import unittest

from math import floor
from datetime import datetime as datetime

from .PythonUtils.testdata import TestData

# Helper functions:
def formatDatum(datum):
    datum['date'] = datetime.strptime(datum['date'], '%Y-%m-%d')
    return datum

def formatTime(hours):
    h = floor(hours)
    m = floor(60 * (hours - h))
    s = floor(60 * (60 * (hours - h) - m))
    return '{:02}:{:02}:{:02}'.format(h, m, s)

def formatOrdinate(y):
    t = '{:.3f}'.format(y)
    while t.endswith('0'):
        t = t[:-1]
    if t.endswith('.'):
        t = t[:-1]
    if t == '-0':
        t = '0'
    return t

def interpolate(data, x):
    i = 0
    while (data[i][0] < x):
        i = i + 1

    return data[i - 1][1] + (data[i][1] - data[i - 1][1]) / (data[i][0] - data[i - 1][0]) * (x - data[i - 1][0])

def groupby(elemList, key=None):
    if key is None:
        key = lambda x: x
    keyList = []
    groupsList = []
    for e in elemList:
        k = key(e)
        try:
            i = keyList.index(k)
            groupsList[i] += [e]
        except (ValueError):
            keyList += [k]
            groupsList += [[e]]
    return groupsList

def recMin(data):
    try:
        return min(map(lambda x: recMin(x), data))
    except:
        return min(data)

def recMax(data):
    try:
        return max(map(lambda x: recMax(x), data))
    except:
        return max(data)

def mapSum(data):
    try:
        map(lambda *x: x, *data)
    except:
        return data

    try:
        return list(map(lambda *datum: sum(datum), *data))
    except:
        return mapSum(list(map(lambda datum: mapSum(datum), data)))

# Helper functions tests:
class HelpersTest(unittest.TestCase):
    @TestData([
        ['1970-01-01', 1970       ],
        ['1999-01-01', 1999       ],
        ['2000-01-01', 2000       ],
        ['2100-01-01', 2100       ],
        ['3000-01-01', 3000       ],
        ['2019-02-01', 2019, 2    ],
        ['2019-07-01', 2019, 7    ],
        ['2019-12-01', 2019, 12   ],
        ['2019-02-02', 2019, 2, 2 ],
        ['2019-02-28', 2019, 2, 28],
        ['2020-02-29', 2020, 2, 29],
        ['2000-02-29', 2000, 2, 29],
        ['2019-06-02', 2019, 6, 2 ],
        ['2019-06-30', 2019, 6, 30],
        ['2019-08-02', 2019, 8, 2 ],
        ['2019-08-31', 2019, 8, 31],
    ])
    def testFormatDatum(self, dateStr, year, month=1, day=1):
        datum = {'date': dateStr}
        datum = formatDatum(datum)
        self.assertEqual(datum['date'].year,  year)
        self.assertEqual(datum['date'].month, month)
        self.assertEqual(datum['date'].day,   day)

    @TestData([
        [ 0,       '00:00:00'],
        [ 0.00028, '00:00:01'],
        [ 0.01667, '00:01:00'],
        [ 1,       '01:00:00'],
        [ 1.01,    '01:00:36'],
        [ 1.1,     '01:06:00'],
        [ 6.5,     '06:30:00'],
        [ 9.9,     '09:54:00'],
        [ 9.99,    '09:59:24'],
        [12,       '12:00:00'],
        [23,       '23:00:00'],
        [23.98334, '23:59:00'],
        [23.99973, '23:59:59'],
    ])
    def testFormatTime(self, time, timeStr):
        self.assertEqual(formatTime(time), timeStr)

    @TestData([
        [-1000,    '-1000'    ],
        [ -999.999, '-999.999'],
        [ -999.99,  '-999.99' ],
        [ -999.9,   '-999.9'  ],
        [ -999,     '-999'    ],
        [ -100.001, '-100.001'],
        [ -100.01,  '-100.01' ],
        [ -100.1,   '-100.1'  ],
        [ -100,     '-100'    ],
        [  -10.001,  '-10.001'],
        [  -10.01,   '-10.01' ],
        [  -10.1,    '-10.1'  ],
        [  -10,      '-10'    ],
        [   -1.001,   '-1.001'],
        [   -1.01,    '-1.01' ],
        [   -1.1,     '-1.1'  ],
        [   -1,       '-1'    ],
        [   -1e-1,    '-0.1'  ],
        [   -1e-2,    '-0.01' ],
        [   -1e-3,    '-0.001'],
        [   -1e-4,     '0'    ],
        [    0,        '0'    ],
        [    1e-4,     '0'    ],
        [    1e-3,     '0.001'],
        [    1e-2,     '0.01' ],
        [    1e-1,     '0.1'  ],
        [    1,        '1'    ],
        [    1.001,    '1.001'],
        [    1.01,     '1.01' ],
        [    1.1,      '1.1'  ],
        [   10,       '10'    ],
        [   10.001,   '10.001'],
        [   10.01,    '10.01' ],
        [   10.1,     '10.1'  ],
        [  100,      '100'    ],
        [  100.001,  '100.001'],
        [  100.01,   '100.01' ],
        [  100.1,    '100.1'  ],
        [  999,      '999'    ],
        [  999.999,  '999.999'],
        [  999.99,   '999.99' ],
        [  999.9,    '999.9'  ],
        [ 1000,     '1000'    ],
    ])
    def testFormatOrdinate(self, value, valueStr):
        self.assertEqual(formatOrdinate(value), valueStr)

    @TestData([
        [[(1, 18), (2, 36)], 1, 18],
        [[(1, 18), (2, 36)], 4/3, 24],
        [[(1, 18), (2, 36)], 1.5, 27],
        [[(1, 18), (2, 36)], 5/3, 30],
        [[(1, 18), (2, 36)], 2, 36],
    ])
    def testInterpolate2(self, coords, x, y):
        self.assertAlmostEqual(interpolate(coords, x), y)
    @TestData([
        [[(1, 18), (2, 36), (4, 54)], 1,    18],
        [[(1, 18), (2, 36), (4, 54)], 4/3,  24],
        [[(1, 18), (2, 36), (4, 54)], 1.5,  27],
        [[(1, 18), (2, 36), (4, 54)], 5/3,  30],
        [[(1, 18), (2, 36), (4, 54)], 2,    36],
        [[(1, 18), (2, 36), (4, 54)], 8/3,  42],
        [[(1, 18), (2, 36), (4, 54)], 3,    45],
        [[(1, 18), (2, 36), (4, 54)], 10/3, 48],
        [[(1, 18), (2, 36), (4, 54)], 4,    54],
    ])
    def testInterpolate3(self, coords, x, y):
        self.assertAlmostEqual(interpolate(coords, x), y)

    def testGroupBy0(self):
        self.assertEqual(groupby([]), [])
    def testGroupBy1(self):
        self.assertEqual(groupby([1]), [[1]])
    def testGroupBy2(self):
        self.assertEqual(groupby([1, 2]), [[1], [2]])
    def testGroupBy3(self):
        self.assertEqual(groupby([1, 2, 1]), [[1, 1], [2]])
    def testGroupByKey3(self):
        self.assertEqual(groupby([1, 2, 3], key=lambda x: x % 2), [[1, 3], [2]])
    def testGroupByKey4(self):
        self.assertEqual(groupby([1, 2, 3, 4], key=lambda x: x % 2), [[1, 3], [2, 4]])

    def testMapSum0(self):
        self.assertEqual(mapSum([1]), [1])
    def testMapSum1(self):
        self.assertEqual(mapSum([1, 2, 3]), [1, 2, 3])
    def testMapSum2(self):
        self.assertEqual(mapSum([[1, 2, 3], [6, 5, 4]]), [7, 7, 7])
    def testMapSum3(self):
        self.assertEqual(mapSum([[[1, 2, 3], [6, 5, 4]], [[9, 8, 7], [4, 5, 6]]]), [20, 20, 20])
    def testMapSum4(self):
        self.assertEqual(mapSum([[[[1, 2, 3], [6, 5, 4]], [[9, 8, 7], [4, 5, 6]]],
                                 [[[1, 2, 3], [6, 5, 4]], [[9, 8, 7], [4, 5, 6]]]]), [40, 40, 40])

    def testRecMin0(self):
        self.assertEqual(recMin([1]), 1)
    def testRecMin1(self):
        self.assertEqual(recMin([4, 5, 6]), 4)
    def testRecMin2(self):
        self.assertEqual(recMin([[1, 2, 3], [6, 5, 4]]), 1)
    def testRecMin3(self):
        self.assertEqual(recMin([[[1, 2, 3], [6, 5, 4]], [[9, 8, 7], [4, 5, 6]]]), 1)
    def testRecMin4(self):
        self.assertEqual(recMin([[[[1, 2, 3], [6, 5, 4]], [[9, 8, 7], [4, 5, 6]]],
                                 [[[1, 2, 3], [6, 5, 4]], [[9, 8, 7], [4, 5, 6]]]]), 1)

    def testRecMax0(self):
        self.assertEqual(recMax([1]), 1)
    def testRecMax1(self):
        self.assertEqual(recMax([1, 2, 3]), 3)
    def testRecMax2(self):
        self.assertEqual(recMax([[1, 2, 3], [6, 5, 4]]), 6)
    def testRecMax3(self):
        self.assertEqual(recMax([[[1, 2, 3], [6, 5, 4]], [[9, 8, 7], [4, 5, 6]]]), 9)
    def testRecMax4(self):
        self.assertEqual(recMax([[[[1, 2, 3], [6, 5, 4]], [[9, 8, 7], [4, 5, 6]]],
                                 [[[1, 2, 3], [6, 5, 4]], [[9, 8, 7], [4, 5, 6]]]]), 9)

if __name__ == '__main__':
    unittest.main(verbosity=2)
