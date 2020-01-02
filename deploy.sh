#! /bin/sh
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
# along with SolarProd. If not, see <http://www.gnu.org/licenses/>

# Creates dist repository:
if [ ! -d "$1" ]; then
    mkdir -p "$1"
fi

# Deploy local files:
sed -e 's|src="js/d3.js"|src="https://d3js.org/d3.v4.min.js"|' \
    -e 's|src="js/FileSaver.js"|src="js/FileSaver.min.js"|' "prod/index.html" > "$1/index.html"
cp "prod/help.html" "$1/"
cp "prod/style.css" "$1/"
cp -r "prod/img" "$1/"
mkdir "$1/js"
cp "prod/js/locale.js" "$1/js/"
cp "prod/js/linedata.js" "$1/js/"
cp "prod/js/histdata.js" "$1/js/"
cp "prod/js/solardata.js" "$1/js/"
cp "prod/js/lineplot.js" "$1/js/"
cp "prod/js/histplot.js" "$1/js/"
cp "prod/js/solarplot.js" "$1/js/"
cp "prod/js/solarlegend.js" "$1/js/"
cp "prod/js/solarchart.js" "$1/js/"
cp "prod/js/popup.js" "$1/js/"
cp "prod/js/tabview.js" "$1/js/"
cp "prod/js/drawgraphs.js" "$1/js/"
cp "prod/js/solarprod.js" "$1/js/"

# Get FileSaver.js from GitHub:
if [ -f 'FileSaver-version.local' ]; then
    FILESAVER_VERSION=$(cat 'FileSaver-version.local')
else
    FILESAVER_VERSION=$(curl "https://github.com/eligrey/FileSaver.js/releases/latest" | sed -e 's|^<html><body>You are being <a href="https://github.com/eligrey/FileSaver.js/releases/tag/\([0-9]\+.[0-9]\+.[0-9]\+\)">redirected</a>.</body></html>$|\1|')
fi
rm "FileSaver.js-$FILESAVER_VERSION.tar.gz" 2> /dev/null
rm -R "FileSaver.js-$FILESAVER_VERSION" 2> /dev/null
wget -O "FileSaver.js-$FILESAVER_VERSION.tar.gz" "https://github.com/eligrey/FileSaver.js/archive/$FILESAVER_VERSION.tar.gz"
tar -xzf "FileSaver.js-$FILESAVER_VERSION.tar.gz"
FILESAVER_PATH=$(find "FileSaver.js-$FILESAVER_VERSION/" -iname FileSaver.min.js)
if [ -z "$FILESAVER_PATH" ]; then
    FILESAVER_PATH=$(find "FileSaver.js-$FILESAVER_VERSION/" -iname FileSaver.js)
fi
cp "$FILESAVER_PATH" "$1/js/FileSaver.min.js"
rm "FileSaver.js-$FILESAVER_VERSION.tar.gz"
rm -R "FileSaver.js-$FILESAVER_VERSION"
