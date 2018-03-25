REPOSITORY DESCRIPTION
----------------------

This repository contains the code for a web page created to display
solar electric production data. The code is quite generic, so it
could actually be used to display any type of electric production data.
You can reuse it freely under the terms of the GPL version 3 (see the 
LICENSE file of this repository, or below for a short note).

FEATURES
--------

Here is the list of the current features (included in version 1.0.0)
- Display daily data using lines.
- Display monthly, yearly or all data using bars.
- Display data per string, per inverter or total when available.
- Legend allows to select shown curves.
- Easily go to previous/next day/month/year.
- Export displayed data as CSV.

Ideas I have to extend the functionalities of the page are listed
[below](#future-developments)

FUTURE DEVELOPMENTS
-------------------

Here is the list of ideas I would like to implement
- Nominal data
- Cursors (to obtain the accurate value of a data point)
- Plant information
- Plant events

If you have any other feature you will be interested in, please let me know.
I will be pleased to develop it if I think it is a must have.

If you want to implement extension, also tell me please. Admittedly you
can do what you desire with the code (under the
[licensing constraints](#licensing-information)), but this will avoid double work.


DEPLOYING
---------

The script [deploy.sh](https://github.com/pasccom/SolarProd/blob/master/deploy.sh)
allows to easily deploy the web page to production server. It takes as only
mandatory argument the path to the folder, where the code should be deployed.

You can select which [FileSaver.js](https://github.com/eligrey/FileSaver.js) 
version you want by creating a `FileSaver-version.local` file and writing
the desired version inside. Currently, FileSaver version 1.3.4 is recommended.

TESTING
-------

The repository inculdes an extensive end-to-end test suite, for the features listed
[above](#features). The testing uses
[Selenium WebDriver](https://www.seleniumhq.org/projects/webdriver/) to automate
browser interaction. Currently only [Firefox](https://www.mozilla.org/fr/firefox/)
is supported and tested against.

The tests are run in a Python virtual environment, so that no system-wide package
installation is needed. To easily setup the test environment, you can use the script
[setup_test.sh](https://github.com/pasccom/SolarProd/blob/master/setup_test.sh),
which takes as optional arguments:
1. The path to the test directory (defaults to working directory)
2. The path to the directory where profiles will be generated (defaults to `profiles`
in test directory)
3. The path to the directory where exported data will be saved (defaults to `export`
in test directory)

If you are not using the latest version of [Firefox](https://www.mozilla.org/fr/firefox/)
you will need to create a `gecko-version.local` file containing the version of
the marionnette to use. Unfortunatlety, I was not able to locate a compatibility table,
so you will have to try various versions of the marionnette until it works. Release dates
may be a good heuristic.

To run the tests, the most handy manner is
```
python -m unittest -v [testsuite[.testcase[.testfixture]]]
```
See [test.py](https://github.com/pasccom/SolarProd/blob/master/test.py) for a list of 
test cases and test fixtures. Running all the test fixtures for version 1.0.0 takes 
approximately *25min* on my PC.

LICENSING INFORMATION
---------------------
These programs are free software: you can redistribute them and/or modify
them under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

These programs are distributed in the hope that they will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
