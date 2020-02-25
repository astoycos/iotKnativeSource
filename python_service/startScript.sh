#!/bin/bash

# Start the first process
python listener/listener.py &
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start my_first_process: $status"
  exit $status
fi

# Start the second process
python app/analysis.py -i 0.0.0.0 -o 8000
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start my_second_process: $status"
  exit $status
fi