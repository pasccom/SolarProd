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

from .PythonUtils.testdata import TestData

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys as Key

from .browser_testcase import BrowserTestCase

class PopupInteractionTest(BrowserTestCase):

    def assertPopup(self, n, title=None, icon=None):
        self.assertEqual(len(self.browser.find_elements_by_class_name('overlay')), n)
        self.assertEqual(len(self.browser.find_elements_by_class_name('popup')), n)

        if (n == 0):
            return

        closeButton = self.browser.find_element_by_class_name('popup').find_element_by_id('close')
        self.assertTrue(closeButton.get_attribute('src').endswith('img/close.png'))

        titleElement = self.browser.find_element_by_class_name('popup').find_element_by_tag_name('h4')
        if title is not None:
            self.assertEqual(titleElement.text, title)
        if icon is not None:
            self.assertTrue(titleElement.find_element_by_tag_name('img').get_attribute('src').endswith(icon))


    @TestData([
        {'popup': 'config', 'title': 'Configuration', 'icon': 'img/config.png'},
        {'popup':   'info', 'title':      'À propos', 'icon':   'img/info.png'},
        {'popup':   'help', 'title':          'Aide', 'icon':   'img/help.png'},
    ])
    def testCloseButton(self, popup, title, icon):
        self.browser.find_element_by_id(popup).click()
        self.assertPopup(1, title, icon)

        self.browser.find_element_by_class_name('popup').find_element_by_id('close').click()
        self.assertPopup(0)

    @TestData([
        {'popup': 'config', 'title': 'Configuration', 'icon': 'img/config.png'},
        {'popup':   'info', 'title':      'À propos', 'icon':   'img/info.png'},
        {'popup':   'help', 'title':          'Aide', 'icon':   'img/help.png'},
    ])
    def testEscapeKey(self, popup, title, icon):
        self.browser.find_element_by_id(popup).click()
        self.assertPopup(1, title, icon)

        self.pressKeys([Key.ESCAPE]).perform()
        self.assertPopup(0)

    @TestData([
        {'px': 0.5, 'pw': 0,   'ww': 0,   'py': 0.5, 'ph': 0,   'wh': 0,   'popup' : 'config'},
        {'px': 0,   'pw': 0,   'ww': 0.5, 'py': 0.5, 'ph': 0,   'wh': 0,   'popup' : 'config'},
        {'px': 0.5, 'pw': 0.5, 'ww': 0.5, 'py': 0.5, 'ph': 0,   'wh': 0,   'popup' : 'config'},
        {'px': 0.5, 'pw': 0,   'ww': 0,   'py': 0,   'ph': 0,   'wh': 0.5, 'popup' : 'config'},
        {'px': 0.5, 'pw': 0.5, 'ww': 0.5, 'py': 0,   'ph': 0,   'wh': 0.5, 'popup' : 'config'},
        {'px': 0.5, 'pw': 0,   'ww': 0,   'py': 0.5, 'ph': 0.5, 'wh': 0.5, 'popup' : 'config'},
        {'px': 0,   'pw': 0,   'ww': 0.5, 'py': 0.5, 'ph': 0.5, 'wh': 0.5, 'popup' : 'config'},
        {'px': 0.5, 'pw': 0.5, 'ww': 0.5, 'py': 0.5, 'ph': 0.5, 'wh': 0.5, 'popup' : 'config'},
        {'px': 0.5, 'pw': 0,   'ww': 0,   'py': 0.5, 'ph': 0,   'wh': 0,   'popup' :   'info'},
        {'px': 0,   'pw': 0,   'ww': 0.5, 'py': 0.5, 'ph': 0,   'wh': 0,   'popup' :   'info'},
        {'px': 0.5, 'pw': 0.5, 'ww': 0.5, 'py': 0.5, 'ph': 0,   'wh': 0,   'popup' :   'info'},
        {'px': 0.5, 'pw': 0,   'ww': 0,   'py': 0,   'ph': 0,   'wh': 0.5, 'popup' :   'info'},
        {'px': 0.5, 'pw': 0.5, 'ww': 0.5, 'py': 0,   'ph': 0,   'wh': 0.5, 'popup' :   'info'},
        {'px': 0.5, 'pw': 0,   'ww': 0,   'py': 0.5, 'ph': 0.5, 'wh': 0.5, 'popup' :   'info'},
        {'px': 0,   'pw': 0,   'ww': 0.5, 'py': 0.5, 'ph': 0.5, 'wh': 0.5, 'popup' :   'info'},
        {'px': 0.5, 'pw': 0.5, 'ww': 0.5, 'py': 0.5, 'ph': 0.5, 'wh': 0.5, 'popup' :   'info'},
        {'px': 0.5, 'pw': 0,   'ww': 0,   'py': 0.5, 'ph': 0,   'wh': 0,   'popup' :   'help'},
        {'px': 0,   'pw': 0,   'ww': 0.5, 'py': 0.5, 'ph': 0,   'wh': 0,   'popup' :   'help'},
        {'px': 0.5, 'pw': 0.5, 'ww': 0.5, 'py': 0.5, 'ph': 0,   'wh': 0,   'popup' :   'help'},
        {'px': 0.5, 'pw': 0,   'ww': 0,   'py': 0,   'ph': 0,   'wh': 0.5, 'popup' :   'help'},
        {'px': 0.5, 'pw': 0.5, 'ww': 0.5, 'py': 0,   'ph': 0,   'wh': 0.5, 'popup' :   'help'},
        {'px': 0.5, 'pw': 0,   'ww': 0,   'py': 0.5, 'ph': 0.5, 'wh': 0.5, 'popup' :   'help'},
        {'px': 0,   'pw': 0,   'ww': 0.5, 'py': 0.5, 'ph': 0.5, 'wh': 0.5, 'popup' :   'help'},
        {'px': 0.5, 'pw': 0.5, 'ww': 0.5, 'py': 0.5, 'ph': 0.5, 'wh': 0.5, 'popup' :   'help'},
    ])
    def testClickOutside(self, popup, px, py, pw, ph, ww, wh):
        self.browser.find_element_by_id(popup).click()
        self.assertPopup(1)

        popupRect = self.browser.find_element_by_class_name('popup').rect
        windowSize = (self.browser.execute_script('return window.innerWidth;'),
                      self.browser.execute_script('return window.innerHeight;'))
        if (windowSize[0] < 362) or (windowSize[1] < 462):
            self.skipTest('Window is too small')

        actions = ActionChains(self.browser)
        actions.move_to_element_with_offset(self.browser.find_element_by_class_name('overlay'),
                                            px*popupRect['x'] + pw*popupRect['width'] + ww*windowSize[0],
                                            py*popupRect['y'] + ph*popupRect['height'] + wh*windowSize[1])
        actions.click()
        actions.perform()
        self.assertPopup(0)

    @TestData([
        {'yOffset': 15, 'popup': 'config'},
        {'yOffset': 45, 'popup': 'config'},
        {'yOffset': 15, 'popup':   'info'},
        {'yOffset': 45, 'popup':   'info'},
        {'yOffset': 15, 'popup':   'help'},
        {'yOffset': 45, 'popup':   'help'},
    ])
    def testClickInside(self, popup, yOffset):
        self.browser.find_element_by_id(popup).click()
        self.assertPopup(1)

        actions = ActionChains(self.browser)
        actions.move_to_element_with_offset(self.browser.find_element_by_class_name('popup'), 15, yOffset)
        actions.click()
        actions.perform()
        self.assertPopup(1)

        self.browser.find_element_by_class_name('popup').find_element_by_id('close').click()
        self.assertPopup(0)
