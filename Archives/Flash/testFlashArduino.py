import serial
import keyboard

arduinoSer = serial.Serial('/dev/ttyACM0', 9600) # connection serie à l'arduino 
print(arduinoSer.name)

def write(ser, str) :
    ser.write(str.encode('ascii'))

while True:
    if keyboard.read_key() == 'f':
        write(arduinoSer, 'f')

