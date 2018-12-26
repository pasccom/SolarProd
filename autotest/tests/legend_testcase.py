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

from .browser_testcase import BrowserTestCase

class LegendTestCase(BrowserTestCase):
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

    def __getLegendListItems(self, parent):
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
        legendItems = self.__getLegendListItems(parent)
        if (len(legendItems) == 0) and (parent is None):
            return [tuple(self.browser.find_element_by_id('legend').find_elements_by_tag_name('span') + [[]])]

        return [
            (self.__removeParents(self.__removeChildren(e.find_elements_by_tag_name('span'),
                                                    e.find_elements_by_tag_name('li'))) + \
            [self.getLegendItems(e)]) for e in legendItems
        ]
