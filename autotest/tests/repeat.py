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

class RepeatTest(ServerTestCase):
    @TestData([2, 3])
    def testYears(self, repeat):
        self.browser.get(self.index)
        self.server.clear_request_log()
        self.clickButton(self.browser.find_element_by_id('plot'), repeat).perform()

        self.assertDate(wait=2)
        self.assertDataRequests([self.dataPath()], wait=2)

    @TestData([
        {'year': 2009, 'repeat': 2},
        {'year': 2010, 'repeat': 2},
        {'year': 2011, 'repeat': 2},
        {'year': 2017, 'repeat': 2},
        {'year': 2018, 'repeat': 2},
        {'year': 2019, 'repeat': 2},
        {'year': 2009, 'repeat': 3},
        {'year': 2010, 'repeat': 3},
        {'year': 2011, 'repeat': 3},
        {'year': 2017, 'repeat': 3},
        {'year': 2018, 'repeat': 3},
        {'year': 2019, 'repeat': 3},
    ])
    def testYear(self, year, repeat):
        self.browser.get(self.index)
        self.selectDate(year)
        self.server.clear_request_log()
        self.clickButton(self.browser.find_element_by_id('plot'), repeat).perform()

        self.assertDate(year, wait=2)
        self.assertDataRequests([self.dataPath(year)], wait=2)

    @TestData([
        {'year': 2010, 'month': 12, 'repeat': 2},
        {'year': 2011, 'month': 6,  'repeat': 2},
        {'year': 2011, 'month': 8,  'repeat': 2},
        {'year': 2017, 'month': 6,  'repeat': 2},
        {'year': 2017, 'month': 8,  'repeat': 2},
        {'year': 2018, 'month': 2,  'repeat': 2},
        {'year': 2010, 'month': 12, 'repeat': 3},
        {'year': 2011, 'month': 6,  'repeat': 3},
        {'year': 2011, 'month': 8,  'repeat': 3},
        {'year': 2017, 'month': 6,  'repeat': 3},
        {'year': 2017, 'month': 8,  'repeat': 3},
        {'year': 2018, 'month': 2,  'repeat': 3},
    ])
    def testMonth(self, year, month, repeat):
        self.browser.get(self.index)
        self.selectDate(year, month)
        self.server.clear_request_log()
        self.clickButton(self.browser.find_element_by_id('plot'), repeat).perform()

        self.assertDate(year, month, wait=2)
        self.assertDataRequests([self.dataPath(year, month)], wait=2)

    @TestData([
        {'year': 2011, 'month': 6, 'day': 24, 'repeat': 2},
        {'year': 2011, 'month': 6, 'day': 26, 'repeat': 2},
        {'year': 2017, 'month': 8, 'day': 6,  'repeat': 2},
        {'year': 2017, 'month': 8, 'day': 8,  'repeat': 2},
        {'year': 2011, 'month': 6, 'day': 24, 'repeat': 3},
        {'year': 2011, 'month': 6, 'day': 26, 'repeat': 3},
        {'year': 2017, 'month': 8, 'day': 6,  'repeat': 3},
        {'year': 2017, 'month': 8, 'day': 8,  'repeat': 3},
    ])
    def testDay(self, year, month, day, repeat):
        self.browser.get(self.index)
        self.selectDate(year, month, day)
        self.server.clear_request_log()
        self.clickButton(self.browser.find_element_by_id('plot'), repeat).perform()

        self.assertDate(year, month, day, wait=2)
        self.assertDataRequests([self.dataPath(year, month, day)], wait=2)

    @TestData([2, 3])
    def testToday(self, repeat):
        self.browser.get(self.index)
        self.server.clear_request_log()
        self.clickButton(self.browser.find_element_by_id('today'), repeat).perform()

        self.assertDate(2017, 8, 8, wait=2)
        self.assertDataRequests([self.dataPath('today')], wait=2)
