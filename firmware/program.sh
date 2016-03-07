#! /bin/bash
prog_dir=$(dirname $0)

cd $prog_dir 

python esptool.py -p $1 write_flash 0x00000 0x00000.bin 0x40000 0x40000.bin

cd -
