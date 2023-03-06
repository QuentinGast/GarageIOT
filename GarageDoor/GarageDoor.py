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

class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master

root = Tk()
app = Window(root)

def mode_automatique():
    print("Automatique")

def mode_manuel():
    print("Manuel")

# set window title
root.wm_title("Controle porte d'aeration")

root.geometry("800x300")

root.eval('tk::PlaceWindow . center')

label_temperature = Label(root, text = "Temperature ambiante : ")
display_temperature = Label(root, text = "0")
label_celsius = Label(root, text = "°C")

label_poucentage_actuel = Label(root, text = "Pourcentage d'ouverture de la porte : ")
display_pourcentage_actuel = Motor(root, text = "0")
label_pourcent_actuel = Label(root, text = "%")

label_controle = Label(root, text = "Controle : ")
label_pourcent = Label(root, text = "%")

label_moteur = Label(root, text = "Moteur : ")
label_direction = Label(root, text = "Direction : ")
label_vitesse = Label(root, text = "Vitesse : ")

entry_pourcent = Entry(root)

def ouvrir_porte():
    display_pourcentage_actuel.moveSteps(1)

def fermer_porte():
    display_pourcentage_actuel.moveSteps(-1)

def stop():
    display_pourcentage_actuel.stop()

btn_automatique = Button(root, text = "Automatique", command = mode_automatique)
btn_manuel = Button(root, text = "Manuel", command = mode_manuel)
btn_ouvrir = Button(root, text = "Ouvrir", command = ouvrir_porte)
btn_fermer = Button(root, text = "Fermer", command = fermer_porte)
btn_stop = Button(root, text = "Stop", command = stop)

label_temperature.grid(row = 0, column = 0, sticky = W, pady = 2)
display_temperature.grid(row = 0, column = 1, sticky = W, pady = 2)
label_celsius.grid(row = 0, column = 2, sticky = W, pady = 2)

label_poucentage_actuel.grid(row = 0, column = 3, sticky = W, pady = 2)
display_pourcentage_actuel.grid(row = 0, column = 4, sticky = W, pady = 2)
label_pourcent_actuel.grid(row = 0, column = 5, sticky = W, pady = 2)

label_controle.grid(row = 1, column = 0, sticky = W, pady = 2)
label_pourcent.grid(row = 2, column = 3, sticky = W, pady = 2)
label_moteur.grid(row = 4, column = 0, sticky = W, pady = 2)
label_direction.grid(row = 5, column = 0, sticky = W, pady = 2)
label_vitesse.grid(row = 5, column = 3, sticky = W, pady = 2)

entry_pourcent.grid(row = 2, column = 2, sticky = W, pady = 2)

btn_automatique.grid(row = 1, column = 1, sticky = W, pady = 2)
btn_manuel.grid(row = 2, column = 1, sticky = W, pady = 2)
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

def update_temperature():
    value = adc.analogRead(0)        # read ADC value A0 pin
    voltage = value / 255.0 * 3.3        # calculate voltage
    try:
        Rt = 10 * voltage / (3.3 - voltage)    # calculate resistance value of thermistor
        tempK = 1/(1/(273.15 + 25) + math.log(Rt/10)/3950.0) # calculate temperature (Kelvin)
        tempC = tempK -273.15        # calculate temperature (Celsius)
    except ZeroDivisionError:
        Rt = 0 # calculate resistance value of thermistor

    display_temperature['text'] = str(round(tempC, 2))
    root.update()
    root.after(1, update_temperature) # run itself again after 1 ms

def destroy():
    adc.close()
    GPIO.cleanup()

if __name__ == '__main__':  # Program entrance
    print ('Program is starting ... ')
    setup()
    try:
        display_pourcentage_actuel.update()
        update_temperature()
        # show window
        root.mainloop()
    except KeyboardInterrupt: # Press ctrl-c to end the program.
        destroy()