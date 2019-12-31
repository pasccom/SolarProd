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

import os
import time

from .server_testcase import ServerTestCase

class PopupErrorTest(ServerTestCase):

    def __init__(self, *args, **kwArgs):
        super().__init__(*args, **kwArgs)
        self.modifs = {}

    def setUpError(self, fileName):
        self.modifs[fileName] = fileName + '.del'
        print(f"Rename {os.path.join(self.baseDir, fileName)} -> {os.path.join(self.baseDir, self.modifs[fileName])}")
        os.rename(os.path.join(self.baseDir, fileName), os.path.join(self.baseDir, self.modifs[fileName]))

    def tearDown(self):
        for fileName, delFileName in self.modifs.items():
            print(f"Rename {os.path.join(self.baseDir, delFileName)} -> {os.path.join(self.baseDir, fileName)}")
            os.rename(os.path.join(self.baseDir, delFileName), os.path.join(self.baseDir, fileName))
        self.modifs = {}

    @TestData([
        {'button': 'config', 'fileName': 'config.html'},
        {'button':   'info', 'fileName':    'info.xml'},
        {'button':   'info', 'fileName': 'info_fr.xsl'},
        {'button':   'help', 'fileName':   'help.html'},
    ])
    def testPopupError(self, button, fileName):
        self.setUpError(fileName)

        self.server.clear_request_log()
        with self.server.hold():
            self.browser.find_element_by_id(button).click()

            self.assertEqual(len(self.browser.find_elements_by_class_name('overlay')), 1)
            self.assertEqual(len(self.browser.find_elements_by_class_name('popup')), 1)
            self.assertEqual(self.browser.find_element_by_class_name('popup').value_of_css_property('display'), 'none')
        time.sleep(1)

        fileRequest = [r for r in self.server.get_request_log() if r['path'] == '/autotest/prod/' + fileName]
        self.assertEqual(len(fileRequest), 1)
        self.assertEqual(fileRequest[0]['code'], 404)

        self.assertEqual(len(self.browser.find_elements_by_class_name('overlay')), 0)
        self.assertEqual(len(self.browser.find_elements_by_class_name('popup')), 0)

        self.tearDown()
