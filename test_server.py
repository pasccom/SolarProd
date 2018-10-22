#!/usr/bin/python
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

from threading import Thread
from contextlib import contextmanager

import os
import time

class TestHTTPRequestHandler(http.SimpleHTTPRequestHandler):
    def log_request(self, code='-', size='-'):
        super().log_request(code, size)
        if isinstance(code, http.HTTPStatus):
            code = code.value
        self.server.log_request({
            'timestamp': time.time(),
            'origin'   : self.client_address[0] + ':' + str(self.client_address[1]),
            'command'  : self.command,
            'path'     : self.path,
            'code'     : code,
            'size'     : size,
        })

class TestHTTPServer(http.HTTPServer):
    def __init__(self, address, handler=TestHTTPRequestHandler):
        super().__init__(address, handler)
        self.__log = []

    def start(self, poll_interval=0.5):
        superObj = super()
        serverThread = Thread(target=lambda: superObj.serve_forever(poll_interval), name='server')
        serverThread.start()
        print('Server started')

    def stop(self):
        self.shutdown()
        print('Server stopped')

    @contextmanager
    def hold(self):
        try:
            self.stop()
            yield None
        finally:
            self.start()

    def log_request(self, requestData):
        self.__log += [requestData]

    def clear_request_log(self):
        print('Request log cleared')
        self.__log = []

    def get_request_log(self):
        return self.__log

if __name__ == '__main__':
    os.chdir('testdata')

    with TestHTTPServer(('localhost', 2222)) as httpd:
        print('Server listening on port {}'.format(httpd.server_port))
        httpd.serve_forever()


