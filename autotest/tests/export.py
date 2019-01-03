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

from selenium.webdriver.common.keys import Keys as Key

import time
import os
import csv

from .PythonUtils.testdata import TestData

from .browser_testcase import BrowserTestCase

class ExportTest(BrowserTestCase):
    def getExportPath(self, var, agg, year=None, month=None, day=None):
        csvFilePath = self.exportPath(var, agg, year, month, day)

        if os.path.isfile(csvFilePath):
            os.remove(csvFilePath)
        return csvFilePath

    def waitExport(self, csvFilePath, t=-1):
        while not os.path.isfile(csvFilePath) or (os.path.getsize(csvFilePath) == 0):
            if (t == 0):
                break
            time.sleep(1)
            t -= 1
        return os.path.isfile(csvFilePath)

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

    @TestData([
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
        self.plot()
        self.selectVar(var)
        self.selectSum(agg)

        csvFilePath = self.getExportPath(var, agg, year, month, day)
        self.export()
        self.assertTrue(self.waitExport(csvFilePath, 5))
        self.assertEqual(self.getExportData(csvFilePath, agg), (self.getData('dates', 'str'), self.getData(var, agg)))
        os.remove(csvFilePath)

    @TestData([
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
    def testKey(self, year, month, day, var, agg):
        self.loadData(year, month, day)

        self.selectDate(year, month, day)
        self.pressKeys([Key.CONTROL, Key.ENTER]).perform()
        self.selectVar(var)
        self.selectSum(agg)

        csvFilePath = self.getExportPath(var, agg, year, month, day)
        self.pressKeys([Key.CONTROL, Key.ARROW_DOWN]).perform()
        self.assertTrue(self.waitExport(csvFilePath, 5))
        self.assertEqual(self.getExportData(csvFilePath, agg), (self.getData('dates', 'str'), self.getData(var, agg)))
        os.remove(csvFilePath)

    @TestData([
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
        self.plot()
        self.selectDate(newYear, newMonth, newDay)

        csvFilePath = self.getExportPath('nrj', 'sum', year, month, day)
        self.export()
        self.assertTrue(self.waitExport(csvFilePath, 5))
        self.assertEqual(self.getExportData(csvFilePath), (self.getData('dates', 'str'), self.getData('nrj', 'sum')))
        os.remove(csvFilePath)

    @TestData([
        {'year': 2019, 'month': None, 'day': None, 'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2018, 'month': 2,    'day': None, 'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2018, 'month': 2,    'day': None, 'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2018, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2018, 'newMonth': 2,    'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2017, 'newMonth': 2,    'newDay': None},
    ])
    def testPartialChangeDate(self, year, month, day, newYear, newMonth, newDay):
        self.loadData(year, month, day)

        self.selectDate(year, month, day)
        self.plot()
        self.selectDate(newYear, newMonth, newDay, partial=True)

        csvFilePath = self.getExportPath('nrj', 'sum', year, month, day)
        self.export()
        self.assertTrue(self.waitExport(csvFilePath, 5))
        self.assertEqual(self.getExportData(csvFilePath), (self.getData('dates', 'str'), self.getData('nrj', 'sum')))
        os.remove(csvFilePath)

    @TestData([
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
        self.plot()
        self.selectDate(newYear, newMonth, newDay)
        self.plot()

        csvFilePath = self.getExportPath('nrj', 'sum',  newYear, newMonth, newDay)
        self.export()
        self.assertTrue(self.waitExport(csvFilePath, 5))
        self.assertEqual(self.getExportData(csvFilePath), (self.getData('dates', 'str'), self.getData('nrj', 'sum')))
        os.remove(csvFilePath)

    @TestData([
        {'year': 2019, 'month': None, 'day': None, 'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2018, 'month': 2,    'day': None, 'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2018, 'month': 2,    'day': None, 'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2018, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2018, 'newMonth': 2,    'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2018, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2018, 'newMonth': 2,    'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2017, 'newMonth': 2,    'newDay': None},
    ])
    def testPartialTransition(self, year, month, day, newYear, newMonth, newDay):
        self.loadData(newYear, newMonth, newDay)

        self.selectDate(year, month, day)
        self.plot()
        self.selectDate(newYear, newMonth, newDay, partial=True)
        self.plot()

        csvFilePath = self.getExportPath('nrj', 'sum',  newYear, newMonth, newDay)
        self.export()
        self.assertTrue(self.waitExport(csvFilePath, 5))
        self.assertEqual(self.getExportData(csvFilePath), (self.getData('dates', 'str'), self.getData('nrj', 'sum')))
        os.remove(csvFilePath)

    @TestData([
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
        self.plot()
        self.browser.find_element_by_id('prev').click()

        csvFilePath = self.getExportPath('nrj', 'sum', prevYear, prevMonth, prevDay)
        self.export()
        self.assertTrue(self.waitExport(csvFilePath, 5))
        self.assertEqual(self.getExportData(csvFilePath), (self.getData('dates', 'str'), self.getData('nrj', 'sum')))
        os.remove(csvFilePath)

    @TestData([
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
        self.plot()
        self.browser.find_element_by_id('next').click()

        csvFilePath = self.getExportPath('nrj', 'sum', nextYear, nextMonth, nextDay)
        self.export()
        self.assertTrue(self.waitExport(csvFilePath, 5))
        self.assertEqual(self.getExportData(csvFilePath), (self.getData('dates', 'str'), self.getData('nrj', 'sum')))
        os.remove(csvFilePath)

    @TestData([
        {'year': 2017, 'month': 8, 'day': 5},
    ])
    def testEmpty(self, year, month, day):
        self.selectDate(year, month, day)
        self.plot()

        csvFilePath = self.getExportPath('nrj', 'sum', year, month, day)
        self.export()
        self.assertFalse(self.waitExport(csvFilePath, 5))
        with self.assertRaises(FileNotFoundError):
            os.remove(csvFilePath)

    @TestData([
        {'year': 2017, 'month': 8, 'day': 5},
    ])
    def testKeyEmpty(self, year, month, day):
        self.selectDate(year, month, day)
        self.pressKeys([Key.CONTROL, Key.ENTER]).perform()

        csvFilePath = self.getExportPath('nrj', 'sum', year, month, day)
        self.pressKeys([Key.CONTROL, Key.ARROW_DOWN]).perform()
        self.assertFalse(self.waitExport(csvFilePath, 5))
        with self.assertRaises(FileNotFoundError):
            os.remove(csvFilePath)

    @TestData([
        {'year': 2017, 'month': 8, 'day': 5, 'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8, 'day': 5, 'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8, 'day': 5, 'newYear': 2018, 'newMonth': 2,    'newDay': None},
        {'year': 2017, 'month': 8, 'day': 5, 'newYear': 2017, 'newMonth': 8,    'newDay': 8   },
    ])
    def testEmptyChangeDate(self, year, month, day, newYear, newMonth, newDay):
        self.selectDate(year, month, day)
        self.plot()
        self.selectDate(newYear, newMonth, newDay)

        csvFilePath = self.getExportPath('nrj', 'sum', year, month, day)
        self.export()
        self.assertFalse(self.waitExport(csvFilePath, 5))
        with self.assertRaises(FileNotFoundError):
            os.remove(csvFilePath)

    @TestData([
        {'year': 2017, 'month': 8, 'day': 5, 'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8, 'day': 5, 'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8, 'day': 5, 'newYear': 2018, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8, 'day': 5, 'newYear': 2018, 'newMonth': 2,    'newDay': None},
    ])
    def testEmptyPartialChangeDate(self, year, month, day, newYear, newMonth, newDay):
        self.selectDate(year, month, day)
        self.plot()
        self.selectDate(newYear, newMonth, newDay, partial=True)

        csvFilePath = self.getExportPath('nrj', 'sum', year, month, day)
        self.export()
        self.assertFalse(self.waitExport(csvFilePath, 5))
        with self.assertRaises(FileNotFoundError):
            os.remove(csvFilePath)

    @TestData([
        {'newYear': 2017, 'newMonth': 8, 'newDay': 5, 'year': None, 'month': None, 'day': None},
        {'newYear': 2017, 'newMonth': 8, 'newDay': 5, 'year': 2019, 'month': None, 'day': None},
        {'newYear': 2017, 'newMonth': 8, 'newDay': 5, 'year': 2018, 'month': 2,    'day': None},
        {'newYear': 2017, 'newMonth': 8, 'newDay': 5, 'year': 2017, 'month': 8,    'day': 5   },
    ])
    def testEmptyTransition(self, year, month, day, newYear, newMonth, newDay):
        self.selectDate(year, month, day)
        self.plot()
        self.selectDate(newYear, newMonth, newDay)
        self.plot()

        csvFilePath = self.getExportPath('nrj', 'sum', year, month, day)
        self.export()
        self.assertFalse(self.waitExport(csvFilePath, 5))
        with self.assertRaises(FileNotFoundError):
            os.remove(csvFilePath)

    @TestData([
        {'year': 2017, 'month': 8, 'day': 6, 'prevYear': 2017, 'prevMonth': 8, 'prevDay': 5},
    ])
    def testEmptyPrev(self, year, month, day, prevYear, prevMonth, prevDay):
        self.selectDate(year, month, day)
        self.plot()
        self.browser.find_element_by_id('prev').click()

        csvFilePath = self.getExportPath('nrj', 'sum', year, month, day)
        self.export()
        self.assertFalse(self.waitExport(csvFilePath, 5))
        with self.assertRaises(FileNotFoundError):
            os.remove(csvFilePath)

    @TestData([
        {'year': 2017, 'month': 8, 'day': 4, 'prevYear': 2017, 'prevMonth': 8, 'prevDay': 5},
    ])
    def testEmptyNext(self, year, month, day, prevYear, prevMonth, prevDay):
        self.selectDate(year, month, day)
        self.plot()
        self.browser.find_element_by_id('next').click()

        csvFilePath = self.getExportPath('nrj', 'sum', year, month, day)
        self.export()
        self.assertFalse(self.waitExport(csvFilePath, 5))
        with self.assertRaises(FileNotFoundError):
            os.remove(csvFilePath)
