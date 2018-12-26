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
from selenium.common import exceptions as selenium

from .PythonUtils.testdata import testData

from .helpers import recMax

from .browser_testcase import BrowserTestCase

class CursorTest(BrowserTestCase):
    def loadToday(self):
        self.browser.find_element_by_id('today').click()

    def loadTodayDCPower(self):
        self.browser.find_element_by_id('today').click()
        self.selectVar('pdc')

    def __assertLineCursor(self, paths, enabled):
        legendItems = self.getLegendItems()
        if all([len(i) == 4 for i in legendItems]):
            legendItemStyles = [(i, self.getStyle(i)) for i, t, b, c in legendItems]
        elif all([len(c) == 0 for t, b, c in legendItems]):
            legendItemStyles = [(i, self.getStyle(i)) for i, t, c in legendItems]
        else:
            legendItemStyles = [(c, self.getStyle(c)) for i, t, children in legendItems for c, t, b, x in children]

        for p in paths:
            c = self.parseColor(p.find_element_by_xpath('..').get_attribute('stroke'))
            o = float(p.get_attribute('stroke-opacity'))
            legendItem = [i for i, s in legendItemStyles if (s['color'] == c) and abs(float(s['opacity']) - o) < 1e-12]
            self.assertEqual(len(legendItem), 1)

            self.browser.execute_script("d3.select(arguments[0]).dispatch('mouseenter');", p)
            for o in paths:
                self.assertClassed(o, 'hovered', enabled and (o == p))
            for o, s in legendItemStyles:
                self.assertClassed(o, 'hovered', enabled and (o == legendItem[0]))

            self.browser.execute_script("d3.select(arguments[0]).dispatch('mouseleave');", p)
            for o in paths:
                self.assertClassed(o, 'hovered', False)
            for o, s in legendItemStyles:
                self.assertClassed(o, 'hovered', False)

            self.browser.execute_script("d3.select(arguments[0]).dispatch('click');", p)
            for o in paths:
                self.assertClassed(o, 'selected', enabled and (o == p))
            for o, s in legendItemStyles:
                self.assertClassed(o, 'hovered', enabled and (o == legendItem[0]))

            actions = ActionChains(self.browser)
            actions.move_to_element_with_offset(self.browser.find_element_by_id('chart'), 200, 200)
            actions.perform()

            if enabled:
                self.assertEqual(len(self.browser.find_element_by_id('xcursor').get_attribute('style')), 0)
                self.assertEqual(len(self.browser.find_element_by_id('ycursor').get_attribute('style')), 0)
            else:
                with self.assertRaises(selenium.NoSuchElementException):
                    self.browser.find_element_by_class_name('cursor')

            self.browser.execute_script("d3.select(arguments[0]).dispatch('click');", self.browser.find_element_by_id('chart'))
            with self.assertRaises(selenium.NoSuchElementException):
                self.browser.find_element_by_class_name('cursor')
            for o in paths:
                self.assertClassed(o, 'selected', False)
            for o, s in legendItemStyles:
                self.assertClassed(o, 'hovered', False)

    def __assertBarLegendItemHovered(self, bar, legendItemStyles, enabled):
        c = self.parseColor(bar.find_element_by_xpath('..').get_attribute('fill'))
        o = float(bar.get_attribute('fill-opacity'))
        legendItem = [i for i, s in legendItemStyles if (s['background-color'][0:3] == c) and abs(s['background-color'][3] - o) < 1e-12]
        self.assertEqual(len(legendItem), 1)

        for o, s in legendItemStyles:
            self.assertClassed(o, 'hovered', enabled and (o == legendItem[0]))

    def __assertBarHovered(self, bar, enabled):
        for o in self.getBars():
            self.assertClassed(o, 'hovered', enabled and (o == bar))

    def __assertBarXCursorLabel(self, bar, enabled):
        xMin = bar.find_element_by_xpath('../..').rect['x']
        xMax = xMin + bar.find_element_by_xpath('../..').rect['width']
        for t in self.browser.find_element_by_id('xaxis').find_elements_by_tag_name('text'):
            self.assertClassed(t, 'cursor', enabled and (xMin < t.rect['x']) and (t.rect['x'] < xMax))

    def __assertBarYCursorLabel(self, bar, data):
        yLabel = None
        # NOTE find_element_by_xpath does not work with SVG
        for e1 in self.browser.find_element_by_id('chart').find_elements_by_xpath('child::*'):
            if yLabel is not None:
                break
            for e2 in e1.find_elements_by_xpath('child::*'):
                if (e2.tag_name == 'text') and ('cursor' in self.getClasses(e2)):
                    yLabel = e2
                    break

        self.assertEqual(yLabel is not None, data is not None)
        if yLabel is not None:
            self.assertLess(abs(float(yLabel.text) - data), 1e-12)

            xLabelMin = yLabel.rect['x']
            xLabelMax = xLabelMin + yLabel.rect['width']
            xBarMin = bar.rect['x']
            xBarMax = xBarMin + bar.rect['width']
            self.assertTrue((xBarMin < xLabelMax) and (xLabelMin < xBarMax))

    def __assertBarCursor(self, bars, enabled, var, agg):
        legendItems = self.getLegendItems()
        if all([len(i) == 4 for i in legendItems]):
            legendItemStyles = [(i, self.getStyle(i)) for i, t, b, c in legendItems]
        elif all([len(c) == 0 for t, b, c in legendItems]):
            legendItemStyles = [(i, self.getStyle(i)) for i, t, c in legendItems]
        else:
            legendItemStyles = [(c, self.getStyle(c)) for i, t, children in legendItems for c, t, b, x in children]

        o = 0
        s = 0
        i = 0
        data = self.getData(var, agg)

        maxData = recMax(data)
        div = 1
        while (abs(maxData) >= 1000):
            div = div*1000
            maxData = maxData / 1000
        while (abs(maxData) <= 1):
            div = div / 1000
            maxData = maxData * 1000

        for b in bars:
            actions = ActionChains(self.browser)
            actions.move_to_element_with_offset(b, b.rect['width'] / 2, b.rect['height'] / 2)
            actions.perform()

            self.__assertBarHovered(b, enabled)
            self.__assertBarLegendItemHovered(b, legendItemStyles, enabled)
            self.__assertBarXCursorLabel(b, enabled)
            self.__assertBarYCursorLabel(b, data[o][s][i] / div if enabled else None)

            actions = ActionChains(self.browser)
            actions.move_to_element_with_offset(b, b.rect['width'] / 2, -10)
            actions.perform()

            self.__assertBarHovered(b, False)
            self.__assertBarLegendItemHovered(b, legendItemStyles, False)
            self.__assertBarXCursorLabel(b, False)
            self.__assertBarYCursorLabel(b, None)

            s = s + 1
            if (s >= len(data[o])):
                s = 0
                o = o + 1
                if (o >= len(data)):
                    o = 0
                    i = i + 1


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
        self.browser.find_element_by_id('today').click()

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
        self.browser.find_element_by_id('today').click()

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

    @testData([
        {'year': None, 'month': None, 'day': None},
        {'year': 2017, 'month': None, 'day': None},
        {'year': 2017, 'month': 8,    'day': None},
        {'year': 2017, 'month': 8,    'day': 8},
    ])
    def testDate(self, year, month, day):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
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

    @testData([
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
        self.browser.find_element_by_id('plot').click()
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

    @testData([
        {'year': None, 'month': None, 'day': None},
        {'year': 2017, 'month': None, 'day': None},
        {'year': 2017, 'month': 8,    'day': None},
        {'year': 2017, 'month': 8,    'day': 8},
    ])
    def testKeyDate(self, year, month, day):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
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

    @testData([
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
        self.browser.find_element_by_id('plot').click()
        self.loadData(year, month, day)

        cursor = self.browser.find_element_by_id('cursor')
        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True)

        self.selectDate(newYear, newMonth, newDay)
        self.browser.find_element_by_id('plot').click()
        self.assertClassed(cursor, 'checked', False)
        self.assertCursor(False)

    @testData([
        {'year': None, 'month': None, 'day': None},
        {'year': 2019, 'month': None, 'day': None},
        {'year': 2018, 'month': 2,    'day': None},
        {'year': 2017, 'month': 8,    'day': 8   },
    ])
    def testNoChangeDate(self, year, month, day):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.loadData(year, month, day)

        cursor = self.browser.find_element_by_id('cursor')
        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True)

        self.browser.find_element_by_id('plot').click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True)

    @testData([
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

    @testData([
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

    @testData([
        {'year': None, 'month': None, 'day': None},
        {'year': 2019, 'month': None, 'day': None},
        {'year': 2018, 'month': 2,    'day': None},
        {'year': 2017, 'month': 8,    'day': 6,  },
        {'year': 2017, 'month': 8,    'day': 8   },
    ])
    def testChangeToday(self, year, month, day):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.loadData(year, month, day)

        cursor = self.browser.find_element_by_id('cursor')
        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True)

        self.browser.find_element_by_id('today').click()
        self.assertClassed(cursor, 'checked', False)
        self.assertCursor(False)

    def testNoChangeToday(self):
        self.browser.find_element_by_id('today').click()

        cursor = self.browser.find_element_by_id('cursor')
        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True)

        self.browser.find_element_by_id('today').click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True)

    @testData([
        {'year': 2019, 'month': None, 'day': None},
        {'year': 2018, 'month': 2,    'day': None},
        {'year': 2017, 'month': 8,    'day': 8   },
    ])
    def testPrev(self, year, month, day):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.loadData(year, month, day)

        cursor = self.browser.find_element_by_id('cursor')
        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True)

        self.browser.find_element_by_id('prev').click()
        self.assertClassed(cursor, 'checked', False)
        self.assertCursor(False)

    @testData([
        {'year': 2009, 'month': None, 'day': None},
        {'year': 2010, 'month': 12,   'day': None},
        {'year': 2011, 'month': 6,    'day': 24  },
    ])
    def testNext(self, year, month, day):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.loadData(year, month, day)

        cursor = self.browser.find_element_by_id('cursor')
        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor(True)

        self.browser.find_element_by_id('next').click()
        self.assertClassed(cursor, 'checked', False)
        self.assertCursor(False)

    @testData([
        {'year': 2017, 'month': 8,    'day': 5},
    ])
    def testEmpty(self, year, month, day):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()

        cursor = self.browser.find_element_by_id('cursor')
        self.assertClassed(cursor, 'checked', False)
        self.assertClassed(cursor, 'disabled', True)
        self.assertCursor(False)

        cursor.click()
        self.assertClassed(cursor, 'checked', False)
        self.assertCursor(False)
