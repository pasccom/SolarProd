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
from selenium.common import exceptions as selenium

from .PythonUtils.testdata import TestData

import random

from .helpers import interpolate, formatTime, formatOrdinate

from .chart_testcase import ChartTestCase

class CursorLineTest(ChartTestCase):

    def __asssertCursorHidden(self, x, y):
        actions = ActionChains(self.browser)
        actions.move_to_element_with_offset(self.browser.find_element_by_id('chart'), x, y)
        actions.perform()

        self.assertEqual(self.browser.find_element_by_id('xcursor').get_attribute('style'), 'display: none;')
        self.assertEqual(self.browser.find_element_by_id('ycursor').get_attribute('style'), 'display: none;')

    def assertCursor(self):
        lineData = self.getLines(self.parsePath)
        div = self.getDivider([d for l, d in lineData])

        chart = self.browser.find_element_by_id('chart')
        xMin = 61
        xMax = xMin - 1 + (chart.rect['width'] - 80) / 1.025
        yMin = 20
        yMax = chart.rect['height'] - 40

        for l, data in lineData:
            self.browser.execute_script("d3.select(arguments[0]).dispatch('click');", l)
            self.assertClassed(l, 'selected', True)

            x = xMin
            while (x < xMax):
                y = random.uniform(yMin, yMax)

                actions = ActionChains(self.browser)
                actions.move_to_element_with_offset(chart, x, y)
                actions.perform()

                xCursor = self.browser.find_element_by_id('xcursor')
                yCursor = self.browser.find_element_by_id('ycursor')

                self.assertEqual(len(xCursor.get_attribute('style')), 0)
                self.assertEqual(len(yCursor.get_attribute('style')), 0)

                xCursorCoords = self.toDataCoords(self.parseTranslate(xCursor))
                yCursorCoords = self.toDataCoords(self.parseTranslate(yCursor))
                yCursorExpected = interpolate(data, xCursorCoords[0])
                self.assertAlmostEqual(yCursorExpected, yCursorCoords[1])

                self.assertEqual(xCursor.find_element_by_tag_name('text').text, formatTime(xCursorCoords[0]))
                self.assertEqual(yCursor.find_element_by_tag_name('text').text, formatOrdinate(yCursorExpected / div))

                x = x + (xMax - xMin) / 12

            self.__asssertCursorHidden(59, random.uniform(yMin, yMax))
            self.__asssertCursorHidden(chart.rect['width'] - 18, random.uniform(yMin, yMax))
            self.__asssertCursorHidden(random.uniform(xMin, xMax), 18)
            self.__asssertCursorHidden(random.uniform(xMin, xMax), chart.rect['height'] - 39)

            self.browser.execute_script("d3.select(arguments[0]).dispatch('click');", chart)
            with self.assertRaises(selenium.NoSuchElementException):
                self.browser.find_element_by_class_name('cursor')
            self.assertClassed(l, 'selected', False)

    @TestData([
        {'var': 'nrj',  'agg': 'sum'},
        {'var': 'nrj',  'agg': 'inv'},
        {'var': 'pac',  'agg': 'sum'},
        {'var': 'pac',  'agg': 'inv'},
        {'var': 'pdc',  'agg': 'sum'},
        {'var': 'pdc',  'agg': 'inv'},
        {'var': 'pdc',  'agg': 'str'},
        {'var': 'udc',  'agg': 'str'},
        {'var': 'temp', 'agg': 'inv'},
    ])
    def testToday(self, var, agg):
        self.plot(True)
        self.selectVar(var)
        self.selectSum(agg)

        cursor = self.browser.find_element_by_id('cursor')

        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor()

    @TestData([
        {'var': 'nrj',  'agg': 'sum'},
        {'var': 'nrj',  'agg': 'inv'},
        {'var': 'pac',  'agg': 'sum'},
        {'var': 'pac',  'agg': 'inv'},
        {'var': 'pdc',  'agg': 'sum'},
        {'var': 'pdc',  'agg': 'inv'},
        {'var': 'pdc',  'agg': 'str'},
        {'var': 'udc',  'agg': 'str'},
        {'var': 'temp', 'agg': 'inv'},
    ])
    def testSubsampled(self, var, agg):
        self.selectDate(2017, 8, 6)
        self.plot()
        self.selectVar(var)
        self.selectSum(agg)

        cursor = self.browser.find_element_by_id('cursor')

        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor()
