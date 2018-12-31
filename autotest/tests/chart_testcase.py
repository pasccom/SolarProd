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
