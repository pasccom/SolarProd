#!/bin/sh

PWD=$(pwd)

TEST_DIR="$PWD"
if [ $# -ge 1 ]; then
    mkdir -p "$1"
    cd "$1"
    TEST_DIR="$(pwd)"
    cd "$PWD"
fi

# Directory where to write profiles (absolute path):
PROFILES_DIR="$TEST_DIR/profiles"
if [ $# -ge 2 ]; then
    mkdir -p "$2"
    cd "$2"
    PROFILES_DIR="$(pwd)"
    cd "$PWD"
fi

# Download directory (absolute path):
EXPORTS_DIR="$TEST_DIR/export"
if [ $# -ge 3 ]; then
    mkdir -p "$3"
    cd "$3"
    EXPORTS_DIR="$PWD"
    cd "$PWD"
elif [ ! -d "$EXPORTS_DIR" ]; then
    mkdir -p "$EXPORTS_DIR"
fi

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
    mkdir -p "$PROFILES_DIR/$1"
    
    # Set download directory to EXPORTS_DIR:
    echo "user_pref(\"browser.download.dir\", \"${EXPORTS_DIR}\");" >> "$PROFILES_DIR/$1/prefs.js"
    echo "user_pref(\"browser.download.folderList\", 2);" >> "$PROFILES_DIR/$1/prefs.js"
    
    # Set mimeTypes.rdf so that CSV files are automatically saved to disk:
    cp "$(dirname $0)/mimeTypes.rdf" "$PROFILES_DIR/$1/"
    
    # Change size:
    if [ $# -gt 1 ]; then
        W=$(expr $2 + 0)
        H=$(expr $3 + 71)
        echo "{\"chrome://browser/content/browser.xul\":{\"main-window\":{\"screenX\":\"1366\",\"screenY\":\"0\",\"width\":\"$W\",\"height\":\"$H\",\"sizemode\":\"normal\"}}}" > "$PROFILES_DIR/$1/xulstore.json"
    fi
    
    echo "DONE"
}

# Check profile dir does not contain spaces:
if check_spaces "PROFILES_DIR" $PROFILES_DIR; then
    exit 1
fi

# Delete old test environment:
ANS=
if [ -d "$TEST_DIR/env" ]; then
    echo "Folder $TEST_DIR/env already exists. Do you want to delete it (y/N)?"
    while true; do
        read ANS
        if [ -z "$ANS" -o "$ANS" == 'n' -o "$ANS" == 'N' ]; then
            echo "OK, skipping"
            ANS='skip'
            break
        fi
        if [ "$ANS" == 'y' -o "$ANS" == 'Y' ]; then
            rm -R "$TEST_DIR/env"
            ANS=
            break
        fi
    done
fi

# Create test environment:
if [ -z "$ANS" ]; then
    virtualenv --system-site-packages "$TEST_DIR/env"
    . "$TEST_DIR/env/bin/activate"
    pip install --upgrade pip
    pip install selenium
    deactivate
fi

# Get and install Gecko driver:
if [ -z "$ANS" ]; then
    if [ -f 'gecko-version.local' ]; then
        GECKO_VERSION=$(cat 'gecko-version.local')
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
    mv geckodriver "$TEST_DIR/env/bin"
    rm "$GECKO_NAME"
fi

    
# Deletes exisiting profiles:
ANS=
if [ $(ls "$PROFILES_DIR" | wc -l) -gt 0 ]; then
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
            break
        fi
    done
fi

# Create new profiles:
if [ -z "$ANS" ]; then
    create_profile "test"
    create_profile "1200x900" 1200 900
    create_profile "1024x768" 1024 768
    create_profile "1023x768" 1023 768
    create_profile  "724x500"  724 500
    create_profile  "723x500"  723 500
    create_profile  "403x200"  403 200
    create_profile  "402x200"  402 200
fi

# Delete old test data:
ANS=
if [ -d "$TEST_DIR/testdata" ]; then
    echo "Folder $TEST_DIR/testdata already exists. Do you want to delete it (y/N)?"
    while true; do
        read ANS
        if [ -z "$ANS" -o "$ANS" == 'n' -o "$ANS" == 'N' ]; then
            echo "OK, skipping"
            ANS='skip'
            break
        fi
        if [ "$ANS" == 'y' -o "$ANS" == 'Y' ]; then
            rm -R "$TEST_DIR/testdata"
            ANS=
            break
        fi
    done
fi

# Create test data:
if [ -z "$ANS" ]; then
    printf "Extracting testdata ...\t\t\t\t\t\t\t"
    tar -xzf "$(dirname $0)/testdata.tar.gz"
    mv "$(dirname $0)/testdata" "$TEST_DIR" 2> /dev/null
    echo "DONE"
    printf "Setting up test environment ...\t\t\t\t\t\t"
    cp -a "$(dirname $0)/prod/img" "$TEST_DIR/testdata/"
    cp -a "$(dirname $0)/prod/js" "$TEST_DIR/testdata/"
    cp -a "$(dirname $0)/prod/style.css" "$TEST_DIR/testdata/"
    cp -a "$(dirname $0)/prod/index.html" "$TEST_DIR/testdata/"
    echo "DONE"
fi
