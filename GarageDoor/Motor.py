import tkinter as tk
import RPi.GPIO as GPIO
import time
import math

MIN_COUNT = 0
MAX_COUNT = 512 * 3.8
MAX_PERCENT = 100
MS = 3 # the delay can not be less than 3ms, otherwise it will exceed speed limit of the motor

motorPins = (12, 16, 18, 22)    # define pins connected to four phase ABCD of stepper motor
CCWStep = (0x01,0x02,0x04,0x08) # define power supply order for rotating anticlockwise 
CWStep = (0x08,0x04,0x02,0x01)  # define power supply order for rotating clockwise

class Motor(tk.Label):
    def __init__(self, *args, **kwargs):
        tk.Label.__init__(self, *args, **kwargs)
        self._cycle = 0
        self._direction = 0
        self._rotation_id = None

    def update(self):
        self.config(text=str(round(self._cycle * 100 / MAX_COUNT, 1)))
        self.after(1, self.update)

    def get(self):
        return round(self._cycle * 100 / MAX_COUNT, 1)
    
    def set_cycle(self, value):
        self._cycle = value

    def get_cycle(self):
        return self._cycle

    # as for four phase stepping motor, four steps is a cycle. the function is used to drive the stepping motor clockwise or anticlockwise to take four steps    
    def moveOneCycle(self):    
        for j in range(0,4,1):      # cycle for power supply order
            for i in range(0,4,1):  # assign to each pin
                if (self._direction == 1):# power supply order clockwise
                    GPIO.output(motorPins[i],((CCWStep[j] == 1<<i) and GPIO.HIGH or GPIO.LOW))
                elif (self._direction == -1) :              # power supply order anticlockwise
                    GPIO.output(motorPins[i],((CWStep[j] == 1<<i) and GPIO.HIGH or GPIO.LOW))
            time.sleep(MS * 0.001)  

    # continuous rotation function, the parameter steps specifies the rotation cycles, every four steps is a cycle
    def moveSteps(self, direction, max_count, min_count):

        if direction == self._direction + 2 or direction == self._direction - 2:
            self._direction = 0
            self.after_cancel(self._rotation_id)

        if direction != self._direction:
            self._direction = direction

        if (self._cycle >= max_count and direction == 1) or (self._cycle <= min_count and direction == -1):
            self._direction = 0
            if self._rotation_id:
                self.after_cancel(self._rotation_id)
            return


        self.moveOneCycle()
        self._cycle += self._direction

        if self._cycle >= max_count or self._cycle <= min_count:
            self._direction = 0
            self.after_cancel(self._rotation_id)
            return

        self._rotation_id = self.after(1, self.moveSteps, self._direction, max_count, min_count)

    def start(self, direction, max_count=MAX_PERCENT, min_count=MIN_COUNT):
        max_count = max_count * MAX_COUNT / 100
        min_count = min_count * MAX_COUNT / 100
        self.moveSteps(direction, max_count, min_count)

    def stop(self):
        self._direction = 0
        self.after_cancel(self._rotation_id)