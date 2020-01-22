import time
import serial #serial connection to Arduino
from tkinter import *  # interface
from MoteurPkg.SerialManagement import availablePorts, serialWrite, SerialReader, selectPort

def handleCallBack(log, line):
    log.insert('0.0', line.decode())

if __name__ == '__main__':

    arduinoSer = selectPort()

    # init custom Serial reader to handle readLine correctly
    serialReader = SerialReader(arduinoSer)

    # GUI init & loop
    window = Tk()
    
    running = True
    def closeWindow(): # Custom callback function to close window & stop loop using running variable
        global running
        running = False
        print ("Window closed")
    window.protocol("WM_DELETE_WINDOW", closeWindow)

    # Create GUI using tkinter
    Label(window, text="Pulse").grid(row = 0, column = 0, columnspan = 2) 
    Label(window, text="pulseDelay").grid(row = 0, column = 2, columnspan = 2)
    pulse = Scale(window, from_=0, to=4000, orient=HORIZONTAL, width=35)
    pulse.grid(row = 1, column = 0, columnspan = 2)
    pulseDelay = Scale(window, from_=0, to=2000, orient=HORIZONTAL, width=35)
    pulseDelay.grid(row = 1, column = 2, columnspan = 2)

    Button(window, text="Left", command = lambda : serialWrite(arduinoSer, "left:" + str(pulse.get()) )).grid(row = 2, column = 0, padx=5, sticky = N)
    Button(window, text="Right", command = lambda : serialWrite(arduinoSer, "right:" + str(pulse.get()) )).grid(row = 2, column = 1, padx=5, sticky = N)
    Button(window, text="setPulseDelay", command = lambda : serialWrite(arduinoSer, "setPulseDelay:" + str(pulseDelay.get()) )).grid(row = 2, column = 2, padx=5, sticky = N)
    Button(window, text="test", command = lambda : serialWrite(arduinoSer, "test:")).grid(row = 2, column = 3, padx=5, sticky = N)
    Label(window, text="CustomCmd").grid(row = 3, column = 0, columnspan = 4, sticky = N)

    # Variables holder fo cmd entry used to send custom cmd to arduino without button
    cmdEntryHolder = StringVar()
    cmdEntryHolder.set("")

    cmdEntry = Entry(window, textvariable=cmdEntryHolder, width = 40)
    cmdEntry.grid(row = 4, column = 0, columnspan = 3)
    Button(window, text="send", command = lambda : serialWrite(arduinoSer, cmdEntryHolder.get())).grid(row = 4, column = 3, sticky = N)

    SerialMonitor = Frame(window, borderwidth=2, relief=GROOVE)
    SerialMonitor.grid(row = 5, column = 0, rowspan = 4, columnspan = 4, padx=10, pady=10)

    scroolBar = Scrollbar(SerialMonitor)
    scroolBar.pack(side=RIGHT, fill=Y)

    log = Text(SerialMonitor, width=30, height=20, takefocus=0)
    log.pack()

    # Attach scrollbar to log box 
    log.config(yscrollcommand=scroolBar.set)
    scroolBar.config(command=log.yview)

    while running:
        window.update() # Call tkinter window update by ourselves
        line = serialReader.readline()
        if line != b"" :
            handleCallBack(log, line)