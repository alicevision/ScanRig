import numpy as np
import threading, logging, os, time, cv2


class SaveWatcher(threading.Thread):
    def __init__(self, stopThread, savingQueue):
        threading.Thread.__init__(self)

        self.running = True
        self.savingQueue = savingQueue
        self.stopThread = stopThread # Array with one boolean


    def run(self):
        while(self.running):
            if not self.savingQueue.empty():
                index, number, frame, path = self.savingQueue.get()
                filename = f'cam_{index}_{number:03d}.jpg'
                outFilepath = os.path.join(path, filename)
                logging.info(f'Writting file={outFilepath}')
                cv2.imwrite(outFilepath, frame)
            
            time.sleep(0.04)

            if self.stopThread[0]:
                self.stop()

    def stop(self):
        if self.savingQueue.empty():
            logging.info("Stopping Saving Thread")
            self.running = False