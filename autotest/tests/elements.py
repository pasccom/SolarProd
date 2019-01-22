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

class ElementsTest(BrowserTestCase):

    def testWindowTitle(self):
        self.assertIn('Ducomquet: Production solaire', self.browser.title)

    @TestData([
        {'name': 'year',    'enabled': True },
        {'name': 'month',   'enabled': False},
        {'name': 'day',     'enabled': False},
        {'name': 'var',     'enabled': False},
        {'name': 'sum',     'enabled': False},
    ])
    def testSelects(self, name, enabled):
        select = self.browser.find_element_by_id(name)
        self.assertEqual(select.tag_name, 'select')
        self.assertEqual(select.is_enabled(), enabled)
        self.assertEqual(select.size['height'], 28)

    @TestData([
        {'name': 'plot',    'enabled': True },
        {'name': 'today',   'enabled': True },
        {'name': 'prev',    'enabled': False},
        {'name': 'next',    'enabled': False},
        {'name': 'cursor',  'enabled': False},
        {'name': 'export',  'enabled': False},
        {'name': 'info',    'enabled': True },
        {'name': 'help',    'enabled': True },
    ])
    def testButtons(self, name, enabled):
        button = self.browser.find_element_by_id(name)
        self.assertEqual(button.tag_name, 'img')
        self.assertClassed(button, 'disabled', not enabled)
        self.assertEqual(button.size['width'], 28)
        self.assertEqual(button.size['height'], 28)

    def testExportToday(self):
        self.plot(True)

        export = self.browser.find_element_by_id('export')
        self.assertClassed(export, 'disabled', False)

    @TestData([
        {'year': None, 'month': None, 'day': None},
        {'year': 2017, 'month': None, 'day': None},
        {'year': 2017, 'month': 8,    'day': None},
        {'year': 2017, 'month': 8,    'day': 8},
    ])
    def testExportDate(self, year, month, day):
        self.selectDate(year, month, day)
        self.plot()

        export = self.browser.find_element_by_id('export')
        self.assertClassed(export, 'disabled', False)

    @TestData([
        {'year': 2017, 'month': 8,    'day': 5},
    ])
    def testExportEmpty(self, year, month, day):
        self.selectDate(year, month, day)
        self.plot()

        export = self.browser.find_element_by_id('export')
        self.assertClassed(export, 'disabled', True)

    def testHelp(self):
        self.assertEqual(self.browser.current_url, self.index)

        self.browser.find_element_by_id('help').click()
        self.assertEqual(self.browser.current_url, self.helpPage)
        self.assertIn('Ducomquet: Aide', self.browser.title)

        self.browser.find_element_by_id('close').click()
        self.assertEqual(self.browser.current_url, self.index)
