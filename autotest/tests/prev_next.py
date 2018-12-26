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

from .PythonUtils.testdata import testData

from .browser_testcase import BrowserTestCase

class PrevNextTest(BrowserTestCase):

    @testData([
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
    @BrowserTestCase.cacheTest
    def testYear(self, year, prevEnabled, nextEnabled):
        self.selectDate(year)

        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')

        self.assertClassed(prevButton, 'disabled', not prevEnabled)
        self.assertClassed(nextButton, 'disabled', not nextEnabled)

    @testData([
        {'year': 2010, 'month': 12, 'prevEnabled': '!cache', 'nextEnabled': True    },
        {'year': 2011, 'month': 6,  'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2011, 'month': 9,  'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2011, 'month': 12, 'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2017, 'month': 2,  'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2017, 'month': 5,  'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2017, 'month': 8,  'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2018, 'month': 2,  'prevEnabled': True,     'nextEnabled': '!cache'},
    ])
    @BrowserTestCase.cacheTest
    def testMonth(self, year, month, prevEnabled, nextEnabled):
        self.selectDate(year, month)

        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')

        self.assertClassed(prevButton, 'disabled',  not prevEnabled)
        self.assertClassed(nextButton, 'disabled',  not nextEnabled)

    @testData([
        {'year': 2011, 'month': 6,  'day': 24, 'prevEnabled': '!cache', 'nextEnabled': True    },
        {'year': 2011, 'month': 6,  'day': 27, 'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2011, 'month': 6,  'day': 30, 'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2017, 'month': 8,  'day': 2,  'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2017, 'month': 8,  'day': 5,  'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2017, 'month': 8,  'day': 8,  'prevEnabled': True,     'nextEnabled': '!cache'},
    ])
    @BrowserTestCase.cacheTest
    def testDay(self, year, month, day, prevEnabled, nextEnabled):
        self.selectDate(year, month, day)

        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')

        self.assertClassed(prevButton, 'disabled', not prevEnabled)
        self.assertClassed(nextButton, 'disabled', not nextEnabled)

    # NOTE The page should not be reloaded before each date
    # that's why @cacheTest is first.
    @BrowserTestCase.cacheTest
    @testData([
        {'year': 2009, 'prevYear': 2009, 'prevEnabled': False             },
        {'year': 2010, 'prevYear': 2009, 'prevEnabled': False             },
        {'year': 2011, 'prevYear': 2010, 'prevEnabled': True              },
        {'year': 2013, 'prevYear': 2011, 'prevEnabled': True              },
        {'year': 2014, 'prevYear': 2013, 'prevEnabled': True              },
        {'year': 2015, 'prevYear': 2014, 'prevEnabled': True              },
        {'year': 2017, 'prevYear': 2015, 'prevEnabled': True              },
        {'year': 2018, 'prevYear': 2017, 'prevEnabled': True              },
        {'year': 2019, 'prevYear': 2018, 'prevEnabled': True              },
        {'year': 2009, 'prevYear': 2009, 'prevEnabled': False, 'repeat': 2},
        {'year': 2010, 'prevYear': 2009, 'prevEnabled': False, 'repeat': 2},
        {'year': 2011, 'prevYear': 2009, 'prevEnabled': False, 'repeat': 2},
        {'year': 2013, 'prevYear': 2010, 'prevEnabled': True,  'repeat': 2},
        {'year': 2014, 'prevYear': 2011, 'prevEnabled': True,  'repeat': 2},
        {'year': 2015, 'prevYear': 2013, 'prevEnabled': True,  'repeat': 2},
        {'year': 2017, 'prevYear': 2014, 'prevEnabled': True,  'repeat': 2},
        {'year': 2018, 'prevYear': 2015, 'prevEnabled': True,  'repeat': 2},
        {'year': 2019, 'prevYear': 2017, 'prevEnabled': True,  'repeat': 2},
        {'year': 2019, 'prevYear': 2010, 'prevEnabled': True,  'repeat': 7},
        {'year': 2019, 'prevYear': 2009, 'prevEnabled': False, 'repeat': 8},
        {'year': 2019, 'prevYear': 2009, 'prevEnabled': False, 'repeat': 9},
    ])
    def testPrevYear(self, year, prevYear, prevEnabled, repeat=1):
        self.selectDate(year)

        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')

        self.clickButton(prevButton, repeat).perform()

        self.assertDate(prevYear)
        self.assertClassed(prevButton, 'disabled', not prevEnabled)
        self.assertClassed(nextButton, 'disabled', False)

    # NOTE The page should not be reloaded before each date
    # that's why @cacheTest is first.
    @BrowserTestCase.cacheTest
    @testData([
        {'year': 2010, 'month': 12, 'prevYear': 2010, 'prevMonth': 12, 'prevEnabled': False              },
        {'year': 2011, 'month': 6,  'prevYear': 2010, 'prevMonth': 12, 'prevEnabled': False              },
        {'year': 2011, 'month': 8,  'prevYear': 2011, 'prevMonth': 6,  'prevEnabled': True               },
        {'year': 2011, 'month': 9,  'prevYear': 2011, 'prevMonth': 8,  'prevEnabled': True               },
        {'year': 2011, 'month': 10, 'prevYear': 2011, 'prevMonth': 9,  'prevEnabled': True               },
        {'year': 2011, 'month': 12, 'prevYear': 2011, 'prevMonth': 10, 'prevEnabled': True               },
        {'year': 2017, 'month': 2,  'prevYear': 2011, 'prevMonth': 12, 'prevEnabled': True               },
        {'year': 2017, 'month': 4,  'prevYear': 2017, 'prevMonth': 2,  'prevEnabled': True               },
        {'year': 2017, 'month': 5,  'prevYear': 2017, 'prevMonth': 4,  'prevEnabled': True               },
        {'year': 2017, 'month': 6,  'prevYear': 2017, 'prevMonth': 5,  'prevEnabled': True               },
        {'year': 2017, 'month': 8,  'prevYear': 2017, 'prevMonth': 6,  'prevEnabled': True               },
        {'year': 2018, 'month': 2,  'prevYear': 2017, 'prevMonth': 8,  'prevEnabled': True               },
        {'year': 2010, 'month': 12, 'prevYear': 2010, 'prevMonth': 12, 'prevEnabled': False, 'repeat': 2 },
        {'year': 2011, 'month': 6,  'prevYear': 2010, 'prevMonth': 12, 'prevEnabled': False, 'repeat': 2 },
        {'year': 2011, 'month': 8,  'prevYear': 2010, 'prevMonth': 12, 'prevEnabled': False, 'repeat': 2 },
        {'year': 2011, 'month': 9,  'prevYear': 2011, 'prevMonth': 6,  'prevEnabled': True,  'repeat': 2 },
        {'year': 2011, 'month': 10, 'prevYear': 2011, 'prevMonth': 8,  'prevEnabled': True,  'repeat': 2 },
        {'year': 2011, 'month': 12, 'prevYear': 2011, 'prevMonth': 9,  'prevEnabled': True,  'repeat': 2 },
        {'year': 2017, 'month': 2,  'prevYear': 2011, 'prevMonth': 10, 'prevEnabled': True,  'repeat': 2 },
        {'year': 2017, 'month': 4,  'prevYear': 2011, 'prevMonth': 12, 'prevEnabled': True,  'repeat': 2 },
        {'year': 2017, 'month': 5,  'prevYear': 2017, 'prevMonth': 2,  'prevEnabled': True,  'repeat': 2 },
        {'year': 2017, 'month': 6,  'prevYear': 2017, 'prevMonth': 4,  'prevEnabled': True,  'repeat': 2 },
        {'year': 2017, 'month': 8,  'prevYear': 2017, 'prevMonth': 5,  'prevEnabled': True,  'repeat': 2 },
        {'year': 2018, 'month': 2,  'prevYear': 2017, 'prevMonth': 6,  'prevEnabled': True,  'repeat': 2 },
        {'year': 2018, 'month': 2,  'prevYear': 2011, 'prevMonth': 6,  'prevEnabled': True,  'repeat': 10},
        {'year': 2018, 'month': 2,  'prevYear': 2010, 'prevMonth': 12, 'prevEnabled': False, 'repeat': 11},
        {'year': 2018, 'month': 2,  'prevYear': 2010, 'prevMonth': 12, 'prevEnabled': False, 'repeat': 12},
    ])
    def testPrevMonth(self, year, month, prevYear, prevMonth, prevEnabled, repeat=1):
        self.selectDate(year, month)

        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')

        self.clickButton(prevButton, repeat).perform()

        self.assertDate(prevYear, prevMonth, wait=5)
        self.assertClassed(prevButton, 'disabled', not prevEnabled)
        self.assertClassed(nextButton, 'disabled', False)

    # NOTE The page should not be reloaded before each date
    # that's why @cacheTest is first.
    @BrowserTestCase.cacheTest
    @testData([
        {'year': 2011, 'month': 6,  'day': 24, 'prevYear': 2011, 'prevMonth': 6,  'prevDay': 24, 'prevEnabled': False              },
        {'year': 2011, 'month': 6,  'day': 26, 'prevYear': 2011, 'prevMonth': 6,  'prevDay': 24, 'prevEnabled': False              },
        {'year': 2011, 'month': 6,  'day': 27, 'prevYear': 2011, 'prevMonth': 6,  'prevDay': 26, 'prevEnabled': True               },
        {'year': 2011, 'month': 6,  'day': 28, 'prevYear': 2011, 'prevMonth': 6,  'prevDay': 27, 'prevEnabled': True               },
        {'year': 2011, 'month': 6,  'day': 30, 'prevYear': 2011, 'prevMonth': 6,  'prevDay': 28, 'prevEnabled': True               },
        {'year': 2011, 'month': 12, 'day': 25, 'prevYear': 2011, 'prevMonth': 6,  'prevDay': 30, 'prevEnabled': True               },
        {'year': 2017, 'month': 2,  'day': 1,  'prevYear': 2011, 'prevMonth': 12, 'prevDay': 31, 'prevEnabled': True               },
        {'year': 2017, 'month': 8,  'day': 2,  'prevYear': 2017, 'prevMonth': 2,  'prevDay': 7,  'prevEnabled': True               },
        {'year': 2017, 'month': 8,  'day': 8,  'prevYear': 2017, 'prevMonth': 8,  'prevDay': 6,  'prevEnabled': True               },
        {'year': 2011, 'month': 6,  'day': 24, 'prevYear': 2011, 'prevMonth': 6,  'prevDay': 24, 'prevEnabled': False, 'repeat': 2 },
        {'year': 2011, 'month': 6,  'day': 26, 'prevYear': 2011, 'prevMonth': 6,  'prevDay': 24, 'prevEnabled': False, 'repeat': 2 },
        {'year': 2011, 'month': 6,  'day': 27, 'prevYear': 2011, 'prevMonth': 6,  'prevDay': 24, 'prevEnabled': False, 'repeat': 2 },
        {'year': 2011, 'month': 6,  'day': 28, 'prevYear': 2011, 'prevMonth': 6,  'prevDay': 26, 'prevEnabled': True,  'repeat': 2 },
        {'year': 2011, 'month': 6,  'day': 30, 'prevYear': 2011, 'prevMonth': 6,  'prevDay': 27, 'prevEnabled': True,  'repeat': 2 },
        {'year': 2011, 'month': 12, 'day': 25, 'prevYear': 2011, 'prevMonth': 6,  'prevDay': 28, 'prevEnabled': True,  'repeat': 2 },
        {'year': 2011, 'month': 12, 'day': 27, 'prevYear': 2011, 'prevMonth': 6,  'prevDay': 30, 'prevEnabled': True,  'repeat': 2 },
        {'year': 2017, 'month': 2,  'day': 1,  'prevYear': 2011, 'prevMonth': 12, 'prevDay': 29, 'prevEnabled': True,  'repeat': 2 },
        {'year': 2017, 'month': 2,  'day': 3,  'prevYear': 2011, 'prevMonth': 12, 'prevDay': 31, 'prevEnabled': True,  'repeat': 2 },
        {'year': 2017, 'month': 8,  'day': 2,  'prevYear': 2017, 'prevMonth': 2,  'prevDay': 5,  'prevEnabled': True,  'repeat': 2 },
        {'year': 2017, 'month': 8,  'day': 4,  'prevYear': 2017, 'prevMonth': 2,  'prevDay': 7,  'prevEnabled': True,  'repeat': 2 },
        {'year': 2017, 'month': 8,  'day': 8,  'prevYear': 2017, 'prevMonth': 8,  'prevDay': 5,  'prevEnabled': True,  'repeat': 2 },
        {'year': 2017, 'month': 8,  'day': 8,  'prevYear': 2011, 'prevMonth': 6,  'prevDay': 26, 'prevEnabled': True,  'repeat': 18},
        {'year': 2017, 'month': 8,  'day': 8,  'prevYear': 2011, 'prevMonth': 6,  'prevDay': 24, 'prevEnabled': False, 'repeat': 19},
        {'year': 2017, 'month': 8,  'day': 8,  'prevYear': 2011, 'prevMonth': 6,  'prevDay': 24, 'prevEnabled': False, 'repeat': 20},
    ])
    def testPrevDay(self, year, month, day, prevYear, prevMonth, prevDay, prevEnabled, repeat=1):
        self.selectDate(year, month, day)

        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')

        self.clickButton(prevButton, repeat).perform()

        self.assertDate(prevYear, prevMonth, prevDay, wait=5)
        self.assertClassed(prevButton, 'disabled', not prevEnabled)
        self.assertClassed(nextButton, 'disabled', False)

    # NOTE The page should not be reloaded before each date
    # that's why @cacheTest is first.
    @BrowserTestCase.cacheTest
    @testData([
        {'year': 2009, 'nextYear': 2010, 'nextEnabled': True              },
        {'year': 2010, 'nextYear': 2011, 'nextEnabled': True              },
        {'year': 2011, 'nextYear': 2013, 'nextEnabled': True              },
        {'year': 2013, 'nextYear': 2014, 'nextEnabled': True              },
        {'year': 2014, 'nextYear': 2015, 'nextEnabled': True              },
        {'year': 2015, 'nextYear': 2017, 'nextEnabled': True              },
        {'year': 2017, 'nextYear': 2018, 'nextEnabled': True              },
        {'year': 2018, 'nextYear': 2019, 'nextEnabled': False             },
        {'year': 2019, 'nextYear': 2019, 'nextEnabled': False             },
        {'year': 2019, 'nextYear': 2019, 'nextEnabled': False, 'repeat': 2},
        {'year': 2018, 'nextYear': 2019, 'nextEnabled': False, 'repeat': 2},
        {'year': 2017, 'nextYear': 2019, 'nextEnabled': False, 'repeat': 2},
        {'year': 2015, 'nextYear': 2018, 'nextEnabled': True,  'repeat': 2},
        {'year': 2014, 'nextYear': 2017, 'nextEnabled': True,  'repeat': 2},
        {'year': 2013, 'nextYear': 2015, 'nextEnabled': True,  'repeat': 2},
        {'year': 2011, 'nextYear': 2014, 'nextEnabled': True,  'repeat': 2},
        {'year': 2010, 'nextYear': 2013, 'nextEnabled': True,  'repeat': 2},
        {'year': 2009, 'nextYear': 2011, 'nextEnabled': True,  'repeat': 2},
        {'year': 2009, 'nextYear': 2018, 'nextEnabled': True,  'repeat': 7},
        {'year': 2009, 'nextYear': 2019, 'nextEnabled': False, 'repeat': 8},
        {'year': 2009, 'nextYear': 2019, 'nextEnabled': False, 'repeat': 9},
    ])
    def testNextYear(self, year, nextYear, nextEnabled, repeat=1):
        self.selectDate(year)

        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')

        self.clickButton(nextButton, repeat).perform()

        self.assertDate(nextYear)
        self.assertClassed(prevButton, 'disabled', False)
        self.assertClassed(nextButton, 'disabled', not nextEnabled)

    # NOTE The page should not be reloaded before each date
    # that's why @cacheTest is first.
    @BrowserTestCase.cacheTest
    @testData([
        {'year': 2018, 'month': 2,  'nextYear': 2018, 'nextMonth': 2,  'nextEnabled': False              },
        {'year': 2017, 'month': 8,  'nextYear': 2018, 'nextMonth': 2,  'nextEnabled': False              },
        {'year': 2017, 'month': 6,  'nextYear': 2017, 'nextMonth': 8,  'nextEnabled': True               },
        {'year': 2017, 'month': 5,  'nextYear': 2017, 'nextMonth': 6,  'nextEnabled': True               },
        {'year': 2017, 'month': 4,  'nextYear': 2017, 'nextMonth': 5,  'nextEnabled': True               },
        {'year': 2017, 'month': 2,  'nextYear': 2017, 'nextMonth': 4,  'nextEnabled': True               },
        {'year': 2011, 'month': 12, 'nextYear': 2017, 'nextMonth': 2,  'nextEnabled': True               },
        {'year': 2011, 'month': 10, 'nextYear': 2011, 'nextMonth': 12, 'nextEnabled': True               },
        {'year': 2011, 'month': 9,  'nextYear': 2011, 'nextMonth': 10, 'nextEnabled': True               },
        {'year': 2011, 'month': 8,  'nextYear': 2011, 'nextMonth': 9,  'nextEnabled': True               },
        {'year': 2011, 'month': 6,  'nextYear': 2011, 'nextMonth': 8,  'nextEnabled': True               },
        {'year': 2010, 'month': 12, 'nextYear': 2011, 'nextMonth': 6,  'nextEnabled': True               },
        {'year': 2018, 'month': 2,  'nextYear': 2018, 'nextMonth': 2,  'nextEnabled': False, 'repeat': 2 },
        {'year': 2017, 'month': 8,  'nextYear': 2018, 'nextMonth': 2,  'nextEnabled': False, 'repeat': 2 },
        {'year': 2017, 'month': 6,  'nextYear': 2018, 'nextMonth': 2,  'nextEnabled': False, 'repeat': 2 },
        {'year': 2017, 'month': 5,  'nextYear': 2017, 'nextMonth': 8,  'nextEnabled': True,  'repeat': 2 },
        {'year': 2017, 'month': 4,  'nextYear': 2017, 'nextMonth': 6,  'nextEnabled': True,  'repeat': 2 },
        {'year': 2017, 'month': 2,  'nextYear': 2017, 'nextMonth': 5,  'nextEnabled': True,  'repeat': 2 },
        {'year': 2011, 'month': 12, 'nextYear': 2017, 'nextMonth': 4,  'nextEnabled': True,  'repeat': 2 },
        {'year': 2011, 'month': 10, 'nextYear': 2017, 'nextMonth': 2,  'nextEnabled': True,  'repeat': 2 },
        {'year': 2011, 'month': 9,  'nextYear': 2011, 'nextMonth': 12, 'nextEnabled': True,  'repeat': 2 },
        {'year': 2011, 'month': 8,  'nextYear': 2011, 'nextMonth': 10, 'nextEnabled': True,  'repeat': 2 },
        {'year': 2011, 'month': 6,  'nextYear': 2011, 'nextMonth': 9,  'nextEnabled': True,  'repeat': 2 },
        {'year': 2010, 'month': 12, 'nextYear': 2011, 'nextMonth': 8,  'nextEnabled': True,  'repeat': 2 },
        {'year': 2010, 'month': 12, 'nextYear': 2017, 'nextMonth': 8,  'nextEnabled': True,  'repeat': 10},
        {'year': 2010, 'month': 12, 'nextYear': 2018, 'nextMonth': 2,  'nextEnabled': False, 'repeat': 11},
        {'year': 2010, 'month': 12, 'nextYear': 2018, 'nextMonth': 2,  'nextEnabled': False, 'repeat': 12},
    ])
    def testNextMonth(self, year, month, nextYear, nextMonth, nextEnabled, repeat=1):
        self.selectDate(year, month)

        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')

        self.clickButton(nextButton, repeat).perform()

        self.assertDate(nextYear, nextMonth, wait=5)
        self.assertClassed(prevButton, 'disabled', False)
        self.assertClassed(nextButton, 'disabled', not nextEnabled)

    # NOTE The page should not be reloaded before each date
    # that's why @cacheTest is first.
    @BrowserTestCase.cacheTest
    @testData([
        {'year': 2017, 'month': 8,  'day': 8,  'nextYear': 2017, 'nextMonth': 8,  'nextDay': 8,  'nextEnabled': False              },
        {'year': 2017, 'month': 8,  'day': 6,  'nextYear': 2017, 'nextMonth': 8,  'nextDay': 8,  'nextEnabled': False              },
        {'year': 2017, 'month': 8,  'day': 5,  'nextYear': 2017, 'nextMonth': 8,  'nextDay': 6,  'nextEnabled': True               },
        {'year': 2017, 'month': 8,  'day': 4,  'nextYear': 2017, 'nextMonth': 8,  'nextDay': 5,  'nextEnabled': True               },
        {'year': 2017, 'month': 8,  'day': 2,  'nextYear': 2017, 'nextMonth': 8,  'nextDay': 4,  'nextEnabled': True               },
        {'year': 2017, 'month': 2,  'day': 7,  'nextYear': 2017, 'nextMonth': 8,  'nextDay': 2,  'nextEnabled': True               },
        {'year': 2011, 'month': 12, 'day': 31, 'nextYear': 2017, 'nextMonth': 2,  'nextDay': 1,  'nextEnabled': True               },
        {'year': 2011, 'month': 6,  'day': 30, 'nextYear': 2011, 'nextMonth': 12, 'nextDay': 25, 'nextEnabled': True               },
        {'year': 2011, 'month': 6,  'day': 24, 'nextYear': 2011, 'nextMonth': 6,  'nextDay': 26, 'nextEnabled': True               },
        {'year': 2017, 'month': 8,  'day': 8,  'nextYear': 2017, 'nextMonth': 8,  'nextDay': 8,  'nextEnabled': False, 'repeat': 2 },
        {'year': 2017, 'month': 8,  'day': 6,  'nextYear': 2017, 'nextMonth': 8,  'nextDay': 8,  'nextEnabled': False, 'repeat': 2 },
        {'year': 2017, 'month': 8,  'day': 5,  'nextYear': 2017, 'nextMonth': 8,  'nextDay': 8,  'nextEnabled': False, 'repeat': 2 },
        {'year': 2017, 'month': 8,  'day': 4,  'nextYear': 2017, 'nextMonth': 8,  'nextDay': 6,  'nextEnabled': True,  'repeat': 2 },
        {'year': 2017, 'month': 8,  'day': 2,  'nextYear': 2017, 'nextMonth': 8,  'nextDay': 5,  'nextEnabled': True,  'repeat': 2 },
        {'year': 2017, 'month': 2,  'day': 7,  'nextYear': 2017, 'nextMonth': 8,  'nextDay': 4,  'nextEnabled': True,  'repeat': 2 },
        {'year': 2017, 'month': 2,  'day': 5,  'nextYear': 2017, 'nextMonth': 8,  'nextDay': 2,  'nextEnabled': True,  'repeat': 2 },
        {'year': 2011, 'month': 12, 'day': 31, 'nextYear': 2017, 'nextMonth': 2,  'nextDay': 3,  'nextEnabled': True,  'repeat': 2 },
        {'year': 2011, 'month': 12, 'day': 29, 'nextYear': 2017, 'nextMonth': 2,  'nextDay': 1,  'nextEnabled': True,  'repeat': 2 },
        {'year': 2011, 'month': 6,  'day': 30, 'nextYear': 2011, 'nextMonth': 12, 'nextDay': 27, 'nextEnabled': True,  'repeat': 2 },
        {'year': 2011, 'month': 6,  'day': 28, 'nextYear': 2011, 'nextMonth': 12, 'nextDay': 25, 'nextEnabled': True,  'repeat': 2 },
        {'year': 2011, 'month': 6,  'day': 24, 'nextYear': 2011, 'nextMonth': 6,  'nextDay': 27, 'nextEnabled': True,  'repeat': 2 },
        {'year': 2011, 'month': 6,  'day': 24, 'nextYear': 2017, 'nextMonth': 8,  'nextDay': 6,  'nextEnabled': True,  'repeat': 18},
        {'year': 2011, 'month': 6,  'day': 24, 'nextYear': 2017, 'nextMonth': 8,  'nextDay': 8,  'nextEnabled': False, 'repeat': 19},
        {'year': 2011, 'month': 6,  'day': 24, 'nextYear': 2017, 'nextMonth': 8,  'nextDay': 8,  'nextEnabled': False, 'repeat': 20},
    ])
    def testNextDay(self, year, month, day, nextYear, nextMonth, nextDay, nextEnabled, repeat=1):
        self.selectDate(year, month, day)

        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')

        self.clickButton(nextButton, repeat).perform()

        self.assertDate(nextYear, nextMonth, nextDay, wait=5)
        self.assertClassed(prevButton, 'disabled', False)
        self.assertClassed(nextButton, 'disabled', not nextEnabled)

    @BrowserTestCase.cacheTest
    def testNoPrevNext(self):
        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')

        self.assertDate()
        self.assertClassed(prevButton, 'disabled', True)
        self.assertClassed(nextButton, 'disabled', True)
