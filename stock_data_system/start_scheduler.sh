#!/bin/bash
# Start the stock data collection scheduler in the background

cd "$(dirname "$0")"

# Kill any existing scheduler processes
pkill -f "daily_scheduler.py"

# Start the scheduler in the background (unbuffered for immediate log updates)
nohup python3 -u daily_scheduler.py > scheduler.log 2>&1 &

# Get the process ID
PID=$!
echo $PID > scheduler.pid

echo "Stock Data Scheduler started!"
echo "Process ID: $PID"
echo "Log file: scheduler.log"
echo ""
echo "To stop the scheduler, run: ./stop_scheduler.sh"
echo "To view logs, run: tail -f scheduler.log"

