#!/bin/sh
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

# PATHES ##########################################################################################
# Absolute path to folder containing script (and related files):
SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR"
SCRIPT_DIR="$PWD"
cd - > /dev/null
# Absolute path to test directory
DEST_DIR="$SCRIPT_DIR"
if [ $# -ge 1 ]; then
    mkdir -p "$1"
    cd "$1"
    DEST_DIR="$PWD"
    cd - > /dev/null
fi
# Absolute path to code directory
CODE_DIR="$SCRIPT_DIR/../prod"
if [ $# -ge 2 ]; then
    if [ -d "$2" ]; then
        echo "Provided code dir '$2' does not exit" >&2
        exit -1
    fi
    cd "$2"
    CODE_DIR="$PWD"
    cd - > /dev/null
else
    cd "$CODE_DIR"
    CODE_DIR="$PWD"
    cd - > /dev/null
fi
# Directory where to write profiles (absolute path):
PROFILES_DIR="$DEST_DIR/profiles"
if [ $# -ge 3 ]; then
    mkdir -p "$3"
    cd "$3"
    PROFILES_DIR="$PWD"
    cd - > /dev/null
elif [ ! -d "$PROFILES_DIR" ]; then
    mkdir -p "$PROFILES_DIR"
fi
# Download directory (absolute path):
EXPORTS_DIR="$DEST_DIR/export"
if [ $# -ge 4 ]; then
    mkdir -p "$4"
    cd "$4"
    EXPORTS_DIR="$PWD"
    cd - > /dev/null
elif [ ! -d "$EXPORTS_DIR" ]; then
    mkdir -p "$EXPORTS_DIR"
fi

# HELPER FUNCTIONS ################################################################################
# Check there are not any space in argument:
#   $1 argument to test
# Returns 0 if there are spaces and 1 otherwise.
check_spaces() {
    DOLLARD='$'
    if [ $# -gt 2 ]; then
        echo "$DOLLARD$1 contains spaces"
        return 0
    fi
    return 1
}

# Create firefox profile:
#   $1: Profile name (mandatory)
#   $2: Window width (optional)
#   $3: Window height (optional)
create_profile() {
    # Check profile name does not contain spaces:
    if check_spaces "PROFILE_NAME" $1; then
        return 0
    fi
    printf "Creating profile \"$PROFILES_DIR/$1\" ...\t"
    
    # Create profile directory:
    mkdir -p "$PROFILES_DIR/$1/extensions"
    
    # Set download directory to EXPORTS_DIR:
    echo "user_pref(\"browser.download.dir\", \"${EXPORTS_DIR}\");" >> "$PROFILES_DIR/$1/prefs.js"
    echo "user_pref(\"browser.cache.memory.enable\", false);" >> "$PROFILES_DIR/$1/prefs.js"
    echo "user_pref(\"browser.cache.disk.enable\", false);" >> "$PROFILES_DIR/$1/prefs.js"
    echo "user_pref(\"browser.cache.offline.enable\", false);" >> "$PROFILES_DIR/$1/prefs.js"
    echo "user_pref(\"browser.download.folderList\", 2);" >> "$PROFILES_DIR/$1/prefs.js"
    echo "user_pref(\"xpinstall.signatures.required\", false);" >> "$PROFILES_DIR/$1/prefs.js"
    
    # Set mimeTypes.rdf so that CSV files are automatically saved to disk:
    cp "$SCRIPT_DIR/mimeTypes.rdf" "$PROFILES_DIR/$1/"
    
    # Install console capture:
    cp console_capture.xpi "$PROFILES_DIR/$1/extensions/console_capture@pas.com.xpi"

    # Change size:
    if [ $# -gt 1 ]; then
        W=$(expr $2 + 0)
        H=$(expr $3 + 74)
        echo "{\"chrome://browser/content/browser.xul\":{\"main-window\":{\"screenX\":\"1366\",\"screenY\":\"0\",\"width\":\"$W\",\"height\":\"$H\",\"sizemode\":\"normal\"}}}" > "$PROFILES_DIR/$1/xulstore.json"
    fi
    
    echo "DONE"
}

# CONFIRM PATHES ##################################################################################
# Check profile dir does not contain spaces:
if check_spaces "PROFILES_DIR" $PROFILES_DIR; then
    exit 1
fi
# Ask user to check paths:
ANS=
ANY=
echo "Code     directory: '$CODE_DIR'"
echo "Dest     directory: '$DEST_DIR'"
echo "Exports  directory: '$EXPORTS_DIR'"
echo "Profiles directory: '$PROFILES_DIR'"
echo "Is this exact (Y/n)?"
while true; do
    read ANS
    if [ -z "$ANS" -o "$ANS" == 'y' -o "$ANS" == 'Y' ]; then
        break
    fi
    if [ "$ANS" == 'n' -o "$ANS" == 'N' ]; then
        echo "OK, quitting"
        exit 0    
    fi
done

# VIRTUAL ENVIRONMENT #############################################################################
# Delete old test environment:
ANS=
if [ -d "$DEST_DIR/env" ]; then
    echo "Folder $DEST_DIR/env already exists. Do you want to delete it (y/N)?"
    while true; do
        read ANS
        if [ -z "$ANS" -o "$ANS" == 'n' -o "$ANS" == 'N' ]; then
            echo "OK, skipping"
            ANS='skip'
            break
        fi
        if [ "$ANS" == 'y' -o "$ANS" == 'Y' ]; then
            rm -R "$DEST_DIR/env"
            ANS=
            ANY='yes'
            break
        fi
    done
fi
# Create test environment:
if [ -z "$ANS" ]; then
    virtualenv --system-site-packages "$DEST_DIR/env"
    . "$DEST_DIR/env/bin/activate"
    pip install --upgrade pip
    pip install selenium
    deactivate
fi
# Get and install Gecko driver:
if [ -z "$ANS" ]; then
    if [ -f "$SCRIPT_DIR/gecko-version.local" ]; then
        GECKO_VERSION=$(cat "$SCRIPT_DIR/gecko-version.local")
    else
        GECKO_VERSION=$(curl "https://github.com/mozilla/geckodriver/releases/latest" | sed -e 's|^<html><body>You are being <a href="https://github.com/mozilla/geckodriver/releases/tag/\(v[0-9]\+.[0-9]\+.[0-9]\+\)">redirected</a>.</body></html>$|\1|')
    fi
    case $(uname -m) in
        x86)
            GECKO_NAME="geckodriver-$GECKO_VERSION-linux32.tar.gz"
            ;;
        x86_64)
            GECKO_NAME="geckodriver-$GECKO_VERSION-linux64.tar.gz"
            ;;
        arm*)
            GECKO_NAME="geckodriver-$GECKO_VERSION-arm7hf.tar.gz"
            ;;
    esac
    rm "$GECKO_NAME" 2> /dev/null
    wget "https://github.com/mozilla/geckodriver/releases/download/$GECKO_VERSION/$GECKO_NAME"
    tar -xzf "$GECKO_NAME"
    mv geckodriver "$DEST_DIR/env/bin"
    rm "$GECKO_NAME"
fi

# PROFILES ########################################################################################
# Deletes exisiting profiles:
ANS=
if [ -n "$(ls "$PROFILES_DIR")" ]; then
    echo "There exists profiles in $PROFILES_DIR. Do you want to delete them (y/N)?"
    while true; do
        read ANS
        if [ -z "$ANS" -o "$ANS" == 'n' -o "$ANS" == 'N' ]; then
            echo "OK, skipping"
            ANS='skip'
            break
        fi
        if [ "$ANS" == 'y' -o "$ANS" == 'Y' ]; then
            rm -R "$PROFILES_DIR"
            ANS=
            ANY='yes'
            break
        fi
    done
fi
# Get ConsoleCapture:
if [ -z "$ANS" ]; then
    if [ -f "$SCRIPT_DIR/ConsoleCapture-version.local" ]; then
        CC_VERSION=$(cat "$SCRIPT_DIR/ConsoleCapture-version.local")
    else
        CC_VERSION="$(curl "https://github.com/pasccom/ConsoleCapture/releases/latest" | sed -e 's|^<html><body>You are being <a href="https://github.com/pasccom/ConsoleCapture/releases/tag/\(v[0-9]\+.[0-9]\+\)">redirected</a>.</body></html>$|\1|')"
    fi
    rm console_capture.xpi 2> /dev/null
    wget "https://github.com/pasccom/ConsoleCapture/releases/download/$CC_VERSION/console_capture.xpi"
fi
# Create new profiles:
if [ -z "$ANS" ]; then
    create_profile "test"
    create_profile "1200x694" 1200 694
    create_profile "1024x655" 1024 655
    create_profile "1023x655" 1023 655
    create_profile  "724x500"  724 500
    create_profile  "723x500"  723 500
    create_profile  "501x200"  501 200
    create_profile  "468x200"  468 200
fi
# Delete ConsoleCapture:
if [ -z "$ANS" ]; then
    rm console_capture.xpi
fi

# PROD DIRECTORY ##################################################################################
# Delete old test data:
ANS=
if [ -d "$DEST_DIR/prod" -a -z "$ANY" ]; then
    echo "Folder $DEST_DIR/prod already exists. Do you want to delete it (Y/n)?"
    while true; do
        read ANS
        if [ -z "$ANS" -o "$ANS" == 'y' -o "$ANS" == 'Y' ]; then
            rm -R "$DEST_DIR/prod"
            ANS=
            break
        fi
        if [ "$ANS" == 'n' -o "$ANS" == 'N' ]; then
            echo "OK, skipping"
            ANS='skip'
            break
        fi
    done
elif [ -d "$DEST_DIR/prod" ]; then
    echo "Folder $DEST_DIR/prod already exists. Do you want to delete it (y/N)?"
    while true; do
        read ANS
        if [ -z "$ANS" -o "$ANS" == 'n' -o "$ANS" == 'N' ]; then
            echo "OK, skipping"
            ANS='skip'
            break
        fi
        if [ "$ANS" == 'y' -o "$ANS" == 'Y' ]; then
            rm -R "$DEST_DIR/prod"
            ANS=
            break
        fi
    done
fi
# Create test data:
if [ -z "$ANS" ]; then
    printf "Extracting testdata ...\t\t\t\t\t\t\t"
    tar -xzf "$SCRIPT_DIR/testdata.tar.gz"
    mv testdata "$DEST_DIR/prod" 2> /dev/null
    echo "DONE"
    printf "Setting up test environment ...\t\t\t\t\t\t"
    cp -a "$CODE_DIR/img" "$DEST_DIR/prod/"
    cp -a "$CODE_DIR/js" "$DEST_DIR/prod/"
    cp -a "$CODE_DIR"/*.css "$DEST_DIR/prod/"
    cp -a "$CODE_DIR"/*.html "$DEST_DIR/prod/"
    echo "DONE"
fi
