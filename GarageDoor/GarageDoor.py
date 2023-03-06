import RPi.GPIO as GPIO
import time
import math
from ADCDevice import *
from tkinter import *

from Motor import Motor

adc = ADCDevice() # Define an ADCDevice class object

motorPins = (12, 16, 18, 22)    # define pins connected to four phase ABCD of stepper motor
CCWStep = (0x01,0x02,0x04,0x08) # define power supply order for rotating anticlockwise 
CWStep = (0x08,0x04,0x02,0x01)  # define power supply order for rotating clockwise

TEMP_MIN = 20
TEMP_MAX = 35

is_automatique = False
is_manuel = False

class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master

root = Tk()
app = Window(root)

# set window title
root.wm_title("Controle porte d'aeration")

root.geometry("500x200")

root.eval('tk::PlaceWindow . center')

label_temperature = Label(root, text = "Temperature ambiante : ")
display_temperature = Label(root, text = "0")
label_celsius = Label(root, text = "°C")

label_poucentage_actuel = Label(root, text = "Ouverture actuelle : ")
motor_controller = Motor(root, text = "0")
label_pourcent_actuel = Label(root, text = "%")

label_controle = Label(root, text = "Controle : ")
label_pourcent = Label(root, text = "%")

label_max = Label(root, text = "Ouverture maximale : ")

entry_pourcent = Entry(root)
entry_pourcent.config(width=5)
entry_pourcent.insert(0, "100")

def mode_automatique():
    state_change("automatique")
    update_automatique()

def mode_manuel():
    state_change("manuel")

btn_automatique = Button(root, text = "Auto", command = mode_automatique)
btn_manuel = Button(root, text = "Manuel", command = mode_manuel)

def ouvrir_porte():
    state_change("ouvrir")
    motor_controller.start(1, get_percent())

def fermer_porte():
    state_change("fermer")
    motor_controller.start(-1)

def stop():
    state_change("manuel")
    motor_controller.stop()

btn_ouvrir = Button(root, text = "Ouvrir", command = ouvrir_porte)
btn_fermer = Button(root, text = "Fermer", command = fermer_porte)
btn_stop = Button(root, text = "Stop", command = stop)

label_temperature.grid(row = 0, column = 0, sticky = W, pady = 2)
display_temperature.grid(row = 0, column = 1, sticky = W, pady = 2)
label_celsius.grid(row = 0, column = 2, sticky = W, pady = 2)

label_controle.grid(row = 1, column = 0, sticky = W, pady = 2)

label_max.grid(row = 2, column = 0, sticky = W, pady = 2)
entry_pourcent.grid(row = 2, column = 1, sticky = W, pady = 2)
label_pourcent.grid(row = 2, column = 2, sticky = W, pady = 2)

label_poucentage_actuel.grid(row = 4, column = 0, sticky = W, pady = 2)
motor_controller.grid(row = 4, column = 1, sticky = W, pady = 2)
label_pourcent_actuel.grid(row = 4, column = 2, sticky = W, pady = 2)

btn_automatique.grid(row = 1, column = 1, sticky = W, pady = 2)
btn_manuel.grid(row = 1, column = 2, sticky = W, pady = 2)
btn_ouvrir.grid(row = 3, column = 1, sticky = W, pady = 2)
btn_fermer.grid(row = 3, column = 2, sticky = W, pady = 2)
btn_stop.grid(row = 3, column = 3, sticky = W, pady = 2)

def setup():
    GPIO.setmode(GPIO.BOARD)       # use PHYSICAL GPIO Numbering
    for pin in motorPins:
        GPIO.setup(pin,GPIO.OUT)

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

def state_change(state):
    global is_automatique
    global is_manuel
    if state == "automatique":
        is_manuel = False
        btn_automatique['state'] = 'disabled'
        btn_manuel['state'] = 'normal'
        btn_ouvrir['state'] = 'disabled'
        btn_fermer['state'] = 'disabled'
        btn_stop['state'] = 'disabled'
        entry_pourcent['state'] = 'disabled'
        is_automatique = True
    elif state == "manuel":
        is_automatique = False
        btn_automatique['state'] = 'normal'
        btn_manuel['state'] = 'disabled'
        btn_ouvrir['state'] = 'normal'
        btn_fermer['state'] = 'normal'
        btn_stop['state'] = 'disabled'
        entry_pourcent['state'] = 'normal'
        is_manuel = True
    elif state == "ouvrir":
        btn_automatique['state'] = 'disabled'
        btn_manuel['state'] = 'disabled'
        btn_ouvrir['state'] = 'disabled'
        btn_fermer['state'] = 'normal'
        btn_stop['state'] = 'normal'
        entry_pourcent['state'] = 'disabled'
        state_ouverture()
    elif state == "fermer":
        btn_automatique['state'] = 'disabled'
        btn_manuel['state'] = 'disabled'
        btn_ouvrir['state'] = 'normal'
        btn_fermer['state'] = 'disabled'
        btn_stop['state'] = 'normal'
        entry_pourcent['state'] = 'disabled'
        state_fermeture()

def state_reset():
    btn_automatique['state'] = 'normal'
    btn_manuel['state'] = 'normal'
    btn_ouvrir['state'] = 'normal'
    btn_fermer['state'] = 'normal'
    btn_stop['state'] = 'normal'
    entry_pourcent['state'] = 'normal'

def state_ouverture():
    if motor_controller.get() >= get_percent():
        btn_automatique['state'] = 'normal'
        btn_ouvrir['state'] = 'disabled'
        btn_fermer['state'] = 'normal'
        btn_stop['state'] = 'disabled'
        entry_pourcent['state'] = 'normal'
    else:
        root.after(1, state_ouverture)

def state_fermeture():
    if motor_controller.get() <= 0:
        btn_automatique['state'] = 'normal'
        btn_ouvrir['state'] = 'normal'
        btn_fermer['state'] = 'disabled'
        btn_stop['state'] = 'disabled'
        entry_pourcent['state'] = 'normal'
    else:
        root.after(1, state_fermeture)

def update():
    root.update()
    root.after(1, update) 

def get_percent():
    # check if entry_pourcent.get() is a number
    if not entry_pourcent.get().isdigit() or int(entry_pourcent.get()) > 100 or int(entry_pourcent.get()) < 0:
        return 100
    return int(entry_pourcent.get())

def update_automatique():
    if not is_automatique:
        return

    temperature = get_temperature()
    temperature = round(temperature, 1)
    percent = (temperature - TEMP_MIN) / (TEMP_MAX - TEMP_MIN) * 100
    percent = int(percent)

    if percent > 100:
        percent = 100
    elif percent < 0:
        percent = 0

    if percent > motor_controller.get():
        motor_controller.start(1, percent)

    elif percent < motor_controller.get():
        motor_controller.start(-1, 100, percent)

    root.after(1000, update_automatique) # run itself again after 1 s
    
def get_temperature():
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

def update_temperature():
    display_temperature['text'] = str(round(get_temperature(), 1))
    root.update()
    root.after(100, update_temperature) # run itself again after 10 ms

def destroy():
    adc.close()
    GPIO.cleanup()

if __name__ == '__main__':  # Program entrance
    print ('Program is starting ... ')
    setup()
    state_change("manuel")
    try:
        motor_controller.update()
        update_temperature()
        # show window
        root.mainloop()
    except KeyboardInterrupt: # Press ctrl-c to end the program.
        destroy()