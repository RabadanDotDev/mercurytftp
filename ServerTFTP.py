import threading
from socket import *
from OpcodeTFTP import *
from PacketTFTP import *
from BytesFIFO  import *
from TransmissionTFTP  import *
from ExceptionTFTP  import *

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
        print("Socket del servidor UDP enllaçat a [" + listenAdress + "]:[" + str(port) + "]")
    
    def __waitRequestPacket(self):
        while True:
            # Recieve packet
            (recievedData, origin) = self.socket.recvfrom(self.requestPacketSize)
            packet = PacketTFTP()
            packet.setEncoded(recievedData)

            print("Paquet de petició (" + str(self.numPacketsRecv) +  "º) rebut: " + str(packet))
            self.numPacketsRecv += 1

            # Return if its a request, send an error and drop it otherwise
            if(packet.getOpcode() == OpcodeTFTP.RRQ() or packet.getOpcode() == OpcodeTFTP.WRQ()):
                return (packet, origin)
            else:
                packet = PacketTFTP()
                packet.setOpcode(OpcodeTFTP.ERROR())
                if(packet.getOpcode() == OpcodeTFTP.NULL()):
                    packet.setErrorcode(ErrorcodeTFTP.IlegalTFTPOperation())
                else:
                    packet.setErrorcode(ErrorcodeTFTP.UnknownTransferID())
                packet.setErrorMsg("")
                self.socket.sendto(packet.getEncoded(), origin)
                print("Petició rebuda incorrecta. Contestant: " + str(packet))


    def acceptConncetion(self, GETHandler, PUTHandler):
        (packet, origin) = self.__waitRequestPacket()

        packetSize = 512
        recievedOpts = packet.getOptions()
        opts = {}
        for opt in recievedOpts:
            if(opt.lower() == "blksize"):
                opts[opt] = recievedOpts[opt]
                packetSize = int(recievedOpts[opt])
                    
        transmission = TransmissionTFTP(packetSize, str.lower(packet.getMode()))
        transmission.setPeer(origin[0], origin[1])
        transmission.setRecognizedServerOptions(opts)

        if(packet.getOpcode() == OpcodeTFTP.RRQ()):
            thread = threading.Thread(target=GETHandler, args=(transmission,packet.getFilename(),))
        elif(packet.getOpcode() == OpcodeTFTP.WRQ()):
            thread = threading.Thread(target=PUTHandler, args=(transmission,packet.getFilename(),))

        self.socket.close()
        transmission.bind(self.listenAdress, self.port)
        print("S'ha tancat el socket del servidor i s'ha re-enllaçat el socket de la transmissió TFTP UDP a [" + self.listenAdress + "]:[" + str(self.port) + "]")
       

        thread.start()
        thread.join()
        print("Transmissió completada.")

        transmission.closeInternalSocket()
        print("Socket de transmissió tancat.")

        self.socket = socket(AF_INET,SOCK_DGRAM)
        self.socket.bind((self.listenAdress, self.port))
        print("Socket UDP del servidor re-enllaçat a [" + self.listenAdress + "]:[" + str(self.port) + "]")
