#!/bin/bash
TARGET="$(date -j -f "%H:%M" "21:25" +%s 2>/dev/null || date -d "today 21:25" +%s)"
START=$(date +%s)
while true; do
  NOW=$(date +%s)
  REMAINING=$((TARGET - NOW))
  if [ $REMAINING -le 0 ]; then
    echo "[TIMER] DONE at $(date '+%H:%M:%S') (target was 9:25 PM CDT / 10:25 PM EST)"
    break
  fi
  MIN=$((REMAINING / 60))
  SEC=$((REMAINING % 60))
  printf "[TIMER] %02d:%02d remaining at %s (target 21:25 CDT / 22:25 EST)\n" $MIN $SEC "$(date '+%H:%M:%S')"
  sleep 60
done
