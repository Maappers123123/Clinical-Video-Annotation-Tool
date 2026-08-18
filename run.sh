#!/bin/bash
# Setup + launcher for macOS and Linux.
#

VENV_DIR=".venv"

echo "Checking environment..."

# ----------------------------------------------------------------------
# Locate a working Python 3 interpreter.
# ----------------------------------------------------------------------

PY_CMD=""
for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
        # Confirm it's actually Python 3, not a Python 2 leftover.
        version_output="$("$candidate" --version 2>&1)"
        if echo "$version_output" | grep -qE "Python 3"; then
            PY_CMD="$candidate"
            break
        fi
    fi
done

if [ -z "$PY_CMD" ]; then
    echo ""
    echo "============================================================"
    echo "  Python 3 was not found on this computer."
    echo "============================================================"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  Install it from https://www.python.org/downloads"
        echo "  (the macOS installer .pkg), then run this script again."
        echo ""
        echo "  If a popup previously asked you to install 'Command"
        echo "  Line Tools', accept that first, then try again too."
    else
        echo "  Install it via your package manager, e.g.:"
        echo "      sudo apt install python3 python3-venv python3-pip"
        echo "  (Debian/Ubuntu) or the equivalent for your distribution."
    fi
    echo "============================================================"
    echo ""
    read -n 1 -s -r -p "Press any key to exit..."
    echo ""
    exit 1
fi

echo "Using Python: $PY_CMD ($($PY_CMD --version 2>&1))"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    venv_error="$("$PY_CMD" -m venv "$VENV_DIR" 2>&1)"
    if [ $? -ne 0 ]; then
        echo ""
        echo "Failed to create virtual environment:"
        echo "$venv_error"
        if echo "$venv_error" | grep -qi "ensurepip"; then
            echo ""
            echo "This usually means the Python venv module isn't installed."
            echo "On Debian/Ubuntu, fix it with:"
            echo "    sudo apt install python3-venv"
            echo "then run this script again."
        fi
        read -n 1 -s -r -p "Press any key to exit..."
        echo ""
        exit 1
    fi
fi

source "$VENV_DIR/bin/activate"
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    read -n 1 -s -r -p "Press any key to exit..."
    echo ""
    exit 1
fi

# From here on, "python"/"pip" refer to the venv's own interpreter, not
# the system one located above.

echo "Ensuring dependencies are installed..."
python -m pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo "Pip upgrade failed."
    read -n 1 -s -r -p "Press any key to exit..."
    echo ""
    exit 1
fi

python -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Dependency installation failed."
    read -n 1 -s -r -p "Press any key to exit..."
    echo ""
    exit 1
fi

echo "Launching Clinical Video Annotation Tool..."
python scorer.py
