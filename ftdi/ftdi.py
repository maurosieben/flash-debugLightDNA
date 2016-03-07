# Gets the arguments pin (cbus3/cbus2) and status (on/off) and sets CBUS pins 
from ctypes import *
import sys
import subprocess 
pin = str(sys.argv[1])
state = str(sys.argv[2])
fdll = CDLL('libftdi.so')
ftdic = create_string_buffer(112)

fdll.ftdi_init(byref(ftdic))

fdll.ftdi_usb_open(byref(ftdic), 0x0403, 0x6001)

# function to set CBUS3 mode and level on FT232RL pin 14
def setCBUS3(status):
    if status == "on":
        fdll.ftdi_set_bitmode(byref(ftdic), 0x88, 0x20)
    else:
        fdll.ftdi_set_bitmode(byref(ftdic), 0x80, 0x20)
# function to set CBUS2 mode and level on FT232RL pin 13
def setCBUS2(status):
    if status == "on":
        fdll.ftdi_set_bitmode(byref(ftdic), 0x44, 0x20) 
        # first byte is to control bit direction and level (high/low) 
        #In this case it sets bit 2 as output and puts it in high levl 
        #The second byte is to set the bitbang mode, which 0x02 for CBUS

    else:
        fdll.ftdi_set_bitmode(byref(ftdic), 0x40, 0x20)

import time

if pin == "cbus3":
    #global state
    setCBUS3(state)
    #time.sleep(5)
    #setCBUS3("off")
else:
    setCBUS2(state)
    #time.sleep(5)
    #setCBUS2("off")

"""
try:
    while True:
        setCBUS3("on")
        time.sleep(1)
        setCBUS3("off")
        time.sleep(1)
except KeyboardInterrupt:
    pass
"""
# reset Bit bang mode to regular and close application
fdll.ftdi_set_bitmode(byref(ftdic), 0x0, 0x00)
fdll.ftdi_usb_close(byref(ftdic))
# restarts ftdi module and remounts usb
subprocess.call('modprobe -r ftdi_sio', shell=True)
subprocess.call('modprobe ftdi_sio vendor=0x0403 product=0x6001', shell=True)

#fdll.ftdi_deinit(byref(ftdic))
