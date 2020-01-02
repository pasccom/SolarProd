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

from selenium import webdriver

import os

from .PythonUtils.testdata import TestData

from .testcase import TestCase

class TabLayoutTest(TestCase):
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
        {'size': (1024, 680)},
        {'size': (950,  680)},
    ])
    def testVeryLargeSizes(self, size):
        self.setUpBrowser(size)
        self.browser.find_element_by_id('info').click()

        tabView = self.browser.find_element_by_class_name('popup').find_element_by_id('content')
        self.assertEqual(tabView.rect['x'], 0.25*size[0])
        self.assertEqual(tabView.rect['y'], 0.15*size[1] + 32)
        self.assertEqual(tabView.rect['width'], 0.5*size[0])
        self.assertEqual(tabView.rect['height'], round(0.7*size[1]) - 32)

        tabBar = tabView.find_element_by_tag_name('ul')
        self.assertEqual(tabBar.rect['x'], 0.25*size[0])
        self.assertEqual(tabBar.rect['y'], 0.15*size[1] + 32)
        self.assertEqual(tabBar.rect['width'], 0.5*size[0])
        self.assertEqual(tabBar.rect['height'], 31)

        pageView = tabView.find_element_by_tag_name('div')
        self.assertEqual(pageView.rect['x'], 0.25*size[0])
        self.assertEqual(pageView.rect['y'], 0.15*size[1] + 32 + 32)
        self.assertEqual(pageView.rect['width'], 0.5*size[0])
        self.assertEqual(pageView.rect['height'], round(0.7*size[1]) - 32 - 32)

        self.assertEqual(tabView.find_element_by_id('left-button').value_of_css_property('display'), 'none')
        self.assertEqual(tabView.find_element_by_id('right-button').value_of_css_property('display'), 'none')

        self.browser.close()
        self.browser = None

    @TestData([
        {'size': (949, 680)},
        {'size': (724, 660)},
    ])
    def testLargeSizes(self, size):
        self.setUpBrowser(size)
        self.browser.find_element_by_id('info').click()

        tabView = self.browser.find_element_by_class_name('popup').find_element_by_id('content')
        self.assertEqual(tabView.rect['x'], 0.25*size[0])
        self.assertEqual(tabView.rect['y'], 0.15*size[1] + 32)
        self.assertEqual(tabView.rect['width'], 0.5*size[0])
        self.assertEqual(tabView.rect['height'], round(0.7*size[1]) - 32)

        tabBar = tabView.find_element_by_tag_name('ul')
        self.assertEqual(tabBar.rect['x'], 0.25*size[0] + 30)
        self.assertEqual(tabBar.rect['y'], 0.15*size[1] + 32)
        self.assertEqual(tabBar.rect['width'], 0.5*size[0] - 30)
        self.assertEqual(tabBar.rect['height'], 31)

        pageView = tabView.find_element_by_tag_name('div')
        self.assertEqual(pageView.rect['x'], 0.25*size[0])
        self.assertEqual(pageView.rect['y'], 0.15*size[1] + 32 + 32)
        self.assertEqual(pageView.rect['width'], 0.5*size[0])
        self.assertEqual(pageView.rect['height'], round(0.7*size[1]) - 32 - 32)

        self.assertEqual(tabView.find_element_by_id('left-button').value_of_css_property('display'), 'block')
        self.assertEqual(tabView.find_element_by_id('right-button').value_of_css_property('display'), 'block')

        self.browser.close()
        self.browser = None

    @TestData([
        {'size': (723, 659)},
        {'size': (362, 462)},
    ])
    def testSmallSizes(self, size):
        self.setUpBrowser(size)
        self.browser.find_element_by_id('info').click()

        tabView = self.browser.find_element_by_class_name('popup').find_element_by_id('content')
        self.assertEqual(tabView.rect['x'], (size[0] - 362) / 2)
        self.assertEqual(tabView.rect['y'], (size[1] - 462) / 2 + 32)
        self.assertEqual(tabView.rect['width'], 362)
        self.assertEqual(tabView.rect['height'], 462 - 32)

        tabBar = tabView.find_element_by_tag_name('ul')
        self.assertEqual(tabBar.rect['x'], (size[0] - 362) / 2 + 30)
        self.assertEqual(tabBar.rect['y'], (size[1] - 462) / 2 + 32)
        self.assertEqual(tabBar.rect['width'], 362 - 30)
        self.assertEqual(tabBar.rect['height'], 31)

        pageView = tabView.find_element_by_tag_name('div')
        self.assertEqual(pageView.rect['x'], (size[0] - 362) / 2)
        self.assertEqual(pageView.rect['y'], (size[1] - 462) / 2 + 32 + 32)
        self.assertEqual(pageView.rect['width'], 362)
        self.assertEqual(pageView.rect['height'], 462 - 32 - 32)

        self.assertEqual(tabView.find_element_by_id('left-button').value_of_css_property('display'), 'block')
        self.assertEqual(tabView.find_element_by_id('right-button').value_of_css_property('display'), 'block')

        self.browser.close()
        self.browser = None

    @TestData([
        {'size': (361, 461)},
    ])
    def testVerySmallSize(self, size):
        self.setUpBrowser(size)
        self.browser.find_element_by_id('info').click()

        tabView = self.browser.find_element_by_class_name('popup').find_element_by_id('content')
        self.assertEqual(tabView.rect['x'], 0)
        self.assertEqual(tabView.rect['y'], 32)
        self.assertEqual(tabView.rect['width'], size[0])
        self.assertEqual(tabView.rect['height'], size[1] - 32)

        tabBar = tabView.find_element_by_tag_name('ul')
        self.assertEqual(tabBar.rect['x'], 30)
        self.assertEqual(tabBar.rect['y'], 32)
        self.assertEqual(tabBar.rect['width'], size[0] - 30)
        self.assertEqual(tabBar.rect['height'], 31)

        pageView = tabView.find_element_by_tag_name('div')
        self.assertEqual(pageView.rect['x'], 0)
        self.assertEqual(pageView.rect['y'], 32 + 32)
        self.assertEqual(pageView.rect['width'], size[0])
        self.assertEqual(pageView.rect['height'], size[1] - 32 - 32)

        self.assertEqual(tabView.find_element_by_id('left-button').value_of_css_property('display'), 'block')
        self.assertEqual(tabView.find_element_by_id('right-button').value_of_css_property('display'), 'block')

        self.browser.close()
        self.browser = None
