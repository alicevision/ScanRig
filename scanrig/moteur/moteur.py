import serial #serial connection to Arduino
from tkinter import *  # interface
import sys # check system
import glob
import time

def serial_ports():
    """ Lists all available serial port names

        raises EnvironmentError on unsupported or unknown platforms
        returns a list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def serialWrite(ser, str):
    print(str)
    str2 = str + "\n"
    ser.write(str2.encode('ascii'))

if __name__ == '__main__':
    print("--- choice one of these port COM corresponding to your microcontroller ---")
    PortsList = serial_ports()
    print(PortsList)
    comNb = -1
    while (comNb < 0 or comNb >= len(PortsList)):
        comNb = int(input("->"))
    
    #  init Serial connection to arduino
    arduinoSer = serial.Serial(PortsList[comNb], 115200)
    print(arduinoSer.name + " selected") # debug

    # GUI init & loop
    window = Tk()

    # vaiables holder
    command = StringVar()
    command.set("")

    Label(window, text="Pulse").grid(row = 0, column = 0, columnspan = 2) 
    Label(window, text="pulseDelay").grid(row = 0, column = 2, columnspan = 2)
    pulse = Scale(window, from_=0, to=4000, orient=HORIZONTAL, width=35)
    pulse.grid(row = 1, column = 0, columnspan = 2)
    pulseDelay = Scale(window, from_=0, to=1000, orient=HORIZONTAL, width=35)
    pulseDelay.grid(row = 1, column = 2, columnspan = 2)

    Button(window, text="Left", command = lambda : serialWrite(arduinoSer, "left:" + str(pulse.get()) )).grid(row = 2, column = 0, padx=5, sticky = N)
    Button(window, text="Right", command = lambda : serialWrite(arduinoSer, "right:" + str(pulse.get()) )).grid(row = 2, column = 1, padx=5, sticky = N)
    Button(window, text="setPulseDelay", command = lambda : serialWrite(arduinoSer, "setPulseDelay:" + str(pulseDelay.get()) )).grid(row = 2, column = 2, padx=5, sticky = N)
    Button(window, text="test", command = lambda : serialWrite(arduinoSer, "test:")).grid(row = 2, column = 3, padx=5, sticky = N)
    Label(window, text="CustomCmd").grid(row = 3, column = 0, columnspan = 4, sticky = N)
    cmdEntry = Entry(window, textvariable=command, width = 40)
    cmdEntry.grid(row = 4, column = 0, columnspan = 3)
    Button(window, text="send", command = lambda : serialWrite(arduinoSer, command.get())).grid(row = 4, column = 3, sticky = N)
    
    window.mainloop() #start loop GUI
