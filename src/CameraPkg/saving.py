import numpy as np
import threading, logging, os, time, cv2


class SaveWatcher(threading.Thread):
    def __init__(self, stopThread, framesToSave, directory):
        threading.Thread.__init__(self)

        self.running = True
        self.framesToSave = framesToSave
        self.stopThread = stopThread # Array with one boolean
        self.directory = directory


    def run(self):
        while(self.running):
            if not self.framesToSave.empty():
                index, number, frame = self.framesToSave.get()
                filename = f'cam_{index}_{number:04d}.jpg'
                outFilepath = os.path.join(self.directory, filename)
                logging.info(f'Writting file={outFilepath}')
                cv2.imwrite(outFilepath, frame)
            
            time.sleep(0.04)

            if self.stopThread[0]:
                self.stop()

    def stop(self):
        if self.framesToSave.empty():
            logging.info("Stopping Saving Thread")
            self.running = False