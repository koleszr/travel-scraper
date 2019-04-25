#!/bin/sh

echo "Exporting environment variables..."
export FLASK_APP="app.py"
export FLASK_DEBUG=1

echo "Installing dependencies..."
pip install --trusted-host pypi.python.org -r requirements.txt --user

echo "Setting work dir to src..."
pushd ./src

echo "Starting app..."
python -m flask run -h 0.0.0.0 --port 4000
