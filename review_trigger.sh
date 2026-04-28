#!/bin/bash
TARGET=$(date -j -f "%H:%M" "21:25" +%s 2>/dev/null || date -d "today 21:25" +%s)
COUNT=0
while true; do
  NOW=$(date +%s)
  REMAINING=$((TARGET - NOW))
  if [ $REMAINING -le 0 ]; then
    echo "[REVIEW] Cycle done at $(date '+%H:%M:%S')"
    break
  fi
  COUNT=$((COUNT+1))
  echo "[REVIEW-CYCLE-$COUNT] $(date '+%H:%M:%S') — please review the site at /Users/rawproductivity/apartment-hunt/index.html for visual appeal, photo coverage, broken images, missing fields. Suggest 1-2 high-impact improvements. Remaining: ${REMAINING}s"
  sleep 300  # 5 min
done
