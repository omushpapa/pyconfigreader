#! /usr/bin/env bash

coverage xml
python-codacy-coverage -r coverage.xml
