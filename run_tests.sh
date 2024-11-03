#!/bin/bash
set -e

~/.venvs/aab/bin/python -m unittest \
    test/*test.py -v --buffer --failfast
