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
# along with SolarProd. If not, see <http://www.gnu.org/licenses/>

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common import exceptions as selenium

import os
import time

from .testcase import TestCase

class BrowserTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        profile = webdriver.FirefoxProfile(os.path.join(cls.profilesDir, 'test'))
        cls.browser = webdriver.Firefox(profile)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        if (cls.browser is not None):
            cls.browser.close()
            cls.browser = None

    def setUp(self, loadIndex=True):
        super().setUp()

        self.browser = self.__class__.browser
        if loadIndex:
            self.browser.get(self.index)

    def getLog(self):
        return self.browser.execute_script('return console.capture.get();')

    def printLog(self):
        for entry in self.getLog():
            try:
                print('{}@{}:{}:{}'.format(entry['caller'], entry['fileName'], entry['lineNumber'], entry['columnNumber']))
            except (KeyError):
                pass
            print(entry['arguments'])

    def clearLog(self):
        self.browser.execute_script('console.capture.clear();')

    def assertClassed(self, obj, cls, classed):
        if (classed):
            self.assertIn(cls, self.getClasses(obj))
        else:
            self.assertNotIn(cls, self.getClasses(obj))

    def assertSelectValue(self, name, value='', wait=0):
        while (wait != 0) and (self.browser.find_element_by_id(name).get_property('value') != str(value)):
            time.sleep(1)
            wait -= 1
        if (self.browser.find_element_by_id(name).get_property('value') != str(value)):
            self.fail('Select "{}" does not have value "{}"'.format(name, value))
        return wait

    def assertDate(self, year='', month='', day='', wait=0):
        wait = self.assertSelectValue('year', str(year), wait)
        wait = self.assertSelectValue('month', str(month), wait)
        wait = self.assertSelectValue('day', str(day), wait)
        return wait

    def selectDate(self, year, month=None, day=None, partial=False):
        if year is not None:
            self.selectOption('year', str(year))
        else:
            self.selectOption('year', '')
        if month is not None:
            self.selectOption('month', self.monthName(month), str(month))
        elif not partial and year is not None:
            self.selectOption('month', '')
        if day is not None:
            self.selectOption('day', str(day))
        elif not partial and month is not None:
            self.selectOption('day', '')

    def selectVar(self, var):
        if var is None:
            return
        try:
            self.selectOption('var', self.longVar(var), var)
        except (ValueError):
            self.selectOption('var', var, self.shortVar(var))

    def selectSum(self, agg):
        if agg is None:
            return
        self.selectOption('sum', self.sumName(agg), agg)

    def waitOptions(self, select, t=-1):
        options = []
        while (len(options) == 0):
            options = select.find_elements_by_tag_name('option')
            if (t == 0):
                raise RuntimeError('Timed out waiting for options')
            time.sleep(1)
            t -= 1
        return options

    def selectOption(self, selectId, option, value=None):
        if value is None:
            value = option

        select = self.browser.find_element_by_id(selectId)
        if (select.get_property('value') == value):
            return

        options = [o for o in self.waitOptions(select, 10) if (o.text == option)]
        try:
            if (select.get_property('value') != value):
                options[0].click()
        except (selenium.InvalidElementStateException):
            pass
        self.assertEqual(select.get_property('value'), value)

    def clickButton(self, button, repeat=1):
        actions = ActionChains(self.browser)
        for r in range(0, repeat):
            actions.move_to_element(button)
            actions.click(button)
        return actions

    def plot(self, today=False, repeat=1):
        if today:
            self.clickButton(self.browser.find_element_by_id('today'), repeat).perform()
        else:
            self.clickButton(self.browser.find_element_by_id('plot'), repeat).perform()

    def plotPrev(self, repeat=1):
        self.clickButton(self.browser.find_element_by_id('prev'), repeat).perform()

    def plotNext(self, repeat=1):
        self.clickButton(self.browser.find_element_by_id('next'), repeat).perform()

    def export(self, repeat=1):
        self.clickButton(self.browser.find_element_by_id('export'), repeat).perform()

    def pressKeys(self, keys, repeat=1):
        actions = ActionChains(self.browser)
        for r in range(0, repeat):
            for key in keys:
                actions.key_down(key)
            for key in reversed(keys):
                actions.key_up(key)
        return actions

    def getClasses(self, element):
        classes = element.get_attribute('class')
        return classes.split(' ') if not classes is None else []

    def getStyle(self, element):
        style = element.get_attribute('style')
        styles = dict([tuple([i.strip() for i in s.strip().split(':')]) for s in style.split(';') if len(s.strip()) > 0])
        styles = dict([self.__parseStyle(k, v) for k, v in styles.items()])
        return styles

    def parseColor(self, value):
        if (value.startswith('rgb(') and value.endswith(')')):
            return tuple([int(c.strip()) for c in value[4:-1].split(',')])
        elif (value.startswith('rgba(') and value.endswith(')')):
            return tuple([(float(c.strip()) if '.' in c else int(c.strip())) for c in value[5:-1].split(',')])
        elif (value.startswith('#') and len(value) == 4):
            return tuple([17*int(c, 16) for c in value[1:]])
        elif (value.startswith('#') and len(value) == 7):
            return int(value[1:3], 16), int(value[3:5], 16), int(value[5:7], 16)
        return value

    def __parseStyle(self, tag, value):
        if (tag == 'color') or (tag == 'background-color') or (tag == 'border-color'):
            return tag, self.parseColor(value)
        return tag, value
