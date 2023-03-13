import math
import RPi.GPIO as GPIO
from ADCDevice import *
from tkinter import *
import tkinter as tk

adc = ADCDevice() # Define an ADCDevice class object

class Temperature(tk.Label):
    def __init__(self, *args, **kwargs):
        tk.Label.__init__(self, *args, **kwargs)
        global adc
        if(adc.detectI2C(0x48)): # Detect the pcf8591.
            adc = PCF8591()
        elif(adc.detectI2C(0x4b)): # Detect the ads7830
            adc = ADS7830()
        else:
            print("No correct I2C address found, \n"
            "Please use command 'i2cdetect -y 1' to check the I2C address! \n"
            "Program Exit. \n")
            exit(-1)

    def get_temperature(self):
        value = adc.analogRead(0)        # read ADC value A0 pin
        voltage = value / 255.0 * 3.3        # calculate voltage
        try:
            Rt = 10 * voltage / (3.3 - voltage)    # calculate resistance value of thermistor
            if Rt == 0:
                return 0
            tempK = 1/(1/(273.15 + 25) + math.log(Rt/10)/3950.0) # calculate temperature (Kelvin)
            tempC = tempK -273.15        # calculate temperature (Celsius)
        except ZeroDivisionError:
            Rt = 0 # calculate resistance value of thermistor
            return 0

        return tempC

    def update(self):
        self.config(text=str(round(self.get_temperature(), 1)))
        self.after(500, self.update)