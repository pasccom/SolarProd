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

import re

from .PythonUtils.testdata import testData

from .chart_testcase import ChartTestCase

class ChartTest(ChartTestCase):
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

    def getTickLength(self, axis):
        attr = 'y2' if axis == 'xaxis' else 'x2'
        ticks = [t.find_element_by_tag_name('line') for t in self.getAxis(axis).find_elements_by_class_name('tick')]
        tickLengthes = [float(t.get_attribute(attr)) for t in ticks]

        length = tickLengthes[0]
        for l in tickLengthes:
            if not (l == length):
                length = None
                break
        self.assertIsNotNone(length)
        return length

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
        lines = [(
            l,
            self.parseColor(l.find_element_by_xpath('..').get_attribute('stroke')),
            float(l.get_attribute('stroke-opacity'))
        ) for l in self.getLines()]

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
        bars = [(
            b,
            self.parseColor(b.find_element_by_xpath('..').get_attribute('fill')),
            float(b.get_attribute('fill-opacity'))
        ) for b in self.getBars()]

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
            return 0., 1.025*float(max(map(lambda x: max(map(max, x)), data)))
        else:
            return min(data), max(data) + 0.025*(max(data) - min(data))

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

    def testEmptyLabel(self):
        self.selectDate(2017, 8, 5)
        self.browser.find_element_by_id('plot').click()

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

    def testEmptyAxis(self):
        self.selectDate(2017, 8, 5)
        self.browser.find_element_by_id('plot').click()

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
        self.assertEqual(self.getTickLength('xaxis'), 6.)

        # Check y axis:
        self.assertRangeEqual(self.getRange('yaxis', False), self.getDataRange(var, agg))
        self.assertEqual(self.getTickLength('yaxis'), -6.)

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
        self.assertEqual(self.getTickLength('xaxis'), 6.)

        # Check y axis:
        self.assertRangeEqual(self.getRange('yaxis', False), self.getDataRange(var, agg))
        self.assertEqual(self.getTickLength('yaxis'), -6.)

    def testEmptyGrid(self):
        self.selectDate(2017, 8, 5)
        self.browser.find_element_by_id('plot').click()

        self.assertEqual(len(self.getAxis('grid').find_elements_by_xpath('./*')), 0)

    @testData([
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
    def testLineGrid(self, year, month, day, var, agg):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.selectVar(var)
        self.selectSum(agg)

        self.assertEqual(self.getTickPositions('yaxis'), self.getTickPositions('grid'))
        self.assertEqual(self.getTickLength('grid'), self.getDomain('xaxis', True)[1]/1.025)

    @testData([
        {'year': None, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': None, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2019, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': 2019, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2018, 'month': 2,    'day': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': 2018, 'month': 2,    'day': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2018, 'month': 2,    'day': None, 'var': 'pwr',  'agg': 'sum'},
        {'year': 2018, 'month': 2,    'day': None, 'var': 'pwr',  'agg': 'inv'},
    ])
    def testBarGrid(self, year, month, day, var, agg):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.selectVar(var)
        self.selectSum(agg)

        self.assertEqual(self.getTickPositions('yaxis'), self.getTickPositions('grid'))
        self.assertEqual(self.getTickLength('grid'), self.getDomain('xaxis', False)[1])

    def testEmptyData(self):
        self.selectDate(2017, 8, 5)
        self.browser.find_element_by_id('plot').click()

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
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2018, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2018, 'newMonth': 2,    'newDay': None},
    ])
    def testEmptyPartialChangeDate(self, year, month, day, newYear, newMonth, newDay):
        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.selectDate(newYear, newMonth, newDay, partial=True)

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
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2018, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2018, 'newMonth': 2,    'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2017, 'newMonth': 2,    'newDay': None},
    ])
    def testLinePartialChangeDate(self, year, month, day, newYear, newMonth, newDay):
        self.loadData(year, month, day)

        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.selectDate(newYear, newMonth, newDay, partial=True)

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
        {'year': 2019, 'month': None, 'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2018, 'month': 2,    'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2018, 'month': 2,    'newYear': 2019, 'newMonth': None, 'newDay': None},
    ])
    def testBarPartialChangeDate(self, year, month, newYear, newMonth, newDay):
        self.loadData(year, month)

        self.selectDate(year, month)
        self.browser.find_element_by_id('plot').click()
        self.selectDate(newYear, newMonth, newDay, partial=True)

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
        {'newYear': None, 'newMonth': None, 'year': 2019, 'month': None, 'day': None},
        {'newYear': None, 'newMonth': None, 'year': 2018, 'month': 2,    'day': None},
        {'newYear': None, 'newMonth': None, 'year': 2017, 'month': 8,    'day': 5   },
        {'newYear': None, 'newMonth': None, 'year': 2017, 'month': 8,    'day': 8   },
        {'newYear': 2019, 'newMonth': None, 'year': 2018, 'month': 2,    'day': None},
        {'newYear': 2019, 'newMonth': None, 'year': 2017, 'month': 8,    'day': 5   },
        {'newYear': 2019, 'newMonth': None, 'year': 2017, 'month': 8,    'day': 8   },
        {'newYear': 2018, 'newMonth': None, 'year': 2017, 'month': 8,    'day': 5   },
        {'newYear': 2018, 'newMonth': None, 'year': 2017, 'month': 8,    'day': 8   },
        {'newYear': 2018, 'newMonth': 2,    'year': 2017, 'month': 8,    'day': 5   },
        {'newYear': 2018, 'newMonth': 2,    'year': 2017, 'month': 8,    'day': 8   },
    ])
    def testBarPartialTransition(self, year, month, day, newYear, newMonth):
        self.loadData(newYear, newMonth)

        self.selectDate(year, month, day)
        self.browser.find_element_by_id('plot').click()
        self.selectDate(newYear, newMonth, partial=True)
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


