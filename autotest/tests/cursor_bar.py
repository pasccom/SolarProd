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

from .PythonUtils.testdata import TestData

from .chart_testcase import ChartTestCase

class CursorBarTest(ChartTestCase):

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

    def assertCursor(self):
        barData = self.getBars(self.parseRect)
        div = self.getDivider([r[1] for b, r in barData])

        for b, r in barData:
            actions = ActionChains(self.browser)
            actions.move_to_element_with_offset(b, b.rect['width'] / 2, b.rect['height'] / 2)
            actions.perform()

            self.assertClassed(b, 'hovered', True)
            self.__assertBarXCursorLabel(b, True)
            self.__assertBarYCursorLabel(b, r[1] / div)

            actions = ActionChains(self.browser)
            actions.move_to_element_with_offset(b, b.rect['width'] / 2, -10)
            actions.perform()

            self.assertClassed(b, 'hovered', False)
            self.__assertBarXCursorLabel(b, False)
            self.__assertBarYCursorLabel(b, None)

    @TestData([
        {'year': None, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': None, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2017, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': 2017, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': 2017, 'month': 8,    'day': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': None, 'var': 'pwr',  'agg': 'sum'},
        {'year': 2017, 'month': 8,    'day': None, 'var': 'pwr',  'agg': 'inv'},
    ])
    def testEnabled(self, year, month, day, var, agg):
        self.loadData(year, month, day)

        self.selectDate(year, month, day)
        self.plot()
        self.selectVar(var)
        self.selectSum(agg)

        cursor = self.browser.find_element_by_id('cursor')

        cursor.click()
        self.assertClassed(cursor, 'checked', True)
        self.assertCursor()
