#!/bin/bash

set -eo pipefail

if [ "$1" == "--clean" ]; then
    rm -fR venv
fi

if [ "$(uname)" == "Darwin" ]; then
    # clang already installed
    brew install python3
elif [ "$(lsb_release -si)" == "Ubuntu" ]; then
    sudo apt-get update
    sudo apt-get install python3 clang
else
    echo "Unknown platform..."
    exit 1
fi

python3 -m venv venv
source venv/bin/activate
pip install -U pip llvmlite sly

echo
echo "Setup complete - now 'source venv/bin/activate'"
