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

    def getLines(self, *args):
        chart = self.browser.find_element_by_id('chart')
        args = [lambda x: x] + list(args)
        return [tuple(f(l) for f in args) for l in chart.find_elements_by_css_selector('path.line')]

    def getLineData(self):
        # NOTE assuming they are in the right order.
        groups = groupby(self.getLines(), key=lambda l: self.getColor(l[0]))
        return [[self.parsePath(p[0].get_attribute('d')) for p in g] for g in groups]

    def getBars(self, *args):
        chart = self.browser.find_element_by_id('chart')
        args = [lambda x: x] + list(args)
        return [tuple(f(b) for f in args) for b in chart.find_elements_by_css_selector('rect.bar')]

    def getBarData(self):
        # NOTE assuming they are in the right order.
        groups = [groupby(g, key=lambda b: self.getOpacity(b[0])) for g in groupby(self.getBars(), key=lambda b: self.getColor(b[0]))]
        return [[[self.parseRect(p[0]) for p in g2] for g2 in g1] for g1 in groups]
