#!/bin/bash

if [ ! -d "venv/"  ]; then
  virtualenv -p python3.9 venv
  source venv/bin/activate
  pip install -U pip setuptools
else
  source venv/bin/activate
fi

if [ ! -f "environ.py"  ]; then
  cp environ.py.dist environ.py
fi

pip install -r requirements.txt

./manage.py migrate
./manage.py test
