#!/bin/bash
if ! /sbin/ifconfig wlan0 | grep -q "inet addr:" ; then
        echo "Reconnect wlan0..."
        /sbin/ifdown wlan0 && /sbin/ifup wlan0
        sleep 1
fi
