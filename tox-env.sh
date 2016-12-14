#!/bin/bash

if [ ! -f "environ.py"  ]; then
  cp environ.py.dist environ.py
fi

pip install `tail requirements.txt -n+2`
