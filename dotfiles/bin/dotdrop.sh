#!/usr/bin/env zsh

#
# {{@@ header() @@}}
#

eval $(grep -v "^#" {{@@ env['HOME'] @@}}/.files/.env.public)
export PYENV_VERSION="dotdrop"
{{@@ env['HOME'] @@}}/.files/dotdrop.sh ${@}
