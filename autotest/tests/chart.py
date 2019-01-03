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

from .chart_testcase import ChartTestCase

class ChartTest(ChartTestCase):

    def loadToday(self):
        self.loadData('today')
        self.plot(True)

    def loadEmpty(self):
        self.loadData(2017, 8, 5)
        self.selectDate(2017, 8, 5)
        self.plot()

    def testEmptyLabel(self):
        self.selectDate(2017, 8, 5)
        self.plot()

        xLabel = self.getLabel('xaxis')
        self.assertEqual(xLabel.text, '')

        yLabel = self.getLabel('yaxis')
        self.assertEqual(yLabel.text, '')

    @TestData([
        {'year': None, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': None, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2019, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': 2019, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2018, 'month': 2,    'day': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': 2018, 'month': 2,    'day': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2018, 'month': 2,    'day': None, 'var': 'pwr',  'agg': 'sum'},
        {'year': 2018, 'month': 2,    'day': None, 'var': 'pwr',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'nrj',  'agg': 'sum'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'nrj',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pac',  'agg': 'sum'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pac',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pdc',  'agg': 'sum'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pdc',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pdc',  'agg': 'str'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'udc',  'agg': 'str'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'temp', 'agg': 'inv'},
    ])
    def testLabel(self, year, month, day, var, agg):
        self.selectDate(year, month, day)
        self.plot()
        self.selectVar(var)
        self.selectSum(agg)

        xLabel = self.getLabel('xaxis')
        if year is None:
            self.assertEqual(xLabel.text, 'Année')
        elif month is None:
            self.assertEqual(xLabel.text, 'Mois')
        elif day is None:
            self.assertEqual(xLabel.text, 'Jour')
        else:
            self.assertEqual(xLabel.text, 'Temps (h)')
        self.assertLabelStyle(xLabel)

        yLabel = self.getLabel('yaxis')
        self.assertRegex(yLabel.text, r'{} \([kMGT]?{}\)'.format(self.longVar(var), self.unit(var)))
        self.assertLabelStyle(yLabel)

    def testEmptyAxis(self):
        self.selectDate(2017, 8, 5)
        self.plot()

        self.assertEqual(len(self.getAxis('xaxis').find_elements_by_xpath('./*')), 0)
        self.assertEqual(len(self.getAxis('yaxis').find_elements_by_xpath('./*')), 0)

    @TestData([
        {'var': 'nrj',  'agg': 'sum'},
        {'var': 'nrj',  'agg': 'inv'},
        {'var': 'pac',  'agg': 'sum'},
        {'var': 'pac',  'agg': 'inv'},
        {'var': 'pdc',  'agg': 'sum'},
        {'var': 'pdc',  'agg': 'inv'},
        {'var': 'pdc',  'agg': 'str'},
        {'var': 'udc',  'agg': 'str'},
        {'var': 'temp', 'agg': 'inv'},
    ], before=loadToday)
    def testLineAxis(self, var, agg):
        self.selectVar(var)
        self.selectSum(agg)

        self.initMapFunction('xaxis')
        self.initMapFunction('yaxis')

        # Check x axis:
        xTickLabels = self.getTickLabels('xaxis')
        self.assertEqual(xTickLabels, list(range(int(min(xTickLabels)), int(max(xTickLabels) + 1))))
        self.assertRangeEqual(self.getRange('xaxis', False), self.getDataRange('dates'))
        self.assertEqual(self.getTickLength('xaxis'), 6.)

        # Check y axis:
        self.assertRangeEqual(self.getRange('yaxis', False), self.getDataRange(var, agg))
        self.assertEqual(self.getTickLength('yaxis'), -6.)

    @TestData([
        {'year': None, 'month': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': None, 'month': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2019, 'month': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': 2019, 'month': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2018, 'month': 2,    'var': 'nrj',  'agg': 'sum'},
        {'year': 2018, 'month': 2,    'var': 'nrj',  'agg': 'inv'},
        {'year': 2018, 'month': 2,    'var': 'pwr',  'agg': 'sum'},
        {'year': 2018, 'month': 2,    'var': 'pwr',  'agg': 'inv'},
    ])
    def testBarAxis(self, year, month, var, agg):
        self.loadData(year, month)

        self.selectDate(year, month)
        self.plot()
        self.selectVar(var)
        self.selectSum(agg)

        if (agg != 'sum'):
            self.initMapFunction('xaxis', True)
        else:
            self.initMapFunction('xaxis', True)
        self.initMapFunction('yaxis')

        # Check x axis:
        xTickLabels = self.getTickLabels('xaxis')
        if (agg != 'sum'):
            self.assertRangeEqual(self.getRange('xaxis', True), (min(xTickLabels) - 0.1 / 2, max(xTickLabels) + 1 + 0.1 / 2))
        else:
            self.assertRangeEqual(self.getRange('xaxis', True), (float(min(xTickLabels)), float(max(xTickLabels) + 1)))
        self.assertEqual(self.getTickLabels('xaxis'), self.getData('dates'))
        self.assertEqual(self.getTickLength('xaxis'), 6.)

        # Check y axis:
        self.assertRangeEqual(self.getRange('yaxis', False), self.getDataRange(var, agg))
        self.assertEqual(self.getTickLength('yaxis'), -6.)

    def testEmptyGrid(self):
        self.selectDate(2017, 8, 5)
        self.plot()

        self.assertEqual(len(self.getAxis('grid').find_elements_by_xpath('./*')), 0)

    @TestData([
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'nrj',  'agg': 'sum'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'nrj',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pac',  'agg': 'sum'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pac',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pdc',  'agg': 'sum'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pdc',  'agg': 'inv'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'pdc',  'agg': 'str'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'udc',  'agg': 'str'},
        {'year': 2017, 'month': 8,    'day': 8,    'var': 'temp', 'agg': 'inv'},
    ])
    def testLineGrid(self, year, month, day, var, agg):
        self.selectDate(year, month, day)
        self.plot()
        self.selectVar(var)
        self.selectSum(agg)

        self.assertEqual(self.getTickPositions('yaxis'), self.getTickPositions('grid'))
        self.assertEqual(self.getTickLength('grid'), self.getDomain('xaxis', True)[1]/1.025)

    @TestData([
        {'year': None, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': None, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2019, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': 2019, 'month': None, 'day': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2018, 'month': 2,    'day': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': 2018, 'month': 2,    'day': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2018, 'month': 2,    'day': None, 'var': 'pwr',  'agg': 'sum'},
        {'year': 2018, 'month': 2,    'day': None, 'var': 'pwr',  'agg': 'inv'},
    ])
    def testBarGrid(self, year, month, day, var, agg):
        self.selectDate(year, month, day)
        self.plot()
        self.selectVar(var)
        self.selectSum(agg)

        self.assertEqual(self.getTickPositions('yaxis'), self.getTickPositions('grid'))
        self.assertEqual(self.getTickLength('grid'), self.getDomain('xaxis', False)[1])

    def testEmptyData(self):
        self.selectDate(2017, 8, 5)
        self.plot()

        self.assertEqual(len(self.getLines()), 0)
        self.assertEqual(len(self.getBars()), 0)

    @TestData([
        {'var': 'nrj',  'agg': 'sum'},
        {'var': 'nrj',  'agg': 'inv'},
        {'var': 'pac',  'agg': 'sum'},
        {'var': 'pac',  'agg': 'inv'},
        {'var': 'pdc',  'agg': 'sum'},
        {'var': 'pdc',  'agg': 'inv'},
        {'var': 'pdc',  'agg': 'str'},
        {'var': 'udc',  'agg': 'str'},
        {'var': 'temp', 'agg': 'inv'},
    ], before=loadToday)
    def testLineData(self, var, agg):
        self.selectVar(var)
        self.selectSum(agg)

        self.initMapFunction('xaxis')
        self.initMapFunction('yaxis')

        self.assertCoordinatesEqual(self.getLineData(), self.getData('dates'), self.getData(var, agg))

    @TestData([
        {'year': None, 'month': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': None, 'month': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2019, 'month': None, 'var': 'nrj',  'agg': 'sum'},
        {'year': 2019, 'month': None, 'var': 'nrj',  'agg': 'inv'},
        {'year': 2018, 'month': 2,    'var': 'nrj',  'agg': 'sum'},
        {'year': 2018, 'month': 2,    'var': 'nrj',  'agg': 'inv'},
        {'year': 2018, 'month': 2,    'var': 'pwr',  'agg': 'sum'},
        {'year': 2018, 'month': 2,    'var': 'pwr',  'agg': 'inv'},
    ])
    def testBarData(self, year, month, var, agg):
        self.loadData(year, month)

        self.selectDate(year, month)
        self.plot()
        self.selectVar(var)
        self.selectSum(agg)

        if (agg != 'sum'):
            self.initMapFunction('xaxis', True)
        else:
            self.initMapFunction('xaxis', True)
        self.initMapFunction('yaxis')

        self.assertBarsEqual(self.getBarData(), self.getData('dates'), self.getData(var, agg))

    @TestData([
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2018, 'newMonth': 2,    'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2017, 'newMonth': 8,    'newDay': 5   },
    ])
    def testEmptyChangeDate(self, year, month, day, newYear, newMonth, newDay):
        self.selectDate(year, month, day)
        self.plot()
        self.selectDate(newYear, newMonth, newDay)

        self.assertEqual(len(self.getLines()), 0)
        self.assertEqual(len(self.getBars()), 0)

    @TestData([
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2018, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 5,    'newYear': 2018, 'newMonth': 2,    'newDay': None},
    ])
    def testEmptyPartialChangeDate(self, year, month, day, newYear, newMonth, newDay):
        self.selectDate(year, month, day)
        self.plot()
        self.selectDate(newYear, newMonth, newDay, partial=True)

        self.assertEqual(len(self.getLines()), 0)
        self.assertEqual(len(self.getBars()), 0)

    @TestData([
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2018, 'newMonth': 2,    'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2017, 'newMonth': 8,    'newDay': 5   },
    ])
    def testLineChangeDate(self, year, month, day, newYear, newMonth, newDay):
        self.loadData(year, month, day)

        self.selectDate(year, month, day)
        self.plot()
        self.selectDate(newYear, newMonth, newDay)

        self.initMapFunction('xaxis')
        self.initMapFunction('yaxis')

        self.assertCoordinatesEqual(self.getLineData(), self.getData('dates'), self.getData('nrj', 'sum'))

    @TestData([
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2018, 'newMonth': None, 'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2018, 'newMonth': 2,    'newDay': None},
        {'year': 2017, 'month': 8,    'day': 8,    'newYear': 2017, 'newMonth': 2,    'newDay': None},
    ])
    def testLinePartialChangeDate(self, year, month, day, newYear, newMonth, newDay):
        self.loadData(year, month, day)

        self.selectDate(year, month, day)
        self.plot()
        self.selectDate(newYear, newMonth, newDay, partial=True)

        self.initMapFunction('xaxis')
        self.initMapFunction('yaxis')

        self.assertCoordinatesEqual(self.getLineData(), self.getData('dates'), self.getData('nrj', 'sum'))

    @TestData([
        {'year': None, 'month': None, 'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': None, 'month': None, 'newYear': 2018, 'newMonth': 2,    'newDay': None},
        {'year': None, 'month': None, 'newYear': 2017, 'newMonth': 8,    'newDay': 5   },
        {'year': None, 'month': None, 'newYear': 2017, 'newMonth': 8,    'newDay': 8   },
        {'year': 2019, 'month': None, 'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2019, 'month': None, 'newYear': 2018, 'newMonth': 2,    'newDay': None},
        {'year': 2019, 'month': None, 'newYear': 2017, 'newMonth': 8,    'newDay': 5   },
        {'year': 2019, 'month': None, 'newYear': 2017, 'newMonth': 8,    'newDay': 8   },
        {'year': 2018, 'month': 2,    'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2018, 'month': 2,    'newYear': 2019, 'newMonth': None, 'newDay': None},
        {'year': 2018, 'month': 2,    'newYear': 2017, 'newMonth': 8,    'newDay': 5   },
        {'year': 2018, 'month': 2,    'newYear': 2017, 'newMonth': 8,    'newDay': 8   },
    ])
    def testBarChangeDate(self, year, month, newYear, newMonth, newDay):
        self.loadData(year, month)

        self.selectDate(year, month)
        self.plot()
        self.selectDate(newYear, newMonth, newDay)

        self.initMapFunction('xaxis', True)
        self.initMapFunction('yaxis')

        self.assertBarsEqual(self.getBarData(), self.getData('dates'), self.getData('nrj', 'sum'))

    @TestData([
        {'year': 2019, 'month': None, 'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2018, 'month': 2,    'newYear': None, 'newMonth': None, 'newDay': None},
        {'year': 2018, 'month': 2,    'newYear': 2019, 'newMonth': None, 'newDay': None},
    ])
    def testBarPartialChangeDate(self, year, month, newYear, newMonth, newDay):
        self.loadData(year, month)

        self.selectDate(year, month)
        self.plot()
        self.selectDate(newYear, newMonth, newDay, partial=True)

        self.initMapFunction('xaxis', True)
        self.initMapFunction('yaxis')

        self.assertBarsEqual(self.getBarData(), self.getData('dates'), self.getData('nrj', 'sum'))

    @TestData([
        {'newYear': 2017, 'newMonth': 8,    'newDay': 5,    'year': None, 'month': None, 'day': None},
        {'newYear': 2017, 'newMonth': 8,    'newDay': 5,    'year': 2019, 'month': None, 'day': None},
        {'newYear': 2017, 'newMonth': 8,    'newDay': 5,    'year': 2018, 'month': 2,    'day': None},
        {'newYear': 2017, 'newMonth': 8,    'newDay': 5,    'year': 2017, 'month': 8,    'day': 5   },
    ])
    def testEmptyTransition(self, year, month, day, newYear, newMonth, newDay):
        self.selectDate(year, month, day)
        self.plot()
        self.selectDate(newYear, newMonth, newDay)
        self.plot()

        self.assertEqual(len(self.getLines()), 0)
        self.assertEqual(len(self.getBars()), 0)

    @TestData([
        {'newYear': 2017, 'newMonth': 8,    'newDay': 8,    'year': None, 'month': None, 'day': None},
        {'newYear': 2017, 'newMonth': 8,    'newDay': 8,    'year': 2019, 'month': None, 'day': None},
        {'newYear': 2017, 'newMonth': 8,    'newDay': 8,    'year': 2018, 'month': 2,    'day': None},
        {'newYear': 2017, 'newMonth': 8,    'newDay': 8,    'year': 2017, 'month': 8,    'day': 5   },
    ])
    def testLineTransition(self, year, month, day, newYear, newMonth, newDay):
        self.loadData(newYear, newMonth, newDay)

        self.selectDate(year, month, day)
        self.plot()
        self.selectDate(newYear, newMonth, newDay)
        self.plot()

        self.initMapFunction('xaxis')
        self.initMapFunction('yaxis')

        self.assertCoordinatesEqual(self.getLineData(), self.getData('dates'), self.getData('nrj', 'sum'))

    @TestData([
        {'newYear': None, 'newMonth': None, 'year': 2019, 'month': None, 'day': None},
        {'newYear': None, 'newMonth': None, 'year': 2018, 'month': 2,    'day': None},
        {'newYear': None, 'newMonth': None, 'year': 2017, 'month': 8,    'day': 5   },
        {'newYear': None, 'newMonth': None, 'year': 2017, 'month': 8,    'day': 8   },
        {'newYear': 2019, 'newMonth': None, 'year': None, 'month': None, 'day': None},
        {'newYear': 2019, 'newMonth': None, 'year': 2018, 'month': 2,    'day': None},
        {'newYear': 2019, 'newMonth': None, 'year': 2017, 'month': 8,    'day': 5   },
        {'newYear': 2019, 'newMonth': None, 'year': 2017, 'month': 8,    'day': 8   },
        {'newYear': 2018, 'newMonth': 2,    'year': None, 'month': None, 'day': None},
        {'newYear': 2018, 'newMonth': 2,    'year': 2019, 'month': None, 'day': None},
        {'newYear': 2018, 'newMonth': 2,    'year': 2017, 'month': 8,    'day': 5   },
        {'newYear': 2018, 'newMonth': 2,    'year': 2017, 'month': 8,    'day': 8   },
    ])
    def testBarTransition(self, year, month, day, newYear, newMonth):
        self.loadData(newYear, newMonth)

        self.selectDate(year, month, day)
        self.plot()
        self.selectDate(newYear, newMonth)
        self.plot()

        self.initMapFunction('xaxis', True)
        self.initMapFunction('yaxis')

        self.assertBarsEqual(self.getBarData(), self.getData('dates'), self.getData('nrj', 'sum'))

    @TestData([
        {'newYear': None, 'newMonth': None, 'year': 2019, 'month': None, 'day': None},
        {'newYear': None, 'newMonth': None, 'year': 2018, 'month': 2,    'day': None},
        {'newYear': None, 'newMonth': None, 'year': 2017, 'month': 8,    'day': 5   },
        {'newYear': None, 'newMonth': None, 'year': 2017, 'month': 8,    'day': 8   },
        {'newYear': 2019, 'newMonth': None, 'year': 2018, 'month': 2,    'day': None},
        {'newYear': 2019, 'newMonth': None, 'year': 2017, 'month': 8,    'day': 5   },
        {'newYear': 2019, 'newMonth': None, 'year': 2017, 'month': 8,    'day': 8   },
        {'newYear': 2018, 'newMonth': None, 'year': 2017, 'month': 8,    'day': 5   },
        {'newYear': 2018, 'newMonth': None, 'year': 2017, 'month': 8,    'day': 8   },
        {'newYear': 2018, 'newMonth': 2,    'year': 2017, 'month': 8,    'day': 5   },
        {'newYear': 2018, 'newMonth': 2,    'year': 2017, 'month': 8,    'day': 8   },
    ])
    def testBarPartialTransition(self, year, month, day, newYear, newMonth):
        self.loadData(newYear, newMonth)

        self.selectDate(year, month, day)
        self.plot()
        self.selectDate(newYear, newMonth, partial=True)
        self.plot()

        self.initMapFunction('xaxis', True)
        self.initMapFunction('yaxis')

        self.assertBarsEqual(self.getBarData(), self.getData('dates'), self.getData('nrj', 'sum'))

    @TestData([
        {'year': 2017, 'month': 8,    'day': 6,    'prevYear': 2017, 'prevMonth': 8,    'prevDay': 5   },
    ])
    def testEmptyPrev(self, year, month, day, prevYear, prevMonth, prevDay):
        self.selectDate(year, month, day)
        self.plot()
        self.browser.find_element_by_id('prev').click()

        self.assertEqual(len(self.getLines()), 0)
        self.assertEqual(len(self.getBars()), 0)

    @TestData([
        {'year': 2011, 'month': 6,    'day': 24,   'prevYear': 2011, 'prevMonth': 6,    'prevDay': 24  },
        {'year': 2011, 'month': 6,    'day': 26,   'prevYear': 2011, 'prevMonth': 6,    'prevDay': 24  },
        {'year': 2011, 'month': 12,   'day': 25,   'prevYear': 2011, 'prevMonth': 6,    'prevDay': 30  },
        {'year': 2017, 'month': 2,    'day': 1,    'prevYear': 2011, 'prevMonth': 12,   'prevDay': 31  },
        {'year': 2017, 'month': 8,    'day': 5,    'prevYear': 2017, 'prevMonth': 8,    'prevDay': 4   },
    ])
    def testLinePrev(self, year, month, day, prevYear, prevMonth, prevDay):
        self.loadData(prevYear, prevMonth, prevDay)

        self.selectDate(year, month, day)
        self.plot()
        self.browser.find_element_by_id('prev').click()

        self.initMapFunction('xaxis')
        self.initMapFunction('yaxis')

        self.assertCoordinatesEqual(self.getLineData(), self.getData('dates'), self.getData('nrj', 'sum'))

    @TestData([
        {'year': 2009, 'month': None, 'prevYear': 2009, 'prevMonth': None},
        {'year': 2010, 'month': None, 'prevYear': 2009, 'prevMonth': None},
        {'year': 2010, 'month': 12,   'prevYear': 2010, 'prevMonth': 12, },
        {'year': 2011, 'month': 6,    'prevYear': 2010, 'prevMonth': 12  },
    ])
    def testBarPrev(self, year, month, prevYear, prevMonth):
        self.loadData(prevYear, prevMonth)

        self.selectDate(year, month)
        self.plot()
        self.browser.find_element_by_id('prev').click()


        self.initMapFunction('xaxis', True)
        self.initMapFunction('yaxis')

        self.assertBarsEqual(self.getBarData(), self.getData('dates'), self.getData('nrj', 'sum'))

    @TestData([
        {'year': 2017, 'month': 8,    'day': 4,    'nextYear': 2017, 'nextMonth': 8,    'nextDay': 5   },
    ])
    def testEmptyNext(self, year, month, day, nextYear, nextMonth, nextDay):
        self.selectDate(year, month, day)
        self.plot()
        self.browser.find_element_by_id('next').click()

        self.assertEqual(len(self.getLines()), 0)
        self.assertEqual(len(self.getBars()), 0)

    @TestData([
        {'year': 2017, 'month': 8,    'day': 8,    'nextYear': 2017, 'nextMonth': 8,    'nextDay': 8   },
        {'year': 2017, 'month': 8,    'day': 6,    'nextYear': 2017, 'nextMonth': 8,    'nextDay': 8   },
        {'year': 2017, 'month': 8,    'day': 5,    'nextYear': 2017, 'nextMonth': 8,    'nextDay': 6   },
        {'year': 2017, 'month': 2,    'day': 7,    'nextYear': 2017, 'nextMonth': 8,    'nextDay': 2   },
        {'year': 2011, 'month': 12,   'day': 31,   'nextYear': 2017, 'nextMonth': 2,    'nextDay': 1   },
    ])
    def testLineNext(self, year, month, day, nextYear, nextMonth, nextDay):
        self.loadData(nextYear, nextMonth, nextDay)

        self.selectDate(year, month, day)
        self.plot()
        self.browser.find_element_by_id('next').click()

        self.initMapFunction('xaxis')
        self.initMapFunction('yaxis')

        self.assertCoordinatesEqual(self.getLineData(), self.getData('dates'), self.getData('nrj', 'sum'))

    @TestData([
        {'year': 2018, 'month': None, 'nextYear': 2019, 'nextMonth': None},
        {'year': 2019, 'month': None, 'nextYear': 2019, 'nextMonth': None},
        {'year': 2018, 'month': 2,    'nextYear': 2018, 'nextMonth': 2   },
        {'year': 2017, 'month': 8,    'nextYear': 2018, 'nextMonth': 2   },
    ])
    def testBarNext(self, year, month, nextYear, nextMonth):
        self.loadData(nextYear, nextMonth)

        self.selectDate(year, month)
        self.plot()
        self.browser.find_element_by_id('next').click()

        self.initMapFunction('xaxis', True)
        self.initMapFunction('yaxis')

        self.assertBarsEqual(self.getBarData(), self.getData('dates'), self.getData('nrj', 'sum'))


