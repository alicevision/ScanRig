import cv2, logging, threading, time, os

import config

class SaveWatcher(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.running = True
    
    def run(self):
        while(self.running):
            if len(config.framesToSave) > 0:
                directory = config.args.output
                filename = f'cam_{config.framesToSave[0][0]}_{config.framesToSave[0][1]:04d}.png'
                outFilepath = os.path.join(directory, filename)
                logging.info(f'Writting file={outFilepath}')
                cv2.imwrite(outFilepath, config.framesToSave[0][2])
                del config.framesToSave[0]
            
            time.sleep(0.04)

            if not config.GLOBAL_RUNNING:
                self.stop()

    def stop(self):
        if len(config.framesToSave) == 0:
            self.running = False