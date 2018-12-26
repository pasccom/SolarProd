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

import unittest
import os
import json
from datetime import datetime as datetime

from .helpers import formatDatum, mapSum

class TestCase(unittest.TestCase):
    baseDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    profilesDir = os.path.join(baseDir, 'profiles')

    def __checkArgument(self, cache, arg):
        if cache is None:
            cache = os.path.isfile(self.cacheDir)
        if (arg == 'cache'):
            return cache
        if (arg == '!cache'):
            return not cache
        return arg

    @staticmethod
    def cacheCheck(fun, cache=None):
        def cacheCheckFun(self, *args, **kwArgs):
            newArgs = (self.__checkArgument(cache, a) for a in args)
            newKwArgs = {k: self.__checkArgument(cache, a) for k, a in kwArgs.items()}
            fun(self, *newArgs, **newKwArgs)
        return cacheCheckFun

    @staticmethod
    def cacheTest(fun):
        def cacheTestFun(self, *args, **kwArgs):
            with self.subTest(msg='Without cache'):
                os.rename(self.cacheDir, self.cacheDir + '.del')
                self.browser.get(self.index)
                self.__class__.cacheCheck(fun, False)(self, *args, **kwArgs)

            with self.subTest(msg='With cache'):
                os.rename(self.cacheDir + '.del', self.cacheDir)
                self.browser.get(self.index)
                self.__class__.cacheCheck(fun, True)(self, *args, **kwArgs)

        return cacheTestFun

    def setUp(self):
        super().setUp()

        self.index = 'file://' + self.__class__.baseDir + '/prod/index.html'
        self.helpPage = 'file://' + self.__class__.baseDir + '/prod/help.html'
        self.profilesDir = self.__class__.profilesDir
        self.cacheDir = os.path.join(self.__class__.baseDir, 'prod', 'list', 'cache.json')

    def listPath(self, year=None, month=None):
        listDir = os.path.join('autotest', 'prod', 'list')
        if year is None:
            return os.path.join(listDir, 'years.json')
        elif month is None:
            return os.path.join(listDir, 'months/{:04d}.json'.format(year))
        else:
            return os.path.join(listDir, 'days/{:04d}/{:02d}.json'.format(year, month))

    def dataPath(self, year=None, month=None, day=None):
        dataDir = os.path.join('autotest', 'prod', 'data')
        if (year == 'today'):
            return os.path.join(dataDir, 'today.json')
        if year is None:
            return os.path.join(dataDir, 'years.json')
        elif month is None:
            return os.path.join(dataDir, 'years/{:04d}.json'.format(year))
        elif day is None:
            return os.path.join(dataDir, 'months/{:04d}/{:02d}.json'.format(year, month))
        else:
            return os.path.join(dataDir, 'days/{:04d}/{:02d}/{:02d}.json'.format(year, month, day))

    def exportPath(self, var, agg, year=None, month=None, day=None):
        exportDir = os.path.join(self.__class__.baseDir, 'export')
        if year is None:
            return os.path.join(exportDir, 'export_{}_{}.csv'.format(var, agg))
        elif month is None:
            return os.path.join(exportDir, 'export_{}_{}_{:04d}.csv'.format(var, agg, year))
        elif day is None:
            return os.path.join(exportDir, 'export_{}_{}_{:02d}-{:04d}.csv'.format(var, agg, month, year))
        else:
            return os.path.join(exportDir, 'export_{}_{}_{:02d}-{:02d}-{:04d}.csv'.format(var, agg, day, month, year))

    def loadData(self, year=None, month=None, day=None):
        # Load data from JSON file:
        with open(self.dataPath(year, month, day), 'r') as jsonFile:
            self.data = json.load(jsonFile)
            if type(self.data) is dict:
                self.data['dates'] = [datetime.strptime(d, '%Y-%m-%d %H:%M') for d in self.data['dates']]
            else:
                self.data = list(map(formatDatum, self.data))
            #print(self.data)

        # Check data is valid:
        if (year == 'today') or (day is not None):
            self.assertEqual([d.strftime('%Y-%m-%d') for d in self.data['dates'][0:-1]],
                             [d.strftime('%Y-%m-%d') for d in self.data['dates'][1:]])
        elif month is not None:
            self.assertEqual([d['date'].strftime('%Y-%m') for d in self.data[0:-1]],
                             [d['date'].strftime('%Y-%m') for d in self.data[1:]])
        elif year is not None:
            self.assertEqual([d['date'].strftime('%Y') for d in self.data[0:-1]],
                             [d['date'].strftime('%Y') for d in self.data[1:]])

    def formatDate(self, date, agg, dateMin, dateMax):
        if (dateMin.year != dateMax.year):
            if (agg == 'str'):
                return date.strftime('%Y')
            else:
                return date.year
        elif (dateMin.month != dateMax.month):
            if (agg == 'str'):
                return date.strftime('%m/%Y')
            else:
                return date.month
        elif (dateMin.day != dateMax.day):
            if (agg == 'str'):
                return date.strftime('%d/%m/%Y')
            else:
                return date.day
        else:
            if (agg == 'str'):
                return date.strftime('%d/%m/%Y %H:%M')
            else:
                return date.hour + date.minute/60

    def getData(self, var, agg=None):
        if type(self.data) is dict:
            if (var != 'dates'):
                if (agg == 'sum'):
                    return [[mapSum(self.data[var])]]
                elif (agg == 'inv'):
                    return list(map(lambda x: [mapSum(x)], self.data[var]))
                elif (agg == 'str'):
                    return self.data[var]
                else:
                    raise ValueError('Invalid aggregation method: {}'.format(agg))
            else:
                dateMin = min(self.data['dates'])
                dateMax = max(self.data['dates'])
                return [self.formatDate(d, agg, dateMin, dateMax) for d in self.data['dates']]
        elif type(self.data) is list:
            if (var != 'dates'):
                if (agg == 'sum'):
                    return [[[sum(d[var]) for d in self.data]]]
                elif (agg == 'inv'):
                    return [[list(d)] for d in zip(*[d[var] for d in self.data])]
                else:
                    raise ValueError('Invalid aggregation method: {}'.format(agg))
            else:
                dateMin = min([d['date'] for d in self.data])
                dateMax = max([d['date'] for d in self.data])
                return [self.formatDate(d['date'], agg, dateMin, dateMax) for d in self.data]
        else:
            raise TypeError('Invalid data type: {}'.format(type(self.data)))
