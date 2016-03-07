#!/usr/bin/python
import os
import sys
import threading
import time
import subprocess

prog_dir = os.path.dirname(os.path.abspath(__file__))
usbarray = []
tpool = []

class myThread (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.process = 0
        self.status = 0
    def run(self):
        print "Starting " + self.name
        # Get lock to synchronize threads
        threadLock.acquire()
        print_time(self.name, 0.1, 3)
        #self.process = subprocess.Popen("sh %s/firmware/program.sh %s > log%s.txt 2>&1 &" %(prog_dir, self.name, self.threadID),shell=True)
        self.process = subprocess.Popen("sh %s/firmware/program.sh %s &" %(prog_dir, self.name), stderr= subprocess.PIPE,stdout= subprocess.PIPE,shell=True)
        # Release so other threads can run
        threadLock.release()
        # get standard and error output in a variable
        out, err = self.process.communicate()
        print self.process.pid
        self.status = self.process.returncode  
        print self.status
        # checks if the process did well 
        if err:
            self.counter += 1
            # if not it tries again twice
            if self.counter < 3:
                print "We are going to the atempt number %d" %(self.counter+1)
                # Should call function to reset ESP here "W0001-0000/1"
                self.run()
        else:
            print "The flashing process on dev %s has gone well" %self.name
        
def print_time(threadName, delay, counter):
    time.sleep(delay)
    print "%s: %s" % (threadName, time.ctime(time.time()))

# list all devices connected and add it to the array
def getUSB():
    global usbarray 
    pss = subprocess.Popen("sh %s/getUSB.sh " %prog_dir ,shell=True)
    f = open("%s/result.txt" %prog_dir, 'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        usb = line.split("\n")
        usbarray.append(usb[0])
        
# Create threads putting it on a array
def createThreads():
    count = 0
    for iten in usbarray:
         tpool.append(myThread(count, iten, 0))
         count += 1

# Start threads 
def startThreads(threads):
    for t in threads:
        t.start()

threadLock = threading.Lock()
getUSB()
createThreads()
startThreads(tpool)

for t in tpool:
    t.join()

print "Exiting Main Thread"
