#!/usr/bin/env python3
# Author: Andreas Spiess
# CoAuthor: Paulo da Silva
# Version 1.0.1 20170502 -> shutdown sleep wrong with 100 seconds
#                           and  if ( flagShutDown == True added and GPIO.input(batterySensPin)==0 ):
# Version 1.0.2 20170522 -> Changed if (  GPIO.input(batterySensPin)==1 : to
#                            if ( flagShutDown == False and GPIO.input(batterySensPin)==1 ):
# Version 1.0.3 20170538 -> Added flagwritelog, flagfanON.

import os
import time
from time import sleep
import signal
import sys
import RPi.GPIO as GPIO
import logging
import logging.handlers
import signal
import sys


my_logger = logging.getLogger('PiPowerLogger')
my_logger.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address = '/dev/log')
my_logger.addHandler(handler)

flagfan        = False
flagShutDown   = False
maxTMP         = 38
fanpin         = 17 # The pin ID, edit here to change it
batterySensPin = 18
flagwritelog   = 0
flagfanON      = 0

def handleFan():
    global flagfan
    global flagfanON
    CPU_temp = float(getCPUtemperature())
    if CPU_temp>maxTMP and flagfanON == 0:
        fanON()
        my_logger.critical("pipower: fan on cpu temp:")
        flagfan = True
    if ( CPU_temp < maxTMP-3 and flagfanON == 1 ):
	if ( flagfan == True ):
            my_logger.critical("pipower: fan off cpu temp:")
            flagfan = False
        fanOFF()
    return()

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(fanpin, GPIO.OUT)
    GPIO.setup(batterySensPin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
    return()

def fanOFF():
    global flagfanON
    GPIO.output(fanpin, False)
    flagfanON = 0
    return()

def fanON():
    global flagfanON
    GPIO.output(fanpin, True)
    flagfanON = 1
    return()

def getCPUtemperature():
    global flagwritelog
    res = os.popen('vcgencmd measure_temp').readline()
    temp =(res.replace("temp=","").replace("'C\n",""))
    flagwritelog = flagwritelog + 1
    ftmp = flagwritelog % 20
    if ( ftmp == 0 ):
        print("temp is {0}".format(temp)) #Uncomment here for testing
        my_logger.critical("pipower: {0}".format(temp))
	flagwritelog = 0
    return temp

def Shutdown(action):  
    fanOFF()
    if( action == 1 ):
        os.system("sudo shutdown -h 1")
        my_logger.critical("pipower: shutdown requested:")
    else:
        os.system("sudo shutdown -c")
        my_logger.critical("pipower: shutdown canceled:")
    sleep(10)
    return()

def signal_handler(signal, frame):
        print('You ask me for... I am going out.!')
        my_logger.critical("pipower:You ask me for... I am going out.! ")
        sys.exit(0)
try:
    #print("My raspberry pi pimped...")
    my_logger.debug('pipower: has been initiated')
    total=0
    flagfan = False
    setup() 
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    #signal.pause()
    my_logger.debug('pipower: signal has been captured')
    fanOFF()
    while True:
        sleep(1)
	handleFan()
        if ( flagShutDown == False and GPIO.input(batterySensPin)==0 ):
		print("Pin power off was turned to on")
                my_logger.critical('pipower: Pin power off was turned to on')
		Shutdown(1)
		flagShutDown = True
        if ( flagShutDown == True and GPIO.input(batterySensPin)==1 ):
                my_logger.critical('pipower: Pin power off was turned to off')
		print("Pin power off was turned to off")
		Shutdown(0)
                flagShutDown = False
	

except KeyboardInterrupt: # trap a CTRL+C keyboard interrupt 
    fanOFF()

