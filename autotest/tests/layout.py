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

class LayoutTest(TestCase):
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

    @TestData([{'size': (1200, 694)}])
    def testVeryLargeSize(self, size):
        self.setUpBrowser(size)

        chart = self.browser.find_element_by_id('chart')
        self.assertEqual(chart.value_of_css_property('display'), 'inline-block')
        self.assertEqual(chart.rect['x'], 8)
        self.assertEqual(chart.rect['y'], 44)
        self.assertEqual(chart.rect['width'], size[0] - 274)
        self.assertEqual(chart.rect['height'], size[1] - 54)

        legend = self.browser.find_element_by_id('legend')
        self.assertEqual(legend.value_of_css_property('display'), 'inline-block')
        self.assertEqual(legend.rect['x'], size[0] - 250 - 8)
        self.assertEqual(legend.rect['y'], 44)
        self.assertEqual(legend.rect['width'], 250)
        self.assertEqual(legend.rect['height'], size[1] - 54)

        self.browser.close()
        self.browser = None

    @TestData([
        {'size': (1024, 680)},
        {'size': (1023, 680)},
        {'size': (724, 660) },
    ])
    def testLargeSizes(self, size):
        self.setUpBrowser(size)

        chart = self.browser.find_element_by_id('chart')
        self.assertEqual(chart.value_of_css_property('display'), 'inline-block')
        self.assertEqual(chart.rect['x'], 8)
        self.assertEqual(chart.rect['y'], 44)
        self.assertEqual(chart.rect['width'], size[0] - 199 - 75*(size[0] - 24 - 700)/300)
        self.assertEqual(chart.rect['height'], size[1] - 54)

        legend = self.browser.find_element_by_id('legend')
        self.assertEqual(legend.value_of_css_property('display'), 'inline-block')
        self.assertEqual(legend.rect['x'], size[0] - 175 - 75*(size[0] - 24 - 700)/300 - 8)
        self.assertEqual(legend.rect['y'], 44)
        self.assertEqual(legend.rect['width'], 175 + 75*(size[0] - 24 - 700)/300)
        self.assertEqual(legend.rect['height'], size[1] - 54)

        self.browser.close()
        self.browser = None

    @TestData([
        {'size': (723, 659)},
        {'size': (565, 200)},
    ])
    def testSmallSizes(self, size):
        self.setUpBrowser(size)

        chart = self.browser.find_element_by_id('chart')
        self.assertEqual(chart.value_of_css_property('display'), 'inline-block')
        self.assertEqual(chart.rect['x'], 8)
        self.assertEqual(chart.rect['y'], 44)
        self.assertEqual(chart.rect['width'], size[0] - 16)
        self.assertEqual(chart.rect['height'], size[1] - 54)

        legend = self.browser.find_element_by_id('legend')
        self.assertEqual(legend.value_of_css_property('display'), 'none')

        self.browser.close()
        self.browser = None

    @TestData([{'size': (564, 200)}])
    def testVerySmallSize(self, size):
        self.setUpBrowser(size)

        chart = self.browser.find_element_by_id('chart')
        self.assertEqual(chart.rect['x'], 8)
        self.assertEqual(chart.rect['y'], 80)
        self.assertEqual(chart.rect['width'], size[0] - 16)
        self.assertEqual(chart.rect['height'], size[1] - 90)

        legend = self.browser.find_element_by_id('legend')
        self.assertEqual(legend.value_of_css_property('display'), 'none')

        self.browser.close()
        self.browser = None
