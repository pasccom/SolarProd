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

import random

from .PythonUtils.testdata import TestData

from .cookies_testcase import CookiesTestCase

class ConfigHomeTest(CookiesTestCase):

    def setUpConfigHome(self):
        self.browser.find_element_by_id('config').click()

        buttons = self.browser.find_element_by_class_name('popup')      \
                              .find_element_by_class_name('buttonBox')  \
                              .find_elements_by_tag_name('input')
        self.okButton = next((b for b in buttons if b.get_attribute('value') == 'Valider'), None)
        self.cancelButton = next((b for b in buttons if b.get_attribute('value') == 'Annuler'), None)
        self.assertIsNotNone(self.okButton)
        self.assertIsNotNone(self.cancelButton)

        self.page = self.browser.find_element_by_class_name('popup').find_element_by_id('content')
        #tabView = self.browser.find_element_by_class_name('popup').find_element_by_id('content')
        #tabPages = zip(tabView.find_element_by_tag_name('ul').find_elements_by_tag_name('li'),
        #               tabView.find_element_by_tag_name('div').find_elements_by_tag_name('div'))
        #tabPages = [tp for tp in tabPages if tp[1].get_attribute('id') == 'home']
        #self.assertEqual(len(tabPages), 1)
        #self.tab, self.page = tabPages[0]

        #self.tab.click()
        self.assertEqual(self.page.value_of_css_property('display'), 'block')

    def __makeChoices(self):
        initChoices = {}
        choices = {}

        for s in ['defaultDate', 'defaultVar', 'defaultSum']:
            select = self.page.find_element_by_id(s)
            initChoices[s] = select.get_property('value')
            random.choice([o for o in self.waitOptions(select)
                               if (o.text != '') and (o.get_attribute('value') not in ['0', '1', 'udc', 'temp', initChoices[s]])]).click()
            choices[s] = select.get_property('value')

            self.assertNotEqual(choices[s], '')
            self.assertNotEqual(choices[s], initChoices[s])

        return choices

    @TestData([
        {'level': None, 'var':   None, 'agg':  None, 'varEnabled': False, 'aggEnabled': False},
        {'level':   -1, 'var':   None, 'agg':  None, 'varEnabled': False, 'aggEnabled': False},
        {'level':    0, 'var':   None, 'agg':  None, 'varEnabled':  True, 'aggEnabled': False},
        {'level':    0, 'var':  'nrj', 'agg':  None, 'varEnabled':  True, 'aggEnabled':  True},
        {'level':    0, 'var':  'nrj', 'agg': 'sum', 'varEnabled':  True, 'aggEnabled':  True},
        {'level':    0, 'var':  'nrj', 'agg': 'inv', 'varEnabled':  True, 'aggEnabled':  True},
        {'level':    1, 'var':   None, 'agg':  None, 'varEnabled':  True, 'aggEnabled': False},
        {'level':    1, 'var':  'nrj', 'agg':  None, 'varEnabled':  True, 'aggEnabled':  True},
        {'level':    1, 'var':  'nrj', 'agg': 'sum', 'varEnabled':  True, 'aggEnabled':  True},
        {'level':    1, 'var':  'nrj', 'agg': 'inv', 'varEnabled':  True, 'aggEnabled':  True},
        {'level':    2, 'var':   None, 'agg':  None, 'varEnabled':  True, 'aggEnabled': False},
        {'level':    2, 'var':  'nrj', 'agg':  None, 'varEnabled':  True, 'aggEnabled':  True},
        {'level':    2, 'var':  'nrj', 'agg': 'sum', 'varEnabled':  True, 'aggEnabled':  True},
        {'level':    2, 'var':  'nrj', 'agg': 'inv', 'varEnabled':  True, 'aggEnabled':  True},
        {'level':    2, 'var':  'pwr', 'agg':  None, 'varEnabled':  True, 'aggEnabled':  True},
        {'level':    2, 'var':  'pwr', 'agg': 'sum', 'varEnabled':  True, 'aggEnabled':  True},
        {'level':    2, 'var':  'pwr', 'agg': 'inv', 'varEnabled':  True, 'aggEnabled':  True},
        {'level':    3, 'var':   None, 'agg':  None, 'varEnabled':  True, 'aggEnabled': False},
        {'level':    3, 'var':  'nrj', 'agg':  None, 'varEnabled':  True, 'aggEnabled':  True},
        {'level':    3, 'var':  'nrj', 'agg': 'sum', 'varEnabled':  True, 'aggEnabled':  True},
        {'level':    3, 'var':  'nrj', 'agg': 'inv', 'varEnabled':  True, 'aggEnabled':  True},
        {'level':    3, 'var':  'pac', 'agg': 'sum', 'varEnabled':  True, 'aggEnabled':  True},
        {'level':    3, 'var':  'pac', 'agg': 'inv', 'varEnabled':  True, 'aggEnabled':  True},
        {'level':    3, 'var':  'pdc', 'agg': 'sum', 'varEnabled':  True, 'aggEnabled':  True},
        {'level':    3, 'var':  'pdc', 'agg': 'inv', 'varEnabled':  True, 'aggEnabled':  True},
        {'level':    3, 'var':  'pdc', 'agg': 'str', 'varEnabled':  True, 'aggEnabled':  True},
        {'level':    3, 'var':  'udc', 'agg': 'str', 'varEnabled':  True, 'aggEnabled':  True},
        {'level':    3, 'var': 'temp', 'agg': 'inv', 'varEnabled':  True, 'aggEnabled':  True},
    ])
    def testInit(self, level, var, agg, varEnabled, aggEnabled):
        self.setUpCookies([{
            'name': 'defaultDate',
            'value': str(level),
        }, {
            'name': 'defaultVar',
            'value': str(var),
        }, {
            'name': 'defaultSum',
            'value': str(agg),
        }])
        self.setUpConfigHome()

        self.assertEqual(self.page.find_element_by_id('defaultDate').get_property('value'), str(level) if level is not None else '')
        self.assertEqual(self.page.find_element_by_id('defaultVar').get_property('disabled'), not varEnabled)
        self.assertEqual(self.page.find_element_by_id('defaultVar').get_property('value'), var or '')
        self.assertEqual(self.page.find_element_by_id('defaultSum').get_property('disabled'), not aggEnabled)
        self.assertEqual(self.page.find_element_by_id('defaultSum').get_property('value'), agg or '')

    def testCancelNoCookie(self):
        self.setUpCookies(None)
        self.setUpConfigHome()

        self.__makeChoices()
        self.cancelButton.click()

        self.assertCookie('defaultDate', None)
        self.assertCookie('defaultVar', None)
        self.assertCookie('defaultSum', None)

    def testValidNoCookie(self):
        self.setUpCookies(None)
        self.setUpConfigHome()

        choices = self.__makeChoices()
        self.okButton.click()

        self.assertCookies(choices)

    @TestData([
        {'level': None, 'var':   None, 'agg':  None},
        {'level':   -1, 'var':   None, 'agg':  None},
        {'level':    0, 'var':   None, 'agg':  None},
        {'level':    1, 'var':   None, 'agg':  None},
        {'level':    2, 'var':   None, 'agg':  None},
        {'level':    2, 'var':  'nrj', 'agg':  None},
        {'level':    2, 'var':  'nrj', 'agg': 'sum'},
        {'level':    2, 'var':  'nrj', 'agg': 'inv'},
        {'level':    2, 'var':  'pwr', 'agg':  None},
        {'level':    2, 'var':  'pwr', 'agg': 'sum'},
        {'level':    2, 'var':  'pwr', 'agg': 'inv'},
        {'level':    3, 'var':   None, 'agg':  None},
        {'level':    3, 'var':  'nrj', 'agg':  None},
        {'level':    3, 'var':  'nrj', 'agg': 'sum'},
        {'level':    3, 'var':  'nrj', 'agg': 'inv'},
        {'level':    3, 'var':  'pac', 'agg': 'sum'},
        {'level':    3, 'var':  'pac', 'agg': 'inv'},
        {'level':    3, 'var':  'pdc', 'agg': 'sum'},
        {'level':    3, 'var':  'pdc', 'agg': 'inv'},
        {'level':    3, 'var':  'pdc', 'agg': 'str'},
        {'level':    3, 'var':  'udc', 'agg': 'str'},
        {'level':    3, 'var': 'temp', 'agg': 'inv'},
    ])
    def testCancelCookie(self, level, var, agg):
        self.setUpCookies([{
            'name': 'defaultDate',
            'value': str(level),
        }, {
            'name': 'defaultVar',
            'value': str(var),
        }, {
            'name': 'defaultSum',
            'value': str(agg),
        }])
        self.setUpConfigHome()

        self.__makeChoices()
        self.cancelButton.click()

        self.assertCookie('defaultDate', level)
        self.assertCookie('defaultVar', var)
        self.assertCookie('defaultSum', agg)

    @TestData([
        {'level': None, 'var':   None, 'agg':  None},
        {'level':   -1, 'var':   None, 'agg':  None},
        {'level':    0, 'var':   None, 'agg':  None},
        {'level':    1, 'var':   None, 'agg':  None},
        {'level':    2, 'var':   None, 'agg':  None},
        {'level':    2, 'var':  'nrj', 'agg':  None},
        {'level':    2, 'var':  'nrj', 'agg': 'sum'},
        {'level':    2, 'var':  'nrj', 'agg': 'inv'},
        {'level':    2, 'var':  'pwr', 'agg':  None},
        {'level':    2, 'var':  'pwr', 'agg': 'sum'},
        {'level':    2, 'var':  'pwr', 'agg': 'inv'},
        {'level':    3, 'var':   None, 'agg':  None},
        {'level':    3, 'var':  'nrj', 'agg':  None},
        {'level':    3, 'var':  'nrj', 'agg': 'sum'},
        {'level':    3, 'var':  'nrj', 'agg': 'inv'},
        {'level':    3, 'var':  'pac', 'agg': 'sum'},
        {'level':    3, 'var':  'pac', 'agg': 'inv'},
        {'level':    3, 'var':  'pdc', 'agg': 'sum'},
        {'level':    3, 'var':  'pdc', 'agg': 'inv'},
        {'level':    3, 'var':  'pdc', 'agg': 'str'},
        {'level':    3, 'var':  'udc', 'agg': 'str'},
        {'level':    3, 'var': 'temp', 'agg': 'inv'},
    ])
    def testValidCookie(self, level, var, agg):
        self.setUpCookies([{
            'name': 'defaultDate',
            'value': str(level),
        }, {
            'name': 'defaultVar',
            'value': str(var),
        }, {
            'name': 'defaultSum',
            'value': str(agg),
        }])
        self.setUpConfigHome()

        choices = self.__makeChoices()
        self.okButton.click()

        self.assertCookies(choices)
