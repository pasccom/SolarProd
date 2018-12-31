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

from datetime import datetime as datetime

# Helper functions:
def formatDatum(datum):
    datum['date'] = datetime.strptime(datum['date'], '%Y-%m-%d')
    return datum

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
