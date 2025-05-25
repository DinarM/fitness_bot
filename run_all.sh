#!/bin/bash
export PYTHONPATH=$(pwd)

python -m app.bots.bot &
python -m app.bots.bot2 &
wait