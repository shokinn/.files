#!/bin/bash

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"

cd $SCRIPTPATH

git submodule foreach git pull origin master
git add dotdrop
git commit -m 'update dotdrop'
git push
