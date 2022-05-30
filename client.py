#!/usr/bin/env python3
from TransmissionTFTP import *

# Defaults
serverName = 'testxaco.rabadan.dev'
serverPort = 12064

# Ask the user what do they want to do
action = ""
while(action != "GET" and action != "PUT"):
    action = input("GET/PUT: ")

# Ask the user for a package size
packageSizeText = "0"
while(not packageSizeText in ["32","64","128","256","512","1024","2048"]):
    packageSizeText = input("Select a valid package size (32, 64, 128, 256, 512, 1024, 2048) bytes: ")
packageSize = int(packageSizeText)

# Ask the user for the mode
modeText = "0"
while(not modeText in ["octet","netascii"]):
    modeText = input("Select a valid mode (octet, netascii): ")

# Ask the user for a file
request = ""
while(len(request.encode()) <= 0 or 512 < len(request.encode())):
    request = input("Filename (between 1 and ?? characters): ")

tt = TransmissionTFTP(blockSize = packageSize, mode=modeText)
tt.setPeer(hostname = serverName, welcomePort = serverPort)

if (action == "PUT" and modeText == "octet"):
    f = open(request, "rb")
    tt.makePUT(request)
    while tt.isBufferInOpened():
        data = f.read(packageSize)
        tt.sendData(data)

        if len(data) < packageSize:
            tt.bufferInClose()

if (action == "PUT" and modeText == "netascii"):
    f = open(request, "r", errors = "replace")
    tt.makePUT(request)
    while tt.isBufferInOpened():
        data = f.read(packageSize)
        tt.sendText(data)

        if len(data) < packageSize:
            tt.bufferInClose()

if (action == "GET" and modeText == "octet"):
    f = open(request, "wb")
    tt.makeGET(request)

    while tt.isBufferInOpened():
        data = tt.readData(packageSize)
        f.write(data)

    f.close()

if (action == "GET" and modeText == "netascii"):
    f = open(request, "w", errors = "replace")
    tt.makeGET(request)

    while tt.isBufferInOpened():
        data = tt.readText(packageSize)
        f.write(data)

    f.close()

tt.waitForTransmissionCompletion()
