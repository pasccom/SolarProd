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

from .PythonUtils.testdata import TestData

from .browser_testcase import BrowserTestCase

class ParentTest(BrowserTestCase):
    def testEmpty(self):
        parentButton = self.browser.find_element_by_id('up')

        self.assertDate()
        self.assertClassed(parentButton, 'disabled', True)

    @BrowserTestCase.cacheTest
    def testAllYears(self):
        self.selectDate()
        self.plot()

        parentButton = self.browser.find_element_by_id('up')

        self.assertDate()
        self.assertClassed(parentButton, 'disabled', True)

    @TestData([
        {'year': 2009},
        {'year': 2014},
        {'year': 2019},
    ])
    def testYears(self, year):
        parentButton = self.browser.find_element_by_id('up')

        self.selectDate(year)
        self.assertTitle(parentButton, "Afficher toutes les années")
        self.plotParent()

        self.assertDate()
        self.assertClassed(parentButton, 'disabled', True)
        self.assertTitle(parentButton, '')

    @TestData([
        {'year': 2010, 'month': 12},
        {'year': 2011, 'month':  8},
        {'year': 2017, 'month':  8},
        {'year': 2018, 'month':  2},
    ])
    def testYear(self, year, month):
        parentButton = self.browser.find_element_by_id('up')

        self.selectDate(year, month)
        self.assertTitle(parentButton, "Afficher toute l'année")
        self.plotParent()

        self.assertDate(year)
        self.assertClassed(parentButton, 'disabled', False)
        self.assertTitle(parentButton, "Afficher toutes les années")

    @TestData([
        {'year': 2011, 'month':  6, 'day': 24},
        {'year': 2011, 'month': 12, 'day': 31},
        {'year': 2017, 'month':  2, 'day':  1},
        {'year': 2017, 'month':  8, 'day':  8},
    ])
    def testMonth(self, year, month, day):
        parentButton = self.browser.find_element_by_id('up')

        self.selectDate(year, month, day)
        self.assertTitle(parentButton, "Afficher tout le mois")
        self.plotParent()

        self.assertDate(year, month)
        self.assertClassed(parentButton, 'disabled', False)
        self.assertTitle(parentButton, "Afficher toute l'année")

    @TestData([
        {'year': 2009, 'month': None, 'day': None, 'var': 'nrj', 'agg': 'sum'},
        {'year': 2009, 'month': None, 'day': None, 'var': 'nrj', 'agg': 'inv'},
        {'year': 2014, 'month': None, 'day': None, 'var': 'nrj', 'agg': 'sum'},
        {'year': 2014, 'month': None, 'day': None, 'var': 'nrj', 'agg': 'inv'},
        {'year': 2019, 'month': None, 'day': None, 'var': 'nrj', 'agg': 'sum'},
        {'year': 2019, 'month': None, 'day': None, 'var': 'nrj', 'agg': 'inv'},
        {'year': 2010, 'month':   12, 'day': None, 'var': 'nrj', 'agg': 'sum'},
        {'year': 2010, 'month':   12, 'day': None, 'var': 'nrj', 'agg': 'inv'},
        {'year': 2011, 'month':    8, 'day': None, 'var': 'nrj', 'agg': 'sum'},
        {'year': 2011, 'month':    8, 'day': None, 'var': 'nrj', 'agg': 'inv'},
        {'year': 2017, 'month':    8, 'day': None, 'var': 'nrj', 'agg': 'sum'},
        {'year': 2017, 'month':    8, 'day': None, 'var': 'nrj', 'agg': 'inv'},
        {'year': 2018, 'month':    2, 'day': None, 'var': 'nrj', 'agg': 'sum'},
        {'year': 2018, 'month':    2, 'day': None, 'var': 'nrj', 'agg': 'inv'},
        {'year': 2011, 'month':    6, 'day':   24, 'var': 'nrj', 'agg': 'sum'},
        {'year': 2011, 'month':    6, 'day':   24, 'var': 'nrj', 'agg': 'inv'},
        {'year': 2011, 'month':   12, 'day':   31, 'var': 'nrj', 'agg': 'sum'},
        {'year': 2011, 'month':   12, 'day':   31, 'var': 'nrj', 'agg': 'inv'},
        {'year': 2017, 'month':    2, 'day':    1, 'var': 'nrj', 'agg': 'sum'},
        {'year': 2017, 'month':    2, 'day':    1, 'var': 'nrj', 'agg': 'inv'},
        {'year': 2017, 'month':    8, 'day':    8, 'var': 'nrj', 'agg': 'sum'},
        {'year': 2017, 'month':    8, 'day':    8, 'var': 'nrj', 'agg': 'inv'},
    ])
    def testVarSum(self, year, month, day, var, agg):
        self.selectDate(year, month, day)
        self.plot()

        self.selectVar(var)
        self.selectSum(agg)
        self.plotParent()

        self.assertDate(year if month is not None else None, month if day is not None else None)
        self.assertSelectValue('var', var)
        self.assertSelectValue('sum', agg)

    @TestData([
        {'year': 2009},
        {'year': 2014},
        {'year': 2019},
    ])
    @BrowserTestCase.cacheTest
    def testPrevNextYears(self, year):
        self.selectDate(year)
        self.plotParent()

        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')

        self.assertClassed(prevButton, 'disabled', True)
        self.assertClassed(nextButton, 'disabled', True)

    @TestData([
        {'year': 2010, 'month': 12},
        {'year': 2011, 'month':  8},
        {'year': 2017, 'month':  8},
        {'year': 2018, 'month':  2},
    ])
    @BrowserTestCase.cacheTest
    def testPrevNextYear(self, year, month):
        self.selectDate(year, month)
        self.plotParent()

        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')

        self.assertClassed(prevButton, 'disabled', False)
        self.assertClassed(nextButton, 'disabled', False)

    @TestData([
        {'year': 2011, 'month':  6, 'day': 24},
        {'year': 2011, 'month': 12, 'day': 31},
        {'year': 2017, 'month':  2, 'day':  1},
        {'year': 2017, 'month':  8, 'day':  8},
    ])
    @BrowserTestCase.cacheTest
    def testPrevNextMonth(self, year, month, day):
        self.selectDate(year, month, day)
        self.plotParent()

        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')

        self.assertClassed(prevButton, 'disabled', False)
        self.assertClassed(nextButton, 'disabled', False)
