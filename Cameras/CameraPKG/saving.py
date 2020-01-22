import numpy as np
import threading, logging, os, time, cv2


class SaveWatcher(threading.Thread):
    def __init__(self, globalRunning, framesToSave, args):
        threading.Thread.__init__(self)

        self.running = True
        self.globalRunning = globalRunning
        self.framesToSave = framesToSave
        self.args = args
    

    def run(self):
        while(self.running):
            if not self.framesToSave.empty():
                directory = self.args.output
                index, number, frame = self.framesToSave.get()
                filename = f'cam_{index}_{number:04d}.{self.args.extension}'
                outFilepath = os.path.join(directory, filename)
                logging.info(f'Writting file={outFilepath}')
                cv2.imwrite(outFilepath, frame)
            
            time.sleep(0.04)

            if not self.globalRunning[0]:
                self.stop()

    def stop(self):
        if self.framesToSave.empty():
            self.running = False