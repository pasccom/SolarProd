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

from .PythonUtils.testdata import TestData

from .legend_testcase import LegendTestCase
from .chart_testcase import ChartTestCase

class LegendTest(ChartTestCase, LegendTestCase):

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
        self.plot(True)

    def testEmpty(self):
        legend = self.browser.find_element_by_id('legend')
        self.assertIn('framed', self.getClasses(legend))
        self.assertEqual(legend.text, '')

    @TestData([
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

    @TestData(['nrj', 'pac', 'pdc'], before=loadToday)
    def testLineTotal(self, var):
        self.selectVar(var)
        self.selectSum('sum')

        lines = self.getLines(self.getColor, self.getOpacity)
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

        # For each line, find associated legend item:
        legendItemStyles = [self.getStyle(i) for i, t, c in legendItems]
        for p, c, o in lines:
            legendItemStyle = [s for s in legendItemStyles if (s['color'] == c) and abs(float(s['opacity']) - o) < 1e-12]

    @TestData(['nrj', 'pac', 'pdc', 'temp'], before=loadToday)
    def testLinePerInverter(self, var):
        self.selectVar(var)
        self.selectSum('inv')

        lines = self.getLines(self.getColor, self.getOpacity)
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

        # For each line, find associated legend item:
        legendItemStyles = [self.getStyle(i) for i, t, b, c in legendItems]
        for p, c, o in lines:
            legendItemStyle = [s for s in legendItemStyles if (s['color'] == c) and abs(float(s['opacity']) - o) < 1e-12]

    @TestData(['pdc', 'udc'], before=loadToday)
    def testLinePerString(self, var):
        self.selectVar(var)
        self.selectSum('str')

        lines = self.getLines(self.getColor, self.getOpacity)
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

        # For each line, find associated legend item:
        legendItemStyles = [self.getStyle(c) for i, b, children in legendItems for c, t, b, x in children]
        for p, c, o in lines:
            legendItemStyle = [s for s in legendItemStyles if (s['color'] == c) and abs(float(s['opacity']) - o) < 1e-12]

    @TestData([
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
        self.plot()
        self.selectVar(var)
        self.selectSum(agg)

        legend = self.browser.find_element_by_id('legend')
        self.assertIn('framed', self.getClasses(legend))
        legendTitle = self.browser.find_element_by_tag_name('h4')
        self.assertEqual(legendTitle.text, 'Légende')
        self.assertLegendTitleStyle(legendTitle)

    @TestData([
        {'year': None, 'month': None, 'var': 'nrj'},
        {'year': 2019, 'month': None, 'var': 'nrj'},
        {'year': 2018, 'month':    2, 'var': 'nrj'},
        {'year': 2018, 'month':    2, 'var': 'pwr'},
    ])
    def testBarTotal(self, year, month, var):
        self.selectDate(year, month)
        self.plot()
        self.selectVar(var)
        self.selectSum('sum')

        bars = self.getBars(self.getColor, self.getOpacity)
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
            rects = [r for r, c, o in bars if (c == legendItemStyle['background-color'][0:3]) and (abs(o - legendItemStyle['background-color'][3]) < 1e-12)]
            self.assertGreater(len(rects), 0)

        # For each bar, find associated legend item:
        legendItemStyles = [self.getStyle(i) for i, t, c in legendItems]
        for r, c, o in bars:
            legendItemStyle = [s for s in legendItemStyles if (s['background-color'][0:3] == c) and abs(s['background-color'][3] - o) < 1e-12]
            self.assertEqual(len(legendItemStyle), 1)
            self.assertEqual(legendItemStyle[0]['color'][0:3], c)
            self.assertEqual(legendItemStyle[0]['color'][3], 0)
            self.assertEqual(legendItemStyle[0]['border-color'][0:3], c)
            self.assertEqual(len(legendItemStyle[0]['border-color']), 3)
            self.assertEqual(legendItemStyle[0]['border-width'], '1px')
            self.assertEqual(legendItemStyle[0]['border-style'], 'solid')

    @TestData([
        {'year': None, 'month': None, 'day': None, 'var': 'nrj'},
        {'year': 2019, 'month': None, 'day': None, 'var': 'nrj'},
        {'year': 2018, 'month':    2, 'day': None, 'var': 'nrj'},
        {'year': 2018, 'month':    2, 'day': None, 'var': 'pwr'},
    ])
    def testBarPerInverter(self, year, month, day, var):
        self.selectDate(year, month, day)
        self.plot()
        self.selectVar(var)
        self.selectSum('inv')

        bars = self.getBars(self.getColor, self.getOpacity)
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
            rects = [r for r, c, o in bars if (c == legendItemStyle['background-color'][0:3]) and (abs(o - float(legendItemStyle['background-color'][3])) < 1e-12)]
            self.assertGreater(len(rects), 0)

            # Check legend input:
            self.assertIn('input', self.getClasses(legendCheckbox))
            checkbox = legendCheckbox.find_element_by_tag_name('input')
            self.assertEqual(checkbox.get_attribute('type'), 'checkbox')
            self.assertTrue(checkbox.get_property('checked'))
            self.assertFalse(checkbox.get_property('indeterminate'))
            checkbox.click()
            self.assertFalse(checkbox.get_property('checked'))
            self.assertFalse(checkbox.get_property('indeterminate'))
            self.assertTrue(all([('display' in self.getStyle(p).keys()) and (self.getStyle(p)['display'] == 'none') for p in rects]))
            checkbox.click()
            self.assertTrue(checkbox.get_property('checked'))
            self.assertFalse(checkbox.get_property('indeterminate'))
            self.assertTrue(all([('display' not in self.getStyle(p).keys()) or (self.getStyle(p)['display'] != 'none') for p in rects]))

        # For each bar, find associated legend item:
        legendItemStyles = [self.getStyle(i) for i, t, b, c in legendItems]
        for r, c, o in bars:
            legendItemStyle = [s for s in legendItemStyles if (s['background-color'][0:3] == c) and abs(s['background-color'][3] - o) < 1e-12]
            self.assertEqual(len(legendItemStyle), 1)
            self.assertEqual(legendItemStyle[0]['color'][0:3], c)
            self.assertEqual(legendItemStyle[0]['color'][3], 0)
            self.assertEqual(legendItemStyle[0]['border-color'][0:3], c)
            self.assertEqual(len(legendItemStyle[0]['border-color']), 3)
            self.assertEqual(legendItemStyle[0]['border-width'], '1px')
            self.assertEqual(legendItemStyle[0]['border-style'], 'solid')

    @TestData([
        {'year': 2017, 'month': 8,    'day': 5},
    ])
    def testEmpty(self, year, month, day):
        self.selectDate(year, month, day)
        self.plot()

        self.assertEqual(len(self.browser.find_element_by_id('legend').find_elements_by_xpath('child::*')), 0)
        self.assertEqual(len(self.browser.find_element_by_id('legend').text), 0)

    @TestData([
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2018, 'newMonth': 2,    'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2017, 'newMonth': 8,    'newDay': 5   },
    ])
    def testEmptyChangeDate(self, year, month, day, newYear, newMonth, newDay):
        self.selectDate(year, month, day)
        self.plot()
        self.selectDate(newYear, newMonth, newDay)

        self.assertEqual(len(self.browser.find_element_by_id('legend').find_elements_by_xpath('child::*')), 0)
        self.assertEqual(len(self.browser.find_element_by_id('legend').text), 0)

    @TestData([
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2018, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2018, 'newMonth': 2,    'newDay': None},
    ])
    def testEmptyPartialChangeDate(self, year, month, day, newYear, newMonth, newDay):
        self.selectDate(year, month, day)
        self.plot()
        self.selectDate(newYear, newMonth, newDay, partial=True)

        self.assertEqual(len(self.browser.find_element_by_id('legend').find_elements_by_xpath('child::*')), 0)
        self.assertEqual(len(self.browser.find_element_by_id('legend').text), 0)

    @TestData([
        {'newYear': 2017, 'newMonth': 8,    'newDay': 5,    'year': None, 'month': None, 'day': None},
        {'newYear': 2017, 'newMonth': 8,    'newDay': 5,    'year': 2019, 'month': None, 'day': None},
        {'newYear': 2017, 'newMonth': 8,    'newDay': 5,    'year': 2018, 'month': 2,    'day': None},
        {'newYear': 2017, 'newMonth': 8,    'newDay': 5,    'year': 2017, 'month': 8,    'day': 5   },
    ])
    def testEmptyTransition(self, year, month, day, newYear, newMonth, newDay):
        self.selectDate(year, month, day)
        self.plot()
        self.selectDate(newYear, newMonth, newDay)
        self.plot()

        self.assertEqual(len(self.browser.find_element_by_id('legend').find_elements_by_xpath('child::*')), 0)
        self.assertEqual(len(self.browser.find_element_by_id('legend').text), 0)

    @TestData([
        {'year': 2017, 'month': 8,    'day': 6,    'prevYear': 2017, 'prevMonth': 8,    'prevDay': 5   },
    ])
    def testEmptyPrev(self, year, month, day, prevYear, prevMonth, prevDay):
        self.selectDate(year, month, day)
        self.plot()
        self.browser.find_element_by_id('prev').click()

        self.assertEqual(len(self.browser.find_element_by_id('legend').find_elements_by_xpath('child::*')), 0)
        self.assertEqual(len(self.browser.find_element_by_id('legend').text), 0)

    @TestData([
        {'year': 2017, 'month': 8,    'day': 4,    'prevYear': 2017, 'prevMonth': 8,    'prevDay': 5   },
    ])
    def testEmptyNext(self, year, month, day, prevYear, prevMonth, prevDay):
        self.selectDate(year, month, day)
        self.plot()
        self.browser.find_element_by_id('next').click()

        self.assertEqual(len(self.browser.find_element_by_id('legend').find_elements_by_xpath('child::*')), 0)
        self.assertEqual(len(self.browser.find_element_by_id('legend').text), 0)
