#!/bin/bash

set -e

python -m src.names_generator.names
python -m src.passport_generator.passport
python -m src.groups_generator.groups