#!/usr/bin/env zsh

#
# {{@@ header() @@}}
#

eval $(grep -v "^#" {{@@ env['HOME'] @@}}/.files/.env.public)
{{@@ env['HOME'] @@}}/.files/dotdrop.sh ${@}
