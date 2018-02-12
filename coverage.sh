#! /usr/bin/env bash

coverage erase
coverage run --source=. --omit=*/setup.py -m unittest discover -s tests/
coverage xml
python-codacy-coverage -r coverage.xml
