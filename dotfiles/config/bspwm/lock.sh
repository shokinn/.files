#!/bin/bash

#
# {{@@ header() @@}}
#

# Set lock screen background
lockscreen="{{@@ env['HOME'] @@}}/.config/bspwm/lock.png"

# Lock all KeePass databases
keepass --lock-all

# Lock the screen
i3lock -u -i $lockscreen
