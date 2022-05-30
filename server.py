#!/usr/bin/env python3
from ServerTFTP import *

# Defaults
listenAdress = ''
welcomePort = 12064
            
def handle_GET(t, filename):
    t.startServerTransmission(dataSender=True)

    dataReadBlock = t.getBlockSize()

    try:
        if(t.getMode() == "octet"):
            f = open(filename, "rb")
        else:
            f = open(filename, "r")
    except OSError:
        print("Could not open the requested file: " + filename)
        t.bufferInClose()
    else:
        while t.isBufferInOpened():
            data = f.read(dataReadBlock)

            if(t.getMode() == "octet"):
                t.sendData(data)
            else:
                t.sendText(data)
            
            if(len(data) < dataReadBlock):
                t.bufferInClose()
            
        f.close()

        t.waitForTransmissionCompletion()

    print("GET ended")

def handle_PUT(t, filename):
    t.startServerTransmission(dataSender=False)

    dataReadBlock = t.getBlockSize()
    try:
        if(t.getMode() == "octet"):
            f = open(filename, "wb")
        else:
            f = open(filename, "w")
    except OSError:
        print("Could not open the requested file: " + filename)
        t.bufferInClose()
    else:
        while t.isBufferInOpened():
            if(t.getMode() == "octet"):
                data = t.readData(dataReadBlock)
            else:
                data = t.readText(dataReadBlock)
            
            f.write(data)

    f.close()
    t.waitForTransmissionCompletion()
    print("PUT ended")

serv = ServerTFTP(listenAdress = listenAdress, port = welcomePort)

while True:
    serv.acceptConncetion(handle_GET, handle_PUT)
