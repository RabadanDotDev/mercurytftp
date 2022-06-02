import threading

# Classe per controlar la entrada i sortida de un FIFO en múltiples threads
class BytesFIFO:
    def __init__(self):
        self._buff = bytearray()
        self._lock = threading.Lock()

    def pushBytes(self, data):
        self._lock.acquire()
        self._buff.extend(data)
        self._lock.release()
    
    def popBytes(self, numBytes):
        self._lock.acquire()
        ret = self._buff[0:numBytes]
        self._buff = self._buff[numBytes:]
        self._lock.release()
        return ret

    def getNumBytes(self):
        self._lock.acquire()
        val = len(self._buff)
        self._lock.release()
        return val 
