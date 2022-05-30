import threading
from socket import *
from OpcodeTFTP import *
from PacketTFTP import *
from BytesFIFO  import *
from TransmissionTFTP  import *

class ServerTFTP:
    # Common ------------------------------------------------------------------
    def __init__(self, listenAdress = "localhost", port = 69):
        self.listenAdress = listenAdress
        self.port = port
        self.requestPacketSize = 512

        self.numPacketsRecv = 0

        # Create socket
        self.socket = socket(AF_INET,SOCK_DGRAM)
        self.socket.bind((listenAdress, port))
        print("Binded Server UDP socket to [" + listenAdress + "]:[" + str(port) + "]")
    
    def __waitRequestPacket(self):
        while True:
            # Recieve packet
            (recievedData, origin) = self.socket.recvfrom(self.requestPacketSize)
            packet = PacketTFTP()
            packet.setEncoded(recievedData)

            print("Request packet recieved (" + str(self.numPacketsRecv) +  "º) recived: " + str(packet))
            self.numPacketsRecv += 1

            # Return if its a request, drop it otherwise
            if(packet.getOpcode() == OpcodeTFTP.RRQ() or packet.getOpcode() == OpcodeTFTP.WRQ()):
                return (packet, origin)

    def acceptConncetion(self, GETHandler, PUTHandler):
        (packet, origin) = self.__waitRequestPacket()
        packetSize = int(packet.getNonStandardBlockSize())
        transmission = TransmissionTFTP(packetSize, str.lower(packet.getMode()))
        transmission.setPeer(origin[0], origin[1])

        if(packet.getOpcode() == OpcodeTFTP.RRQ()):
            thread = threading.Thread(target=GETHandler, args=(transmission,packet.getFilename(),))
        elif(packet.getOpcode() == OpcodeTFTP.WRQ()):
            thread = threading.Thread(target=PUTHandler, args=(transmission,packet.getFilename(),))
        else:
            print("Unknown request recieved")
            return

        self.socket.close()
        transmission.bind(self.listenAdress, self.port)
        print("Closed server socket and rebinded TransmissionTFTP UDP socket to [" + self.listenAdress + "]:[" + str(self.port) + "]")

        thread.start()
        thread.join()
        print("Transmission done")

        transmission.closeInternalSocket()
        print("Tranmsision socket closed")

        self.socket = socket(AF_INET,SOCK_DGRAM)
        self.socket.bind((self.listenAdress, self.port))
        print("Rebinded Server UDP socket to [" + self.listenAdress + "]:[" + str(self.port) + "]")
