#!/usr/bin/env python3
from ServerTFTP import *
import errno

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
    except (FileNotFoundError, OSError) as e:
        if(type(e) == FileNotFoundError):
            print(filename + "not found. Finishing conection...")
            t.sendErrorAndStop(ErrorcodeTFTP.FileNotFound(), "")
        elif(e.errno == errno.EACCES):
            print("Access violation. Finishing conection...")
            t.sendErrorAndStop(ErrorcodeTFTP.AccessViolation(), "")
        else:
            print("Could not open the requested file: " + filename)
            print(filename + "already exists. Finishing conection...")
            t.sendErrorAndStop(ErrorcodeTFTP.NULL(), "Unkown error")
    else:
        try:
            while t.isBufferInOpened():
                data = f.read(dataReadBlock)

                if(t.getMode() == "octet"):
                    t.sendData(data)
                else:
                    t.sendText(data)
                
                if(len(data) < dataReadBlock):
                    t.bufferInClose()
        except OSError as e:
            print("Could not open the requested file: " + filename)
            print(filename + "already exists. Finishing conection...")
            t.sendErrorAndStop(ErrorcodeTFTP.NULL(), "Unkown error")
            
        f.close()

        t.waitForTransmissionCompletion()

    print("GET ended")

def handle_PUT(t, filename):
    t.startServerTransmission(dataSender=False)

    dataReadBlock = t.getBlockSize()
    try:
        if(t.getMode() == "octet"):
            f = open(filename, "bx")
        else:
            f = open(filename, "x")
    except (FileExistsError, OSError) as e:
        if(type(e) == FileExistsError):
            print(filename + "already exists. Finishing conection...")
            t.sendErrorAndStop(ErrorcodeTFTP.AlreadyExists(), "")
        elif(e.errno == errno.ENOSPC):
            print("No space available. Finishing conection...")
            t.sendErrorAndStop(ErrorcodeTFTP.DiskFull(), "")
        elif(e.errno == errno.EACCES):
            print("Access violation. Finishing conection...")
            t.sendErrorAndStop(ErrorcodeTFTP.AccessViolation(), "")
        else:
            print("Could not open the requested file: " + filename)
            print(filename + "already exists. Finishing conection...")
            t.sendErrorAndStop(ErrorcodeTFTP.NULL(), "Unkown error")
    else:
        try:
            while t.isBufferInOpened():
                if(t.getMode() == "octet"):
                    data = t.readData(dataReadBlock)
                else:
                    data = t.readText(dataReadBlock)
                
                f.write(data)
        except OSError as e:
            if(e.errno == errno.ENOSPC):
                print("No space available. Finishing conection...")
                t.sendErrorAndStop(ErrorcodeTFTP.DiskFull(), "")
            else:
                print("Could not open the requested file: " + filename)
                print(filename + "already exists. Finishing conection...")
                t.sendErrorAndStop(ErrorcodeTFTP.NULL(), "Unkown error")

        f.close()
    
    t.waitForTransmissionCompletion()
    print("PUT ended")

serv = ServerTFTP(listenAdress = listenAdress, port = welcomePort)

while True:
    serv.acceptConncetion(handle_GET, handle_PUT)
