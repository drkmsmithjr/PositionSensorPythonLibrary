#!/usr/bin/python

import pigpio # http://abyz.co.uk/rpi/pigpio/python.html
import read_PWM_Mark
import read_SENT

import time
#import threading
import sys

# This will define a Position Sensor Class Object
# Part numbers Supported:
# LX3301A
# LX3302A

# recognizable output protocals
# SENT
SENT = 'SENT'
# PWM
PWW = 'PWM'

# Default BCM GPIO pins to connect to the Sensor
IO1 = 23
IO2_DOUT = 25
IO3_AOUT = 24
IO4 = 12

class PositionSensor():

    def __init__(self,partnumber = 'LX3302A', protocol = 'SENT', pin = IO3_AOUT):

        # start a pi object
        pi = pigpio.pi()

        self.fault = False

        self.partnumber = partnumber
        self.protocol = protocol
        self.pins = pin
        # start the thread to sample output depending on the output
        if protocol == 'SENT':
           print("SENT protocol")
           self.SENT = read_SENT.SENTReader(pi,self.pins)
        elif protocol == 'PWM':
           print("PWM protocol")
           # start the PWM object
           self.PWM = read_PWM_Mark.reader(pi, self.pins)

    def DutyRatio(self):
        if self.protocol == 'PWM':
           return self.PWM.duty_cycle()
        else:
           return 0

    def dataSENT(self):
        if self.protocol == 'SENT':
            # sample until SENTData fault but return after 10 tries
            fault = True
            while (fault == True):
                SENTStatus, returnData, returnData2,SENTTick, SENTCrc, fault, SENTPeriod = self.SENT.SENTData()
            return returnData
        else:
            return 0

    def dataSENTEasy(self):
        # read the sent channel for the LX3302AQPW-EASY
        # this channel has position plus airgap information
        if (self.protocol == 'SENT') and (self.partnumber=='LX3302A'):
            # sample until SENTData fault but return after 10 tries
            fault = True
            while (fault == True):
                SENTStatus, returnData, returnData2,SENTTick, SENTCrc, fault, SENTPeriod = self.SENT.SENTData()
            return returnData, returnData2
        else:
            return 0, 0

    def PWMFreq(self):
        if self.protocol == 'PWM':
           return self.PWM.frequency()
        else:
           return 0

    def PWMPulse(self):
        if self.protocol == 'PWM':
           return self.PWM.pulse_width()
        else:
           return 0

    def Quit(self):
        #self.OutputSampleThread.join()
        print("Inside Quit")
        if self.protocol == 'PWM':
           self.PWM.cancel()
           pi.stop()

Type = ''

if __name__ == "__main__":

   # read two outptus from the LX3302A and connect to the BCD GPIO pin
   x = PositionSensor('LX3302A','SENT', 18)
   #y = PositionSensor('LX3302A','PWM','IO3')

   while True:
         #print("Duty Ratio: %s SENT_duty: %s PWM Frequency: %s SENT: %s " % (round(y.DutyRatio(),2),(round(x.dataSENT()/4096.0*100,2)),round(y.PWMFreq(),2),x.dataSENT()))
         #print("SENT_duty: %s SENT: %s " % ((round(x.dataSENT()/4096.0*100,2)),x.dataSENT()))
        data, airgap = x.dataSENTEasy()
        print("SENT = %s AIRGAP = %s" % (data,airgap))
        time.sleep(0.1)
