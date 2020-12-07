#!  /usr/bin/python3
#----------------------------------------------------------
#   Name: threads.py
#   Author: xyy15926
#   Created at: 2018-09-17 15:02:34
#   Updated at: 2018-09-17 23:23:03
#   Description: 
#----------------------------------------------------------

import threading
import time
from multiprocessing import Queue

class MultiThreads():

    def __init__(self, target):
        self.queue = Queue()
        self.target = target

    def _target(self, *args, **kwargs):
        output = self.target(*args, **kwargs)
        print(output)
        self.queue.put(output)

    def set_threads(self, num, args=[]):
        self.num = num
        self.threads = []
        for i in range(num):
            if len(args) == 0:
                self.threads.append(threading.Thread(
                    target = self._target,
                    name = "thread-%s" % (i)))
            elif len(args) == 1:
                self.threads.append(threading.Thread(
                    target = self._target,
                    name = "thread-%s" % (i),
                    args = args[0],
                    kwargs = args[1]))
            elif len(args) == num:
                self.threads.append(threading.Thread(
                    target = self._target,
                    name = "thread-%s" % (i),
                    args = args[i][0],
                    kwargs = args[i][1]))
            else:
                raise(Exception("invalid args"))

    def start_threads(self):
        for thread in self.threads:
            thread.start()
        for thread in self.threads:
            thread.join()

    def handle(self):
        pass



def __test_target(id):
    import time
    time.sleep(2)
    return id

if __name__ == "__main__":
    num  = 2
    __test = MultiThreads(__test_target)
    __test.set_threads(num, [([],{"id": i}) for i in range(num)])
    __test.start_threads()
    count = 0
    while(True):
        if not __test.queue.empty():
            print(__test.queue.get())
            count += 1
        if count == num:
            break
        time.sleep(1)


