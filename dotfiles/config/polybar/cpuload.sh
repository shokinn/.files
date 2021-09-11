#!/usr/bin/env bash

#
# {{@@ header() @@}}
#

load=$(uptime | grep -ohe 'load average[s:][: ].*' | sed 's/,//g' | awk '{print $3" "$4" "$5}')

echo -n $load
