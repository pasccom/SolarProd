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

from .server_testcase import ServerTestCase
from .chart_testcase import ChartTestCase

import time

class DefaultPlotTest(ServerTestCase, ChartTestCase):

    def setUp(self):
        super().setUp(False)

    def __loadIndex(self, cookie=None):
        self.browser.get(self.index)
        if cookie is None:
            return
        self.browser.add_cookie(cookie)

        self.browser.get(self.index)
        time.sleep(1)
        self.assertEqual(self.browser.get_cookie(cookie['name'])['value'], str(cookie['value']))

    @TestData([
        {'level': -1, 'year': None, 'month': None, 'day': None},
        {'level':  0, 'year': None, 'month': None, 'day': None},
        {'level':  1, 'year': 2019, 'month': None, 'day': None},
        {'level':  2, 'year': 2018, 'month':    2, 'day': None},
        {'level':  3, 'year': 2017, 'month':    8, 'day':    8},
    ])
    def testSelectors(self, level, year, month, day):
        self.__loadIndex({
            'name': 'defaultPlot',
            'value': str(level),
        })

        self.assertDate(year, month, day)

    @TestData([
        {'level': -1, 'prevEnabled': False, 'nextEnabled': False, 'upEnabled': False},
        {'level':  0, 'prevEnabled': False, 'nextEnabled': False, 'upEnabled': False},
        {'level':  1, 'prevEnabled':  True, 'nextEnabled': False, 'upEnabled':  True},
        {'level':  2, 'prevEnabled':  True, 'nextEnabled': False, 'upEnabled':  True},
        {'level':  3, 'prevEnabled':  True, 'nextEnabled': False, 'upEnabled':  True},
    ])
    def testButtons(self, level, prevEnabled, nextEnabled, upEnabled):
        self.__loadIndex({
            'name': 'defaultPlot',
            'value': str(level),
        })

        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')
        parentButton = self.browser.find_element_by_id('up')

        self.assertClassed(prevButton, 'disabled', not prevEnabled)
        self.assertClassed(nextButton, 'disabled', not nextEnabled)
        self.assertClassed(parentButton, 'disabled', not upEnabled)

    @TestData([
        {'level': -1, 'year': None, 'month': None, 'day': None},
    ])
    def testEmptyPlot(self, level, year, month, day):
        self.__loadIndex({
            'name': 'defaultPlot',
            'value': str(level),
        })

        self.assertEqual(len(self.getAxis('xaxis').find_elements_by_xpath('./*')), 0)
        self.assertEqual(len(self.getAxis('yaxis').find_elements_by_xpath('./*')), 0)
        self.assertEqual(len(self.getLines()), 0)
        self.assertEqual(len(self.getBars()), 0)

    @TestData([
        {'level':  0, 'year': None, 'month': None, 'day': None},
        {'level':  1, 'year': 2019, 'month': None, 'day': None},
        {'level':  2, 'year': 2018, 'month':    2, 'day': None},
    ])
    def testBarPlot(self, level, year, month, day):
        self.__loadIndex({
            'name': 'defaultPlot',
            'value': str(level),
        })

        # Check data:
        self.loadData(year, month, day)
        self.assertBarsEqual(self.getBarData(), self.getData('dates'), self.getData('nrj', 'sum'))

        # Check x axis:
        xTickLabels = self.getTickLabels('xaxis')
        self.assertRangeEqual(self.getRange('xaxis', True), (float(min(xTickLabels)), float(max(xTickLabels) + 1)))
        self.assertEqual(self.getTickLabels('xaxis'), self.getData('dates'))
        self.assertEqual(self.getTickLength('xaxis'), 6.)

        # Check y axis:
        self.assertRangeEqual(self.getRange('yaxis', False), self.getDataRange('nrj', 'sum'))
        self.assertEqual(self.getTickLength('yaxis'), -6.)

        self.clearMapFunctions()

    @TestData([
        {'level':  3},
    ])
    def testLinePlot(self, level):
        self.__loadIndex({
            'name': 'defaultPlot',
            'value': str(level),
        })

        # Check data:
        self.loadData('today')
        self.assertCoordinatesEqual(self.getLineData(), self.getData('dates'), self.getData('nrj', 'sum'))

        # Check x axis:
        xTickLabels = self.getTickLabels('xaxis')
        self.assertEqual(xTickLabels, list(range(int(min(xTickLabels)), int(max(xTickLabels) + 1))))
        self.assertRangeEqual(self.getRange('xaxis', False), self.getDataRange('dates'))
        self.assertEqual(self.getTickLength('xaxis'), 6.)

        # Check y axis:
        self.assertRangeEqual(self.getRange('yaxis', False), self.getDataRange('nrj', 'sum'))
        self.assertEqual(self.getTickLength('yaxis'), -6.)
