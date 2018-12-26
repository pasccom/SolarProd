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
    monthNames = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
    shortVars = ['nrj',     'pwr',       'pac',          'uac',        'pdc',          'udc',        'temp']
    longVars =  ['Énergie', 'Puissance', 'Puissance AC', 'Tension AC', 'Puissance DC', 'Tension DC', 'Température']
    units =     ['Wh',      'W',         'W',            'V',          'W',            'V',          '°C']
    sumNames = {
        'sum': 'Total',
        'inv': 'Par onduleur',
        'str': 'Par string'
    }

    def __checkArgument(self, cache, arg):
        if cache is None:
            cache = os.path.isfile(self.cacheDir)
        if (arg == 'cache'):
            return cache
        if (arg == '!cache'):
            return not cache
        return arg

    @staticmethod
    def cacheCheck(fun, cache=None):
        def cacheCheckFun(self, *args, **kwArgs):
            newArgs = (self.__checkArgument(cache, a) for a in args)
            newKwArgs = {k: self.__checkArgument(cache, a) for k, a in kwArgs.items()}
            fun(self, *newArgs, **newKwArgs)
        return cacheCheckFun

    @staticmethod
    def cacheTest(fun):
        def cacheTestFun(self, *args, **kwArgs):
            with self.subTest(msg='Without cache'):
                os.rename(self.cacheDir, self.cacheDir + '.del')
                self.browser.get(self.index)
                self.__class__.cacheCheck(fun, False)(self, *args, **kwArgs)

            with self.subTest(msg='With cache'):
                os.rename(self.cacheDir + '.del', self.cacheDir)
                self.browser.get(self.index)
                self.__class__.cacheCheck(fun, True)(self, *args, **kwArgs)

        return cacheTestFun

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

    def longVar(self, var):
        return self.__class__.longVars[self.__class__.shortVars.index(var)]

    def unit(self, var):
        try:
            return self.__class__.units[self.__class__.shortVars.index(var)]
        except (ValueError):
            return self.__class__.units[self.__class__.longVars.index(var)]

    def monthName(self, month):
        return self.__class__.monthNames[month - 1]

    def monthNumber(self, monthName):
        return self.__class__.monthNames.index(monthName) + 1

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
            self.selectOption('var', var, self.__class__.shortVars[self.__class__.longVars.index(var)])

    def selectSum(self, agg):
        if agg is None:
            return
        self.selectOption('sum', self.__class__.sumNames[agg], agg)

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

    def getLines(self):
        chart = self.browser.find_element_by_id('chart')
        return chart.find_elements_by_css_selector('path.line')

    def getBars(self):
        chart = self.browser.find_element_by_id('chart')
        return chart.find_elements_by_css_selector('rect.bar')

    def __removeChildren(self, elements, src=None):
        children = []
        for item in elements:
            if src is None:
                children += item.find_elements_by_tag_name(item.tag_name)
            else:
                for srcItem in src:
                    children += srcItem.find_elements_by_tag_name(item.tag_name)
        for child in children:
            try:
                elements.remove(child)
            except (ValueError):
                pass
        return elements

    def __removeParents(self, elements):
        return [e for e in elements if len(e.find_elements_by_tag_name(e.tag_name)) == 0]

    def getLegendListItems(self, parent):
        if parent is None:
            parent = self.browser.find_element_by_id('legend')
        legendItemList = parent.find_elements_by_tag_name('ul')
        self.__removeChildren(legendItemList)
        self.assertLessEqual(len(legendItemList), 1)

        legendItems = []
        for item in legendItemList:
            legendItems += item.find_elements_by_xpath('child::li')
        return legendItems

    def getLegendItems(self, parent=None):
        legendItems = self.getLegendListItems(parent)
        if (len(legendItems) == 0) and (parent is None):
            return [tuple(self.browser.find_element_by_id('legend').find_elements_by_tag_name('span') + [[]])]

        return [
            (self.__removeParents(self.__removeChildren(e.find_elements_by_tag_name('span'),
                                                    e.find_elements_by_tag_name('li'))) + \
            [self.getLegendItems(e)]) for e in legendItems
        ]

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
