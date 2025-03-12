#!/bin/bash
# Enable swap to prevent crashes due to low memory
fallocate -l 1G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# Start the app
gunicorn --workers=1 --timeout 300 app:app
