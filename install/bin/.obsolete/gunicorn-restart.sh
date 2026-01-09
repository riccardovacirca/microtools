#!/bin/bash
# Restart Gunicorn API Gateway
/workspace/project/install/bin/gunicorn-stop.sh
sleep 1
/workspace/project/install/bin/gunicorn-start.sh
