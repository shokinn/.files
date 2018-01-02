#
# {{@@ env['dotdrop_warning'] @@}}
#

#!/bin/bash

# Set lock screen background
lockscreen="$HOME/.config/bspwm/lock.png"

# Lock all KeePass databases
keepass --lock-all

# Lock the screen
i3lock -u -i $lockscreen
