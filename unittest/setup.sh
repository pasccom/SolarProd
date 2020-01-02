#!/bin/sh
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

# PATHES ##########################################################################################
# Absolute path to folder containing script (and related files):
SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR"
SCRIPT_DIR="$PWD"
cd - > /dev/null
# Absolute path to destination directory
DEST_DIR="$SCRIPT_DIR"
if [ $# -ge 1 ]; then
    mkdir -p "$1"
    cd "$1"
    DEST_DIR="$PWD"
    cd - > /dev/null
elif [ ! -d "$DEST_DIR" ]; then
    mkdir -p "$DEST_DIR"
fi
# Absolute path to GenTest directory
GENTEST_SRC_DIR="$SCRIPT_DIR/GenTest"
if [ $# -ge 2 ]; then
    if [ -d "$2" ]; then
        echo "Provided code dir '$2' does not exit" >&2
        exit -1
    fi
    cd "$2"
    GENTEST_SRC_DIR="$PWD"
    cd - > /dev/null
fi
# Absolute path to jasmine directory
JASMINE_DIR="$DEST_DIR/jasmine"
if [ $# -ge 3 ]; then
    mkdir -p "$3"
    cd "$3"
    JASMINE_DIR="$PWD"
    cd - > /dev/null
elif [ ! -d "$JASMINE_DIR" ]; then
    mkdir -p "$JASMINE_DIR"
fi
# Absolute path to gentest directory
GENTEST_DIR="$DEST_DIR/gentest"
if [ $# -ge 4 ]; then
    mkdir -p "$4"
    cd "$4"
    GENTEST_DIR="$PWD"
    cd - > /dev/null
elif [ ! -d "$GENTEST_DIR" ]; then
    mkdir -p "$GENTEST_DIR"
fi
# Ask user to check paths:
ANS=
echo "Script  directory: '$SCRIPT_DIR'"
echo "GenTest directory: '$GENTEST_SRC_DIR'"
echo "Dest    directory: '$DEST_DIR'"
echo "jasmine directory: '$JASMINE_DIR'"
echo "gentest directory: '$GENTEST_DIR'"
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

# DEST DIR SETUP ##################################################################################
# Setup test diretory:
if [ ! "$SCRIPT_DIR" = "$DEST_DIR" ]; then
    # When folder already contains testrunner.html, ask user what to do:
    ANS=
    if [ -f "$DEST_DIR/testrunner.html" ]; then
        echo "Folder $DEST_DIR already exists. Do you want to delete it (y/N)?"
        while true; do
            read ANS
            if [ -z "$ANS" -o "$ANS" == 'n' -o "$ANS" == 'N' ]; then
                echo "OK, skipping"
                ANS='skip'
                break
            fi
            if [ "$ANS" == 'y' -o "$ANS" == 'Y' ]; then
                ANS=
                ANY='yes'
                break
            fi
        done
    fi
    # Copy source files:
    if [ -z $ANS ]; then
        cp "$SCRIPT_DIR/testrunner.html" "$DEST_DIR/testrunner.html"
        cp -a "$SCRIPT_DIR/specs" "$DEST_DIR/"
    fi
fi

# JASMINE SETUP ###################################################################################
# Delete existing Jasmine files:
ANS=
if [ -n "$(ls -A "$JASMINE_DIR")" ]; then
    echo "Folder $JASMINE_DIR is not empty. Do you want to delete its contents (y/N)?"
    while true; do
        read ANS
        if [ -z "$ANS" -o "$ANS" == 'n' -o "$ANS" == 'N' ]; then
            echo "OK, skipping"
            ANS='skip'
            break
        fi
        if [ "$ANS" == 'y' -o "$ANS" == 'Y' ]; then
            rm -R "$JASMINE_DIR"/*
            ANS=
            ANY='yes'
            break
        fi
    done
fi
# Get Jasmine files:
if [ -z "$ANS" ]; then
    if [ -f "$SCRIPT_DIR/jasmine-version.local" ]; then
        JASMINE_VERSION=$(cat "$SCRIPT_DIR/jasmine-version.local")
    else
        JASMINE_VERSION=$(curl "https://github.com/jasmine/jasmine/releases/latest" | sed -e 's|^<html><body>You are being <a href="https://github.com/jasmine/jasmine/releases/tag/v\([0-9]\+.[0-9]\+.[0-9]\+\)">redirected</a>.</body></html>$|\1|')
    fi
    rm "jasmine-standalone-$JASMINE_VERSION.zip" 2> /dev/null
    wget "https://github.com/jasmine/jasmine/releases/download/v$JASMINE_VERSION/jasmine-standalone-$JASMINE_VERSION.zip"
    mkdir "Jasmine"
    cd "Jasmine"
    mv "../jasmine-standalone-$JASMINE_VERSION.zip" .
    unzip "jasmine-standalone-$JASMINE_VERSION.zip"
    mv "lib/jasmine-$JASMINE_VERSION"/* "$JASMINE_DIR"
    cd ..
    rm -R "Jasmine"
fi
# Get Jasmine Ajax files:
if [ -z "$ANS" ]; then
    if [ -f "$SCRIPT_DIR/jasmine-ajax-version.local" ]; then
        JASMINE_AJAX_VERSION=$(cat "$SCRIPT_DIR/jasmine-ajax-version.local")
    else
        JASMINE_AJAX_VERSION=$(curl "https://github.com/jasmine/jasmine-ajax/releases/latest" | sed -e 's|^<html><body>You are being <a href="https://github.com/jasmine/jasmine-ajax/releases/tag/v\([0-9]\+.[0-9]\+.[0-9]\+\)">redirected</a>.</body></html>$|\1|')
    fi
    rm "v$JASMINE_AJAX_VERSION.tar.gz" 2> /dev/null
    wget "https://github.com/jasmine/jasmine-ajax/archive/v$JASMINE_AJAX_VERSION.tar.gz"
    tar -xzf "v$JASMINE_AJAX_VERSION.tar.gz"
    cp "jasmine-ajax-$JASMINE_AJAX_VERSION/lib/mock-ajax.js" "$JASMINE_DIR"
    rm -R "jasmine-ajax-$JASMINE_AJAX_VERSION"
    rm "v$JASMINE_AJAX_VERSION.tar.gz"
fi

# GENTEST SETUP ###################################################################################
# Delete existing GenTest files:
ANS=
if [ -n "$(ls -A "$GENTEST_DIR")" ]; then
    echo "Folder $GENTEST_DIR is not empty. Do you want to overwrite its contents (y/N)?"
    while true; do
        read ANS
        if [ -z "$ANS" -o "$ANS" == 'n' -o "$ANS" == 'N' ]; then
            echo "OK, skipping"
            ANS='skip'
            break
        fi
        if [ "$ANS" == 'y' -o "$ANS" == 'Y' ]; then
            rm -R "$GENTEST_DIR"/*
            ANS=
            ANY='yes'
            break
        fi
    done
fi
# Copy GenTest files:
if [ -z "$ANS" ]; then
    cp "$SCRIPT_DIR/GenTest/jasmine/jasmine-gentest.js" "$GENTEST_DIR"
    cp "$SCRIPT_DIR/GenTest/lib"/* "$GENTEST_DIR"
fi
