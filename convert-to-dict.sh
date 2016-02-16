#!/bin/sh
name=$(basename "$1" .txt)

sed -e 's/\t/:/' -e 's/\t/ (/' -e 's/$/)/' "$1" |
  dictfmt --utf8 --allchars -s "dict.cc $name" -j "dict.cc-$name"
