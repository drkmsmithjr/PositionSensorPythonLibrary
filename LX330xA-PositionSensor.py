#!/usr/bin/python
import RPi.GPIO as GPIO
import math
import time
import threading

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
IO2 = 18
IO3_AOUT = 15
IO4_DOUT = 14



class PositionSensor():

    def __init__(self,partnumber = 'LX3302A', protocal = 'SENT', pin = 'IO3'):
        
        self.partnumber = partnumber
        self.protocal = protocal
        if pin == 'IO3':
            self.pins = IO3_AOUT
        elif pin == 'IO2':
            self.pins = IO2
		
        self.data = 0
        self.PWMFreq = 0
        self.Arg1 = self.pins
        self.Arg2 = 0
		
        #setup GPIO to use the BCM numbering.  The adufruit extension shows the BCM 
        # BCM numbering
        GPIO.setmode(GPIO.BCM)   
        # set warnings false to avoid generating errors when the channel was set already
        GPIO.setwarnings(False)		
        # Set all GPIO pins to inputs.     
        GPIO.setup(IO1,GPIO.IN)
        GPIO.setup(IO2,GPIO.IN)
        GPIO.setup(IO3_AOUT,GPIO.IN)
        GPIO.setup(IO4_DOUT,GPIO.IN)
         		
        # The arguments will be the outputs that are utilized by the IC
        
        # start the thread to sample output depending on the output 
        if protocal == 'SENT':
            self.OutputSampleThread = threading.Thread(target = self.SENTSample, args = (self.Arg1,self.Arg2))
        elif protocal == 'PWM':
            self.OutputSampleThread = threading.Thread(target = self.PWMSample, args = (self.Arg1,self.Arg2))
        self.OutputSampleThread.daemon = True 
        self.OutputSampleThread.start()
              

    def SENTSample(self,Arg1,Arg2):
        
        # this will run in a loop and sample the SENT path 
        while True:
           # read the Status nibble
		   # read three data nibbles - 12bit data
		   # ready three data nibbles - 12bit data repeated
		   # read the CRC code 
            print("inside SENTPWM")
		   
   
    def PWMSample(self,Arg1,Arg2):
        
        # this will run in a loop and sample the PWM path
        # the algorithm will read leading edge PWM.  the
        # states:   The output is high,  wait until the output goes low.
        # states:   the output is low, wait until the output goes high.
        # An error occurs if delay too much that we had to break out of loop.   		
        INPUT = GPIO.input(Arg1)
        StartPeriod = time.time()
        PWMDuty = 0
        PWMFreq = 0
        while True:
            INPUT = GPIO.input(Arg1)
            # read the PWM signal
            while INPUT == False:
                INPUT = GPIO.input(Arg1)
		    # measure time and calculate the Period.
            PulseRiseEdge = time.time()
			
            while INPUT == True:
                INPUT = GPIO.input(Arg1)
            PulseFallEdge = time.time()				
			
            StopPeriod = PulseFallEdge
            ClockPeriod = StopPeriod - StartPeriod
            StartPeriod = StopPeriod
			#clock frequency to nearest Hertz
            self.PWMFreq = math.floor(1/ClockPeriod+.5)
						
            PulseWidth = PulseFallEdge - PulseRiseEdge
			# duty ratio with two digits
            self.data = (math.floor(PulseWidth/ClockPeriod*10000+.5))/100.0			
		                
    def Get_Data(self):
         
        return self.data 

    def Get_Freq(self):
         
        return self.PWMFreq 		
		
		
  
if __name__ == "__main__":
        print "hello world"
        x = PositionSensor('LX3302A','PWM','IO2')
        
        while True:
            print("Duty Ration: %s    Frequency: %s" % (int(x.Get_Data()),int(x.Get_Freq())))
            time.sleep(.01)
           