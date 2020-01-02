# Copyright 2018-2020 Pascal COMBES <pascom@orange.fr>
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
from lxml import etree as xml

from selenium.webdriver.common.keys import Keys as Key

from .PythonUtils.testdata import TestData

from .browser_testcase import BrowserTestCase

class HelpTest(BrowserTestCase):

    def processXml(self, xmlStr):
        entities = {'nbsp': '\u00A0'}

        for entity, char in entities.items():
            xmlStr = xmlStr.replace('&' + entity + ';', char)

        deleteLeadingWhitespace = re.compile(r'^\s*', re.MULTILINE)
        deleteTailingWhitespace = re.compile(r'\s*$', re.MULTILINE)

        xmlStr = deleteLeadingWhitespace.sub('', xmlStr)
        xmlStr = deleteTailingWhitespace.sub('', xmlStr)

        return xmlStr

    def assertXmlEqual(self, found, expected):
        self.assertEqual(self.processXml(found), self.processXml(expected))

    def checkHelp(self):
        parser = xml.HTMLParser(remove_blank_text=True, remove_comments=True)

        expectedTree = xml.parse(self.helpFile, parser=parser)
        expectedContent = expectedTree.xpath('child::body/descendant::div[@id="content"]')

        html = self.browser.execute_script("return d3.select('.popup').select('#content').html()");
        tree = xml.fromstring('<div id="content">\n        ' + html + '\n        </div>', parser=parser)
        content = tree.xpath('child::body/descendant::div[@id="content"]')

        self.maxDiff = None
        self.assertXmlEqual(xml.tounicode(content[0]), xml.tounicode(expectedContent[0]))

    def testHelp(self):
        self.browser.find_element_by_id('help').click()
        self.checkHelp()

    def testKeyHelp(self):
        self.pressKeys([Key.CONTROL, Key.F1]).perform()
        self.checkHelp()
