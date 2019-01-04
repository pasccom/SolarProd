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

from .tests.helpers import HelpersTest
from .tests.elements import ElementsTest
from .tests.layout import LayoutTest
from .tests.select import SelectTest
from .tests.export import ExportTest
from .tests.prev_next import PrevNextTest
from .tests.left_right_key import LeftRightKeyTest
from .tests.repeat import RepeatTest
from .tests.slow_prev_next import SlowPrevNextTest
from .tests.slow_key import SlowKeyTest
from .tests.legend import LegendTest
from .tests.chart import ChartTest
from .tests.cursor import CursorTest
from .tests.cursor_legend import CursorLegendTest
from .tests.cursor_bar import CursorBarTest
from .tests.cursor_line import CursorLineTest

if __name__ == '__main__':
    unittest.main(verbosity=2)
