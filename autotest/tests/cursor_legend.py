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

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys as Key
from selenium.common import exceptions as selenium

from .PythonUtils.testdata import TestData

from .legend_testcase import LegendTestCase
from .chart_testcase import ChartTestCase

class CursorLegendTest(ChartTestCase, LegendTestCase):
    def loadToday(self):
        self.plot(True)

    def loadTodayDCPower(self):
        self.plot(True)
        self.selectVar('pdc')

    def assertCursor(self, enabled, testMeasure=False):
        legendItems = self.getLegendItems()

        if all([len(i) == 1 for i in legendItems]):
            legendItemStyles = []
        elif all([len(i) == 4 for i in legendItems]):
            legendItemStyles = [(i, self.getStyle(i)) for i, t, b, c in legendItems]
        elif all([len(c) == 0 for t, b, c in legendItems]):
            legendItemStyles = [(i, self.getStyle(i)) for i, t, c in legendItems]
        else:
            legendItemStyles = [(c, self.getStyle(c)) for i, t, children in legendItems for c, t, b, x in children]

        if (len(legendItemStyles) == 0):
            self.assertFalse(enabled)

        bars = self.getBars(self.getColor, self.getOpacity)
        lines = self.getLines(self.getColor, self.getOpacity)

        prevElems = []
        prevI = None
        for i, s in legendItemStyles:
            if not (len(bars) == 0):
                elems = [r for r, c, o in bars if (s['background-color'][0:3] == c) and (abs(float(s['background-color'][3]) - o) < 1e-12)]
            elif not (len(lines) == 0):
                elems = [p for p, c, o in lines if (s['color'] == c) and (abs(float(s['opacity']) - o) < 1e-12)]
            else:
                self.fail('There should be bars or lines')
            self.assertGreater(len(elems), 0)

            actions = ActionChains(self.browser)
            actions.move_to_element_with_offset(i, i.rect['width'] / 2, i.rect['height'] / 2)
            actions.perform()

            for oi, os in legendItemStyles:
                self.assertClassed(oi, 'hovered', enabled and (oi in [i, prevI]))
            for r, c, o in bars:
                self.assertClassed(r, 'hovered', enabled and (r in elems))
                self.assertClassed(r, 'selected', enabled and (r in prevElems))
            for p, c, o in lines:
                self.assertClassed(p, 'hovered', enabled and (p in elems))
                self.assertClassed(p, 'selected', enabled and (p in prevElems))

            actions = ActionChains(self.browser)
            actions.move_to_element_with_offset(i, -10, i.rect['height'] / 2)
            actions.perform()

            for oi, os in legendItemStyles:
                self.assertClassed(oi, 'hovered', enabled and (oi == prevI))
            for r, c, o in bars:
                self.assertClassed(r, 'hovered', False)
                self.assertClassed(r, 'selected', enabled and (r in prevElems))
            for p, c, o in lines:
                self.assertClassed(p, 'hovered', False)
                self.assertClassed(p, 'selected', enabled and (p in prevElems))

            if testMeasure and (len(lines) != 0):
                prevElems = elems
                prevI = i

                actions = ActionChains(self.browser)
                actions.move_to_element_with_offset(i, i.rect['width'] / 2, i.rect['height'] / 2)
                actions.click()
                actions.perform()

                for oi, os in legendItemStyles:
                    self.assertClassed(oi, 'hovered', oi == i)
                for p, c, o in lines:
                    self.assertClassed(p, 'selected', p in prevElems)

                actions = ActionChains(self.browser)
                actions.move_to_element_with_offset(i, -10, i.rect['height'] / 2)
                actions.perform()

                for oi, os in legendItemStyles:
                    self.assertClassed(oi, 'hovered', oi == i)
                for p, c, o in lines:
                    self.assertClassed(p, 'selected', p in prevElems)

                actions = ActionChains(self.browser)
                actions.move_to_element_with_offset(self.browser.find_element_by_id('chart'), 200, 200)
                actions.perform()

                if enabled:
                    self.assertEqual(len(self.browser.find_element_by_id('xcursor').get_attribute('style')), 0)
                    self.assertEqual(len(self.browser.find_element_by_id('ycursor').get_attribute('style')), 0)
                else:
                    with self.assertRaises(selenium.NoSuchElementException):
                        self.browser.find_element_by_class_name('cursor')

    def testToday(self):
        self.plot(True)

        cursor = self.browser.find_element_by_id('cursor')
        self.assertClassed(cursor, 'checked', False)
        self.assertClassed(cursor, 'disabled', False)
        self.assertCursor(False)

        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True, True)

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
        self.assertCursor(True, True)

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

        cursor = self.browser.find_element_by_id('cursor')
        self.assertClassed(cursor, 'checked', False)
        self.assertClassed(cursor, 'disabled', False)
        self.assertCursor(False)

        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True, True)

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
        self.selectVar(var)
        self.selectSum(agg)

        cursor = self.browser.find_element_by_id('cursor')
        self.assertClassed(cursor, 'checked', False)
        self.assertClassed(cursor, 'disabled', False)
        self.assertCursor(False)

        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True, True)

        cursor.click()
        self.assertClassed(cursor, 'checked', False)
        self.assertCursor(False)

    @TestData([
        {'year': None, 'month': None, 'day': None},
        {'year': 2017, 'month': None, 'day': None},
        {'year': 2017, 'month': 8,    'day': None},
        {'year': 2017, 'month': 8,    'day': 8},
    ])
    def testKeyDate(self, year, month, day):
        self.selectDate(year, month, day)
        self.plot()

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
        self.assertCursor(True, True)

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

        cursor = self.browser.find_element_by_id('cursor')
        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True, True)

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
        self.assertCursor(True, True)

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
        self.assertCursor(True, True)

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

        cursor = self.browser.find_element_by_id('cursor')
        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True, True)

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

        cursor = self.browser.find_element_by_id('cursor')
        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True, True)

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

        cursor = self.browser.find_element_by_id('cursor')
        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True, True)

        self.plotNext()
        self.assertClassed(cursor, 'checked', False)
        self.assertCursor(False)

    @TestData([
        {'year': 2009, 'month': None, 'day': None},
        {'year': 2019, 'month': None, 'day': None},
        {'year': 2010, 'month':   12, 'day': None},
        {'year': 2018, 'month':    2, 'day': None},
        {'year': 2011, 'month':    6, 'day':   24},
        {'year': 2017, 'month':    8, 'day':    8},
    ])
    def testParent(self, year, month, day):
        self.selectDate(year, month, day)
        self.plot()

        cursor = self.browser.find_element_by_id('cursor')
        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True, True)

        self.plotParent()
        self.assertClassed(cursor, 'checked', False)
        self.assertCursor(False)

    @TestData([
        {'year': 2009, 'month': None, 'day': None},
        {'year': 2019, 'month': None, 'day': None},
        {'year': 2010, 'month':   12, 'day': None},
        {'year': 2018, 'month':    2, 'day': None},
        {'year': 2011, 'month':    6, 'day':   24},
        {'year': 2017, 'month':    8, 'day':    8},
    ])
    def testChild(self, year, month, day):
        self.selectDate(year if month is not None else None, month if day is not None else None)
        self.plot()

        cursor = self.browser.find_element_by_id('cursor')
        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True, True)

        if (day is not None):
            self.plotChild(day)
        elif (month is not None):
            self.plotChild(month)
        else:
            self.plotChild(year)
        self.assertClassed(cursor, 'checked', False)
        self.assertCursor(False)

    @TestData([
        {'year': 2017, 'month': 8,    'day': 5},
    ])
    def testChildEmpty(self, year, month, day):
        self.selectDate(year, month)
        self.plot()

        cursor = self.browser.find_element_by_id('cursor')
        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True, True)

        self.plotChild(day)
        self.assertClassed(cursor, 'checked', False)
        self.assertClassed(cursor, 'disabled', True)
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
