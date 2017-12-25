#!/usr/bin/env sh
#
# {{@@ env['dotdrop_warning'] @@}}
#

# Terminate already running bar instances
killall -q polybar
killall -q refresh_bar_usb_nic.sh

# Wait until the processes have been shut down
while pgrep -u $UID -x polybar >/dev/null; do sleep 1; done

# Launch bar1 and bar2
polybar -r -q 9560-top &
polybar -r -q 9560-bottom &
$HOME/.config/polybar/refresh_bar_usb_nic.sh &
