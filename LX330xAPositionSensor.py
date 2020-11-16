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

# BCM GPIO pins to connect to the Sensor
IO1 = 23
IO2_DOUT = 18
IO3_AOUT = 24

class PositionSensor():

    def __init__(self,partnumber = 'LX3302A', protocol = 'SENT', pin = 'IO3'):

        # start a pi object
        pi = pigpio.pi()

        self.partnumber = partnumber
        self.protocol = protocol
        if (pin == 'IO3') or (pin == 'AOUT'):
           self.pins = IO3_AOUT
        elif (pin == 'IO2') or (pin == 'DOUT'):
           self.pins = IO2_DOUT
        elif pin == 'IO1':
           self.pins = IO1
        else:
           print("No correct pin detected... this is an error")

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
            # only return the first data
            return self.SENT.SENTData()[0]

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

   # read two outptus from the LX3302A, both IO2 and IO3 as follows:
   x = PositionSensor('LX3302A','SENT','IO2')
   y = PositionSensor('LX3302A','PWM','IO3')

   while True:
         print("Duty Ratio: %s SENT_duty: %s PWM Frequency: %s SENT: %s " % (round(y.DutyRatio(),2),(round(x.dataSENT()/4096.0*100,2)),round(y.PWMFreq(),2),x.dataSENT()))
         time.sleep(0.1)
