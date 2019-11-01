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
from selenium.webdriver.common.action_chains import ActionChains

import os
import time

from .PythonUtils.testdata import TestData

from .testcase import TestCase

class TabScrollTest(TestCase):
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

    def setUpTest(self, size):
        self.setUpBrowser(size)
        self.browser.find_element_by_id('info').click()

        self.tabView = self.browser.find_element_by_class_name('popup').find_element_by_id('content')
        self.tabBar = self.tabView.find_element_by_tag_name('ul')

        ActionChains(self.browser).move_to_element(self.tabView.find_element_by_id('right-button')).perform()

    def __getTabPositions(self, *coordinates):
        if (len(coordinates) > 1):
            return tuple(self.__getTabPositions(c) for c in coordinates)

        if (coordinates[0] == 'left'):
            return [t.rect['x'] for t in self.tabBar.find_elements_by_tag_name('li')]
        elif (coordinates[0] == 'right'):
            return [t.rect['x'] + t.rect['width'] for t in self.tabBar.find_elements_by_tag_name('li')]
        if (coordinates[0] == 'top'):
            return [t.rect['y'] for t in self.tabBar.find_elements_by_tag_name('li')]
        elif (coordinates[0] == 'bottom'):
            return [t.rect['y'] + t.rect['height'] for t in self.tabBar.find_elements_by_tag_name('li')]
        else:
            raise ValueError(f"Invalid coordinate: {coordinates[0]}")

    def scroll(self, direction):
        ActionChains(self.browser).click(self.tabView.find_element_by_id(direction + '-button')).perform()
        return self.__getTabPositions('left', 'right')

    def autoScroll(self, direction, t):
        ActionChains(self.browser).click_and_hold(self.tabView.find_element_by_id(direction + '-button')).perform()
        time.sleep(t)
        ActionChains(self.browser).release().perform()

        prevTabLeft, prevTabRight = self.__getTabPositions('left', 'right')
        time.sleep(t)
        tabLeft, tabRight = self.__getTabPositions('left', 'right')

        self.assertTrue(all(x == x0 for x, x0 in zip(tabLeft, prevTabLeft)))
        self.assertTrue(all(x == x0 for x, x0 in zip(tabRight, prevTabRight)))
        return tabLeft, tabRight

    def autoScrollToMax(self, direction):
        prevTabLeft, prevTabRight = self.__getTabPositions('left', 'right')

        ActionChains(self.browser).click_and_hold(self.tabView.find_element_by_id(direction + '-button')).perform()
        while (True):
            time.sleep(0.05)
            tabLeft, tabRight = self.__getTabPositions('left', 'right')
            if all(x == x0 for x, x0 in zip(tabLeft, prevTabLeft)) and all(x == x0 for x, x0 in zip(tabRight, prevTabRight)):
                    ActionChains(self.browser).release().perform()
                    return (tabLeft, tabRight)
            prevTabLeft = tabLeft
            prevTabRight = tabRight

    def __checkConsistency(self, initTab, tab):
        return all(x - x0 == tab[-1] - initTab[-1] for x, x0 in zip(tab, initTab))

    def __checkVerticalConsistency(self):
        return all(t.rect['y'] == self.tabBar.rect['y'] for t in self.tabBar.find_elements_by_tag_name('li')) and \
               all(t.rect['height'] == self.tabBar.rect['height'] for t in self.tabBar.find_elements_by_tag_name('li'))

    @TestData([
        {'size': (949, 680)},
        {'size': (361, 461)},
    ])
    def testScrollRight(self, size):
        self.setUpTest(size)

        prevTabLeft, prevTabRight = self.__getTabPositions('left', 'right')

        while (True):
            tabLeft, tabRight = self.scroll('right')

            self.assertTrue(self.__checkVerticalConsistency())
            self.assertTrue(self.__checkConsistency(prevTabLeft, tabLeft))
            self.assertTrue(self.__checkConsistency(prevTabRight, tabRight))

            self.assertGreaterEqual(tabRight[-1], self.tabBar.rect['x'] + self.tabBar.rect['width'] - 26)
            if (tabRight[-1] == self.tabBar.rect['x'] + self.tabBar.rect['width'] - 26):
                self.browser.close()
                self.browser = None
                break
            else:
                self.assertEqual(tabLeft[-1] - prevTabLeft[-1], -5)

            prevTabLeft = tabLeft
            prevTabRight = tabRight

    @TestData([
        {'size': (949, 680)},
        {'size': (361, 461)},
    ])
    def testMaxAutoScrollRight(self, size):
        self.setUpTest(size)

        initTabLeft, initTabRight = self.__getTabPositions('left', 'right')

        tabLeft, tabRight = self.autoScrollToMax('right')

        self.assertTrue(self.__checkVerticalConsistency())
        self.assertTrue(self.__checkConsistency(initTabLeft, tabLeft))
        self.assertTrue(self.__checkConsistency(initTabRight, tabRight))

        self.assertEqual(tabRight[-1], self.tabBar.rect['x'] + self.tabBar.rect['width'] - 26)

        self.browser.close()
        self.browser = None

    @TestData([
        {'size': (949, 680)},
        {'size': (361, 461)},
    ])
    def testAutoScrollRight(self, size):
        self.setUpTest(size)

        initTabLeft, initTabRight = self.__getTabPositions('left', 'right')
        tabLeft, tabRight = self.autoScroll('right', 0.2)

        self.assertTrue(self.__checkVerticalConsistency())
        self.assertTrue(self.__checkConsistency(initTabLeft, tabLeft))
        self.assertTrue(self.__checkConsistency(initTabRight, tabRight))

        self.assertLess(tabLeft[0], self.tabView.rect['x'] + 22)
        self.assertGreater(tabRight[-1], self.tabBar.rect['x'] + self.tabBar.rect['width'] - 26)
        self.assertEqual((tabLeft[-1] - initTabLeft[-1]) % 5, 0)

        self.browser.close()
        self.browser = None

    @TestData([
        {'size': (949, 680)},
        {'size': (361, 461)},
    ])
    def testScrollLeft(self, size):
        self.setUpTest(size)
        self.autoScrollToMax('right')

        prevTabLeft, prevTabRight = self.__getTabPositions('left', 'right')

        while (True):
            tabLeft, tabRight = self.scroll('left')

            self.assertTrue(self.__checkVerticalConsistency())
            self.assertTrue(self.__checkConsistency(prevTabLeft, tabLeft))
            self.assertTrue(self.__checkConsistency(prevTabRight, tabRight))

            self.assertLessEqual(tabLeft[0], self.tabView.rect['x'] + 22)
            if (tabLeft[0] == self.tabView.rect['x'] + 22):
                self.browser.close()
                self.browser = None
                break
            else:
                self.assertEqual(tabLeft[0] - prevTabLeft[0], 5)

            prevTabLeft = tabLeft
            prevTabRight = tabRight

    @TestData([
        {'size': (949, 680)},
        {'size': (361, 461)},
    ])
    def testMaxAutoScrollLeft(self, size):
        self.setUpTest(size)
        self.autoScrollToMax('right')

        initTabLeft, initTabRight = self.__getTabPositions('left', 'right')

        tabLeft, tabRight = self.autoScrollToMax('left')

        self.assertTrue(self.__checkVerticalConsistency())
        self.assertTrue(self.__checkConsistency(initTabLeft, tabLeft))
        self.assertTrue(self.__checkConsistency(initTabRight, tabRight))

        self.assertEqual(tabLeft[0], self.tabView.rect['x'] + 22)

        self.browser.close()
        self.browser = None

    @TestData([
        {'size': (949, 680)},
        {'size': (361, 461)},
    ])
    def testAutoScrollLeft(self, size):
        self.setUpTest(size)
        self.autoScrollToMax('right')

        initTabLeft, initTabRight = self.__getTabPositions('left', 'right')
        tabLeft, tabRight = self.autoScroll('left', 0.2)

        self.assertTrue(self.__checkVerticalConsistency())
        self.assertTrue(self.__checkConsistency(initTabLeft, tabLeft))
        self.assertTrue(self.__checkConsistency(initTabRight, tabRight))

        self.assertLess(tabLeft[0], self.tabView.rect['x'] + 22)
        self.assertGreater(tabRight[-1], self.tabBar.rect['x'] + self.tabBar.rect['width'] - 26)
        self.assertEqual((tabLeft[-1] - initTabLeft[-1]) % 5, 0)

        self.browser.close()
        self.browser = None


