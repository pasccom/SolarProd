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
from selenium.common import exceptions as selenium
import unittest
from PythonUtils.testdata import testData
from datetime import datetime as datetime
import os
import re
import json
import csv
import time

# Helper functions (and tests):
def formatDatum(datum):
    datum['date'] = datetime.strptime(datum['date'], '%Y-%m-%d')
    return datum

def mapSum(data):
    try:
        map(lambda *x: x, *data)
    except:
        return data
    
    try:
        return list(map(lambda *datum: sum(datum), *data))
    except:
        return mapSum(list(map(lambda datum: mapSum(datum), data)))
    
class HelperTest(unittest.TestCase):
    def testMapSum0(self):
        self.assertEqual(mapSum([1]), [1])
    def testMapSum1(self):
        self.assertEqual(mapSum([1, 2, 3]), [1, 2, 3])
    def testMapSum2(self):
        self.assertEqual(mapSum([[1, 2, 3], [6, 5, 4]]), [7, 7, 7])
    def testMapSum3(self):
        self.assertEqual(mapSum([[[1, 2, 3], [6, 5, 4]], [[9, 8, 7], [4, 5, 6]]]), [20, 20, 20])
    def testMapSum4(self):
        self.assertEqual(mapSum([[[[1, 2, 3], [6, 5, 4]], [[9, 8, 7], [4, 5, 6]]],
                                 [[[1, 2, 3], [6, 5, 4]], [[9, 8, 7], [4, 5, 6]]]]), [40, 40, 40])

class TestCase(unittest.TestCase):
    baseDir = None
    
    @classmethod
    def setUpClass(cls):
        if cls.baseDir is None:
            cls.baseDir = os.path.dirname(os.path.abspath(__file__))
            cls.profilesDir = os.path.join(cls.baseDir, 'profiles')
        
    def __init__(self, *args, **kwArgs):
        super().__init__(*args, **kwArgs)
        TestCase.setUpClass()
        
        self.index = 'file://' + self.__class__.baseDir + '/testdata/index.html'
        self.profilesDir = self.__class__.profilesDir
        self.cacheDir = os.path.join('testdata', 'list', 'cache.json')
        
    def listPath(self, year=None, month=None):
        listDir = os.path.join('testdata', 'list') 
        if year is None:
            return os.path.join(listDir, 'years.json')
        elif month is None:
            return os.path.join(listDir, 'months/{:04d}.json'.format(year))
        else:
            return os.path.join(listDir, 'days/{:04d}/{:02d}.json'.format(year, month))
        
    def dataPath(self, year=None, month=None, day=None):
        dataDir = os.path.join('testdata', 'data') 
        if (year == 'today'):
            return os.path.join(dataDir, 'today.json')
        if year is None:
            return os.path.join(dataDir, 'years.json')
        elif month is None:
            return os.path.join(dataDir, 'years/{:04d}.json'.format(year))
        elif day is None:
            return os.path.join(dataDir, 'months/{:04d}/{:02d}.json'.format(year, month))
        else:
            return os.path.join(dataDir, 'days/{:04d}/{:02d}/{:02d}.json'.format(year, month, day))
        
    def exportPath(self, var, agg, year=None, month=None, day=None):
        exportDir = 'export'
        if year is None:
            return os.path.join(exportDir, 'export_{}_{}.csv'.format(var, agg))
        elif month is None:
            return os.path.join(exportDir, 'export_{}_{}_{:04d}.csv'.format(var, agg, year))
        elif day is None:
            return os.path.join(exportDir, 'export_{}_{}_{:02d}-{:04d}.csv'.format(var, agg, month, year))
        else:
            return os.path.join(exportDir, 'export_{}_{}_{:02d}-{:02d}-{:04d}.csv'.format(var, agg, day, month, year))
        
    def loadData(self, year=None, month=None, day=None):
        # Load data from JSON file:
        with open(self.dataPath(year, month, day), 'r') as jsonFile:
            self.data = json.load(jsonFile)
            if type(self.data) is dict:
                self.data['dates'] = [datetime.strptime(d, '%Y-%m-%d %H:%M') for d in self.data['dates']]
            else:
                self.data = list(map(formatDatum, self.data))
            #print(self.data)
    
        # Check data is valid:
        if (year == 'today') or (day is not None):
            self.assertEqual([d.strftime('%Y-%m-%d') for d in self.data['dates'][0:-1]],
                             [d.strftime('%Y-%m-%d') for d in self.data['dates'][1:]])
        elif month is not None:
            self.assertEqual([d['date'].strftime('%Y-%m') for d in self.data[0:-1]],
                             [d['date'].strftime('%Y-%m') for d in self.data[1:]])
        elif year is not None:
            self.assertEqual([d['date'].strftime('%Y') for d in self.data[0:-1]],
                             [d['date'].strftime('%Y') for d in self.data[1:]])
     
    def formatDate(self, date, agg, dateMin, dateMax):
        if (dateMin.year != dateMax.year):
            if (agg == 'str'):
                return date.strftime('%Y')
            else:
                return date.year
        elif (dateMin.month != dateMax.month):
            if (agg == 'str'):
                return date.strftime('%m/%Y')
            else:
                return date.month
        elif (dateMin.day != dateMax.day):
            if (agg == 'str'):
                return date.strftime('%d/%m/%Y')
            else:
                return date.day
        else:
            if (agg == 'str'):
                return date.strftime('%d/%m/%Y %H:%M')
            else:
                return date.hour + date.minute/60
     
    def getData(self, var, agg=None):
        if type(self.data) is dict: 
            if (var != 'dates'):
                if (agg == 'sum'):
                    return [[mapSum(self.data[var])]]
                elif (agg == 'inv'):
                    return list(map(lambda x: [mapSum(x)], self.data[var]))
                elif (agg == 'str'):
                    return self.data[var]
                else:
                    raise ValueError('Invalid aggregation method: {}'.format(agg))
            else:
                dateMin = min(self.data['dates'])
                dateMax = max(self.data['dates'])
                return [self.formatDate(d, agg, dateMin, dateMax) for d in self.data['dates']]
        elif type(self.data) is list:
            if (var != 'dates'):
                if (agg == 'sum'):
                    return [[[sum(d[var]) for d in self.data]]]
                elif (agg == 'inv'):
                    return [[list(d)] for d in zip(*[d[var] for d in self.data])]
                else:
                    raise ValueError('Invalid aggregation method: {}'.format(agg))
            else:
                dateMin = min([d['date'] for d in self.data])
                dateMax = max([d['date'] for d in self.data])
                return [self.formatDate(d['date'], agg, dateMin, dateMax) for d in self.data]
        else:
            raise TypeError('Invalid data type: {}'.format(type(self.data)))
     
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
        
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        profile = webdriver.FirefoxProfile(os.path.join(cls.profilesDir, 'test'))
        cls.browser = webdriver.Firefox(profile)
    
    @classmethod
    def tearDownClass(cls):
        if (cls.browser is not None):
            cls.browser.close()
            cls.browser = None
    
    def setUp(self):
        self.browser = self.__class__.browser
        self.browser.get(self.index)
     
    def assertEnabled(self, obj, enabled):
        if (enabled):
            self.assertNotIn('disabled', self.getClasses(obj))
        else:
            self.assertIn('disabled', self.getClasses(obj))
     
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
    
    def selectDate(self, year, month=None, day=None):
        if year is not None:
            self.selectOption('year', str(year))
        else:
            self.selectOption('year', '')
        if month is not None:
            self.selectOption('month', self.monthName(month), str(month))
        elif year is not None:
            self.selectOption('month', '')
        if day is not None:
            self.selectOption('day', str(day))
        elif month is not None:
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
                break
            time.sleep(1)
            t -= 1
        return options

    def selectOption(self, selectId, option, value=None):
        if value is None:
            value = option
        
        select = self.browser.find_element_by_id(selectId)
        if (select.get_property('value') == value):
            return
            
        options = [o for o in self.waitOptions(select) if (o.text == option)]
        try:
            if (select.get_property('value') != value):
                options[0].click()
        except (selenium.InvalidElementStateException):
            pass
        self.assertEqual(select.get_property('value'), value)
        
    def getClasses(self, element):
        classes = element.get_attribute('class')
        return classes.split(' ')
    
    def getLines(self):
        chart = self.browser.find_element_by_id('chart')
        return [(
            p, 
            self.__parseColor(p.find_element_by_xpath('..').get_attribute('stroke')), 
            float(p.get_attribute('stroke-opacity'))
        ) for p in chart.find_elements_by_css_selector('path.line')]
    
    def getBars(self):
        chart = self.browser.find_element_by_id('chart')
        return [(
            p,
            self.__parseColor(p.find_element_by_xpath('..').get_attribute('fill')), 
            float(p.get_attribute('fill-opacity'))
        ) for p in chart.find_elements_by_css_selector('rect.bar')]
    
    def getStyle(self, element):
        style = element.get_attribute('style')
        styles = dict([tuple([i.strip() for i in s.strip().split(':')]) for s in style.split(';') if len(s.strip()) > 0])
        styles = dict([self.__parseStyle(k, v) for k, v in styles.items()])
        return styles
        
    def __parseColor(self, value):
        if (value.startswith('rgb(') and value.endswith(')')):
            return tuple([int(c.strip()) for c in value[4:-1].split(',')])
        elif (value.startswith('#') and len(value) == 4):
            return tuple([17*int(c, 16) for c in value[1:]])
        elif (value.startswith('#') and len(value) == 7):
            return int(value[1:3], 16), int(value[3:5], 16), int(value[5:7], 16) 
        return value
    
    def __parseStyle(self, tag, value):
        if (tag == 'color'):
            return tag, self.__parseColor(value)
        return tag, value
            
class ElementsTest(BrowserTestCase):
        
    def testWindowTitle(self):
        self.assertIn('Ducomquet: Production solaire', self.browser.title)

    @testData([
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
     
    @testData([
        {'name': 'plot',    'enabled': True },
        {'name': 'today',   'enabled': True },
        {'name': 'prev',    'enabled': False},
        {'name': 'next',    'enabled': False},
        {'name': 'export',  'enabled': False},
    ])
    def testButtons(self, name, enabled):
        button = self.browser.find_element_by_id(name)
        self.assertEqual(button.tag_name, 'img')
        self.assertEnabled(button, enabled)
        self.assertEqual(button.size['width'], 28)
        self.assertEqual(button.size['height'], 28)

    def testExportToday(self):
        self.browser.find_element_by_id('today').click()
        
        export = self.browser.find_element_by_id('export')
        self.assertEnabled(export, True)
        
    @testData([
        {'year': None, 'month': None, 'day': None},
        {'year': 2017, 'month': None, 'day': None},
        {'year': 2017, 'month': 8,    'day': None},
        {'year': 2017, 'month': 8,    'day': 8},
    ])
    def testExportDate(self, year, month, day):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        
        export = self.browser.find_element_by_id('export')
        self.assertEnabled(export, True)

    @testData([
        {'year': 2017, 'month': 8,    'day': 5},
    ])
    def testExportEmpty(self, year, month, day):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()

        export = self.browser.find_element_by_id('export')
        self.assertEnabled(export, False)

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
    
    @testData([{'size': (1200, 694)}])
    def testVeryLargeSize(self, size):
        self.setUpBrowser(size)
        
        chart = self.browser.find_element_by_id('chart')
        self.assertEqual(chart.size['width'], size[0] - 274)
        self.assertEqual(chart.size['height'], size[1] - 54)
        legend = self.browser.find_element_by_id('legend')
        self.assertEqual(legend.size['width'], 250)
        self.assertEqual(legend.size['height'], size[1] - 54)
        self.browser.close()
        self.browser = None
    
    @testData([
        {'size': (1024, 655)},
        {'size': (1023, 655)},
        {'size': (724, 500) },
    ])
    def testLargeSizes(self, size):
        self.setUpBrowser(size)
            
        chart = self.browser.find_element_by_id('chart')
        self.assertEqual(chart.size['width'], size[0] - 199 - 75*(size[0] - 24 - 700)/300)
        self.assertEqual(chart.size['height'], size[1] - 54)
        legend = self.browser.find_element_by_id('legend')
        self.assertEqual(legend.size['width'], 175 + 75*(size[0] - 24 - 700)/300)
        self.assertEqual(legend.size['height'], size[1] - 54)
        self.browser.close()
        self.browser = None
       
    @testData([
        {'size': (723, 500)},
        {'size': (403, 200)},
    ])
    def testSmallSizes(self, size):
        self.setUpBrowser(size)
            
        chart = self.browser.find_element_by_id('chart')
        self.assertEqual(chart.size['width'], size[0] - 16)
        self.assertEqual(chart.size['height'], size[1] - 54)
        self.browser.close()
        self.browser = None

    @testData([{'size': (402, 200)}])
    def testVerySmallSize(self, size):
        self.setUpBrowser(size)
        
        chart = self.browser.find_element_by_id('chart')
        self.assertEqual(chart.size['width'], size[0] - 16)
        self.assertEqual(chart.size['height'], size[1] - 92)
        self.browser.close()
        self.browser = None

class SelectTest(BrowserTestCase):
    def testYears(self):
        select = self.browser.find_element_by_id('year')
        options = [o.text for o in self.waitOptions(select)]
        
        with open(self.listPath(), 'r') as jsonFile:
            expected = json.load(jsonFile)
        expected = [''] + [str(y) for y in expected]
        
        self.assertEqual(options, expected)
        self.assertTrue(select.is_enabled())
        self.assertEqual(select.get_property('value'), '')
        
    @testData([
        {'year': 2009},
        {'year': 2010},
        {'year': 2011},
        {'year': 2014},
        {'year': 2017},
        {'year': 2018},
        {'year': 2019},
    ])
    def testMonths(self, year):
        self.selectDate(year)
        
        select = self.browser.find_element_by_id('month')
        options = [o.text for o in self.waitOptions(select, 5)]
        
        try:
            with open(self.listPath(year), 'r') as jsonFile:
                expected = json.load(jsonFile)
            expected = [''] + [self.monthName(m) for m in expected]
        except (FileNotFoundError):
            expected = []
            
        self.assertEqual(options, expected)
        if (len(expected) == 0):
            self.assertFalse(select.is_enabled())
        else:
            self.assertTrue(select.is_enabled())
            self.assertEqual(select.get_property('value'), '')
    
    @testData([
        {'year': 2010, 'month': 12},
        {'year': 2011, 'month': 6 },
        {'year': 2011, 'month': 9 },
        {'year': 2011, 'month': 12},
        {'year': 2017, 'month': 2 },
        {'year': 2017, 'month': 5 },
        {'year': 2017, 'month': 8 },
        {'year': 2018, 'month': 2 },
    ])
    def testDays(self, year, month, expected=None):
        self.selectDate(year, month)
        
        select = self.browser.find_element_by_id('day')
        options = [o.text for o in self.waitOptions(select, 5)]
        
        try:
            with open(self.listPath(year, month), 'r') as jsonFile:
                expected = json.load(jsonFile)
            expected = [''] + [str(d) for d in expected]
        except (FileNotFoundError):
            expected = []
        
        self.assertEqual(options, expected)
        if (len(expected) == 0):
            self.assertFalse(select.is_enabled())
        else:
            self.assertTrue(select.is_enabled())
            self.assertEqual(select.get_property('value'), '')
                
    @testData([
        {'year': None, 'month': None, 'day': None, 'expected': set(['Énergie'])                                                             },
        {'year': 2017, 'month': None, 'day': None, 'expected': set(['Énergie'])                                                             },
        {'year': 2017, 'month': 8,    'day': None, 'expected': set(['Énergie', 'Puissance'])                                                },
        {'year': 2017, 'month': 8,    'day': 8,    'expected': set(['Énergie', 'Puissance AC', 'Puissance DC', 'Tension DC', 'Température'])},
        {'year': 2017, 'month': 8,    'day': 5,    'expected': set([])                                                                      },
    ])
    def testVar(self, year, month, day, expected):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        
        select = self.browser.find_element_by_id('var')
        options = [o.text for o in self.waitOptions(select, 5)]
        
        self.assertEqual(set(options), expected)
        self.assertEqual(select.is_enabled(), len(expected) > 0)

    @testData([
        {'year': None, 'month': None, 'day': None, 'var': 'nrj',  'expected': set(['Total', 'Par onduleur'])              },
        {'year': 2017, 'month': None, 'day': None, 'var': 'nrj',  'expected': set(['Total', 'Par onduleur'])              }, 
        {'year': 2017, 'month': 8,    'day': None, 'var': 'nrj',  'expected': set(['Total', 'Par onduleur'])              }, 
        {'year': 2017, 'month': 8,    'day': None, 'var': 'pwr',  'expected': set(['Total', 'Par onduleur'])              },
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'nrj',  'expected': set(['Total', 'Par onduleur'])              },
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pac',  'expected': set(['Total', 'Par onduleur'])              },
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pdc',  'expected': set(['Total', 'Par onduleur', 'Par string'])}, 
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'udc',  'expected': set(['Par string'])                         },   
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'temp', 'expected': set(['Par onduleur'])                       },
        {'year': 2017, 'month': 8,    'day': 5,    'var': None,   'expected': set([])                                     },
    ])
    def testSum(self, year, month, day, var, expected):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.selectVar(var)
        
        select = self.browser.find_element_by_id('sum')
        options = [o.text for o in self.waitOptions(select, 5)]
        
        self.assertEqual(set(options), expected)
        self.assertEqual(select.is_enabled(), len(expected) > 1)
    
    def testToday(self):
        self.browser.find_element_by_id('today').click()
        
        day = self.browser.find_element_by_id('day')
        self.waitOptions(day)
        self.assertTrue(day.is_enabled())
        self.assertEqual(day.get_property('value'), '8')
        
        year = self.browser.find_element_by_id('year')
        self.assertTrue(year.is_enabled())
        self.assertEqual(year.get_property('value'), '2017')
        
        month = self.browser.find_element_by_id('month')
        self.assertTrue(month.is_enabled())
        self.assertEqual(month.get_property('value'), '8')
        
        var = self.browser.find_element_by_id('var')
        self.assertTrue(var.is_enabled())
        
        aggr = self.browser.find_element_by_id('sum')
        self.assertTrue(aggr.is_enabled())

class ExportTest(BrowserTestCase):
    def waitExport(self, var, agg, year=None, month=None, day=None, t=-1):
        csvFilePath = self.exportPath(var, agg, year, month, day)
        
        if os.path.isfile(csvFilePath):
            os.remove(csvFilePath)
        
        self.browser.find_element_by_id('export').click()
        while not os.path.isfile(csvFilePath):
            if (t == 0):
                break
            time.sleep(1)
            t -= 1
        return csvFilePath
    
    def getExportData(self, csvFilePath, agg='sum'):
        csvDates = []
        csvData = [[[]]]
        with open(csvFilePath, 'r', encoding='utf-8-sig', newline='') as csvFile:
            csvReader = csv.reader(csvFile, delimiter=',', lineterminator='\r\n')
            for i, row in enumerate(csvReader):
                # Check and retrieve headers:
                if (agg == 'sum'):
                    if (i == 0):
                        self.assertEqual(row[0], 'Date')
                        self.assertEqual(row[1], 'Total')
                        header1 = [0]
                        header2 = [0]
                        continue
                elif (agg == 'inv'):
                    if (i == 0):
                        self.assertEqual(row[0], 'Date')
                        for h in row[1:]:
                            self.assertRegex(h, r'^Onduleur [1-9][0-9]*$')
                        header1 = [int(h[9:]) - 1 for h in row[1:]]
                        header2 = [0]*len(row[1:])
                        continue
                elif (agg == 'str'):
                    if (i == 0):
                        self.assertEqual(row[0], 'Date')
                        for h in row[1:]:
                            self.assertRegex(h, r'^Onduleur [1-9][0-9]*$')
                        header1 = [int(h[9:]) - 1 for h in row[1:]]
                        continue
                    if (i == 1):
                        self.assertEqual(row[0], '')
                        for h in row[1:]:
                            self.assertRegex(h, r'^String [1-9][0-9]*$')
                        header2 = [int(h[7:]) - 1 for h in row[1:]]
                        continue
                else:
                    raise ValueError('Invalid aggregation: {}'.format(agg))
                # Parse data:
                csvDates += [row[0]]
                for j, datum in enumerate(row[1:]):
                    try:
                        csvData[header1[j]][header2[j]] += [int(datum)]
                    except (IndexError):
                        try:
                            csvData[header1[j]] += [[]]
                            csvData[header1[j]][header2[j]] += [int(datum)]
                        except (IndexError):
                            csvData += [[[]]]
                            csvData[header1[j]][header2[j]] += [int(datum)]
        return (csvDates, csvData)
    
    @testData([
        {'year': None, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': None, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2019, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': 2019, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2018, 'month': 2,    'day': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': 2018, 'month': 2,    'day': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2018, 'month': 2,    'day': None, 'var': 'pwr',  'agg': 'sum'},
        {'year': 2018, 'month': 2,    'day': None, 'var': 'pwr',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'nrj',  'agg': 'sum'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'nrj',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pac',  'agg': 'sum'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pac',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pdc',  'agg': 'sum'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pdc',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pdc',  'agg': 'str'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'udc',  'agg': 'str'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'temp', 'agg': 'inv'},
    ])
    def testNormal(self, year, month, day, var, agg):
        self.loadData(year, month, day)
        
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.selectVar(var)
        self.selectSum(agg)
        
        csvFilePath = self.waitExport(var, agg, year, month, day, 5)
        self.assertTrue(os.path.isfile(csvFilePath))
        self.assertEqual(self.getExportData(csvFilePath, agg), (self.getData('dates', 'str'), self.getData(var, agg)))
        os.remove(csvFilePath)
    
    @testData([
        {'year': None, 'month': None, 'day': None, 'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': None, 'month': None, 'day': None, 'newYear': 2018, 'newMonth': 2,    'newDay': None},
        {'year': None, 'month': None, 'day': None, 'newYear': 2017, 'newMonth': 8,    'newDay': 5   },
        {'year': None, 'month': None, 'day': None, 'newYear': 2017, 'newMonth': 8,    'newDay': 8   },
        {'year': 2019, 'month': None, 'day': None, 'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2019, 'month': None, 'day': None, 'newYear': 2018, 'newMonth': 2,    'newDay': None},
        {'year': 2019, 'month': None, 'day': None, 'newYear': 2017, 'newMonth': 8,    'newDay': 5   },
        {'year': 2019, 'month': None, 'day': None, 'newYear': 2017, 'newMonth': 8,    'newDay': 8   },
        {'year': 2018, 'month': 2,    'day': None, 'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2018, 'month': 2,    'day': None, 'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2018, 'month': 2,    'day': None, 'newYear': 2017, 'newMonth': 8,    'newDay': 5   },
        {'year': 2018, 'month': 2,    'day': None, 'newYear': 2017, 'newMonth': 8,    'newDay': 8   },
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2018, 'newMonth': 2,    'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2017, 'newMonth': 8,    'newDay': 5   },
    ])
    def testChangeDate(self, year, month, day, newYear, newMonth, newDay):
        self.loadData(year, month, day)
        
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.selectDate(newYear, newMonth, newDay)
        
        csvFilePath = self.waitExport('nrj', 'sum', year, month, day, 5)
        self.assertTrue(os.path.isfile(csvFilePath))
        self.assertEqual(self.getExportData(csvFilePath), (self.getData('dates', 'str'), self.getData('nrj', 'sum')))
        os.remove(csvFilePath)

    @testData([
        {'year': None, 'month': None, 'day': None, 'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': None, 'month': None, 'day': None, 'newYear': 2018, 'newMonth': 2,    'newDay': None},
        {'year': None, 'month': None, 'day': None, 'newYear': 2017, 'newMonth': 8,    'newDay': 8   },
        {'year': 2019, 'month': None, 'day': None, 'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2019, 'month': None, 'day': None, 'newYear': 2018, 'newMonth': 2,    'newDay': None},
        {'year': 2019, 'month': None, 'day': None, 'newYear': 2017, 'newMonth': 8,    'newDay': 8   },
        {'year': 2018, 'month': 2,    'day': None, 'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2018, 'month': 2,    'day': None, 'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2018, 'month': 2,    'day': None, 'newYear': 2017, 'newMonth': 8,    'newDay': 8   },
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2018, 'newMonth': 2,    'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2017, 'newMonth': 8,    'newDay': 8   },
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2018, 'newMonth': 2,    'newDay': None},
    ])
    def testTransition(self, year, month, day, newYear, newMonth, newDay):
        self.loadData(newYear, newMonth, newDay)

        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.selectDate(newYear, newMonth, newDay)
        self.browser.find_element_by_id('plot').click()

        csvFilePath = self.waitExport('nrj', 'sum', newYear, newMonth, newDay, 5)
        self.assertTrue(os.path.isfile(csvFilePath))
        self.assertEqual(self.getExportData(csvFilePath), (self.getData('dates', 'str'), self.getData('nrj', 'sum')))
        os.remove(csvFilePath)
        
    @testData([
        {'year': 2009, 'month': None, 'day': None, 'prevYear': 2009, 'prevMonth': None, 'prevDay': None},
        {'year': 2010, 'month': None, 'day': None, 'prevYear': 2009, 'prevMonth': None, 'prevDay': None},
        {'year': 2010, 'month': 12,   'day': None, 'prevYear': 2010, 'prevMonth': 12,   'prevDay': None},
        {'year': 2011, 'month': 6,    'day': None, 'prevYear': 2010, 'prevMonth': 12,   'prevDay': None},
        {'year': 2011, 'month': 6,    'day': 24,   'prevYear': 2011, 'prevMonth': 6,    'prevDay': 24  },
        {'year': 2011, 'month': 6,    'day': 26,   'prevYear': 2011, 'prevMonth': 6,    'prevDay': 24  },
        {'year': 2011, 'month': 12,   'day': 25,   'prevYear': 2011, 'prevMonth': 6,    'prevDay': 30  },
        {'year': 2017, 'month': 2,    'day': 1,    'prevYear': 2011, 'prevMonth': 12,   'prevDay': 31  },
        {'year': 2017, 'month': 8,    'day': 5,    'prevYear': 2017, 'prevMonth': 8,    'prevDay': 4   },
    ])
    def testPrev(self, year, month, day, prevYear, prevMonth, prevDay):
        self.loadData(prevYear, prevMonth, prevDay)
        
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.browser.find_element_by_id('prev').click()
        
        csvFilePath = self.waitExport('nrj', 'sum', prevYear, prevMonth, prevDay, 5)
        self.assertTrue(os.path.isfile(csvFilePath))
        self.assertEqual(self.getExportData(csvFilePath), (self.getData('dates', 'str'), self.getData('nrj', 'sum')))
        os.remove(csvFilePath)
    
    @testData([
        {'year': 2018, 'month': None, 'day': None, 'nextYear': 2019, 'nextMonth': None, 'nextDay': None},
        {'year': 2019, 'month': None, 'day': None, 'nextYear': 2019, 'nextMonth': None, 'nextDay': None},
        {'year': 2018, 'month': 2,    'day': None, 'nextYear': 2018, 'nextMonth': 2,    'nextDay': None},
        {'year': 2017, 'month': 8,    'day': None, 'nextYear': 2018, 'nextMonth': 2,    'nextDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'nextYear': 2017, 'nextMonth': 8,    'nextDay': 8   },
        {'year': 2017, 'month': 8,    'day': 6,    'nextYear': 2017, 'nextMonth': 8,    'nextDay': 8   },
        {'year': 2017, 'month': 8,    'day': 5,    'nextYear': 2017, 'nextMonth': 8,    'nextDay': 6   },
        {'year': 2017, 'month': 2,    'day': 7,    'nextYear': 2017, 'nextMonth': 8,    'nextDay': 2   },
        {'year': 2011, 'month': 12,   'day': 31,   'nextYear': 2017, 'nextMonth': 2,    'nextDay': 1   },
    ])
    def testNext(self, year, month, day, nextYear, nextMonth, nextDay):
        self.loadData(nextYear, nextMonth, nextDay)
        
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.browser.find_element_by_id('next').click()
        
        csvFilePath = self.waitExport('nrj', 'sum', nextYear, nextMonth, nextDay, 5)
        self.assertTrue(os.path.isfile(csvFilePath))
        self.assertEqual(self.getExportData(csvFilePath), (self.getData('dates', 'str'), self.getData('nrj', 'sum')))
        os.remove(csvFilePath)

    @testData([
        {'year': 2017, 'month': 8, 'day': 5},
    ])
    def testEmpty(self, year, month, day):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()

        csvFilePath = self.waitExport('nrj', 'sum', year, month, day, 5)
        self.assertFalse(os.path.isfile(csvFilePath))
        with self.assertRaises(FileNotFoundError):
            os.remove(csvFilePath)

    @testData([
        {'year': 2017, 'month': 8, 'day': 5, 'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8, 'day': 5, 'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8, 'day': 5, 'newYear': 2018, 'newMonth': 2,    'newDay': None},
        {'year': 2017, 'month': 8, 'day': 5, 'newYear': 2017, 'newMonth': 8,    'newDay': 5   },
    ])
    def testEmptyChangeDate(self, year, month, day, newYear, newMonth, newDay):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.selectDate(newYear, newMonth, newDay)

        csvFilePath = self.waitExport('nrj', 'sum', year, month, day, 5)
        self.assertFalse(os.path.isfile(csvFilePath))
        with self.assertRaises(FileNotFoundError):
            os.remove(csvFilePath)

    @testData([
        {'newYear': 2017, 'newMonth': 8, 'newDay': 5, 'year': None, 'month': None, 'day': None},
        {'newYear': 2017, 'newMonth': 8, 'newDay': 5, 'year': 2019, 'month': None, 'day': None},
        {'newYear': 2017, 'newMonth': 8, 'newDay': 5, 'year': 2018, 'month': 2,    'day': None},
        {'newYear': 2017, 'newMonth': 8, 'newDay': 5, 'year': 2017, 'month': 8,    'day': 5   },
    ])
    def testEmptyTransition(self, year, month, day, newYear, newMonth, newDay):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.selectDate(newYear, newMonth, newDay)
        self.browser.find_element_by_id('plot').click()

        csvFilePath = self.waitExport('nrj', 'sum', year, month, day, 5)
        self.assertFalse(os.path.isfile(csvFilePath))
        with self.assertRaises(FileNotFoundError):
            os.remove(csvFilePath)

    @testData([
        {'year': 2017, 'month': 8, 'day': 6, 'prevYear': 2017, 'prevMonth': 8, 'prevDay': 5},
    ])
    def testEmptyPrev(self, year, month, day, prevYear, prevMonth, prevDay):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.browser.find_element_by_id('prev').click()

        csvFilePath = self.waitExport('nrj', 'sum', year, month, day, 5)
        self.assertFalse(os.path.isfile(csvFilePath))
        with self.assertRaises(FileNotFoundError):
            os.remove(csvFilePath)

    @testData([
        {'year': 2017, 'month': 8, 'day': 4, 'prevYear': 2017, 'prevMonth': 8, 'prevDay': 5},
    ])
    def testEmptyNext(self, year, month, day, prevYear, prevMonth, prevDay):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.browser.find_element_by_id('next').click()

        csvFilePath = self.waitExport('nrj', 'sum', year, month, day, 5)
        self.assertFalse(os.path.isfile(csvFilePath))
        with self.assertRaises(FileNotFoundError):
            os.remove(csvFilePath)

class PrevNextTest(BrowserTestCase):
    
    def __checkArgument(self, cache, arg):
        if (arg == 'cache'):
            return cache
        if (arg == '!cache'):
            return not cache
        return arg
    
    def cacheTest(fun):
        def cacheTestFun(self, *args, **kwArgs):
            with self.subTest(msg='Without cache'):
                os.rename(self.cacheDir, self.cacheDir + '.del')
                self.browser.get(self.index)
                
                newArgs = (self.__checkArgument(False, a) for a in args)
                newKwArgs = {k: self.__checkArgument(False, a) for k, a in kwArgs.items()}
                fun(self, *newArgs, **newKwArgs)
                
            with self.subTest(msg='With cache'):
                os.rename(self.cacheDir + '.del', self.cacheDir)
                self.browser.get(self.index)
                
                newArgs = (self.__checkArgument(True, a) for a in args)
                newKwArgs = {k: self.__checkArgument(True, a) for k, a in kwArgs.items()}
                fun(self, *newArgs, **newKwArgs)
                
        return cacheTestFun
    
    @testData([
        {'year': 2009, 'prevEnabled': False, 'nextEnabled': True },
        {'year': 2010, 'prevEnabled': True,  'nextEnabled': True },
        {'year': 2011, 'prevEnabled': True,  'nextEnabled': True },
        {'year': 2013, 'prevEnabled': True,  'nextEnabled': True },
        {'year': 2014, 'prevEnabled': True,  'nextEnabled': True },
        {'year': 2015, 'prevEnabled': True,  'nextEnabled': True },
        {'year': 2017, 'prevEnabled': True,  'nextEnabled': True },
        {'year': 2018, 'prevEnabled': True,  'nextEnabled': True },
        {'year': 2019, 'prevEnabled': True,  'nextEnabled': False},
    ])
    @cacheTest
    def testYear(self, year, prevEnabled, nextEnabled):
        self.selectDate(year)
        
        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')
        
        self.assertEnabled(prevButton, prevEnabled)
        self.assertEnabled(nextButton, nextEnabled)
    
    @testData([
        {'year': 2010, 'month': 12, 'prevEnabled': '!cache', 'nextEnabled': True    },
        {'year': 2011, 'month': 6,  'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2011, 'month': 9,  'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2011, 'month': 12, 'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2017, 'month': 2,  'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2017, 'month': 5,  'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2017, 'month': 8,  'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2018, 'month': 2,  'prevEnabled': True,     'nextEnabled': '!cache'},
    ])
    @cacheTest
    def testMonth(self, year, month, prevEnabled, nextEnabled):
        self.selectDate(year, month)
        
        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')
        
        self.assertEnabled(prevButton, prevEnabled)
        self.assertEnabled(nextButton, nextEnabled)
        
    @testData([
        {'year': 2011, 'month': 6,  'day': 24, 'prevEnabled': '!cache', 'nextEnabled': True    },
        {'year': 2011, 'month': 6,  'day': 27, 'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2011, 'month': 6,  'day': 30, 'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2017, 'month': 8,  'day': 2,  'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2017, 'month': 8,  'day': 5,  'prevEnabled': True,     'nextEnabled': True    },
        {'year': 2017, 'month': 8,  'day': 8,  'prevEnabled': True,     'nextEnabled': '!cache'},
    ])  
    @cacheTest
    def testDay(self, year, month, day, prevEnabled, nextEnabled):
        self.selectDate(year, month, day)
        
        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')
        
        self.assertEnabled(prevButton, prevEnabled)
        self.assertEnabled(nextButton, nextEnabled)
    
    # NOTE The page should not be reloaded before each date
    # that's why @cacheTest is first.
    @cacheTest
    @testData([
        {'year': 2009, 'prevYear': 2009, 'prevEnabled': False},
        {'year': 2010, 'prevYear': 2009, 'prevEnabled': False},
        {'year': 2011, 'prevYear': 2010, 'prevEnabled': True },
        {'year': 2013, 'prevYear': 2011, 'prevEnabled': True },
        {'year': 2014, 'prevYear': 2013, 'prevEnabled': True },
        {'year': 2015, 'prevYear': 2014, 'prevEnabled': True },
        {'year': 2017, 'prevYear': 2015, 'prevEnabled': True },
        {'year': 2018, 'prevYear': 2017, 'prevEnabled': True },
        {'year': 2019, 'prevYear': 2018, 'prevEnabled': True },
    ])
    def testPrevYear(self, year, prevYear, prevEnabled):
        self.selectDate(year)
        
        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')
        
        prevButton.click()
        
        self.assertEqual(self.browser.find_element_by_id('year').get_property('value'), str(prevYear))
        self.assertEqual(self.browser.find_element_by_id('month').get_property('value'), '')
        self.assertEqual(self.browser.find_element_by_id('day').get_property('value'), '')
        
        self.assertEnabled(prevButton, prevEnabled)
        self.assertEnabled(nextButton, True)
   
    # NOTE The page should not be reloaded before each date
    # that's why @cacheTest is first.
    @cacheTest
    @testData([
        {'year': 2010, 'month': 12, 'prevYear': 2010, 'prevMonth': 12, 'prevEnabled': False},
        {'year': 2011, 'month': 6,  'prevYear': 2010, 'prevMonth': 12, 'prevEnabled': False},
        {'year': 2011, 'month': 8,  'prevYear': 2011, 'prevMonth': 6,  'prevEnabled': True },
        {'year': 2011, 'month': 9,  'prevYear': 2011, 'prevMonth': 8,  'prevEnabled': True },
        {'year': 2011, 'month': 10, 'prevYear': 2011, 'prevMonth': 9,  'prevEnabled': True },
        {'year': 2011, 'month': 12, 'prevYear': 2011, 'prevMonth': 10, 'prevEnabled': True },
        {'year': 2017, 'month': 2,  'prevYear': 2011, 'prevMonth': 12, 'prevEnabled': True },
        {'year': 2017, 'month': 4,  'prevYear': 2017, 'prevMonth': 2,  'prevEnabled': True },
        {'year': 2017, 'month': 5,  'prevYear': 2017, 'prevMonth': 4,  'prevEnabled': True },
        {'year': 2017, 'month': 6,  'prevYear': 2017, 'prevMonth': 5,  'prevEnabled': True },
        {'year': 2017, 'month': 8,  'prevYear': 2017, 'prevMonth': 6,  'prevEnabled': True },
        {'year': 2018, 'month': 2,  'prevYear': 2017, 'prevMonth': 8,  'prevEnabled': True },
    ])
    def testPrevMonth(self, year, month, prevYear, prevMonth, prevEnabled):
        self.selectDate(year, month)
        
        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')
        
        prevButton.click()
        
        self.assertEqual(self.browser.find_element_by_id('year').get_property('value'), str(prevYear))
        self.assertEqual(self.browser.find_element_by_id('month').get_property('value'), str(prevMonth))
        self.assertEqual(self.browser.find_element_by_id('day').get_property('value'), '')
        
        self.assertEnabled(prevButton, prevEnabled)
        self.assertEnabled(nextButton, True)
    
    # NOTE The page should not be reloaded before each date
    # that's why @cacheTest is first.
    @cacheTest
    @testData([
        {'year': 2011, 'month': 6,  'day': 24, 'prevYear': 2011, 'prevMonth': 6,  'prevDay': 24, 'prevEnabled': False},
        {'year': 2011, 'month': 6,  'day': 26, 'prevYear': 2011, 'prevMonth': 6,  'prevDay': 24, 'prevEnabled': False},
        {'year': 2011, 'month': 6,  'day': 27, 'prevYear': 2011, 'prevMonth': 6,  'prevDay': 26, 'prevEnabled': True },
        {'year': 2011, 'month': 6,  'day': 28, 'prevYear': 2011, 'prevMonth': 6,  'prevDay': 27, 'prevEnabled': True },
        {'year': 2011, 'month': 6,  'day': 30, 'prevYear': 2011, 'prevMonth': 6,  'prevDay': 28, 'prevEnabled': True },
        {'year': 2011, 'month': 12, 'day': 25, 'prevYear': 2011, 'prevMonth': 6,  'prevDay': 30, 'prevEnabled': True },
        {'year': 2017, 'month': 2,  'day': 1,  'prevYear': 2011, 'prevMonth': 12, 'prevDay': 31, 'prevEnabled': True },
        {'year': 2017, 'month': 8,  'day': 2,  'prevYear': 2017, 'prevMonth': 2,  'prevDay': 7,  'prevEnabled': True },
        {'year': 2017, 'month': 8,  'day': 8,  'prevYear': 2017, 'prevMonth': 8,  'prevDay': 6,  'prevEnabled': True },
    ])
    def testPrevDay(self, year, month, day, prevYear, prevMonth, prevDay, prevEnabled):
        self.selectDate(year, month, day)
        
        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')
        
        prevButton.click()
        
        self.assertEqual(self.browser.find_element_by_id('year').get_property('value'), str(prevYear))
        self.assertEqual(self.browser.find_element_by_id('month').get_property('value'), str(prevMonth))
        self.assertEqual(self.browser.find_element_by_id('day').get_property('value'), str(prevDay))
        
        self.assertEnabled(prevButton, prevEnabled)
        self.assertEnabled(nextButton, True)
    
    # NOTE The page should not be reloaded before each date
    # that's why @cacheTest is first.
    @cacheTest   
    @testData([
        {'year': 2009, 'nextYear': 2010, 'nextEnabled': True },
        {'year': 2010, 'nextYear': 2011, 'nextEnabled': True },
        {'year': 2011, 'nextYear': 2013, 'nextEnabled': True },
        {'year': 2013, 'nextYear': 2014, 'nextEnabled': True },
        {'year': 2014, 'nextYear': 2015, 'nextEnabled': True },
        {'year': 2015, 'nextYear': 2017, 'nextEnabled': True },
        {'year': 2017, 'nextYear': 2018, 'nextEnabled': True },
        {'year': 2018, 'nextYear': 2019, 'nextEnabled': False},
        {'year': 2019, 'nextYear': 2019, 'nextEnabled': False},
    ])
    def testNextYear(self, year, nextYear, nextEnabled):
        self.selectDate(year)
        
        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')
        
        nextButton.click()
        
        self.assertEqual(self.browser.find_element_by_id('year').get_property('value'), str(nextYear))
        self.assertEqual(self.browser.find_element_by_id('month').get_property('value'), '')
        self.assertEqual(self.browser.find_element_by_id('day').get_property('value'), '')
        
        self.assertEnabled(prevButton, True)
        self.assertEnabled(nextButton, nextEnabled)
    
    # NOTE The page should not be reloaded before each date
    # that's why @cacheTest is first.
    @cacheTest
    @testData([
        {'year': 2018, 'month': 2,  'nextYear': 2018, 'nextMonth': 2,  'nextEnabled': False},
        {'year': 2017, 'month': 8,  'nextYear': 2018, 'nextMonth': 2,  'nextEnabled': False},
        {'year': 2017, 'month': 6,  'nextYear': 2017, 'nextMonth': 8,  'nextEnabled': True },
        {'year': 2017, 'month': 5,  'nextYear': 2017, 'nextMonth': 6,  'nextEnabled': True },
        {'year': 2017, 'month': 4,  'nextYear': 2017, 'nextMonth': 5,  'nextEnabled': True },
        {'year': 2017, 'month': 2,  'nextYear': 2017, 'nextMonth': 4,  'nextEnabled': True },
        {'year': 2011, 'month': 12, 'nextYear': 2017, 'nextMonth': 2,  'nextEnabled': True },
        {'year': 2011, 'month': 10, 'nextYear': 2011, 'nextMonth': 12, 'nextEnabled': True },
        {'year': 2011, 'month': 9,  'nextYear': 2011, 'nextMonth': 10, 'nextEnabled': True },
        {'year': 2011, 'month': 8,  'nextYear': 2011, 'nextMonth': 9,  'nextEnabled': True },
        {'year': 2011, 'month': 6,  'nextYear': 2011, 'nextMonth': 8,  'nextEnabled': True },
        {'year': 2010, 'month': 12, 'nextYear': 2011, 'nextMonth': 6,  'nextEnabled': True },
    ])
    def testNextMonth(self, year, month, nextYear, nextMonth, nextEnabled):
        self.selectDate(year, month)
        
        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')
        
        nextButton.click()
        
        self.assertEqual(self.browser.find_element_by_id('year').get_property('value'), str(nextYear))
        self.assertEqual(self.browser.find_element_by_id('month').get_property('value'), str(nextMonth))
        self.assertEqual(self.browser.find_element_by_id('day').get_property('value'), '')
        
        self.assertEnabled(prevButton, True)
        self.assertEnabled(nextButton, nextEnabled)
        
    # NOTE The page should not be reloaded before each date
    # that's why @cacheTest is first.
    @cacheTest
    @testData([
        {'year': 2017, 'month': 8,  'day': 8,  'nextYear': 2017, 'nextMonth': 8,  'nextDay': 8,  'nextEnabled': False},
        {'year': 2017, 'month': 8,  'day': 6,  'nextYear': 2017, 'nextMonth': 8,  'nextDay': 8,  'nextEnabled': False},
        {'year': 2017, 'month': 8,  'day': 5,  'nextYear': 2017, 'nextMonth': 8,  'nextDay': 6,  'nextEnabled': True },
        {'year': 2017, 'month': 8,  'day': 4,  'nextYear': 2017, 'nextMonth': 8,  'nextDay': 5,  'nextEnabled': True },
        {'year': 2017, 'month': 8,  'day': 2,  'nextYear': 2017, 'nextMonth': 8,  'nextDay': 4,  'nextEnabled': True },
        {'year': 2017, 'month': 2,  'day': 7,  'nextYear': 2017, 'nextMonth': 8,  'nextDay': 2,  'nextEnabled': True },
        {'year': 2011, 'month': 12, 'day': 31, 'nextYear': 2017, 'nextMonth': 2,  'nextDay': 1,  'nextEnabled': True },
        {'year': 2011, 'month': 6,  'day': 30, 'nextYear': 2011, 'nextMonth': 12, 'nextDay': 25, 'nextEnabled': True },
        {'year': 2011, 'month': 6,  'day': 24, 'nextYear': 2011, 'nextMonth': 6,  'nextDay': 26, 'nextEnabled': True },
    ])
    def testNextDay(self, year, month, day, nextYear, nextMonth, nextDay, nextEnabled):
        self.selectDate(year, month, day)
        
        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')
        
        nextButton.click()
        
        self.assertEqual(self.browser.find_element_by_id('year').get_property('value'), str(nextYear))
        self.assertEqual(self.browser.find_element_by_id('month').get_property('value'), str(nextMonth))
        self.assertEqual(self.browser.find_element_by_id('day').get_property('value'), str(nextDay))
        
        self.assertEnabled(prevButton, True)
        self.assertEnabled(nextButton, nextEnabled)
    
    @cacheTest
    def testNoPrevNext(self):
        prevButton = self.browser.find_element_by_id('prev')
        nextButton = self.browser.find_element_by_id('next')
        
        prevButton.click()
        
        self.assertEqual(self.browser.find_element_by_id('year').get_property('value'), '')
        self.assertEqual(self.browser.find_element_by_id('month').get_property('value'), '')
        self.assertEqual(self.browser.find_element_by_id('day').get_property('value'), '')
        
        self.assertEnabled(prevButton, False)
        self.assertEnabled(nextButton, False)
     
class LegendTest(BrowserTestCase):
    
    def removeChildren(self, elements, src=None):
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
    
    def removeParents(self, elements):
        return [e for e in elements if len(e.find_elements_by_tag_name(e.tag_name)) == 0]
    
    def getLegendListItems(self, parent):
        if parent is None:
            parent = self.browser.find_element_by_id('legend')
        legendItemList = parent.find_elements_by_tag_name('ul')
        self.removeChildren(legendItemList)
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
            (self.removeParents(self.removeChildren(e.find_elements_by_tag_name('span'), 
                                                    e.find_elements_by_tag_name('li'))) + \
            [self.getLegendItems(e)]) for e in legendItems
        ]
            
    def assertLegendTitleStyle(self, title):
        self.assertEqual(title.value_of_css_property('font-family'), 'sans-serif')
        self.assertEqual(title.value_of_css_property('font-size'), '16px')
        self.assertEqual(title.value_of_css_property('font-weight'), '700')
        self.assertEqual(title.value_of_css_property('font-style'), 'normal')
        self.assertEqual(title.value_of_css_property('text-decoration'), 'none')
        self.assertEqual(title.value_of_css_property('text-anchor'), 'start')
    
    def assertLegendItemStyle(self, item):
        self.assertEqual(item.value_of_css_property('font-family'), 'sans-serif')
        self.assertEqual(item.value_of_css_property('font-size'), '16px')
        self.assertEqual(item.value_of_css_property('font-weight'), '400')
        self.assertEqual(item.value_of_css_property('font-style'), 'normal')
        self.assertEqual(item.value_of_css_property('text-decoration'), 'none')
        self.assertEqual(item.value_of_css_property('text-anchor'), 'start')
    
    
    def loadToday(self):
        self.browser.find_element_by_id('today').click()
    
    def testEmpty(self):
        legend = self.browser.find_element_by_id('legend')
        self.assertIn('framed', self.getClasses(legend))
        self.assertEqual(legend.text, '')
    
    @testData([
        {'var': 'nrj',  'agg': 'sum'},
        {'var': 'pac',  'agg': 'sum'},
        {'var': 'pdc',  'agg': 'sum'},
        {'var': 'nrj',  'agg': 'inv'},
        {'var': 'pac',  'agg': 'inv'},
        {'var': 'pdc',  'agg': 'inv'},
        {'var': 'temp', 'agg': 'inv'},
        {'var': 'pdc',  'agg': 'str'},
        {'var': 'udc',  'agg': 'str'},
    ], before=loadToday)
    def testLineTitle(self, var, agg):
        self.selectVar(var)
        self.selectSum(agg)
        
        legend = self.browser.find_element_by_id('legend')
        self.assertIn('framed', self.getClasses(legend))
        legendTitle = self.browser.find_element_by_tag_name('h4')
        self.assertEqual(legendTitle.text, 'Légende')
        self.assertLegendTitleStyle(legendTitle)
     
    @testData(['nrj', 'pac', 'pdc'], before=loadToday)
    def testLineTotal(self, var):
        self.selectVar(var)
        self.selectSum('sum')

        lines = self.getLines()
        legendItems = self.getLegendItems()
        
        for legendElements in legendItems:
            self.assertEqual(len(legendElements), 3)
            legendItem, legendText, legendChildren = legendElements
            
            # Check legend text:
            self.assertNotIn('legenditem', self.getClasses(legendText))
            self.assertEqual(legendText.text, 'Total')
            self.assertLegendItemStyle(legendText)
            
            # Check item element (line):
            self.assertIn('legenditem', self.getClasses(legendItem))
            self.assertEqual(legendItem.text, '——————')
            
            # Find associated line:
            legendItemStyle = self.getStyle(legendItem)
            path = [p for p, c, o in lines if (c == legendItemStyle['color']) and (abs(o - float(legendItemStyle['opacity'])) < 1e-12)]
            self.assertEqual(len(path), 1)
    
    @testData(['nrj', 'pac', 'pdc', 'temp'], before=loadToday)
    def testLinePerInverter(self, var):
        self.selectVar(var)
        self.selectSum('inv')

        lines = self.getLines()
        legendItems = self.getLegendItems()
        
        for i, legendElements in enumerate(legendItems):
            self.assertEqual(len(legendElements), 4)
            legendItem, legendText, legendCheckbox, legendChildren = legendElements
            
            # Check legend text:
            self.assertNotIn('legenditem', self.getClasses(legendText))
            self.assertEqual(legendText.text, 'Onduleur ' + str(i + 1))
            self.assertLegendItemStyle(legendText)
            
            # Check item element (line):
            self.assertIn('legenditem', self.getClasses(legendItem))
            self.assertEqual(legendItem.text, '——————')
            
            # Find associated line:
            legendItemStyle = self.getStyle(legendItem)
            path = [p for p, c, o in lines if (c == legendItemStyle['color']) and (abs(o - float(legendItemStyle['opacity'])) < 1e-12)]
            self.assertEqual(len(path), 1)
            path = path[0]
            
            # Check legend input:
            self.assertIn('input', self.getClasses(legendCheckbox))
            checkbox = legendCheckbox.find_element_by_tag_name('input')
            self.assertEqual(checkbox.get_attribute('type'), 'checkbox')
            self.assertTrue(checkbox.get_property('checked'))
            self.assertFalse(checkbox.get_property('indeterminate'))
            checkbox.click()
            self.assertFalse(checkbox.get_property('checked'))
            self.assertFalse(checkbox.get_property('indeterminate'))
            self.assertTrue(('display' in self.getStyle(path).keys()) and (self.getStyle(path)['display'] == 'none'))
            checkbox.click()
            self.assertTrue(checkbox.get_property('checked'))
            self.assertFalse(checkbox.get_property('indeterminate'))
            self.assertTrue(('display' not in self.getStyle(path).keys()) or (self.getStyle(path)['display'] != 'none'))
          
    @testData(['pdc', 'udc'], before=loadToday)
    def testLinePerString(self, var):
        self.selectVar(var)
        self.selectSum('str')

        lines = self.getLines()
        groups = set([p.find_element_by_xpath('..') for p, c, o in lines])
        legendItems = self.getLegendItems()
        
        for i, legendElements in enumerate(legendItems):
            self.assertEqual(len(legendElements), 3)
            legendText, legendCheckbox, legendSubItems = legendElements
            
            parentCheckbox = legendCheckbox.find_element_by_tag_name('input')
            subCheckboxes = []
            subPaths = []
            
            for j, legendSubElements in enumerate(legendSubItems):
                self.assertEqual(len(legendSubElements), 4)
                legendSubItem, legendSubText, legendSubCheckbox, legendChildren = legendSubElements
            
                # Check item element (line):
                self.assertIn('legenditem', self.getClasses(legendSubItem))
                self.assertEqual(legendSubItem.text, '——————')
                
                # Find associate line:
                legendSubItemStyle = self.getStyle(legendSubItem)
                path = [p for p, c, o in lines if (c == legendSubItemStyle['color']) and (abs(o - float(legendSubItemStyle['opacity'])) < 1e-12)]
                self.assertEqual(len(path), 1)
                path = path[0]
                subPaths += [path]
                
                # Check legend text:
                self.assertNotIn('legenditem', self.getClasses(legendSubText))
                self.assertEqual(legendSubText.text, 'String ' + str(j + 1))
                self.assertLegendItemStyle(legendSubText)
                
                # Check legend input:
                self.assertIn('input', self.getClasses(legendSubCheckbox))
                subCheckbox = legendSubCheckbox.find_element_by_tag_name('input')
                subCheckboxes += [subCheckbox]
                self.assertEqual(subCheckbox.get_attribute('type'), 'checkbox')
                self.assertTrue(subCheckbox.get_property('checked'))
                self.assertFalse(subCheckbox.get_property('indeterminate'))
                subCheckbox.click()
                self.assertFalse(subCheckbox.get_property('checked'))
                self.assertFalse(subCheckbox.get_property('indeterminate'))
                self.assertTrue(parentCheckbox.get_property('checked'))
                self.assertTrue(parentCheckbox.get_property('indeterminate'))
                self.assertTrue(('display' in self.getStyle(path).keys()) and (self.getStyle(path)['display'] == 'none'))
                subCheckbox.click()
                self.assertTrue(subCheckbox.get_property('checked'))
                self.assertFalse(subCheckbox.get_property('indeterminate'))
                self.assertTrue(parentCheckbox.get_property('checked'))
                self.assertFalse(parentCheckbox.get_property('indeterminate'))
                self.assertTrue(('display' not in self.getStyle(path).keys()) or (self.getStyle(path)['display'] != 'none'))
            
            # Check legend text:
            self.assertNotIn('legenditem', self.getClasses(legendText))
            self.assertEqual(legendText.text, 'Onduleur ' + str(i + 1))
            self.assertLegendItemStyle(legendText)
            
            # Check legend input:
            self.assertIn('input', self.getClasses(legendCheckbox))
            checkbox = legendCheckbox.find_element_by_tag_name('input')
            self.assertEqual(checkbox.get_attribute('type'), 'checkbox')
            self.assertTrue(checkbox.get_property('checked'))
            self.assertFalse(checkbox.get_property('indeterminate'))
            checkbox.click()
            self.assertFalse(checkbox.get_property('checked'))
            self.assertFalse(checkbox.get_property('indeterminate'))
            self.assertFalse(any([c.get_property('checked') for c in subCheckboxes]))
            self.assertFalse(any([c.get_property('indeterminate') for c in subCheckboxes]))
            self.assertTrue(all([('display' in self.getStyle(p).keys()) and (self.getStyle(p)['display'] == 'none') for p in subPaths]))
            checkbox.click()
            self.assertTrue(checkbox.get_property('checked'))
            self.assertFalse(checkbox.get_property('indeterminate'))
            self.assertTrue(all([c.get_property('checked') for c in subCheckboxes]))
            self.assertFalse(any([c.get_property('indeterminate') for c in subCheckboxes]))
            self.assertTrue(all([('display' not in self.getStyle(p).keys()) or (self.getStyle(p)['display'] != 'none') for p in subPaths]))
            
            # Check sub checkboxes uncheck parent checkbox:
            for subCheckbox in subCheckboxes:
                subCheckbox.click()
                self.assertFalse(subCheckbox.get_property('checked'))
                self.assertFalse(subCheckbox.get_property('indeterminate'))
            self.assertFalse(checkbox.get_property('checked'))
            self.assertFalse(checkbox.get_property('indeterminate'))
            self.assertTrue(all([('display' in self.getStyle(p).keys()) and (self.getStyle(p)['display'] == 'none') for p in subPaths]))
            for subCheckbox in subCheckboxes:
                subCheckbox.click()
                self.assertTrue(subCheckbox.get_property('checked'))
                self.assertFalse(subCheckbox.get_property('indeterminate'))
            self.assertTrue(checkbox.get_property('checked'))
            self.assertFalse(checkbox.get_property('indeterminate'))
            self.assertTrue(all([('display' not in self.getStyle(p).keys()) or (self.getStyle(p)['display'] != 'none') for p in subPaths]))
        
    @testData([
        {'year': None, 'month': None, 'var': 'nrj', 'agg': 'sum'},
        {'year': None, 'month': None, 'var': 'nrj', 'agg': 'inv'},
        {'year': 2019, 'month': None, 'var': 'nrj', 'agg': 'sum'},
        {'year': 2019, 'month': None, 'var': 'nrj', 'agg': 'inv'},
        {'year': 2018, 'month':    2, 'var': 'nrj', 'agg': 'sum'},
        {'year': 2018, 'month':    2, 'var': 'nrj', 'agg': 'inv'},
        {'year': 2018, 'month':    2, 'var': 'pwr', 'agg': 'sum'},
        {'year': 2018, 'month':    2, 'var': 'pwr', 'agg': 'inv'},
    ])
    def testBarTitle(self, year, month, var, agg):
        self.selectDate(year, month)
        self.browser.find_element_by_id('plot').click()
        self.selectVar(var)
        self.selectSum(agg)
        
        legend = self.browser.find_element_by_id('legend')
        self.assertIn('framed', self.getClasses(legend))
        legendTitle = self.browser.find_element_by_tag_name('h4')
        self.assertEqual(legendTitle.text, 'Légende')
        self.assertLegendTitleStyle(legendTitle)
        
    @testData([
        {'year': None, 'month': None, 'var': 'nrj'},
        {'year': 2019, 'month': None, 'var': 'nrj'},
        {'year': 2018, 'month':    2, 'var': 'nrj'},
        {'year': 2018, 'month':    2, 'var': 'pwr'},
    ])
    def testBarTotal(self, year, month, var):
        self.selectDate(year, month)
        self.browser.find_element_by_id('plot').click()
        self.selectVar(var)
        self.selectSum('sum')

        bars = self.getBars()
        legendItems = self.getLegendItems()
        
        for legendElements in legendItems:
            self.assertEqual(len(legendElements), 3)
            legendItem, legendText, legendChildren = legendElements
            
            # Check legend text:
            self.assertNotIn('legenditem', self.getClasses(legendText))
            self.assertEqual(legendText.text, 'Total')
            self.assertLegendItemStyle(legendText)
            
            # Check item element (line):
            self.assertIn('legenditem', self.getClasses(legendItem))
            self.assertEqual(legendItem.text, '——————')
            
            # Find associated line:
            legendItemStyle = self.getStyle(legendItem)
            pathes = [p for p, c, o in bars if (c == legendItemStyle['color']) and (abs(o - float(legendItemStyle['opacity'])) < 1e-12)]
            self.assertGreater(len(pathes), 0)

    @testData([
        {'year': None, 'month': None, 'day': None, 'var': 'nrj'},
        {'year': 2019, 'month': None, 'day': None, 'var': 'nrj'},
        {'year': 2018, 'month':    2, 'day': None, 'var': 'nrj'},
        {'year': 2018, 'month':    2, 'day': None, 'var': 'pwr'},
    ])
    def testBarPerInverter(self, year, month, day, var):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.selectVar(var)
        self.selectSum('inv')

        bars = self.getBars()
        legendItems = self.getLegendItems()
        
        for i, legendElements in enumerate(legendItems):
            self.assertEqual(len(legendElements), 4)
            legendItem, legendText, legendCheckbox, legendChildren = legendElements
            
            # Check legend text:
            self.assertNotIn('legenditem', self.getClasses(legendText))
            self.assertEqual(legendText.text, 'Onduleur ' + str(i + 1))
            self.assertLegendItemStyle(legendText)
            
            # Check item element (line):
            self.assertIn('legenditem', self.getClasses(legendItem))
            self.assertEqual(legendItem.text, '——————')
            
            # Find associated line:
            legendItemStyle = self.getStyle(legendItem)
            pathes = [p for p, c, o in bars if (c == legendItemStyle['color']) and (abs(o - float(legendItemStyle['opacity'])) < 1e-12)]
            self.assertGreater(len(pathes), 0)
            
            # Check legend input:
            self.assertIn('input', self.getClasses(legendCheckbox))
            checkbox = legendCheckbox.find_element_by_tag_name('input')
            self.assertEqual(checkbox.get_attribute('type'), 'checkbox')
            self.assertTrue(checkbox.get_property('checked'))
            self.assertFalse(checkbox.get_property('indeterminate'))
            checkbox.click()
            self.assertFalse(checkbox.get_property('checked'))
            self.assertFalse(checkbox.get_property('indeterminate'))
            self.assertTrue(all([('display' in self.getStyle(p).keys()) and (self.getStyle(p)['display'] == 'none') for p in pathes]))
            checkbox.click()
            self.assertTrue(checkbox.get_property('checked'))
            self.assertFalse(checkbox.get_property('indeterminate'))
            self.assertTrue(all([('display' not in self.getStyle(p).keys()) or (self.getStyle(p)['display'] != 'none') for p in pathes]))

    @testData([
        {'year': 2017, 'month': 8,    'day': 5},
    ])
    def testEmpty(self, year, month, day):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()

        self.assertEqual(len(self.browser.find_element_by_id('legend').find_elements_by_xpath('child::*')), 0)
        self.assertEqual(len(self.browser.find_element_by_id('legend').text), 0)

    @testData([
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2018, 'newMonth': 2,    'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2017, 'newMonth': 8,    'newDay': 5   },
    ])
    def testEmptyChangeDate(self, year, month, day, newYear, newMonth, newDay):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.selectDate(newYear, newMonth, newDay)

        self.assertEqual(len(self.browser.find_element_by_id('legend').find_elements_by_xpath('child::*')), 0)
        self.assertEqual(len(self.browser.find_element_by_id('legend').text), 0)

    @testData([
        {'newYear': 2017, 'newMonth': 8,    'newDay': 5,    'year': None, 'month': None, 'day': None},
        {'newYear': 2017, 'newMonth': 8,    'newDay': 5,    'year': 2019, 'month': None, 'day': None},
        {'newYear': 2017, 'newMonth': 8,    'newDay': 5,    'year': 2018, 'month': 2,    'day': None},
        {'newYear': 2017, 'newMonth': 8,    'newDay': 5,    'year': 2017, 'month': 8,    'day': 5   },
    ])
    def testEmptyTransition(self, year, month, day, newYear, newMonth, newDay):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.selectDate(newYear, newMonth, newDay)
        self.browser.find_element_by_id('plot').click()

        self.assertEqual(len(self.browser.find_element_by_id('legend').find_elements_by_xpath('child::*')), 0)
        self.assertEqual(len(self.browser.find_element_by_id('legend').text), 0)

    @testData([
        {'year': 2017, 'month': 8,    'day': 6,    'prevYear': 2017, 'prevMonth': 8,    'prevDay': 5   },
    ])
    def testEmptyPrev(self, year, month, day, prevYear, prevMonth, prevDay):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.browser.find_element_by_id('prev').click()

        self.assertEqual(len(self.browser.find_element_by_id('legend').find_elements_by_xpath('child::*')), 0)
        self.assertEqual(len(self.browser.find_element_by_id('legend').text), 0)

    @testData([
        {'year': 2017, 'month': 8,    'day': 4,    'prevYear': 2017, 'prevMonth': 8,    'prevDay': 5   },
    ])
    def testEmptyNext(self, year, month, day, prevYear, prevMonth, prevDay):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.browser.find_element_by_id('next').click()

        self.assertEqual(len(self.browser.find_element_by_id('legend').find_elements_by_xpath('child::*')), 0)
        self.assertEqual(len(self.browser.find_element_by_id('legend').text), 0)

class ChartTest(BrowserTestCase):
    def __init__(self, *args, **kwArgs):
        super().__init__(*args, **kwArgs)
        
        self.lineWidth = 1;
       
    def parseTranslate(self, group, axis=None):
        transform = group.get_attribute('transform')
        match = re.fullmatch(r'translate\(([0-9]*(?:\.[0-9]*)?),([0-9]*(?:\.[0-9]*)?)\)', transform)
        self.assertIsNotNone(match)
        if (axis == 'xaxis'):
            return float(match.group(1))
        elif (axis == 'yaxis') or (axis == 'grid'):
            return float(match.group(2))
        else:
            return (float(match.group(1)), float(match.group(2)))
        
    def parseCoords(self, elem, axis):
        if (axis == 'xaxis'):
            x = elem.get_attribute('x')
            if x is not None:
                return float(x)
            x1 = elem.get_attribute('x1')
            x2 = elem.get_attribute('x2')
            self.assertEqual(x1, x2)
            if x1 is not None:
                return float(x1)
            return 0
        else:
            y = elem.get_attribute('y')
            if y is not None:
                return float(y)
            y1 = elem.get_attribute('y1')
            y2 = elem.get_attribute('y2')
            self.assertEqual(y1, y2)
            if y1 is not None:
                return float(y1)
            return 0
    
    def getAxis(self, axis):
        chart = self.browser.find_element_by_id('chart')
        if (axis == 'grid'):
            return chart.find_element_by_class_name('grid')
        else:
            return chart.find_element_by_id(axis)
    
    def getDomain(self, axis, arrow=True):
        try:
            domain = self.getAxis(axis).find_element_by_class_name('domain')
        except (selenium.NoSuchElementException):
            return None
        
        self.assertEqual(domain.tag_name, 'path')
        if (arrow):
            self.assertEqual(domain.get_attribute('marker-end'), 'url(#arrowhead)')
        else:
            self.assertIsNone(domain.get_attribute('marker-end'))
            
        match = re.fullmatch(r'M([0-9]*(?:\.[0-9]*)?),([0-9]*(?:\.[0-9]*)?)([VH])([0-9]*(?:\.[0-9]*)?)([VH])([0-9]*(?:\.[0-9]*)?)', domain.get_attribute('d'))
        self.assertIsNotNone(match)
        
        if (match.group(5) == 'H'):
            begin = float(match.group(1))
        elif (match.group(5) == 'V'):
            begin = float(match.group(2))
        else:
            raise ValueError('Impossible')
        end = float(match.group(6))
        
        return (begin - self.lineWidth / 2, end - self.lineWidth / 2)
        
    def getTickLabels(self, axis):
        ticks = self.getAxis(axis).find_elements_by_class_name('tick')
        try:
            tickLabels = [float(t.find_element_by_tag_name('text').text) for t in ticks]
        except (ValueError):
            tickLabels = [self.monthNumber(t.find_element_by_tag_name('text').text) for t in ticks]
    
        scale = 1
        axisLabel = self.getLabel(axis)
        #if (axis == 'yaxis'):
        prefixes = 'kMGT'
        match = re.search(r' \(([{}])'.format(prefixes), axisLabel.text)
        if match is not None:
            scale = 10 ** (3 + 3*prefixes.index(match.group(1)))
    
        return list(map(lambda x: scale*x, tickLabels))
    
    def getTickPositions(self, axis, centered=False):
        ticks = self.getAxis(axis).find_elements_by_class_name('tick')
        offsets = [self.parseTranslate(t, axis) for t in ticks]
        
        delta = list(map(lambda x, y: abs(x - y), offsets, offsets[1:]))
        self.assertTrue(all(map(lambda x, y: abs(x - y) < 1e-7, delta, delta[1:])))
        
        labels = [t.find_element_by_tag_name('text') for t in ticks]
        ticks = [t.find_element_by_tag_name('line') for t in ticks]
        
        labelPos = [self.parseCoords(l, axis) for l in labels]
        tickPos = [self.parseCoords(t, axis) for t in ticks]
        if centered:
            self.assertEqual(max(list(map(lambda l, t: int(abs(l + delta[0]/2 - t)), labelPos, tickPos))), 0)
        else:
            self.assertEqual(tickPos, labelPos)
        
        delta = list(map(lambda x, y: abs(x - y), tickPos, tickPos[1:]))
        self.assertTrue(all(map(lambda x, y: abs(x - y) < 1e-7, delta, delta[1:])))
        
        if centered:
            return list(map(lambda x, y: x + y, offsets, tickPos))
        else:
            return list(map(lambda x, y: x + y - self.lineWidth / 2, offsets, tickPos))
    
    def initMapFunction(self, axis, centered=False, extraPadding=0):
        ticks = self.getTickPositions(axis, centered)
        tickLabels = self.getTickLabels(axis)
        
        iM, xM = max(enumerate(ticks), key=lambda t: t[0])
        im, xm = min(enumerate(ticks), key=lambda t: t[0])
        
        if centered:
            setattr(self, axis[0] + 'Map', lambda x: tickLabels[max(0, min(len(tickLabels) - 1, int(1 + im + (x - xm) * (iM - im) / (xM - xm))))] + 1 + im + (x - xm) * (iM - im) / (xM - xm) - max(0, min(len(tickLabels) - 1, int(1 + im + (x - xm) * (iM - im) / (xM - xm)))) - extraPadding)
        else:
            setattr(self, axis[0] + 'Map', lambda x: tickLabels[im] + (x - xm) * (tickLabels[iM] - tickLabels[im]) / (xM - xm))
        
    def parsePath(self, path):
        self.assertRegex(path, r'^M([0-9]+(?:\.[0-9]*)?,[0-9]+(?:\.[0-9]*)?)(?:L([0-9]+(?:\.[0-9]*)?,[0-9]+(?:\.[0-9]*)?))*$')
        coords = [tuple([float(n) for n in c.split(',')]) for c in path[1:].split('L')]
        return [(self.xMap(c[0]), self.yMap(c[1])) for c in coords]
        
    def parseRect(self, rect):
        offset1 = self.parseTranslate(rect.find_element_by_xpath('../..'))
        offset2 = self.parseTranslate(rect.find_element_by_xpath('..'))
        
        return (
            self.xMap(float(rect.get_attribute('x')) + offset1[0] + offset2[0]),
            self.yMap(float(rect.get_attribute('y')) + offset1[1] + offset2[1]),
            self.xMap(float(rect.get_attribute('x')) + offset1[0] + offset2[0] + float(rect.get_attribute('width'))),
            self.yMap(float(rect.get_attribute('y')) + offset1[1] + offset2[1] + float(rect.get_attribute('height'))) 
        )
        
        
    def getLineData(self):
        # Grouping lines by color:
        # NOTE assuming they are in the right order.
        groups = []
        lines = self.getLines()
        for p, c, o in lines:
            ok = False
            for i in range(0, len(groups)):
                if (groups[i][0][1] == c):
                    if not ok:
                        groups[i] += [(p, c, o)]
                        ok = True
                    break
            if not ok:
                groups += [[(p, c, o)]]
            
        return [[self.parsePath(p.get_attribute('d')) for p, c, o in g] for g in groups]
        
    def getBarData(self):
        # Grouping bars by color and opacity:
        # NOTE assuming they are in the right order.
        groups = []
        bars = self.getBars()
        for p, c, o in bars:
            ok = False
            for i in range(0, len(groups)):
                if (groups[i][0][0][1] == c):
                    for j in range(0, len(groups[i])):
                        if (groups[i][j][0][2] == o):
                            groups[i][j] += [(p, c, o)]
                            ok = True
                            break
                    if not ok:
                        groups[i] += [[(p, c, o)]]
                        ok = True
                    break
            if not ok:
                groups += [[[(p, c, o)]]]
                
        return [[[self.parseRect(p) for p, c, o in g2] for g2 in g1] for g1 in groups]
        
    def getLabel(self, axis):
        chart = self.browser.find_element_by_id('chart')
        labels = [e.find_element_by_tag_name('text') for e in chart.find_elements_by_class_name('label')]
        if (axis == 'xaxis'):
            labels = [e for e in labels if e.get_attribute('transform') is None]
        elif (axis == 'yaxis'):
            labels = [e for e in labels if e.get_attribute('transform') is not None]
        else:
            raise ValueError('Unknown axis: {}'.format(axis))
        self.assertEqual(len(labels), 1)
        return labels[0]
    
    def getRange(self, axis, centered):
        return tuple(map(getattr(self, axis[0] + 'Map'), self.getDomain(axis, not centered)))
    
    def getDataRange(self, var, agg=None):
        data = self.getData(var, agg)
        if agg is not None:
            return 0., float(max(map(lambda x: max(map(max, x)), data)))
        else:
            return min(data), max(data)
    
    def assertRangeEqual(self, range1, range2):
        self.assertAlmostEqual(range1[0], range2[0])
        self.assertAlmostEqual(range1[1], range2[1])
    
    def assertCoordinatesEqual(self, coords, x, y):
        for i, c in enumerate(coords):
            if type(c) is tuple:
                self.assertAlmostEqual(c[0], x[i])
                self.assertAlmostEqual(c[1], y[i])
            else:
                self.assertCoordinatesEqual(c, x, y[i])
                
    def assertRectanglesEqual(self, rects, x, y, nBars=None, bar=None):
        if nBars is None:
            nBars = len(rects) * max([len(r) for r in rects])
        
        for i, r in enumerate(rects):
            if type(r) is tuple:
                if (nBars == 1):
                    begin = 0.01
                    end   = 0.99
                else:
                    begin = 0.05 + (0.9 / nBars) * (bar + 0.01)
                    end   = 0.05 + (0.9 / nBars) * (bar + 0.99)
                self.assertAlmostEqual(r[0], x[i] + begin)
                self.assertAlmostEqual(r[1], y[i])
                self.assertAlmostEqual(r[2], x[i] + end)
                self.assertAlmostEqual(r[3], 0.0)
            else:
                if bar is not None:
                    b = bar
                else:
                    b = i
                self.assertRectanglesEqual(r, x, y[i], nBars, b)
    
    def assertLabelStyle(self, label):
        self.assertEqual(label.value_of_css_property('font-family'), 'sans-serif')
        self.assertEqual(label.value_of_css_property('font-size'), '12px')
        self.assertEqual(label.value_of_css_property('font-weight'), '700')
        self.assertEqual(label.value_of_css_property('font-style'), 'normal')
        self.assertEqual(label.value_of_css_property('text-decoration'), 'none')
        self.assertEqual(label.value_of_css_property('text-anchor'), 'middle')
    
    def loadToday(self):
        self.loadData('today')
        self.browser.find_element_by_id('today').click()
      
    def loadEmpty(self):
        self.loadData(2017, 8, 5)
        self.selectDate(2017, 8, 5)
        self.browser.find_element_by_id('plot').click()
       
    @testData([
        {'var': 'nrj',  'agg': 'sum'},
        {'var': 'nrj',  'agg': 'inv'},
        {'var': 'pac',  'agg': 'sum'},
        {'var': 'pac',  'agg': 'inv'},
        {'var': 'pdc',  'agg': 'sum'},
        {'var': 'pdc',  'agg': 'inv'},
        {'var': 'pdc',  'agg': 'str'},
        {'var': 'udc',  'agg': 'str'},
        {'var': 'temp', 'agg': 'inv'},
    ], before=loadEmpty)   
    def testEmptyLabel(self, var, agg):
        self.selectVar(var)
        self.selectSum(agg)
        
        xLabel = self.getLabel('xaxis')
        self.assertEqual(xLabel.text, '')
        
        yLabel = self.getLabel('yaxis')
        self.assertEqual(yLabel.text, '')
      
    @testData([
        {'year': None, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': None, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2019, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': 2019, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2018, 'month': 2,    'day': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': 2018, 'month': 2,    'day': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2018, 'month': 2,    'day': None, 'var': 'pwr',  'agg': 'sum'},
        {'year': 2018, 'month': 2,    'day': None, 'var': 'pwr',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'nrj',  'agg': 'sum'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'nrj',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pac',  'agg': 'sum'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pac',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pdc',  'agg': 'sum'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pdc',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pdc',  'agg': 'str'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'udc',  'agg': 'str'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'temp', 'agg': 'inv'},
    ])
    def testLabel(self, year, month, day, var, agg):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.selectVar(var)
        self.selectSum(agg)
        
        xLabel = self.getLabel('xaxis')
        if year is None:
            self.assertEqual(xLabel.text, 'Année')
        elif month is None:
            self.assertEqual(xLabel.text, 'Mois')
        elif day is None:
            self.assertEqual(xLabel.text, 'Jour')
        else:
            self.assertEqual(xLabel.text, 'Temps (h)')
        self.assertLabelStyle(xLabel)
        
        yLabel = self.getLabel('yaxis')
        self.assertRegex(yLabel.text, r'{} \([kMGT]?{}\)'.format(self.longVar(var), self.unit(var)))
        self.assertLabelStyle(yLabel)
    
    @testData([
        {'var': 'nrj',  'agg': 'sum'},
        {'var': 'nrj',  'agg': 'inv'},
        {'var': 'pac',  'agg': 'sum'},
        {'var': 'pac',  'agg': 'inv'},
        {'var': 'pdc',  'agg': 'sum'},
        {'var': 'pdc',  'agg': 'inv'},
        {'var': 'pdc',  'agg': 'str'},
        {'var': 'udc',  'agg': 'str'},
        {'var': 'temp', 'agg': 'inv'},
    ], before=loadEmpty)
    def testEmptyAxis(self, var, agg):
        self.selectVar(var)
        self.selectSum(agg)
        
        self.assertEqual(len(self.getAxis('xaxis').find_elements_by_xpath('./*')), 0)
        self.assertEqual(len(self.getAxis('yaxis').find_elements_by_xpath('./*')), 0)
    
    @testData([
        {'var': 'nrj',  'agg': 'sum'},
        {'var': 'nrj',  'agg': 'inv'},
        {'var': 'pac',  'agg': 'sum'},
        {'var': 'pac',  'agg': 'inv'},
        {'var': 'pdc',  'agg': 'sum'},
        {'var': 'pdc',  'agg': 'inv'},
        {'var': 'pdc',  'agg': 'str'},
        {'var': 'udc',  'agg': 'str'},
        {'var': 'temp', 'agg': 'inv'},
    ], before=loadToday)
    def testLineAxis(self, var, agg):
        self.selectVar(var)
        self.selectSum(agg)
        
        self.initMapFunction('xaxis')
        self.initMapFunction('yaxis')
        
        # Check x axis:
        xTickLabels = self.getTickLabels('xaxis')
        self.assertEqual(xTickLabels, list(range(int(min(xTickLabels)), int(max(xTickLabels) + 1))))
        self.assertRangeEqual(self.getRange('xaxis', False), self.getDataRange('dates'))
        
        # Check y axis:
        self.assertRangeEqual(self.getRange('yaxis', False), self.getDataRange(var, agg))
        
    @testData([
        {'year': None, 'month': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': None, 'month': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2019, 'month': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': 2019, 'month': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2018, 'month': 2,    'var': 'nrj',  'agg': 'sum'},
        {'year': 2018, 'month': 2,    'var': 'nrj',  'agg': 'inv'},
        {'year': 2018, 'month': 2,    'var': 'pwr',  'agg': 'sum'},
        {'year': 2018, 'month': 2,    'var': 'pwr',  'agg': 'inv'},
    ])
    def testBarAxis(self, year, month, var, agg):
        self.loadData(year, month)
        
        self.selectDate(year, month)
        self.browser.find_element_by_id('plot').click()
        self.selectVar(var)
        self.selectSum(agg)
        
        if (agg != 'sum'):
            self.initMapFunction('xaxis', True)
        else:
            self.initMapFunction('xaxis', True)
        self.initMapFunction('yaxis')
        
        # Check x axis:
        xTickLabels = self.getTickLabels('xaxis')
        if (agg != 'sum'):
            self.assertRangeEqual(self.getRange('xaxis', True), (min(xTickLabels) - 0.1 / 2, max(xTickLabels) + 1 + 0.1 / 2))
        else:
            self.assertRangeEqual(self.getRange('xaxis', True), (float(min(xTickLabels)), float(max(xTickLabels) + 1)))
        self.assertEqual(self.getTickLabels('xaxis'), self.getData('dates'))
        
        # Check y axis:
        self.assertRangeEqual(self.getRange('yaxis', False), self.getDataRange(var, agg))
    
    @testData([
        {'var': 'nrj',  'agg': 'sum'},
        {'var': 'nrj',  'agg': 'inv'},
        {'var': 'pac',  'agg': 'sum'},
        {'var': 'pac',  'agg': 'inv'},
        {'var': 'pdc',  'agg': 'sum'},
        {'var': 'pdc',  'agg': 'inv'},
        {'var': 'pdc',  'agg': 'str'},
        {'var': 'udc',  'agg': 'str'},
        {'var': 'temp', 'agg': 'inv'},
    ], before=loadEmpty)
    def testEmptyGrid(self, var, agg):
        self.selectVar(var)
        self.selectSum(agg)
        
        self.assertEqual(len(self.getAxis('grid').find_elements_by_xpath('./*')), 0)
    
    @testData([
        {'year': None, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': None, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2019, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': 2019, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2018, 'month': 2,    'day': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': 2018, 'month': 2,    'day': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2018, 'month': 2,    'day': None, 'var': 'pwr',  'agg': 'sum'},
        {'year': 2018, 'month': 2,    'day': None, 'var': 'pwr',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'nrj',  'agg': 'sum'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'nrj',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pac',  'agg': 'sum'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pac',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pdc',  'agg': 'sum'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pdc',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pdc',  'agg': 'str'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'udc',  'agg': 'str'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'temp', 'agg': 'inv'},
    ])
    def testGrid(self, year, month, day, var, agg):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.selectVar(var)
        self.selectSum(agg)
        
        self.assertEqual(self.getTickPositions('yaxis'), self.getTickPositions('grid'))
    
    @testData([
        {'var': 'nrj',  'agg': 'sum'},
        {'var': 'nrj',  'agg': 'inv'},
        {'var': 'pac',  'agg': 'sum'},
        {'var': 'pac',  'agg': 'inv'},
        {'var': 'pdc',  'agg': 'sum'},
        {'var': 'pdc',  'agg': 'inv'},
        {'var': 'pdc',  'agg': 'str'},
        {'var': 'udc',  'agg': 'str'},
        {'var': 'temp', 'agg': 'inv'},
    ], before=loadEmpty)
    def testEmptyData(self, var, agg):
        self.selectVar(var)
        self.selectSum(agg)
        
        self.assertEqual(len(self.getLines()), 0)
        self.assertEqual(len(self.getBars()), 0)
    
    @testData([
        {'var': 'nrj',  'agg': 'sum'},
        {'var': 'nrj',  'agg': 'inv'},
        {'var': 'pac',  'agg': 'sum'},
        {'var': 'pac',  'agg': 'inv'},
        {'var': 'pdc',  'agg': 'sum'},
        {'var': 'pdc',  'agg': 'inv'},
        {'var': 'pdc',  'agg': 'str'},
        {'var': 'udc',  'agg': 'str'},
        {'var': 'temp', 'agg': 'inv'},
    ], before=loadToday)
    def testLineData(self, var, agg):
        self.selectVar(var)
        self.selectSum(agg)
        
        self.initMapFunction('xaxis')
        self.initMapFunction('yaxis')
        
        self.assertCoordinatesEqual(self.getLineData(), self.getData('dates'), self.getData(var, agg))
    
    @testData([
        {'year': None, 'month': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': None, 'month': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2019, 'month': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': 2019, 'month': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2018, 'month': 2,    'var': 'nrj',  'agg': 'sum'},
        {'year': 2018, 'month': 2,    'var': 'nrj',  'agg': 'inv'},
        {'year': 2018, 'month': 2,    'var': 'pwr',  'agg': 'sum'},
        {'year': 2018, 'month': 2,    'var': 'pwr',  'agg': 'inv'},
    ])
    def testBarData(self, year, month, var, agg):
        self.loadData(year, month)
        
        self.selectDate(year, month)
        self.browser.find_element_by_id('plot').click()
        self.selectVar(var)
        self.selectSum(agg)
        
        if (agg != 'sum'):
            self.initMapFunction('xaxis', True)
        else:
            self.initMapFunction('xaxis', True)
        self.initMapFunction('yaxis')
        
        self.assertRectanglesEqual(self.getBarData(), self.getData('dates'), self.getData(var, agg))
    
    @testData([
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2018, 'newMonth': 2,    'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2017, 'newMonth': 8,    'newDay': 5   },
    ])
    def testEmptyChangeDate(self, year, month, day, newYear, newMonth, newDay):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.selectDate(newYear, newMonth, newDay)
        
        self.assertEqual(len(self.getLines()), 0)
        self.assertEqual(len(self.getBars()), 0)
    
    @testData([
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2018, 'newMonth': 2,    'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2017, 'newMonth': 8,    'newDay': 5   },
    ])
    def testLineChangeDate(self, year, month, day, newYear, newMonth, newDay):
        self.loadData(year, month, day)
        
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.selectDate(newYear, newMonth, newDay)
        
        self.initMapFunction('xaxis')
        self.initMapFunction('yaxis')
        
        self.assertCoordinatesEqual(self.getLineData(), self.getData('dates'), self.getData('nrj', 'sum'))
        
    @testData([
        {'year': None, 'month': None, 'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': None, 'month': None, 'newYear': 2018, 'newMonth': 2,    'newDay': None},
        {'year': None, 'month': None, 'newYear': 2017, 'newMonth': 8,    'newDay': 5   },
        {'year': None, 'month': None, 'newYear': 2017, 'newMonth': 8,    'newDay': 8   },
        {'year': 2019, 'month': None, 'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2019, 'month': None, 'newYear': 2018, 'newMonth': 2,    'newDay': None},
        {'year': 2019, 'month': None, 'newYear': 2017, 'newMonth': 8,    'newDay': 5   },
        {'year': 2019, 'month': None, 'newYear': 2017, 'newMonth': 8,    'newDay': 8   },
        {'year': 2018, 'month': 2,    'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2018, 'month': 2,    'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2018, 'month': 2,    'newYear': 2017, 'newMonth': 8,    'newDay': 5   },
        {'year': 2018, 'month': 2,    'newYear': 2017, 'newMonth': 8,    'newDay': 8   },
    ])
    def testBarChangeDate(self, year, month, newYear, newMonth, newDay):
        self.loadData(year, month)
        
        self.selectDate(year, month)
        self.browser.find_element_by_id('plot').click()
        self.selectDate(newYear, newMonth, newDay)
        
        self.initMapFunction('xaxis', True)
        self.initMapFunction('yaxis')
        
        self.assertRectanglesEqual(self.getBarData(), self.getData('dates'), self.getData('nrj', 'sum'))
    
    @testData([
        {'newYear': 2017, 'newMonth': 8,    'newDay': 5,    'year': None, 'month': None, 'day': None},
        {'newYear': 2017, 'newMonth': 8,    'newDay': 5,    'year': 2019, 'month': None, 'day': None},
        {'newYear': 2017, 'newMonth': 8,    'newDay': 5,    'year': 2018, 'month': 2,    'day': None},
        {'newYear': 2017, 'newMonth': 8,    'newDay': 5,    'year': 2017, 'month': 8,    'day': 5   },
    ])
    def testEmptyTransition(self, year, month, day, newYear, newMonth, newDay):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.selectDate(newYear, newMonth, newDay)
        self.browser.find_element_by_id('plot').click()
        
        self.assertEqual(len(self.getLines()), 0)
        self.assertEqual(len(self.getBars()), 0)
    
    @testData([
        {'newYear': 2017, 'newMonth': 8,    'newDay': 8,    'year': None, 'month': None, 'day': None},
        {'newYear': 2017, 'newMonth': 8,    'newDay': 8,    'year': 2019, 'month': None, 'day': None},
        {'newYear': 2017, 'newMonth': 8,    'newDay': 8,    'year': 2018, 'month': 2,    'day': None},
        {'newYear': 2017, 'newMonth': 8,    'newDay': 8,    'year': 2017, 'month': 8,    'day': 5   },
    ])
    def testLineTransition(self, year, month, day, newYear, newMonth, newDay):
        self.loadData(newYear, newMonth, newDay)
        
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.selectDate(newYear, newMonth, newDay)
        self.browser.find_element_by_id('plot').click()
        
        self.initMapFunction('xaxis')
        self.initMapFunction('yaxis')
        
        self.assertCoordinatesEqual(self.getLineData(), self.getData('dates'), self.getData('nrj', 'sum'))
        
    @testData([
        {'newYear': None, 'newMonth': None, 'year': 2019, 'month': None, 'day': None},
        {'newYear': None, 'newMonth': None, 'year': 2018, 'month': 2,    'day': None},
        {'newYear': None, 'newMonth': None, 'year': 2017, 'month': 8,    'day': 5   },
        {'newYear': None, 'newMonth': None, 'year': 2017, 'month': 8,    'day': 8   },
        {'newYear': 2019, 'newMonth': None, 'year': None, 'month': None, 'day': None},
        {'newYear': 2019, 'newMonth': None, 'year': 2018, 'month': 2,    'day': None},
        {'newYear': 2019, 'newMonth': None, 'year': 2017, 'month': 8,    'day': 5   },
        {'newYear': 2019, 'newMonth': None, 'year': 2017, 'month': 8,    'day': 8   },
        {'newYear': 2018, 'newMonth': 2,    'year': None, 'month': None, 'day': None},
        {'newYear': 2018, 'newMonth': 2,    'year': 2019, 'month': None, 'day': None},
        {'newYear': 2018, 'newMonth': 2,    'year': 2017, 'month': 8,    'day': 5   },
        {'newYear': 2018, 'newMonth': 2,    'year': 2017, 'month': 8,    'day': 8   },
    ])
    def testBarTransition(self, year, month, day, newYear, newMonth):
        self.loadData(newYear, newMonth)
        
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.selectDate(newYear, newMonth)
        self.browser.find_element_by_id('plot').click()
        
        self.initMapFunction('xaxis', True)
        self.initMapFunction('yaxis')
        
        self.assertRectanglesEqual(self.getBarData(), self.getData('dates'), self.getData('nrj', 'sum'))

    @testData([
        {'year': 2017, 'month': 8,    'day': 6,    'prevYear': 2017, 'prevMonth': 8,    'prevDay': 5   },
    ])
    def testEmptyPrev(self, year, month, day, prevYear, prevMonth, prevDay):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.browser.find_element_by_id('prev').click()
        
        self.assertEqual(len(self.getLines()), 0)
        self.assertEqual(len(self.getBars()), 0)
        
    @testData([
        {'year': 2011, 'month': 6,    'day': 24,   'prevYear': 2011, 'prevMonth': 6,    'prevDay': 24  },
        {'year': 2011, 'month': 6,    'day': 26,   'prevYear': 2011, 'prevMonth': 6,    'prevDay': 24  },
        {'year': 2011, 'month': 12,   'day': 25,   'prevYear': 2011, 'prevMonth': 6,    'prevDay': 30  },
        {'year': 2017, 'month': 2,    'day': 1,    'prevYear': 2011, 'prevMonth': 12,   'prevDay': 31  },
        {'year': 2017, 'month': 8,    'day': 5,    'prevYear': 2017, 'prevMonth': 8,    'prevDay': 4   },
    ])
    def testLinePrev(self, year, month, day, prevYear, prevMonth, prevDay):
        self.loadData(prevYear, prevMonth, prevDay)
        
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.browser.find_element_by_id('prev').click()
        
        self.initMapFunction('xaxis')
        self.initMapFunction('yaxis')
        
        self.assertCoordinatesEqual(self.getLineData(), self.getData('dates'), self.getData('nrj', 'sum'))
    
    @testData([
        {'year': 2009, 'month': None, 'prevYear': 2009, 'prevMonth': None},
        {'year': 2010, 'month': None, 'prevYear': 2009, 'prevMonth': None},
        {'year': 2010, 'month': 12,   'prevYear': 2010, 'prevMonth': 12, },
        {'year': 2011, 'month': 6,    'prevYear': 2010, 'prevMonth': 12  },
    ])
    def testBarPrev(self, year, month, prevYear, prevMonth):
        self.loadData(prevYear, prevMonth)
        
        self.selectDate(year, month)
        self.browser.find_element_by_id('plot').click()
        self.browser.find_element_by_id('prev').click()
        

        self.initMapFunction('xaxis', True)
        self.initMapFunction('yaxis')
        
        self.assertRectanglesEqual(self.getBarData(), self.getData('dates'), self.getData('nrj', 'sum'))
    
    @testData([
        {'year': 2017, 'month': 8,    'day': 4,    'nextYear': 2017, 'nextMonth': 8,    'nextDay': 5   },
    ])
    def testEmptyNext(self, year, month, day, nextYear, nextMonth, nextDay):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.browser.find_element_by_id('next').click()
        
        self.assertEqual(len(self.getLines()), 0)
        self.assertEqual(len(self.getBars()), 0)
    
    @testData([
        {'year': 2017, 'month': 8,    'day': 8,    'nextYear': 2017, 'nextMonth': 8,    'nextDay': 8   },
        {'year': 2017, 'month': 8,    'day': 6,    'nextYear': 2017, 'nextMonth': 8,    'nextDay': 8   },
        {'year': 2017, 'month': 8,    'day': 5,    'nextYear': 2017, 'nextMonth': 8,    'nextDay': 6   },
        {'year': 2017, 'month': 2,    'day': 7,    'nextYear': 2017, 'nextMonth': 8,    'nextDay': 2   },
        {'year': 2011, 'month': 12,   'day': 31,   'nextYear': 2017, 'nextMonth': 2,    'nextDay': 1   },
    ])
    def testLineNext(self, year, month, day, nextYear, nextMonth, nextDay):
        self.loadData(nextYear, nextMonth, nextDay)
        
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.browser.find_element_by_id('next').click()
        
        self.initMapFunction('xaxis')
        self.initMapFunction('yaxis')
        
        self.assertCoordinatesEqual(self.getLineData(), self.getData('dates'), self.getData('nrj', 'sum'))
        
    @testData([
        {'year': 2018, 'month': None, 'nextYear': 2019, 'nextMonth': None},
        {'year': 2019, 'month': None, 'nextYear': 2019, 'nextMonth': None},
        {'year': 2018, 'month': 2,    'nextYear': 2018, 'nextMonth': 2   },
        {'year': 2017, 'month': 8,    'nextYear': 2018, 'nextMonth': 2   },
    ])
    def testBarNext(self, year, month, nextYear, nextMonth):
        self.loadData(nextYear, nextMonth)
        
        self.selectDate(year, month)
        self.browser.find_element_by_id('plot').click()
        self.browser.find_element_by_id('next').click()
        
        self.initMapFunction('xaxis', True)
        self.initMapFunction('yaxis')
        
        self.assertRectanglesEqual(self.getBarData(), self.getData('dates'), self.getData('nrj', 'sum'))
    
if __name__ == '__main__':
    unittest.main(verbosity=2)
