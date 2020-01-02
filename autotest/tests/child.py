# Copyright 2018-2020 Pascal COMBES <pascom@orange.fr>
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

from .chart_testcase import ChartTestCase

class ChildTest(ChartTestCase):

    @TestData([
        {'year': 2009},
        {'year': 2014},
        {'year': 2019},
    ])
    def testYears(self, year):
        self.selectDate()
        self.plot()
        self.plotChild(year)

        self.assertDate(year)
        parentButton = self.browser.find_element_by_id('up')
        self.assertClassed(parentButton, 'disabled', False)
        self.assertTitle(parentButton, "Afficher toutes les années")

    @TestData([
        {'year': 2010, 'month': 12},
        {'year': 2011, 'month':  8},
        {'year': 2017, 'month':  8},
        {'year': 2018, 'month':  2},
    ])
    def testMonth(self, year, month):
        self.selectDate(year)
        self.plot()
        self.plotChild(month)

        self.assertDate(year, month)
        parentButton = self.browser.find_element_by_id('up')
        self.assertClassed(parentButton, 'disabled', False)
        self.assertTitle(parentButton, "Afficher toute l'année")

    @TestData([
        {'year': 2011, 'month':  6, 'day': 24},
        {'year': 2011, 'month': 12, 'day': 31},
        {'year': 2017, 'month':  2, 'day':  1},
        {'year': 2017, 'month':  8, 'day':  8},
    ])
    def testDay(self, year, month, day):
        self.selectDate(year, month)
        self.plot()
        self.plotChild(day)

        self.assertDate(year, month, day)
        parentButton = self.browser.find_element_by_id('up')
        self.assertClassed(parentButton, 'disabled', False)
        self.assertTitle(parentButton, "Afficher tout le mois")

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
        self.selectDate(year if month is not None else None, month if day is not None else None)
        self.plot()

        self.selectVar(var)
        self.selectSum(agg)

        if (month is None):
            self.plotChild(year)
        elif (day is None):
            self.plotChild(month)
        else:
            self.plotChild(day)

        self.assertDate(year, month, day)
        self.assertSelectValue('var', var)
        self.assertSelectValue('sum', agg)

    @TestData([
        {'year': 2009, 'prevEnabled': False, 'nextEnabled': True },
        {'year': 2010, 'prevEnabled': True,  'nextEnabled': True },
        {'year': 2011, 'prevEnabled': True,  'nextEnabled': True },
        {'year': 2013, 'prevEnabled': True,  'nextEnabled': True },
        {'year': 2014, 'prevEnabled': True,  'nextEnabled': True },
        {'year': 2015, 'prevEnabled': True,  'nextEnabled': True },
        {'year': 2017, 'prevEnabled': True,  'nextEnabled': True },
        {'year': 2018, 'prevEnabled': True,  'nextEnabled': True },
        {'year': 2019, 'prevEnabled': True,  'nextEnabled': False},
    ])
    @ChartTestCase.cacheTest
    def testPrevNextYear(self, year, prevEnabled, nextEnabled):
        self.selectDate()
        self.plot()
        self.plotChild(year)

        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')

        self.assertClassed(prevButton, 'disabled', not prevEnabled)
        self.assertClassed(nextButton, 'disabled', not nextEnabled)

    @TestData([
        {'year': 2010, 'month': 12, 'prevEnabled': '!cache', 'nextEnabled': True    },
        {'year': 2011, 'month': 6,  'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2011, 'month': 9,  'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2011, 'month': 12, 'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2017, 'month': 2,  'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2017, 'month': 5,  'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2017, 'month': 8,  'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2018, 'month': 2,  'prevEnabled': True,     'nextEnabled': '!cache'},
    ])
    @ChartTestCase.cacheTest
    def testPrevNextMonth(self, year, month, prevEnabled, nextEnabled):
        self.selectDate(year)
        self.plot()
        self.plotChild(month)

        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')

        self.assertClassed(prevButton, 'disabled',  not prevEnabled)
        self.assertClassed(nextButton, 'disabled',  not nextEnabled)

    @TestData([
        {'year': 2011, 'month': 6,  'day': 24, 'prevEnabled': '!cache', 'nextEnabled': True    },
        {'year': 2011, 'month': 6,  'day': 27, 'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2011, 'month': 6,  'day': 30, 'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2017, 'month': 8,  'day': 2,  'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2017, 'month': 8,  'day': 5,  'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2017, 'month': 8,  'day': 8,  'prevEnabled': True,     'nextEnabled': '!cache'},
    ])
    @ChartTestCase.cacheTest
    def testPrevNextDay(self, year, month, day, prevEnabled, nextEnabled):
        self.selectDate(year, month)
        self.plot()
        self.plotChild(day)

        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')

        self.assertClassed(prevButton, 'disabled', not prevEnabled)
        self.assertClassed(nextButton, 'disabled', not nextEnabled)
