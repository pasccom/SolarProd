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
# along with SolarProd. If not, see <http://www.gnu.org/licenses/

import json

from .PythonUtils.testdata import TestData

from .browser_testcase import BrowserTestCase

class SelectTest(BrowserTestCase):
    def testYears(self):
        select = self.browser.find_element_by_id('year')

        with open(self.listPath(), 'r') as jsonFile:
            expected = json.load(jsonFile)
        expected = [''] + [str(y) for y in expected]

        self.assertEqual([o.text for o in self.waitOptions(select, 5)], expected)
        self.assertTrue(select.is_enabled())
        self.assertEqual(select.get_property('value'), '')

    @TestData([
        {'year': 2009},
        {'year': 2010},
        {'year': 2011},
        {'year': 2014},
        {'year': 2017},
        {'year': 2018},
        {'year': 2019},
    ])
    def testMonths(self, year):
        self.selectDate(year)
        select = self.browser.find_element_by_id('month')

        try:
            with open(self.listPath(year), 'r') as jsonFile:
                expected = json.load(jsonFile)
            expected = [''] + [self.monthName(m) for m in expected]

            self.assertEqual([o.text for o in self.waitOptions(select, 5)], expected)
            self.assertTrue(select.is_enabled())
            self.assertEqual(select.get_property('value'), '')
        except (FileNotFoundError):
            with self.assertRaises(RuntimeError):
                self.waitOptions(select, 5)
            self.assertFalse(select.is_enabled())

    @TestData([
        {'year': 2010, 'month': 12},
        {'year': 2011, 'month': 6 },
        {'year': 2011, 'month': 9 },
        {'year': 2011, 'month': 12},
        {'year': 2017, 'month': 2 },
        {'year': 2017, 'month': 5 },
        {'year': 2017, 'month': 8 },
        {'year': 2018, 'month': 2 },
    ])
    def testDays(self, year, month, expected=None):
        self.selectDate(year, month)
        select = self.browser.find_element_by_id('day')

        try:
            with open(self.listPath(year, month), 'r') as jsonFile:
                expected = json.load(jsonFile)
            expected = [''] + [str(d) for d in expected]

            self.assertEqual([o.text for o in self.waitOptions(select, 5)], expected)
            self.assertTrue(select.is_enabled())
            self.assertEqual(select.get_property('value'), '')
        except (FileNotFoundError):
            with self.assertRaises(RuntimeError):
                self.waitOptions(select, 5)
            self.assertFalse(select.is_enabled())

    @TestData([
        {'year': None, 'month': None, 'day': None, 'expected': set(['Énergie'])                                                             },
        {'year': 2017, 'month': None, 'day': None, 'expected': set(['Énergie'])                                                             },
        {'year': 2017, 'month': 8,    'day': None, 'expected': set(['Énergie', 'Puissance'])                                                },
        {'year': 2017, 'month': 8,    'day': 8,    'expected': set(['Énergie', 'Puissance AC', 'Puissance DC', 'Tension DC', 'Température'])},
    ])
    def testVar(self, year, month, day, expected):
        self.selectDate(year, month, day)
        self.plot()

        select = self.browser.find_element_by_id('var')
        options = [o.text for o in self.waitOptions(select, 5)]

        self.assertEqual(set(options), expected)
        self.assertEqual(select.is_enabled(), len(expected) > 0)

    @TestData([
        {'year': 2017, 'month': 8,    'day': 5},
    ])
    def testEmptyVar(self, year, month, day):
        self.selectDate(year, month, day)
        self.plot()

        select = self.browser.find_element_by_id('var')
        self.assertFalse(select.is_enabled())

        with self.assertRaises(RuntimeError):
            self.waitOptions(select, 10)

    @TestData([
        {'year': None, 'month': None, 'day': None, 'var': 'nrj',  'expected': set(['Total', 'Par onduleur'])              },
        {'year': 2017, 'month': None, 'day': None, 'var': 'nrj',  'expected': set(['Total', 'Par onduleur'])              },
        {'year': 2017, 'month': 8,    'day': None, 'var': 'nrj',  'expected': set(['Total', 'Par onduleur'])              },
        {'year': 2017, 'month': 8,    'day': None, 'var': 'pwr',  'expected': set(['Total', 'Par onduleur'])              },
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'nrj',  'expected': set(['Total', 'Par onduleur'])              },
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pac',  'expected': set(['Total', 'Par onduleur'])              },
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pdc',  'expected': set(['Total', 'Par onduleur', 'Par string'])},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'udc',  'expected': set(['Par string'])                         },
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'temp', 'expected': set(['Par onduleur'])                       },
    ])
    def testSum(self, year, month, day, var, expected):
        self.selectDate(year, month, day)
        self.plot()
        self.selectVar(var)

        select = self.browser.find_element_by_id('sum')
        options = [o.text for o in self.waitOptions(select, 5)]

        self.assertEqual(set(options), expected)
        self.assertEqual(select.is_enabled(), len(expected) > 1)

    @TestData([
        {'year': 2017, 'month': 8,    'day': 5},
    ])
    def testEmptySum(self, year, month, day):
        self.selectDate(year, month, day)
        self.plot()

        select = self.browser.find_element_by_id('sum')
        self.assertFalse(select.is_enabled())

        with self.assertRaises(RuntimeError):
            self.waitOptions(select, 10)

    def testToday(self):
        self.browser.find_element_by_id('today').click()

        year = self.browser.find_element_by_id('year')
        self.assertTrue(year.is_enabled())
        self.assertEqual(year.get_property('value'), '2017')

        month = self.browser.find_element_by_id('month')
        self.assertTrue(month.is_enabled())
        self.assertEqual(month.get_property('value'), '8')

        day = self.browser.find_element_by_id('day')
        self.waitOptions(day, 5)
        self.assertTrue(day.is_enabled())
        self.assertEqual(day.get_property('value'), '8')

        var = self.browser.find_element_by_id('var')
        self.assertTrue(var.is_enabled())

        aggr = self.browser.find_element_by_id('sum')
        self.assertTrue(aggr.is_enabled())
