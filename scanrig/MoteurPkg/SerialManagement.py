import sys # check system
import serial #serial connection to Arduino
import glob
import time
import threading

def availablePorts():
    """
    Returns a list of all serial ports available on the system
    Raises EnvironmentError on unsupported or unknown platforms
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
        try: #try open ports
            s = serial.Serial(port)
            s.close()
            result.append(port) # if it success add this port
        except (OSError, serial.SerialException):
            pass
    return result

def serialWrite(ser, cmdString):
    """
    function used to send data to our serial port in utf-8
    """
    s = cmdString + "\n"
    cmd = bytearray()
    cmd.extend(s.encode('ascii'))
    print("cmdString : '", str(cmd), "'")
    try:
        nb = ser.write(cmd)
        print("bytes written : ", str(nb))
    except	serial.SerialTimeoutException :
        print("error timeOut")

def selectPort(baudrate = 9600):
    print("--- Choice one of these port COM corresponding to your microcontroller ---")
    portsList = availablePorts()
    if len(portsList) <= 0:
        print("error : any port found")
        exit(1)
    print(portsList)
    comNb = -1
    while (comNb < 0 or comNb >= len(portsList)):
        comNb = int(input("->"))
    
    try :# Init Serial connection to arduino
        ser = serial.Serial(portsList[comNb], baudrate , timeout = 1)
    except:
        print("Error during serial port initialization")
        exit(1)
    print(ser.name + " opened") # info
    return ser

class SerialReader:
    def __init__(self, serial):
        self.buffer = bytearray()
        self.serial = serial

    def readline(self):
        """
        handle bytes already in buffer
        return space in bytes (b' ') if there is no line to handle
        """
        i = self.buffer.find(b'\n') # look for endOfLine in buffer
        if i >= 0:
            line = self.buffer[:i] # read line
            self.buffer = self.buffer[i+1:] # keep other data in buffer
            return line

        # handle new incoming data
        i = min(2048, self.serial.in_waiting) #limit to 2048 read
        if(i > 0):
            data = self.serial.read(i) # read all available bytes
            print("new data : '", data, "'")
            self.buffer += data
        return b' '

    def clearBuffer(self):
        i = self.serial.in_waiting
        self.serial.flush()
        print("serial clean : ", i, " bytes)")


