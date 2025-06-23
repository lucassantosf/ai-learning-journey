#!/bin/bash

while true; do
  echo "Running email bot... $(date +"%Y-%m-%d %H:%M:%S")"
  python app.py
  echo "Waiting for next run... $(date +"%Y-%m-%d %H:%M:%S")"
  sleep 60
done
