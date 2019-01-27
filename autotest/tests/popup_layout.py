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

from selenium import webdriver

import os

from .PythonUtils.testdata import TestData

from .testcase import TestCase

class PopupLayoutTest(TestCase):
    def setUpBrowser(self, expectedSize):
        profile = webdriver.FirefoxProfile(os.path.join(self.profilesDir, '{}x{}'.format(expectedSize[0], expectedSize[1])))
        self.browser = webdriver.Firefox(profile)
        actualSize = (self.browser.execute_script('return window.innerWidth;'),
                      self.browser.execute_script('return window.innerHeight;'))
        if (actualSize != expectedSize):
            self.browser.close()
            self.browser = None
            self.skipTest('Could not set properly browser window size: {} != {}'.format(actualSize, expectedSize))

        self.browser.get(self.index)

    def tearDown(self):
        if (self.browser is not None):
            self.browser.close()
            self.browser = None


    @TestData([
        {'size': (1024, 680), 'button': 'info'},
        {'size': (724,  660), 'button': 'info'},
        {'size': (1024, 680), 'button': 'help'},
        {'size': (724,  660), 'button': 'help'},
    ])
    def testLargeSizes(self, size, button):
        self.setUpBrowser(size)
        self.browser.find_element_by_id(button).click()

        overlay = self.browser.find_element_by_class_name('overlay')
        self.assertEqual(overlay.rect['x'], 0)
        self.assertEqual(overlay.rect['y'], 0)
        self.assertEqual(overlay.rect['width'], size[0])
        self.assertEqual(overlay.rect['height'], size[1])

        popup = self.browser.find_element_by_class_name('popup')
        self.assertEqual(popup.rect['x'], 0.25*size[0])
        self.assertEqual(popup.rect['y'], 0.15*size[1])
        self.assertEqual(popup.rect['width'], 0.5*size[0])
        self.assertEqual(popup.rect['height'], round(0.7*size[1]))

        content = popup.find_element_by_id('content')
        self.assertEqual(content.rect['x'], 0.25*size[0])
        self.assertEqual(content.rect['y'], 0.15*size[1] + 32)
        self.assertEqual(content.rect['width'], 0.5*size[0])
        self.assertEqual(content.rect['height'], round(0.7*size[1]) - 32)

        self.browser.close()
        self.browser = None

    @TestData([
        {'size': (723, 659), 'button': 'info'},
        {'size': (362, 462), 'button': 'info'},
        {'size': (723, 659), 'button': 'help'},
        {'size': (362, 462), 'button': 'help'},
    ])
    def testSmallSizes(self, size, button):
        self.setUpBrowser(size)
        self.browser.find_element_by_id(button).click()

        overlay = self.browser.find_element_by_class_name('overlay')
        self.assertEqual(overlay.rect['x'], 0)
        self.assertEqual(overlay.rect['y'], 0)
        self.assertEqual(overlay.rect['width'], size[0])
        self.assertEqual(overlay.rect['height'], size[1])

        popup = self.browser.find_element_by_class_name('popup')
        self.assertEqual(popup.rect['x'], (size[0] - 362) / 2)
        self.assertEqual(popup.rect['y'], (size[1] - 462) / 2)
        self.assertEqual(popup.rect['width'], 362)
        self.assertEqual(popup.rect['height'], 462)

        content = popup.find_element_by_id('content')
        self.assertEqual(content.rect['x'], (size[0] - 362) / 2)
        self.assertEqual(content.rect['y'], (size[1] - 462) / 2 + 32)
        self.assertEqual(content.rect['width'], 362)
        self.assertEqual(content.rect['height'], 462 - 32)

        self.browser.close()
        self.browser = None

    @TestData([
        {'size': (361, 461), 'button': 'info'},
        {'size': (361, 461), 'button': 'help'},
    ])
    def testVerySmallSize(self, size, button):
        self.setUpBrowser(size)
        self.browser.find_element_by_id(button).click()

        overlay = self.browser.find_element_by_class_name('overlay')
        self.assertEqual(overlay.rect['x'], 0)
        self.assertEqual(overlay.rect['y'], 0)
        self.assertEqual(overlay.rect['width'], size[0])
        self.assertEqual(overlay.rect['height'], size[1])

        popup = self.browser.find_element_by_class_name('popup')
        self.assertEqual(popup.rect['x'], 0)
        self.assertEqual(popup.rect['y'], 0)
        self.assertEqual(popup.rect['width'], size[0])
        self.assertEqual(popup.rect['height'], size[1])

        content = popup.find_element_by_id('content')
        self.assertEqual(content.rect['x'], 0)
        self.assertEqual(content.rect['y'], 32)
        self.assertEqual(content.rect['width'], size[0])
        self.assertEqual(content.rect['height'], size[1] - 32)

        self.browser.close()
        self.browser = None
