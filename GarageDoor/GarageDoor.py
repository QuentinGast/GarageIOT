import RPi.GPIO as GPIO
import time
from ADCDevice import *
from tkinter import *

from Motor import Motor
from UltrasonicRanging import Ultrasonic
from Temperature import Temperature

adc = ADCDevice()  # Define an ADCDevice class object

motorPins = (12, 16, 18, 22,)  # define pins connected to four phase ABCD of stepper motor
CCWStep = (0x01, 0x02, 0x04, 0x08,)  # define power supply order for rotating anticlockwise
CWStep = (0x08, 0x04, 0x02, 0x01)  # define power supply order for rotating clockwise

SAVE_PATH = "GarageDoor/save.txt"

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

# set window size
root.geometry("500x200")

# set window position
root.eval("tk::PlaceWindow . center")

# initialize labels and controllers
# temperature
label_temperature = Label(root, text="Temperature ambiante : ")
temperature_controller = Temperature(root, text="0")
label_celsius = Label(root, text="°C")

# motor
label_poucentage_actuel = Label(root, text="Ouverture actuelle : ")
motor_controller = Motor(root, text="0")
label_pourcent_actuel = Label(root, text="%")

# distance
label_distance_actuelle = Label(root, text="Distance actuelle : ")
distance_controller = Ultrasonic(root, text="0")
label_cm = Label(root, text="cm")

# state
label_controle = Label(root, text="Controle : ")
label_pourcent = Label(root, text="%")

# buttons and entries
label_max = Label(root, text="Ouverture maximale : ")

entry_pourcent = Entry(root)
entry_pourcent.config(width=5)
entry_pourcent.insert(0, "100")

# functions for buttons
def mode_automatique():
    state_change("automatique")
    update_automatique()


def mode_manuel():
    state_change("manuel")


btn_automatique = Button(root, text="Auto", command=mode_automatique)
btn_manuel = Button(root, text="Manuel", command=mode_manuel)


def ouvrir_porte():
    state_change("ouvrir")
    motor_controller.start(1, get_percent())


def fermer_porte():
    state_change("fermer")
    motor_controller.start(-1)


def stop():
    state_change("manuel")
    motor_controller.stop()


# buttons
btn_ouvrir = Button(root, text="Ouvrir", command=ouvrir_porte)
btn_fermer = Button(root, text="Fermer", command=fermer_porte)
btn_stop = Button(root, text="Stop", command=stop)

# setting display widgets position in window
label_temperature.grid(row=0, column=0, sticky=W, pady=2)
temperature_controller.grid(row=0, column=1, sticky=W, pady=2)
label_celsius.grid(row=0, column=2, sticky=W, pady=2)

label_controle.grid(row=1, column=0, sticky=W, pady=2)

label_max.grid(row=2, column=0, sticky=W, pady=2)
entry_pourcent.grid(row=2, column=1, sticky=W, pady=2)
label_pourcent.grid(row=2, column=2, sticky=W, pady=2)

label_poucentage_actuel.grid(row=4, column=0, sticky=W, pady=2)
motor_controller.grid(row=4, column=1, sticky=W, pady=2)
label_pourcent_actuel.grid(row=4, column=2, sticky=W, pady=2)

label_distance_actuelle.grid(row=5, column=0, sticky=W, pady=2)
distance_controller.grid(row=5, column=1, sticky=W, pady=2)
label_cm.grid(row=5, column=2, sticky=W, pady=2)

btn_automatique.grid(row=1, column=1, sticky=W, pady=2)
btn_manuel.grid(row=1, column=2, sticky=W, pady=2)
btn_ouvrir.grid(row=3, column=1, sticky=W, pady=2)
btn_fermer.grid(row=3, column=2, sticky=W, pady=2)
btn_stop.grid(row=3, column=3, sticky=W, pady=2)

# code begins here
def state_change(state):
    global is_automatique
    global is_manuel
    if state == "automatique":
        is_manuel = False
        btn_automatique["state"] = "disabled"
        btn_manuel["state"] = "normal"
        btn_ouvrir["state"] = "disabled"
        btn_fermer["state"] = "disabled"
        btn_stop["state"] = "disabled"
        entry_pourcent["state"] = "disabled"
        is_automatique = True
    elif state == "manuel":
        is_automatique = False
        btn_automatique["state"] = "normal"
        btn_manuel["state"] = "disabled"
        btn_ouvrir["state"] = "normal"
        btn_fermer["state"] = "normal"
        btn_stop["state"] = "disabled"
        entry_pourcent["state"] = "normal"
        is_manuel = True
    elif state == "ouvrir":
        btn_automatique["state"] = "disabled"
        btn_manuel["state"] = "disabled"
        btn_ouvrir["state"] = "disabled"
        btn_fermer["state"] = "normal"
        btn_stop["state"] = "normal"
        entry_pourcent["state"] = "disabled"
        state_ouverture()
    elif state == "fermer":
        btn_automatique["state"] = "disabled"
        btn_manuel["state"] = "disabled"
        btn_ouvrir["state"] = "normal"
        btn_fermer["state"] = "disabled"
        btn_stop["state"] = "normal"
        entry_pourcent["state"] = "disabled"
        state_fermeture()


def state_reset():
    btn_automatique["state"] = "normal"
    btn_manuel["state"] = "normal"
    btn_ouvrir["state"] = "normal"
    btn_fermer["state"] = "normal"
    btn_stop["state"] = "normal"
    entry_pourcent["state"] = "normal"


def state_ouverture():
    if motor_controller.get() >= get_percent():
        btn_automatique["state"] = "normal"
        btn_ouvrir["state"] = "disabled"
        btn_fermer["state"] = "normal"
        btn_stop["state"] = "disabled"
        entry_pourcent["state"] = "normal"
    else:
        root.after(1, state_ouverture)


def state_fermeture():
    if motor_controller.get() <= 0:
        btn_automatique["state"] = "normal"
        btn_ouvrir["state"] = "normal"
        btn_fermer["state"] = "disabled"
        btn_stop["state"] = "disabled"
        entry_pourcent["state"] = "normal"
    else:
        root.after(1, state_fermeture)


# get the percent from the entry
def get_percent():
    # check if entry_pourcent.get() is a number
    if (
        not entry_pourcent.get().isdigit()
        or int(entry_pourcent.get()) > 100
        or int(entry_pourcent.get()) < 0
    ):
        return 100
    return int(entry_pourcent.get())


# update in automatic mode
def update_automatique():
    if not is_automatique:
        return

    temperature = temperature_controller.get_temperature()
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

    root.after(1000, update_automatique)  # run itself again after 1 s


#  update display
def update():
    root.update()
    root.after(10, update)


def setup():
    GPIO.setmode(GPIO.BOARD)  # use PHYSICAL GPIO Numbering
    for pin in motorPins:
        GPIO.setup(pin, GPIO.OUT)

    # get the current opening
    global motor_controller
    with open(SAVE_PATH, "r") as f:
        motor_controller.set_cycle(int(f.read()))


def on_closing():
    # save the current opening
    with open(SAVE_PATH, "w") as f:
        f.write(str(motor_controller.get_cycle()))
    time.sleep(0.5)
    destroy()


def destroy():
    adc.close()
    GPIO.cleanup()
    root.destroy()


if __name__ == "__main__":  # Program entrance
    print("Program is starting ... ")
    setup()
    # manual mode by default
    state_change("manuel")
    try:
        root.protocol("WM_DELETE_WINDOW", on_closing)
        motor_controller.update()
        distance_controller.update()
        temperature_controller.update()
        # show window
        root.mainloop()
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        on_closing()
