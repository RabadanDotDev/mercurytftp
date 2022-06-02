#!/usr/bin/env python3
from TransmissionTFTP import *

print( \
"""
  __  __                             _______ ______ _______ _____  
 |  \/  |                           |__   __|  ____|__   __|  __ \ 
 | \  / | ___ _ __ ___ _   _ _ __ _   _| |  | |__     | |  | |__) |
 | |\/| |/ _ \ '__/ __| | | | '__| | | | |  |  __|    | |  |  ___/ 
 | |  | |  __/ | | (__| |_| | |  | |_| | |  | |       | |  | |     
 |_|  |_|\___|_|  \___|\__,_|_|   \__, |_|  |_|       |_|  |_|     
                                   __/ |                           
                                  |___/                            
                                
    - Per Raul Rabadan Arroyo i Jaume Pérez Medina -
""")

# Valors per defecte
serverName = 'testxaco.rabadan.dev'
serverPort = 12064

# Demanar a l'usuari si vol un servidor diferent al per defecte
serverNameIn = input("Nom del servidor (per defecte: testxaco.rabadan.dev): ")
if(serverNameIn != ""):
    serverName = serverNameIn

# Demanar a l'usuari si vol un port diferent al per defecte
serverPortIn = input("Port del servidor (per defecte: 12064): ")
if(serverPortIn != ""):
    serverPort = int(serverPortIn)

# Demanar a l'usuari si vol fer un GET o un PUT
action = ""
while(action != "GET" and action != "PUT"):
    action = input("GET/PUT: ")

# Demanar a l'usuari una mida de paquet
packageSizeText = "0"
while(not packageSizeText in ["32","64","128","256","512","1024","2048"]):
    packageSizeText = input("Escull una mida de paquet vàlida: (32, 64, 128, 256, 512, 1024, 2048) bytes: ")
packageSize = int(packageSizeText)

# Demanar a l'usuari un mode de transmissió
modeText = "0"
while(not modeText in ["octet","netascii"]):
    modeText = input("Escull un mode de transmissió vàlid (octet, netascii): ")

# Demanar a l'usuari pel nom de l'arxiu
request = ""
while(len(request.encode()) <= 0 or 128 < len(request.encode())):
    request = input("Nom del fitxer (entre 1 i 128 characters): ")

# Fer transmissió
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
