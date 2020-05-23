#!/bin/bash

sudo -H pip3.7 install setuptools wheel tox pytest --upgrade

python3.7 setup.py sdist
python3.7 setup.py bdist_wheel

sudo -H python3.7 setup.py develop

py.test tests -x

