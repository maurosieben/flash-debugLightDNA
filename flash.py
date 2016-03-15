import sys
import random
import os, subprocess
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QThread
from main_flash import Ui_Dialog
import time

count = 0
red ="\033[1;31;40m"
green = "\033[1;32;40m"
normal = "\033[0;37;40m"

prog_dir = os.path.dirname(os.path.abspath(__file__))

class MyDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.start.clicked.connect(self.start)
        self.RED = QtGui.QColor(255,0,0)
        self.GRAY = QtGui.QColor(170,170,255)
        self.GREEN = QtGui.QColor(0,255,0)
        self.colorArray = [self.RED, self.GRAY, self.GREEN]
        # array with esp leds
        self.ledESP_array = [self.ui.led_esp1, self.ui.led_esp2, self.ui.led_esp3, self.ui.led_esp4, self.ui.led_esp5, self.ui.led_esp6, self.ui.led_esp7, self.ui.led_esp8]
        # array with msp leds
        self.ledMSP_array = [self.ui.led_msp1, self.ui.led_msp2, self.ui.led_msp3, self.ui.led_msp4, self.ui.led_msp5, self.ui.led_msp6, self.ui.led_msp7, self.ui.led_msp8]

        self.tpool =[]
        self.usbarray = []
    
    #function to start process
    def start(self):
        global count
        if count != 0:
            pass
            #clear arrays
            del self.tpool[:]
            del self.usbarray[:]
            #clean screen
            self.clean_all()
            self.getUSB()
            self.createThreads()
        else:
            #start process
            self.getUSB()
            self.createThreads()
            count = 1

    #change LED status
    def blink(self, tid, color, dev):
        if dev is True:
            self.ledESP_array[tid-1].setColor(self.colorArray[color])
            self.ledESP_array[tid-1].on()
        else:
            self.ledMSP_array[tid-1].setColor(self.colorArray[color])
            self.ledMSP_array[tid-1].on()
            

    #get attached LightDNA devices
    def getUSB(self):
        pss = subprocess.Popen("ls /dev/ttyLDNA* > result.txt",shell=True)
        time.sleep(0.2)
        f = open("%s/result.txt" %prog_dir, 'r')
        lines = f.readlines()
        f.close()
        for line in lines:
            usb = line.split("\n")
            # Putting devices on an array 
            if (usb[0] != "/dev/ttyLDNAC1") and (usb[0] != "/dev/ttyLDNAC2"):
                self.usbarray.append(usb[0])

    def createThreads(self):
        if len(self.usbarray) != 0:
            for iten in self.usbarray:
                tdid=iten.split('A')
                tdid=int(tdid[1])
                # creating and appending regular threads
                self.tpool.append(Threadled(tdid, iten, 0))
                # Connecting the signal which changes LED status
                self.connect(self.tpool[len(self.tpool)-1], QtCore.SIGNAL("blink"), self.blink)
                self.tpool[len(self.tpool)-1].start()

    #change all leds to gray and turn them off
    def clean_all(self):
        for iten in range(len(self.ledESP_array)):
            self.ledESP_array[iten].setColor(self.GRAY)
            self.ledMSP_array[iten].setColor(self.GRAY)
            self.ledESP_array[iten].off()
            self.ledMSP_array[iten].off()

class Threadled(QThread):
    def __init__(self,tid,name,counter):
        QThread.__init__(self)
        self.tid = tid
        self.name = name
        self.counter = counter
        
    def __del__(self):
        self.wait()

    def run(self):
        print "%sStarting %s\n" %(normal, self.name)
        self.emit(QtCore.SIGNAL("blink"), self.tid, 1, True)
        self.flashESP()
        self.emit(QtCore.SIGNAL("blink"), self.tid, 1, False)
        self.flashMSP()
        return
    
    def flashESP(self):        
        self.process = subprocess.Popen("sh %s/firmware/program.sh %s &" %(prog_dir, self.name), stderr= subprocess.PIPE,stdout= subprocess.PIPE,shell=True)
        
        # get standard and error output in a variable
        out, err = self.process.communicate()

        # checks if the process did well 
        if err:
            self.counter += 1
            # if not it tries again twice
            if self.counter < 3:
                print "%sThe flashing process on %s has failled" %(red,self.name)
                print "%sWe are going to the attempt number %d\n" %(normal, self.counter+1)
                # Should call function to reset ESP here "W0001-0000/1"
                self.flashESP()
            else:
                print "%sWe are out of attempts on %s for ESP\n" %(red,self.name)
                self.emit(QtCore.SIGNAL("blink"), self.tid, 0, True)
                self.counter = 0 
        else:
            print "%sThe ESP flashing process on dev %s has gone well\n" %(green,self.name)
            self.emit(QtCore.SIGNAL("blink"), self.tid, 2, True)
            self.counter = 0 
                    
    def flashMSP(self):            
        msp_status = bool(random.getrandbits(1))
        time.sleep(3)
        if msp_status is True: 
            self.counter += 1
            if self.counter < 3:
                self.flashMSP()
            else:
                print "%sWe are out of attempts on %s for MSP\n" %(red,self.name)
                self.emit(QtCore.SIGNAL("blink"), self.tid, 0, False)
                self.counter = 0 

        else:
            self.emit(QtCore.SIGNAL("blink"), self.tid, 2, False)
            print "%sThe MSP flashing process on dev %s has gone well\n" %(green,self.name)
            self.counter = 0 

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MyDialog()
    myapp.show()
    sys.exit(app.exec_())
