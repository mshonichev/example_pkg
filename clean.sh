#!/bin/bash

find . -name __pycache__ -type d | xargs -i{} rm -rf {}
find . -name .pytest_cache -type d | xargs -i{} rm -rf {}
find . -name "*.egg-info" -type d | xargs -i{} rm -rf {}

rm -rf .eggs
rm -rf .tox
rm -rf build
rm -rf dist
