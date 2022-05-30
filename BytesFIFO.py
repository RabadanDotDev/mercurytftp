import threading

class BytesFIFO:
    def __init__(self):
        self.__buff = bytearray()
        self.__lock = threading.Lock()

    def pushBytes(self, data):
        self.__lock.acquire()
        self.__buff.extend(data)
        self.__lock.release()
    
    def popBytes(self, numBytes):
        self.__lock.acquire()
        ret = self.__buff[0:numBytes]
        self.__buff = self.__buff[numBytes:]
        self.__lock.release()
        return ret

    def getNumBytes(self):
        self.__lock.acquire()
        val = len(self.__buff)
        self.__lock.release()
        return val 
