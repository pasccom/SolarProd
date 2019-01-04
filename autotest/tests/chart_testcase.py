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

from .helpers import groupby
from .browser_testcase import BrowserTestCase

class ChartTestCase(BrowserTestCase):
    def __init__(self, *args, **kwArgs):
        super().__init__(*args, **kwArgs)

        self.lineWidth = 1;

    def selectVar(self, *args, **kwArgs):
        super().selectVar(*args, **kwArgs)
        self.clearMapFunctions()

    def selectSum(self, *args, **kwArgs):
        super().selectSum(*args, **kwArgs)
        self.clearMapFunctions()

    def plot(self, *args, **kwArgs):
        super().plot(*args, **kwArgs)
        self.clearMapFunctions()

    def plotPrev(self, *args, **kwArgs):
        super().plotPrev(*args, **kwArgs)
        self.clearMapFunctions()

    def plotNext(self, *args, **kwArgs):
        super().plotNext(*args, **kwArgs)
        self.clearMapFunctions()

    def getColor(self, elem):
        if elem.tag_name == 'path':
            return self.parseColor(elem.find_element_by_xpath('..').get_attribute('stroke'))
        elif elem.tag_name == 'rect':
            return self.parseColor(elem.find_element_by_xpath('..').get_attribute('fill'))
        else:
            raise ValueError('Unknown element: {}'.format(elem.tag_name))

    def getOpacity(self, elem):
        if elem.tag_name == 'path':
            return float(elem.get_attribute('stroke-opacity'))
        elif elem.tag_name == 'rect':
            return float(elem.get_attribute('fill-opacity'))
        else:
            raise ValueError('Unknown element: {}'.format(elem.tag_name))

    def parseTranslate(self, group, axis=None):
        transform = group.get_attribute('transform')
        match = re.fullmatch(r'translate\(([0-9]*(?:\.[0-9]*)?), *([0-9]*(?:\.[0-9]*)?)\)', transform)
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
        elif (axis == 'yaxis') or (axis == 'grid'):
            y = elem.get_attribute('y')
            if y is not None:
                return float(y)
            y1 = elem.get_attribute('y1')
            y2 = elem.get_attribute('y2')
            self.assertEqual(y1, y2)
            if y1 is not None:
                return float(y1)
            return 0
        else:
            raise NotImplementedError()

    def parsePath(self, path):
        self.initMapFunctions(False)

        self.assertRegex(path, r'^M([0-9]+(?:\.[0-9]*)?,[0-9]+(?:\.[0-9]*)?)(?:L([0-9]+(?:\.[0-9]*)?,[0-9]+(?:\.[0-9]*)?))*$')
        coords = [tuple([float(n) for n in c.split(',')]) for c in path[1:].split('L')]
        return [(self.xMap(c[0]), self.yMap(c[1])) for c in coords]

    def parseRect(self, rect):
        self.initMapFunctions(True)

        offset1 = self.parseTranslate(rect.find_element_by_xpath('../..'))
        offset2 = self.parseTranslate(rect.find_element_by_xpath('..'))

        return (
            self.xMap(float(rect.get_attribute('x')) + offset1[0] + offset2[0]),
            self.yMap(float(rect.get_attribute('y')) + offset1[1] + offset2[1]),
            self.xMap(float(rect.get_attribute('x')) + offset1[0] + offset2[0] + float(rect.get_attribute('width'))),
            self.yMap(float(rect.get_attribute('y')) + offset1[1] + offset2[1] + float(rect.get_attribute('height')))
        )

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
        if not hasattr(self, axis[0] + 'Map'):
            self.initMapFunction(axis, centered)

        return tuple(map(getattr(self, axis[0] + 'Map'), self.getDomain(axis, not centered)))

    def getDataRange(self, var, agg=None):
        data = self.getData(var, agg)
        if agg is not None:
            return 0., 1.025*float(max(map(lambda x: max(map(max, x)), data)))
        else:
            return min(data), max(data) + 0.025*(max(data) - min(data))

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

    def initMapFunction(self, axis, centered):
        ticks = self.getTickPositions(axis, centered)
        tickLabels = self.getTickLabels(axis)

        iM, xM = max(enumerate(ticks), key=lambda t: t[0])
        im, xm = min(enumerate(ticks), key=lambda t: t[0])

        if centered:
            setattr(self, axis[0] + 'Map', lambda x: tickLabels[max(0, min(len(tickLabels) - 1, int(1 + im + (x - xm) * (iM - im) / (xM - xm))))] + 1 + im + (x - xm) * (iM - im) / (xM - xm) - max(0, min(len(tickLabels) - 1, int(1 + im + (x - xm) * (iM - im) / (xM - xm)))))
        else:
            setattr(self, axis[0] + 'Map', lambda x: tickLabels[im] + (x - xm) * (tickLabels[iM] - tickLabels[im]) / (xM - xm))

    def initMapFunctions(self, centered):
        if not hasattr(self, 'xMap'):
            self.initMapFunction('xaxis', centered)
        if not hasattr(self, 'yMap'):
            self.initMapFunction('yaxis', False)

    def clearMapFunctions(self):
        try:
            delattr(self, 'xMap')
        except (AttributeError):
            pass

        try:
            delattr(self, 'yMap')
        except (AttributeError):
            pass

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

    def assertBarsEqual(self, rects, x, y, nBars=None, bar=None):
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
                self.assertBarsEqual(r, x, y[i], nBars, b)

    def assertLabelStyle(self, label):
        self.assertEqual(label.value_of_css_property('font-family'), 'sans-serif')
        self.assertEqual(label.value_of_css_property('font-size'), '12px')
        self.assertEqual(label.value_of_css_property('font-weight'), '700')
        self.assertEqual(label.value_of_css_property('font-style'), 'normal')
        self.assertEqual(label.value_of_css_property('text-decoration'), 'none')
        self.assertEqual(label.value_of_css_property('text-anchor'), 'middle')

    def getLines(self, *args):
        chart = self.browser.find_element_by_id('chart')
        if (len(args) == 0):
            return [l for l in chart.find_elements_by_css_selector('path.line')]
        else:
            args = [lambda x: x] + list(args)
            return [tuple(f(l) for f in args) for l in chart.find_elements_by_css_selector('path.line')]

    def getLineGroups(self, *args):
        lines = self.getLines(*args)
        if (len(args) == 0):
            return groupby(lines, key=lambda l: self.getColor(l))
        else:
            return groupby(lines, key=lambda l: self.getColor(l[0]))

    def getLineData(self):
        # NOTE assuming they are in the right order.
        return [[self.parsePath(l.get_attribute('d')) for l in g] for g in self.getLineGroups()]

    def getBars(self, *args):
        chart = self.browser.find_element_by_id('chart')
        if (len(args) == 0):
            return [b for b in chart.find_elements_by_css_selector('rect.bar')]
        else:
            args = [lambda x: x] + list(args)
            return [tuple(f(b) for f in args) for b in chart.find_elements_by_css_selector('rect.bar')]

    def getBarGroups(self, *args):
        bars = self.getBars(*args)
        if (len(args) == 0):
            return [groupby(g, key=lambda b: self.getOpacity(b)) for g in groupby(bars, key=lambda b: self.getColor(b))]
        else:
            return [groupby(g, key=lambda b: self.getOpacity(b[0])) for g in groupby(bars, key=lambda b: self.getColor(b[0]))]

    def getBarData(self):
        # NOTE assuming they are in the right order.
        return [[[self.parseRect(b) for b in g2] for g2 in g1] for g1 in self.getBarGroups()]
