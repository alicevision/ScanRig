import numpy as np
import threading, logging, os, time, cv2

import config

class SaveWatcher(threading.Thread):
    def __init__(self, globalRunning, framesToSave):
        threading.Thread.__init__(self)

        self.running = True
        self.globalRunning = globalRunning
        self.framesToSave = framesToSave
    

    def run(self):
        while(self.running):
            if len(self.framesToSave) > 0:
                directory = config.ARGS.output
                filename = f'cam_{self.framesToSave[0][0]}_{self.framesToSave[0][1]:04d}.{config.ARGS.extension}'
                outFilepath = os.path.join(directory, filename)
                logging.info(f'Writting file={outFilepath}')
                cv2.imwrite(outFilepath, self.framesToSave[0][2])
                del self.framesToSave[0]
            
            time.sleep(0.04)

            if not self.globalRunning[0]:
                self.stop()

    def stop(self):
        if len(self.framesToSave) == 0:
            self.running = False