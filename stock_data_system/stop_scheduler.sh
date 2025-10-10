#!/bin/bash
# Stop the stock data collection scheduler

cd "$(dirname "$0")"

if [ -f scheduler.pid ]; then
    PID=$(cat scheduler.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo "Scheduler stopped (PID: $PID)"
        rm scheduler.pid
    else
        echo "Scheduler not running (stale PID file removed)"
        rm scheduler.pid
    fi
else
    # Try to kill by process name
    pkill -f "daily_scheduler.py"
    if [ $? -eq 0 ]; then
        echo "Scheduler stopped"
    else
        echo "No scheduler process found"
    fi
fi

