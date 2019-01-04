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

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys as Key

from .PythonUtils.testdata import TestData

from .legend_testcase import LegendTestCase
from .chart_testcase import ChartTestCase

class CursorTest(ChartTestCase, LegendTestCase):
    def loadToday(self):
        self.plot(True)

    def loadTodayDCPower(self):
        self.plot(True)
        self.selectVar('pdc')

    def __assertLineHovered(self, lines, path, enabled):
        for o in lines:
            self.assertClassed(o, 'hovered', enabled and (o == path))

    def __assertLineSelected(self, lines, path, enabled):
        for o in lines:
            self.assertClassed(o, 'selected', enabled and (o == path))

    def __assertLineLegendItemHovered(self, legendItemStyles, path, enabled):
        c = self.parseColor(path.find_element_by_xpath('..').get_attribute('stroke'))
        o = float(path.get_attribute('stroke-opacity'))
        legendItem = [i for i, s in legendItemStyles if (s['color'] == c) and abs(float(s['opacity']) - o) < 1e-12]
        self.assertEqual(len(legendItem), 1)

        for o, s in legendItemStyles:
            self.assertClassed(o, 'hovered', enabled and (o == legendItem[0]))

    def __assertLineCursor(self, paths, enabled):
        legendItemStyles = self.getLegendItemStyles()

        for p in paths:
            self.browser.execute_script("d3.select(arguments[0]).dispatch('mouseenter');", p)
            self.__assertLineHovered(paths, p, enabled)
            self.__assertLineLegendItemHovered(legendItemStyles, p, enabled)

            self.browser.execute_script("d3.select(arguments[0]).dispatch('mouseleave');", p)
            self.__assertLineHovered(paths, p, False)
            self.__assertLineLegendItemHovered(legendItemStyles, p, False)

            self.browser.execute_script("d3.select(arguments[0]).dispatch('click');", p)
            self.__assertLineSelected(paths, p, enabled)
            self.__assertLineLegendItemHovered(legendItemStyles, p, enabled)

            self.browser.execute_script("d3.select(arguments[0]).dispatch('click');", self.browser.find_element_by_id('chart'))
            self.__assertLineSelected(paths, p, False)
            self.__assertLineLegendItemHovered(legendItemStyles, p, False)

    def __assertBarLegendItemHovered(self, legendItemStyles, bar, enabled):
        c = self.parseColor(bar.find_element_by_xpath('..').get_attribute('fill'))
        o = float(bar.get_attribute('fill-opacity'))
        legendItem = [i for i, s in legendItemStyles if (s['background-color'][0:3] == c) and abs(s['background-color'][3] - o) < 1e-12]
        self.assertEqual(len(legendItem), 1)

        for o, s in legendItemStyles:
            self.assertClassed(o, 'hovered', enabled and (o == legendItem[0]))

    def __assertBarHovered(self, bars, bar, enabled):
        for o in bars:
            self.assertClassed(o, 'hovered', enabled and (o == bar))

    def __assertBarCursor(self, bars, enabled, var, agg):
        legendItemStyles = self.getLegendItemStyles()

        for b in bars:
            actions = ActionChains(self.browser)
            actions.move_to_element_with_offset(b, b.rect['width'] / 2, b.rect['height'] / 2)
            actions.perform()
            self.__assertBarHovered(bars, b, enabled)
            self.__assertBarLegendItemHovered(legendItemStyles, b, enabled)

            actions = ActionChains(self.browser)
            actions.move_to_element_with_offset(b, b.rect['width'] / 2, -10)
            actions.perform()
            self.__assertBarHovered(bars, b, False)
            self.__assertBarLegendItemHovered(legendItemStyles, b, False)

    def assertCursor(self, enabled, var='nrj', agg='sum'):
        paths = self.getLines()
        bars = self.getBars()

        if not (len(paths) == 0):
            self.__assertLineCursor(paths, enabled)
        elif not (len(bars) == 0):
            self.__assertBarCursor(bars, enabled, var, agg)
        else:
            self.assertFalse(enabled)

    def testToday(self):
        self.plot(True)

        cursor = self.browser.find_element_by_id('cursor')
        self.assertClassed(cursor, 'checked', False)
        self.assertClassed(cursor, 'disabled', False)
        self.assertCursor(False)

        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True)

        cursor.click()
        self.assertClassed(cursor, 'checked', False)
        self.assertCursor(False)

    def testKeyToday(self):
        self.plot(True)

        cursor = self.browser.find_element_by_id('cursor')
        self.assertClassed(cursor, 'checked', False)
        self.assertClassed(cursor, 'disabled', False)
        self.assertCursor(False)

        self.pressKeys([Key.ESCAPE]).perform()
        self.assertClassed(cursor, 'checked', False)
        self.assertCursor(False)

        self.pressKeys([Key.CONTROL, 'c']).perform()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True)

        self.pressKeys([Key.CONTROL, 'c']).perform()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True)

        self.pressKeys([Key.ESCAPE]).perform()
        self.assertClassed(cursor, 'checked', False)
        self.assertCursor(False)

    @TestData([
        {'year': None, 'month': None, 'day': None},
        {'year': 2017, 'month': None, 'day': None},
        {'year': 2017, 'month': 8,    'day': None},
        {'year': 2017, 'month': 8,    'day': 8},
    ])
    def testDate(self, year, month, day):
        self.selectDate(year, month, day)
        self.plot()
        self.loadData(year, month, day)

        cursor = self.browser.find_element_by_id('cursor')
        self.assertClassed(cursor, 'checked', False)
        self.assertClassed(cursor, 'disabled', False)
        self.assertCursor(False)

        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True)

        cursor.click()
        self.assertClassed(cursor, 'checked', False)
        self.assertCursor(False)

    @TestData([
        {'year': None, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': None, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2017, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': 2017, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': 2017, 'month': 8,    'day': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': None, 'var': 'pwr',  'agg': 'sum'},
        {'year': 2017, 'month': 8,    'day': None, 'var': 'pwr',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'nrj',  'agg': 'sum'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'nrj',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pac',  'agg': 'sum'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pac',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pdc',  'agg': 'sum'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pdc',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pdc',  'agg': 'str'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'udc',  'agg': 'str'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'temp', 'agg': 'inv'},
    ])
    def testVarAndSum(self, year, month, day, var, agg):
        self.selectDate(year, month, day)
        self.plot()
        self.loadData(year, month, day)
        self.selectVar(var)
        self.selectSum(agg)

        cursor = self.browser.find_element_by_id('cursor')
        self.assertClassed(cursor, 'checked', False)
        self.assertClassed(cursor, 'disabled', False)
        self.assertCursor(False, var, agg)

        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True, var, agg)

        cursor.click()
        self.assertClassed(cursor, 'checked', False)
        self.assertCursor(False, var, agg)

    @TestData([
        {'year': None, 'month': None, 'day': None},
        {'year': 2017, 'month': None, 'day': None},
        {'year': 2017, 'month': 8,    'day': None},
        {'year': 2017, 'month': 8,    'day': 8},
    ])
    def testKeyDate(self, year, month, day):
        self.selectDate(year, month, day)
        self.plot()
        self.loadData(year, month, day)

        cursor = self.browser.find_element_by_id('cursor')
        self.assertClassed(cursor, 'checked', False)
        self.assertClassed(cursor, 'disabled', False)
        self.assertCursor(False)

        self.pressKeys([Key.ESCAPE]).perform()
        self.assertClassed(cursor, 'checked', False)
        self.assertCursor(False)

        self.pressKeys([Key.CONTROL, 'c']).perform()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True)

        self.pressKeys([Key.CONTROL, 'c']).perform()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True)

        self.pressKeys([Key.ESCAPE]).perform()
        self.assertClassed(cursor, 'checked', False)
        self.assertCursor(False)

    @TestData([
        {'year': None, 'month': None, 'day': None, 'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': None, 'month': None, 'day': None, 'newYear': 2018, 'newMonth': 2,    'newDay': None},
        {'year': None, 'month': None, 'day': None, 'newYear': 2017, 'newMonth': 8,    'newDay': 8   },
        {'year': 2019, 'month': None, 'day': None, 'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2019, 'month': None, 'day': None, 'newYear': 2018, 'newMonth': 2,    'newDay': None},
        {'year': 2019, 'month': None, 'day': None, 'newYear': 2017, 'newMonth': 8,    'newDay': 8   },
        {'year': 2018, 'month': 2,    'day': None, 'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2018, 'month': 2,    'day': None, 'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2018, 'month': 2,    'day': None, 'newYear': 2017, 'newMonth': 8,    'newDay': 8   },
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2018, 'newMonth': 2,    'newDay': None},
    ])
    def testChangeDate(self, year, month, day, newYear, newMonth, newDay):
        self.selectDate(year, month, day)
        self.plot()
        self.loadData(year, month, day)

        cursor = self.browser.find_element_by_id('cursor')
        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True)

        self.selectDate(newYear, newMonth, newDay)
        self.plot()
        self.assertClassed(cursor, 'checked', False)
        self.assertCursor(False)

    @TestData([
        {'year': None, 'month': None, 'day': None},
        {'year': 2019, 'month': None, 'day': None},
        {'year': 2018, 'month': 2,    'day': None},
        {'year': 2017, 'month': 8,    'day': 8   },
    ])
    def testNoChangeDate(self, year, month, day):
        self.selectDate(year, month, day)
        self.plot()
        self.loadData(year, month, day)

        cursor = self.browser.find_element_by_id('cursor')
        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True)

        self.plot()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True)

    @TestData([
        {'var': 'nrj',  'newVar': 'pac',  'agg': 'sum'},
        {'var': 'nrj',  'newVar': 'pdc',  'agg': 'sum'},
        {'var': 'nrj',  'newVar': 'udc',  'agg': 'sum'},
        {'var': 'nrj',  'newVar': 'temp', 'agg': 'sum'},
        {'var': 'pac',  'newVar': 'nrj',  'agg': 'sum'},
        {'var': 'pac',  'newVar': 'pdc',  'agg': 'sum'},
        {'var': 'pac',  'newVar': 'udc',  'agg': 'sum'},
        {'var': 'pac',  'newVar': 'temp', 'agg': 'sum'},
        {'var': 'pdc',  'newVar': 'nrj',  'agg': 'sum'},
        {'var': 'pdc',  'newVar': 'pac',  'agg': 'sum'},
        {'var': 'pdc',  'newVar': 'udc',  'agg': 'sum'},
        {'var': 'pdc',  'newVar': 'temp', 'agg': 'sum'},
        {'var': 'udc',  'newVar': 'nrj',  'agg': 'str'},
        {'var': 'udc',  'newVar': 'pac',  'agg': 'str'},
        {'var': 'udc',  'newVar': 'pdc',  'agg': 'str'},
        {'var': 'udc',  'newVar': 'temp', 'agg': 'str'},
        {'var': 'temp', 'newVar': 'nrj',  'agg': 'inv'},
        {'var': 'temp', 'newVar': 'pac',  'agg': 'inv'},
        {'var': 'temp', 'newVar': 'pdc',  'agg': 'inv'},
        {'var': 'temp', 'newVar': 'udc',  'agg': 'inv'},
    ], before=loadToday)
    def testChangeVar(self, var, newVar, agg):
        self.selectVar(var)
        self.selectSum(agg)

        cursor = self.browser.find_element_by_id('cursor')
        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True)

        self.selectVar(newVar)
        self.assertClassed(cursor, 'checked', False)
        self.assertCursor(False)

    @TestData([
        {'agg': 'sum', 'newAgg': 'inv'},
        {'agg': 'sum', 'newAgg': 'str'},
        {'agg': 'inv', 'newAgg': 'sum'},
        {'agg': 'inv', 'newAgg': 'str'},
        {'agg': 'str', 'newAgg': 'sum'},
        {'agg': 'str', 'newAgg': 'inv'},
    ], before=loadTodayDCPower)
    def testChangeSum(self, agg, newAgg):
        self.selectSum(agg)

        cursor = self.browser.find_element_by_id('cursor')
        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True)

        self.selectSum(newAgg)
        self.assertClassed(cursor, 'checked', False)
        self.assertCursor(False)

    @TestData([
        {'year': None, 'month': None, 'day': None},
        {'year': 2019, 'month': None, 'day': None},
        {'year': 2018, 'month': 2,    'day': None},
        {'year': 2017, 'month': 8,    'day': 6,  },
        {'year': 2017, 'month': 8,    'day': 8   },
    ])
    def testChangeToday(self, year, month, day):
        self.selectDate(year, month, day)
        self.plot()
        self.loadData(year, month, day)

        cursor = self.browser.find_element_by_id('cursor')
        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True)

        self.plot(True)
        self.assertClassed(cursor, 'checked', False)
        self.assertCursor(False)

    def testNoChangeToday(self):
        self.plot(True)

        cursor = self.browser.find_element_by_id('cursor')
        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True)

        self.plot(True)
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True)

    @TestData([
        {'year': 2019, 'month': None, 'day': None},
        {'year': 2018, 'month': 2,    'day': None},
        {'year': 2017, 'month': 8,    'day': 8   },
    ])
    def testPrev(self, year, month, day):
        self.selectDate(year, month, day)
        self.plot()
        self.loadData(year, month, day)

        cursor = self.browser.find_element_by_id('cursor')
        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True)

        self.plotPrev()
        self.assertClassed(cursor, 'checked', False)
        self.assertCursor(False)

    @TestData([
        {'year': 2009, 'month': None, 'day': None},
        {'year': 2010, 'month': 12,   'day': None},
        {'year': 2011, 'month': 6,    'day': 24  },
    ])
    def testNext(self, year, month, day):
        self.selectDate(year, month, day)
        self.plot()
        self.loadData(year, month, day)

        cursor = self.browser.find_element_by_id('cursor')
        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True)

        self.plotNext()
        self.assertClassed(cursor, 'checked', False)
        self.assertCursor(False)

    @TestData([
        {'year': 2017, 'month': 8,    'day': 5},
    ])
    def testEmpty(self, year, month, day):
        self.selectDate(year, month, day)
        self.plot()

        cursor = self.browser.find_element_by_id('cursor')
        self.assertClassed(cursor, 'checked', False)
        self.assertClassed(cursor, 'disabled', True)
        self.assertCursor(False)

        cursor.click()
        self.assertClassed(cursor, 'checked', False)
        self.assertCursor(False)
