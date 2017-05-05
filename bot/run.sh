#!/bin/sh
COUNTER=0

while :
do
        sleep 1
        COUNTER=`expr $COUNTER + 1`
        python35 bot.py
        now=$(date + "%T")
        echo "Self Has restarted $COUNTER times as of $now"
done
