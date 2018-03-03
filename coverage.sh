#! /usr/bin/env bash

tox
coverage xml
python-codacy-coverage -r coverage.xml
