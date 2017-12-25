#!/bin/bash

######################
#
# {{@@ env['dotdrop_warning'] @@}}
#
# This script detects if an USB NIC was connected and reloads the bar
#

while true; do
	# Get PID of the bottom bar
	pid_bottom_bar=$(ps -x | awk '!/awk/ && /9560-bottom/ {print $1}')
	# 1st USB port (right)
	if [[ -z $USB_NIC1 ]]; then
		USB_NIC1=$(ip link | awk '!/awk/ && /enp0s20f0u1/ {print $2}' | cut -d":" -f1)
		if [[ -n $USB_NIC1 ]]; then
			polybar-msg -p $pid_bottom_bar cmd restart
		fi
	elif [[ -n $USB_NIC1 ]]; then
		USB_NIC1_CHECK=$(ip link | awk '!/awk/ && /enp0s20f0u1/ {print $2}' | cut -d":" -f1)
		if [[ -z $USB_NIC1_CHECK ]]; then
			unset USB_NIC1
			polybar-msg -p $pid_bottom_bar cmd restart
		fi
	fi
	
	# 2nd USB port (left)
	if [[ -z $USB_NIC2 ]]; then
		USB_NIC2=$(ip link | awk '!/awk/ && /enp0s20f0u2/ {print $2}' | cut -d":" -f1)
		if [[ -n $USB_NIC2 ]]; then
			polybar-msg -p $pid_bottom_bar cmd restart
		fi
	elif [[ -n $USB_NIC2 ]]; then
		USB_NIC2_CHECK=$(ip link | awk '!/awk/ && /enp0s20f0u2/ {print $2}' | cut -d":" -f1)
		if [[ -z $USB_NIC2_CHECK ]]; then
			unset USB_NIC2
			polybar-msg -p $pid_bottom_bar cmd restart
		fi
	fi
	
	sleep 5
done
