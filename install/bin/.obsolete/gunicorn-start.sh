#!/bin/bash
# Start API Gateway with Gunicorn (for development testing)
cd /workspace/api
gunicorn -c gunicorn_conf.py main:app
