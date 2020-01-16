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

def serialWrite(ser, str):
    """
    function used to send data to our serial port in utf-8
    """
    ser.write(str.encode('utf-8'))
    ser.write(b"\n") # add endOfLine

# custom exception for our class
class EmptyNewLineError(Exception):
   """Raised when the Serial incoming newline is empty"""
   pass

class SerialReader:
    def __init__(self, serial):
        self.buffer = bytearray()
        self.serial = serial

    def readline(self):
        # handle bytes already in buffer
        i = self.buffer.find(b"\n") # look for endOfLine
        if i >= 0:
            line = self.buffer[:i+1] #read line
            self.buffer = self.buffer[i+1:] #keep other in buffer
            return line
        
        # handle new incoming data
        i = max(1, min(2048, self.serial.in_waiting)) #clamp read number
        data = self.serial.read(i) # read all availible bytes
        i = data.find(b"\n") #if line was found
        if i >= 0:
            line = self.buffer + data[:i+1]
            self.buffer[0:] = data[i+1:]
            return line
        else:
            self.buffer.extend(data)
            raise EmptyNewLineError

