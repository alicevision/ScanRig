#------------------------- IMPORTS
import time
from MoteurPkg.SerialManagement import availablePorts, serialWrite, SerialReader, selectPort

#------------------------- SCRIPT

def main():
    GLOBAL_RUNNING = [True]

    # Initialize arduino
    arduinoSer = selectPort(9600)
    # Init custom Serial reader to handle readLine correctly
    serialReader = SerialReader(arduinoSer)

    # Give the motor instructions - direction:totalAngle,stepAngle,transition,time
    serialReader.clearBuffer()
    # time.sleep(4)
    # serialWrite(arduinoSer, "leftCaptureFull:360,15,45,45")
    # serialWrite(arduinoSer, "leftSmooth:1,10,30")
    print("open: " + str(arduinoSer.is_open))
    serialWrite(arduinoSer, "s:")
    time.sleep(2)
    serialWrite(arduinoSer, "leftSmooth:1,10,30\nblabla:12\n")
    # Read frame

    # Main loop
    while(GLOBAL_RUNNING[0]):

        # While the motor is rotating (before to arrive to a step angle)
        # while(line == b''):
        line = serialReader.readline()
    
        # When the motor reaches the step angle
        if line == b'Capture\r':
            # Read frame
            print("capture cam")

        # When the motor reaches the end    
        elif line == b'Success\r' :
            print("Success!!!!")
            GLOBAL_RUNNING[0] = False

        elif line != b'':
            print("line : \"" + str(line) + "\"")
            # GLOBAL_RUNNING[0] = False

        time.sleep(0.01)

    print("End of Script")
    return

if __name__ == "__main__":
    main()