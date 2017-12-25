#!/usr/bin/env bash
#
# {{@@ env['dotdrop_warning'] @@}}
#

load=$(uptime | grep -ohe 'load average[s:][: ].*' | sed 's/,//g' | awk '{print $3" "$4" "$5}')

echo -n $load
