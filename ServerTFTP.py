import threading
from socket import *
from OpcodeTFTP import *
from PacketTFTP import *
from BytesFIFO  import *
from TransmissionTFTP  import *
from ExceptionTFTP  import *

# Classe per facilitar el control del servidor TFTP
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
    
    # Esperar un paquet de inici de conexió, retorna el paquet i l'origen d'aquest
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

    # Esperar per l'inici d'una connexió. Quan arriba, inicialitza un 
    # TransmissionTFTP com a servidor i ho proporciona a la funció GETHandler o
    # PUTHandler segons correspongui
    def acceptConncetion(self, GETHandler, PUTHandler):
        # Esperar inici connexió
        (packet, origin) = self.__waitRequestPacket()

        # Detectar opcions demanades
        packetSize = 512
        recievedOpts = packet.getOptions()
        opts = {}
        for opt in recievedOpts:
            if(opt.lower() == "blksize"):
                opts[opt] = recievedOpts[opt]
                packetSize = int(recievedOpts[opt])
                    
        # Crear transmission TFTP i inicialitzar aquest
        transmission = TransmissionTFTP(packetSize, str.lower(packet.getMode()))
        transmission.setPeer(origin[0], origin[1])
        if len(opts) > 0:
            transmission.setRecognizedServerOptions(opts)

        # Inicialitzar thread que administrará la connexió
        if(packet.getOpcode() == OpcodeTFTP.RRQ()):
            thread = threading.Thread(target=GETHandler, args=(transmission,packet.getFilename(),))
        elif(packet.getOpcode() == OpcodeTFTP.WRQ()):
            thread = threading.Thread(target=PUTHandler, args=(transmission,packet.getFilename(),))

        # Realitzar la transmissió
        
        # Degut a que volem permetre NAT traverssal de forma simple, 
        # proporcionem el port del servidor al TransmssionTFTP. En cas de voler
        # acceptar múltiples clients, això haurà de canviar.

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
