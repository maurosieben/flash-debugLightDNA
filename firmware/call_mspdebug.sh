#! /bin/bash
prog_dir=$(dirname $0)

cd $prog_dir

mspdebug tilib "prog lightdna.elf"

cd -
