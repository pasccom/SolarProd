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

import os

from .PythonUtils.testdata import TestData

from .browser_testcase import BrowserTestCase

class TabInteractionTest(BrowserTestCase):
    def __checkConsistency(self):
        return all(tabActive == pageDisplayed
                   for tabActive, pageDisplayed
                   in zip(['active-tab' in self.getClasses(t) for t in self.tabs],
                          [p.value_of_css_property('display') != 'none' for p in self.pages]))

    def setUp(self):
        super().setUp(True)
        self.browser.find_element_by_id('info').click()
        tabView = self.browser.find_element_by_class_name('popup').find_element_by_id('content')
        self.tabs = tabView.find_element_by_tag_name('ul').find_elements_by_tag_name('li')
        self.pages = tabView.find_element_by_tag_name('div').find_elements_by_tag_name('div')



    def testClick(self):
        self.assertEqual(len(self.tabs), len(self.pages))
        self.assertTrue('active-tab' in self.getClasses(self.tabs[0]))
        self.assertTrue(self.__checkConsistency())

        for tab in self.tabs:
            tab.click()
            self.assertTrue('active-tab' in self.getClasses(tab))
            self.assertTrue(self.__checkConsistency())

    def testHover(self):
        self.assertTrue(all(self.parseColor(t.value_of_css_property('background-color')) != (187, 221, 255)
                            for t in self.tabs))

        for tab in self.tabs:
            ActionChains(self.browser).move_to_element(tab).perform()
            self.assertEqual(self.parseColor(tab.value_of_css_property('background-color')), (187, 221, 255))
            self.assertTrue(all(self.parseColor(t.value_of_css_property('background-color')) != (187, 221, 255)
                                 for t in self.tabs if t is not tab))


