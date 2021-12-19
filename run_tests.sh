#!/bin/sh

if [ -d venv ];
then
  echo "The virtual environment exists. Activating now...."
  . venv/bin/activate
else
  echo "The virtual environment DOES NOT exist. Creating one...."
  python3 -m venv venv

  echo "Activating the virtual environment...."
  . venv/bin/activate

  echo "Upgrading pip...."
  python -m pip install --upgrade pip

  echo "Installing requirements...."
  pip install -r requirements.txt
fi

echo "Running tests...."
pytest
