#!/bin/bash
fallocate -l 1G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
exec gunicorn -w 1 -k uvicorn.workers.UvicornWorker app:app
