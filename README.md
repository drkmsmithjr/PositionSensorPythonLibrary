# Position Sensor Python Library

This python library will read a Raspberry Pi GPIO pin connected
to a Microchip LX3302A or LX3301A inductive position sensor.  The filtering added to the signal reliably sample the signals but require a low bandwidth.    This is good for generic monitoring.  

## The LX3301A and LX3302A should be set to 250Hz PWM
* The real time nature of the signals require a slow PWM signal to be reliably read by the Raspberry Pi Natively.    
* The PWM signals has a 100 tap low pass filter to filter out any noise due to linux kernal sampling.    
* Connect the Sensor IO pins to the BCM GPIO pins as follows
** IO1 = 23
** IO2 = 18
** IO3_AOUT = 24
** IO4_DOUT = 14


The protocols currently working:
1. PWM
2. SENT is NOW WORKING  
