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

import http.server as http

import time

from .test_server import TestHTTPServer
from .browser_testcase import BrowserTestCase

class ServerTestCase(BrowserTestCase):
    server = None
    port = 0

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        if cls.server is None:
            cls.server = TestHTTPServer(('', cls.port))
            cls.server.start()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        if (cls.server is not None):
            cls.server.stop()
            cls.server.server_close()

    def setUp(self, loadIndex=True):
        super().setUp(False)
        self.server = self.__class__.server
        self.index = 'http://' + self.server.server_name + ':' + str(self.server.server_port) + '/autotest/prod'
        if loadIndex:
            self.browser.get(self.index)

    def assertDataRequests(self, expected, wait=0):
        dataRequests = [r['path'][1:] for r in self.server.get_request_log() if (r['command'] == 'GET') and r['path'].startswith('/autotest/prod/data/')]
        while (wait != 0) and (len(dataRequests) != len(expected)):
            time.sleep(1)
            wait-=1
            dataRequests = [r['path'][1:] for r in self.server.get_request_log() if (r['command'] == 'GET') and r['path'].startswith('/autotest/prod/data/')]
        print(dataRequests)
        self.assertEqual(dataRequests, expected)
