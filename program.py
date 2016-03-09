#!/usr/bin/python
import os
import sys
import threading
import time
import subprocess

red ="\033[1;31;40m"
green = "\033[1;32;40m"
normal = "\033[0;37;40m"

prog_dir = os.path.dirname(os.path.abspath(__file__))
usbarray = []
tpool = []
statusv = ['#', '#', '#', '#', '#', '#','#','#'] 
died  = False

class myThread (threading.Thread):
    def __init__(self, threadID, name, counter, status):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.process = 0
        self.status = status
        statusv.insert(self.threadID,self.status)

    def run(self):
        global statusv
        print "%sStarting %s\n" %(normal, self.name)

        # Get lock to synchronize threads
        threadLock.acquire()
        
        #print_time(self.name, 0.1, 3)
        #self.process = subprocess.Popen("sh %s/firmware/program.sh %s > log%s.txt 2>&1 &" %(prog_dir, self.name, self.threadID),shell=True)
        self.process = subprocess.Popen("sh %s/firmware/program.sh %s &" %(prog_dir, self.name), stderr= subprocess.PIPE,stdout= subprocess.PIPE,shell=True)

        # Release so other threads can run
        threadLock.release()

        # get standard and error output in a variable
        out, err = self.process.communicate()

        # checks if the process did well 
        if err:
            self.counter += 1
            self.status = 'x'
            statusv.insert(self.threadID,self.status)
            
            # if not it tries again twice
            if self.counter < 3:
                print "%sThe flashing process on %s has failled" %(red,self.name)
                print "%sWe are going to the attempt number %d\n" %(normal, self.counter+1)
                # Should call function to reset ESP here "W0001-0000/1"
                self.run()
            else:
                print "%sWe are out of attempts on %s\n" %(red,self.name)
        else:
            self.status = 'v' 
            statusv.insert(self.threadID,'v')
            print "%sThe flashing process on dev %s has gone well\n" %(green,self.name)
"""
class myPthread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        global statusv,tpool,died
        threadLock.acquire()
        #print_status(statusv)
        threadLock.release()
        if died is False:
            self.run(


# prints boards status on screen. '#' = undefined, 'o' = in process, 'x' has failled, 'v' = passed
def print_status(statusv):
    buf =  "[%s %s %s %s %s %s %s %s]" %(statusv[0], statusv[1],statusv[2], statusv[3], statusv[4], statusv[5], statusv[6], statusv[7])
    os.system('clear') 
    print "%s" %buf
    time.sleep(0.5)

"""

def print_time(threadName, delay, counter):
    time.sleep(delay)
    print "%s: %s" % (threadName, time.ctime(time.time()))

# list all devices connected and add it to the array
def getUSB():
    global usbarray 
    pss = subprocess.Popen("sh %s/getUSB.sh " %prog_dir ,shell=True)
    time.sleep(0.1)
    f = open("%s/result.txt" %prog_dir, 'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        usb = line.split("\n")
        # Putting devices on array less the controllers one
        if (usb[0] != "/dev/ttyLDNAC1") and (usb[0] != "/dev/ttyLDNAC2"):
            usbarray.append(usb[0])
        
# Create threads putting it on a array
def createThreads():
    global statusv
    if len(usbarray) != 0:
        for iten in usbarray:
            tid=iten.split('A')
            tid=int(tid[1])
            # creating and appending regular threads
            tpool.append(myThread(tid, iten, 0, 'o'))
        
# Start threads 
def startThreads(threads):
    if len(threads) != 0:
        for t in threads:
            t.start()
        
threadLock = threading.Lock()
getUSB()
createThreads()
startThreads(tpool)

if len(tpool) != 0:
    for t in tpool:
        t.join()
    died = True

print "%sExiting Main Thread" %normal
