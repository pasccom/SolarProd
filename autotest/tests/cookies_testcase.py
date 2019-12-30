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

from .server_testcase import ServerTestCase

import time
from datetime import datetime

class CookiesTestCase(ServerTestCase):

    def setUp(self):
        super().setUp(False)

    def setUpCookies(self, cookies=None):
        self.browser.get(self.index)
        if cookies is None:
            return
        for cookie in cookies:
            cookie['path'] = '/autotest/prod/'
            if cookie['value'] != 'None':
                self.browser.add_cookie(cookie)
            else:
                self.browser.delete_cookie(cookie['name'])

        self.browser.get(self.index)
        time.sleep(1)
        for cookie in cookies:
            if cookie['value'] != 'None':
                self.assertEqual(self.browser.get_cookie(cookie['name'])['value'], str(cookie['value']))
            else:
                self.assertIsNone(self.browser.get_cookie(cookie['name']))

    def assertCookies(self, cookies):
        for n, v in cookies.items():
            self.assertCookie(n, v)

    def assertCookie(self, name, value):
        cookie = self.browser.get_cookie(name)
        if value is None:
            self.assertIsNone(cookie)
        else:
            self.assertEqual(cookie['value'], str(value))
            try:
                self.assertEqual(datetime.utcfromtimestamp(cookie['expiry']).isoformat(), '9999-12-31T23:59:59')
            except (KeyError):
                pass
