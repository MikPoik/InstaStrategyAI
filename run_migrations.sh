#!/bin/bash
export FLASK_APP=main.py
flask db upgrade
