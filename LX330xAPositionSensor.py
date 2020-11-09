#!/usr/bin/python
import RPi.GPIO as GPIO
import math
import time
import threading
import sys
import statistics as st

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
IO3_AOUT = 24
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
        self.status = 0
        self.chan1 = 0
        self.chan2 = 0
        self.chan3 = 0
        self.chan4 = 0
        self.chan5 = 0
        self.chan6 = 0
        self.crc = 0
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
            print("SENT protocol")
            self.OutputSampleThread = threading.Thread(target = self.SENTSample, args = (self.Arg1,self.Arg2))
        elif protocal == 'PWM':
            print("PWM protocol")
            self.OutputSampleThread = threading.Thread(target = self.PWMSample, args = (self.Arg1,self.Arg2))
        self.OutputSampleThread.daemon = True
        self.OutputSampleThread.start()


    def SENTSample(self,Arg1,Arg2):
        # at this time, the SENT solution does not seem to work
        # this will run in a loop and sample the SENT path
        while True:
           # read the Status nibble
           # measure the pulse width of each period
           self.data = self.DetectNibble(Arg1)
           while self.data > 40000000:
              # get status nibble
              self.status = self.DetectNibble(Arg1)
              self.chan1  = self.DetectNibble(Arg1)
              self.chan2  = self.DetectNibble(Arg1)
              self.chan3  = self.DetectNibble(Arg1)
              self.chan4  = self.DetectNibble(Arg1)
              self.chan5  = self.DetectNibble(Arg1)
              self.chan6  = self.DetectNibble(Arg1)
              self.crc    = self.DetectNibble(Arg1)

    def PWMSample(self,Arg1,Arg2):

        # this will run in a loop and sample the PWM path
        # the algorithm will read leading edge PWM.  the
        # states:   The output is high,  wait until the output goes low.
        # states:   the output is low, wait until the output goes high.
        # An error occurs if delay too much that we had to break out of loop.

        # inplemented a LPF for the data
        # also implemented an outlier filter for erroneous data
        INPUT = GPIO.input(Arg1)
        StartPeriod = time.time()
        PWMDuty = 0
        PWMFreq = 0


        # low pass filter taps
        LPF = [0]*100
        tempval = 0
        tempval2 = 1
        lastPWMFreq = 1
        outliers = 0.04


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
            # filtering outlier frequency data
            tempval = (math.floor(PulseWidth/ClockPeriod*10000+.5))/100.0
            if abs(1.0*self.PWMFreq/lastPWMFreq -1)< outliers:
               # filter out values great than a certain amount.
               if abs(1.0*tempval/tempval2 - 1) < outliers:
                  LPF.pop()
                  LPF.insert(0,tempval)
                  indexval = len(LPF)
                  tempval2 = 0
                  for x in LPF:
                     tempval2 += (1.0/indexval)*x
                  self.data = tempval2
            tempval2 = tempval
            lastPWMFreq = self.PWMFreq
               # duty ratio with two digits
            #tempval = (math.floor(PulseWidth/ClockPeriod*10000+.5))/100.0


    def Get_Data(self):
        return self.data

    def Get_Freq(self):
        return self.PWMFreq

    def Quit(self):
        #self.OutputSampleThread.join()
        print("Inside Quit")

    def DetectNibble(self,Arg1,ClockTick = .000024):
        # this will detect the NibbleType
        # we assume that the input is zero voltage
        # ensure we are not within one period

        PulseFallEdge = []
        PulseRiseEdge = []

        NumInterations = 15

        # avoiding a partial period
        INPUT = GPIO.input(Arg1)
        if INPUT == False:
            while INPUT == False:
               INPUT = GPIO.input(Arg1)
            while INPUT == True:
               INPUT = GPIO.input(Arg1)
            while INPUT == False:
               INPUT = GPIO.input(Arg1)
            while INPUT == True:
               INPUT = GPIO.input(Arg1)
        else:
            while INPUT == True:
               INPUT = GPIO.input(Arg1)
            while INPUT == False:
               INPUT = GPIO.input(Arg1)
            while INPUT == True:
               INPUT = GPIO.input(Arg1)

        pulsewidth = 0
        #searching for the first sync pulse
        while pulsewidth < (ClockTick*40) or pulsewidth > (ClockTick*50):
            time1 = time.clock()
            #look for rising edge
            while INPUT == False:
                INPUT = GPIO.input(Arg1)
            #look for falling edge
            while INPUT == True:
                INPUT = GPIO.input(Arg1)
            time2 = time.clock()
            pulsewidth = time2-time1

        PulseFallEdge.append(time2)
        #capturing data
        for x in range (0,9*NumInterations):
           #look for risign edge
           while INPUT == False:
               INPUT = GPIO.input(Arg1)
           #PulseRiseEdge.append(time.clock())
           #look for falling edge
           while INPUT == True:
               INPUT = GPIO.input(Arg1)
           PulseFallEdge.append(time.clock())
        #Positive_Value = math.floor((PulseFallEdgeTwo - PulseRiseEdgeOne)/ClockTick+0.5)
        #Period_Value = math.floor((PulseFallEdgeTwo - PulseFallEdgeOne)/ClockTick+0.5)
        period = []
        pulse = []
        status = []
        data1 = []
        data2 = []
        data3 = []
        data4 = []
        data5 = []
        data6 = []
        CRC = []
        #finding all the periodss
        for x in range (0,9*NumInterations):
            y = math.floor(((PulseFallEdge[x+1]-PulseFallEdge[x])/ClockTick)*100)/100.0
            period.append(y)
            if x%9 == 0:
                status.append(y)
            if x%9 == 1:
                data1.append(y)
            if x%9 == 2:
                data2.append(y)
            if x%9 == 3:
                data3.append(y)
            if x%9 == 4:
                data4.append(y)
            if x%9 == 5:
                data5.append(y)
            if x%9 == 6:
                data6.append(y)
            if x%9 == 7:
                CRC.append(y)
            if x%9 == 8:
                pulse.append(y)
            #pulse.append((PulseFallEdge[x+1]-PulseRiseEdge[x])/ClockTick)
        #print("PulseFallEdge: %s" % PulseFallEdge)
        #print("PulseRiseEdge: %s" % PulseRiseEdge)
        #print("pulse:         %s" % pulse)
        if len(pulse) > 0:
           syncpulse = st.median(pulse)
           tick = 51.0 / 56
           statuspulse = math.floor((st.median(status)-12*tick)*100+.5)/100
           data1pulse =  math.floor((st.median(data1)-12*tick)*100+.5)/100
           data2pulse =  math.floor((st.median(data2)-12*tick)*100+.5)/100
           data3pulse = st.median(data3)-12*tick
           data4pulse = st.median(data4)-12*tick
           data5pulse = st.median(data5)-12*tick
           data6pulse = st.median(data6)-12*tick
           CRCpulse = st.median(CRC)-12*tick
           print("pulse:  %s %s  " % (syncpulse, pulse))
           print("status: %s %s  " % (statuspulse, status))
           print("data1:  %s %s  " % (data1pulse, data1))
           print("data2:  %s %s  " % (data2pulse, data2))
           print("data3:  %s %s  " % (data3pulse, data3))
           print("data4:  %s %s  " % (data4pulse, data4))
           print("data5:  %s %s  " % (data5pulse, data5))
           print("data6:  %s %s  " % (data6pulse, data6))
           print("  CRC:  %s %s  " % (CRCpulse, CRC))


        #self.data = Value
        return 120


Type = 'PWM'

if __name__ == "__main__":

   if len(sys.argv) >= 2:
      if sys.argv[1] == 'SENT':
         x = PositionSensor('LX3302A','SENT','IO2')
         Type = 'SENT'
      else:
         x = PositionSensor('LX3302A','PWM','IO3')
         Type = 'PWM'
   else:
      x = PositionSensor('LX3302A','PWM','IO3')
      Type = 'PWM'

   print "hello world"

   while True:
      if Type == 'SENT':
         print("Start Lenth: %s Status: %s Data1: %s-%s-%s Data2: %s-%s-%s CRC: %s " % (int(x.Get_Data()),int(x.status),int(x.chan1),int(x.chan2),int(x.chan3),int(x.chan4),int(x.chan5),int(x.chan6),int(x.crc)))
      else:
         print("Duty Ration: %s    Frequency: %s" % (int(x.Get_Data()),int(x.Get_Freq())))
      time.sleep(5)
