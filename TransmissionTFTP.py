import threading
import time
from socket import *
from OpcodeTFTP import *
from PacketTFTP import *
from BytesFIFO  import *
from ExceptionTFTP  import *

# Classe per facilitar el control de la transmissió TFTP
class TransmissionTFTP:
    # Common ------------------------------------------------------------------
    def __init__(self, blockSize = 512, mode = "octet"):
        self.maxPacketSize = blockSize + 4
        self.blockSize     = blockSize
        self.mode          = mode

        self.server       = False
        self.dataSender   = False
        self.dataReciever = False

        self.numPacketsSentRecv = 0

        self.numCurrentBlock = 0

        self.bufferDataInOpen = True
        self.bufferDataIn     = BytesFIFO()
        self.bufferDataOut    = BytesFIFO()

        self.forceStop = False
        self.hasRecognizedOptions = False

        print("Creada transimissió TFTP amb mida de bloc: [" + str(blockSize) + "] i mode [" + mode + "].")

    # Incrementador del nombre de bloc esperat en el moment
    def __incrementNumCurrentBlock(self):
        self.numCurrentBlock = (self.numCurrentBlock + 1) % 65536

    # send/read packet --------------------------------------------------------
    # Enviar un paquet, en cas que hi hagi un error reintentar.
    def __sendPacket(self, packet):
        while True:
            try:
                self.socket.sendto(packet.getEncoded(), (self.hostname, self.port))
                self.numPacketsSentRecv += 1
            except Exception as e:
                print("Error a l'enviar el paquet (" + str(self.numPacketsSentRecv) + "): " + str(e) + ". Tornant a intentar en 2 segons...")
                time.sleep(2)
            else:
                print("Paquet (" + str(self.numPacketsSentRecv) +  "º) eniat: " + str(packet))
                return
    
    # Rebre un paquet. El retorna només si forma part dels opcodes esperats o 
    # hi ha cualsevol error en el moment d'esperar a que arribi el paquet
    def __readPacket(self, expectedOpcodes):
        while True:
            # Crear y rebre dades del paquet
            packet = PacketTFTP()

            try:
                (recievedData, origin) = self.socket.recvfrom(self.maxPacketSize)
            except OSError as o:
                packet.setOpcode(OpcodeTFTP.NULL())
                packet.setNumBlock(-1)
                print("Error al llegir paquet: " + str(o))
                return packet

            packet.setEncoded(recievedData)

            print("Paquet (" + str(self.numPacketsSentRecv) +  "º) rebut: "          \
                    + str(origin[0]) + ":" + str(origin[1]) + "->" + str(packet) + " " \
                    + "Opcodes esperats: " + ' '.join([o.name for o in expectedOpcodes]) + " " \
                    + "Nombre de seqüència actual: " + str(self.numCurrentBlock)               \
                )
            self.numPacketsSentRecv += 1

            # Respondre immediatament amb un error si l'origen es incorrecte i 
            # no s'ha fet la reasignació inicial de origen
            if((origin[0] != self.hostname or origin[1] != self.port) and self.originUpdated):
                errorPacket = PacketTFTP()
                errorPacket.setErrorcode(ErrorcodeTFTP.UnknownTransferID())
                errorPacket.setErrorMsg("")
                self.__sendPacket(errorPacket)
                continue
            elif(not self.originUpdated):
                (self.hostname, self.port) = origin
                self.originUpdated = True

            # Comprovar si s'ha rebut un paquet d'error. Generar una excepció 
            # en cas afirmatiu
            if(packet.getOpcode() == OpcodeTFTP.ERROR()):
                raise ExceptionTFTP(packet.getErrorcode().meaning + " " + packet.getErrorMsg())

            # Comprobar si s'ha rebut un paquet invàlid i generar excepció en 
            # cas afirmatiu
            if(packet.getOpcode() == OpcodeTFTP.NULL()):
                errorPacket = PacketTFTP()
                errorPacket.setErrorcode(ErrorcodeTFTP.IlegalTFTPOperation())
                errorPacket.setErrorMsg("")
                self.__sendPacket(errorPacket)
                raise ExceptionTFTP("Paquet corrupte rebut.")

            # Retornar el paquet si era l'esperat, ignorar-lo en cas negatiu
            if(packet.getOpcode() in expectedOpcodes):
                return packet

    # make/read Data ----------------------------------------------------------
    def __makeDATA(self):
        # Llegir dades del buffer
        while (self.bufferDataInOpen and \
            self.bufferDataIn.getNumBytes() < self.blockSize):
            time.sleep(0.001)
        data = self.bufferDataIn.popBytes(self.blockSize)

        # Crear paquet de dades
        packet = PacketTFTP()
        packet.setOpcode(OpcodeTFTP.DATA())
        packet.setNumBlock(self.numCurrentBlock)
        packet.setDataEncoded(data)

        return packet

    def __readDATA(self):
        # Esperar per un paquet de dades i retornar quan es rebi
        while not self.forceStop:
            packet = self.__readPacket([OpcodeTFTP.DATA()])
            return packet

        # Retornar paquet amb nombre -1 en cas de forçar la terminació
        packet = PacketTFTP()
        packet.setOpcode(OpcodeTFTP.NULL())
        packet.setNumBlock(-1)
        
    # make/read ACK -----------------------------------------------------------
    # Crear paquet ACK amb el nombre de bloc actual
    def __makeACK(self):
        packet = PacketTFTP()
        packet.setOpcode(OpcodeTFTP.ACK())
        packet.setNumBlock(self.numCurrentBlock)

        # Retornar
        return packet

    # Crear paquet OACK segons les opcions reconegudes
    def __makeOACK(self):
        packet = PacketTFTP()
        packet.setOpcode(OpcodeTFTP.OACK())
        for opt in self.recognizedOptions:
            packet.setOption(opt, self.recognizedOptions[opt])

        # Return
        return packet

    # Esperar per un paquet ACK i obtenir el seu nombre de bloc
    def __readACK(self):
        while not self.forceStop:
            packet = self.__readPacket([OpcodeTFTP.ACK()])
            return packet.getNumBlock()

        return -1

    # send/recv dataThread ----------------------------------------------------
    # Realitzar procés d'enviament de dades a partir del que hi hagi en el buffer
    def __sendData(self):
        self.numCurrentBlock = 1

        while not self.forceStop:
            # Crear paquet DATA
            packet = self.__makeDATA()

            # Enviar paquet
            self.__sendPacket(packet)

            # Esperar per ACK i reenviar fins que s'obtingui un de vàlid
            while (self.__readACK() != self.numCurrentBlock and not self.forceStop):
                print("ACK equivocat rebut o perdut, re-enviant DATA...")
                self.__sendPacket(packet)

            if(self.forceStop):
                break

            # Calcular el següent nombre de seqüència
            self.__incrementNumCurrentBlock()

            # Finalitzar si no hi han mes dades
            if(len(packet.getDataEncoded()) < self.blockSize):
                break

    # Iniciar el procés d'enviar dades i capturar els possibles errors en el 
    # thread
    def __sendDataThread(self):
        try:
            self.__sendData()
        except Exception as e:
            print("L'enviament de dades ha estat interromput degut a una excepció." + str(e))
            
            self.bufferInClose()

    # Realitzar procés de rebre dades i dipositar-les en el buffer
    def __recvData(self, packetDataRequest):
        # Inicialitzar nombre de bloc esperat
        self.numCurrentBlock = 1

        while self.isBufferInOpened() and not self.forceStop:
            # Esperar per paquet DATA
            packet = self.__readDATA()

            # Reenviar la petició de dades anterior (ACK/RRQ) 
            while (packet.getNumBlock() != self.numCurrentBlock and not self.forceStop):
                print("DATA equivocat rebut o perdut, re-enviant ACK/petició...")
                self.__sendPacket(packetDataRequest)
                packet = self.__readDATA()

            if(self.forceStop):
                break

            # Guardar les dades rebudes en el buffer de sortida
            self.bufferDataOut.pushBytes(packet.getDataEncoded())

            # Crear ACK i enviar
            packetDataRequest = self.__makeACK()
            self.__sendPacket(packetDataRequest)
            self.__incrementNumCurrentBlock()

            # Finalitzar si es detecta final de les dades
            if(len(packet.getDataEncoded()) < self.blockSize):
                self.bufferInClose()

    # Iniciar el procés de rebre dades i capturar els possibles errors en el 
    # thread
    def __recvDataThread(self, packetDataRequest):
        try:
            self.__recvData(packetDataRequest)
        except Exception as e:
            print("La recepció de dades ha acabat degut a una excepció: " + str(e))
            self.bufferInClose()

    # make PUT/GET ------------------------------------------------------------
    # Inicialitzar transmissió per fer un PUT i executar-ho en un altre thread
    def makePUT(self, filename):
        # Inicialtizar paràmetres
        self.dataSender = True

        # Crear paquet WRQ
        packet = PacketTFTP()
        packet.setOpcode(OpcodeTFTP.WRQ())
        packet.setFilename(filename)
        packet.setMode(self.mode)
        packet.setOption("blksize", self.blockSize)

        # Enviar WRQ
        self.__sendPacket(packet)

        # Esperar per un OACK/ACK
        while True:
            pkg = self.__readPacket([OpcodeTFTP.OACK(), OpcodeTFTP.ACK()])

            if(pkg.getOpcode() == OpcodeTFTP.OACK()):
                break
            
            if(pkg.getNumBlock == 0):
                break

            self.__sendPacket(packet)

        # Tractar OACK en cas que es rebi
        if(pkg.getOpcode() == OpcodeTFTP.OACK()):
            opts = pkg.getOptions()
            for opt in opts:
                if (opt == "blksize"):
                    self.blockSize = int(opts["blksize"])
                else:
                    self._sendError(ErrorcodeTFTP.InvalidOptions(), "Opcions de transmissió invalides")
                    self.bufferInClose()
                    print("Opcions al 0ACK rebut invàlides")
                    return False
        else:
            self.blockSize = 512

        # Iniciar thread de enviament de dades
        self.thread = threading.Thread(target=TransmissionTFTP.__sendDataThread, args=(self,))
        self.thread.start()

    # Inicialitzar transmissió per fer un GET i executar-ho en un altre thread
    def makeGET(self, filename):
        # Inicialtizar paràmetres
        self.dataReciever = True

        # Crear paquet RRQ
        packet = PacketTFTP()
        packet.setOpcode(OpcodeTFTP.RRQ())
        packet.setFilename(filename)
        packet.setMode(self.mode)
        packet.setOption("blksize", self.blockSize)

        # Enviar RRQ
        self.__sendPacket(packet)

        # Esperar per un OACK/ACK
        while True:
            pkg = self.__readPacket([OpcodeTFTP.OACK(), OpcodeTFTP.DATA()])

            if(pkg.getOpcode() == OpcodeTFTP.OACK()):
                break
            
            if(pkg.getNumBlock == 0):
                break

            self.__sendPacket(packet)

        # Tractar OACK en cas que es rebi
        if(pkg.getOpcode() == OpcodeTFTP.OACK()):
            opts = pkg.getOptions()
            for opt in opts:
                if (opt == "blksize"):
                    self.blockSize = int(opts["blksize"])
                else:
                    self._sendError(ErrorcodeTFTP.InvalidOptions, "Opcions de resposta invàlides")
                    self.bufferInClose()
                    print("Opcions al  0ACK rebut invàlides")
                    return False

            # Enviar ACK0 per reconeixer el OACK
            self.numCurrentBlock = 0
            packet = self.__makeACK()
            self.__sendPacket(packet)
        else:
            self.blockSize = 512

        # Iniciar thread de recepció de dades
        self.thread = threading.Thread(target=TransmissionTFTP.__recvDataThread, args=(self,packet,))
        self.thread.start()

    # server ------------------------------------------------------------------
    # Inicialitzar per fer una transmissió per part del servidor
    def startServerTransmission(self, dataSender):
        # Inicialtizar paràmetres
        self.dataReciever  = not dataSender
        self.dataSender    =     dataSender
        self.originUpdated = True
        self.server        = True

        if(self.dataReciever):
            # Enviar confirmació d'inici del PUT
            if(self.hasRecognizedOptions):
                # Enviar OACK
                packet = self.__makeOACK()
                self.__sendPacket(packet)
            else:
                # Enviar ACK0
                packet = self.__makeACK()
                self.__sendPacket(packet)

            # Iniciar thread de recepció de dades
            self.thread = threading.Thread(target=TransmissionTFTP.__recvDataThread, args=(self,packet,))
        else:
            # Enviar confirmació d'inici del GET en cas que hi hagi opcions per reconèixer
            if(self.hasRecognizedOptions):
                # Enviar OACK
                packet = self.__makeOACK()
                self.__sendPacket(packet)

                # Esperar per ACK0
                while(self.__readACK() != 0 and not self.forceStop):
                    self.__sendPacket(packet)
                
                if(self.forceStop):
                    print("Error al llegir ACK0")
                    self.bufferInClose()
                    
            # Iniciar thread d'enviament de dades
            self.thread = threading.Thread(target=TransmissionTFTP.__sendDataThread, args=(self,))

        self.thread.start()

    # Seleccionar opcions reconegudes
    def setRecognizedServerOptions(self, opts):
        self.hasRecognizedOptions = True
        self.recognizedOptions = opts

    # send/read data -----------------------------------------------------------
    # Posar dades codificades en el buffer de entrada
    def sendData(self, data):
        if(self.mode == "octet"):
            self.bufferDataIn.pushBytes(data)

    # Recuperar dades codificades en el buffer del buffer de sortida
    def readData(self, length):
        if(self.mode == "octet"):
            return self.bufferDataOut.popBytes(length)
        else:
            return bytes()

    # Posar text en el buffer de entrada
    def sendText(self, text):
        if(self.mode != "netascii"):
            return
        
        # Convert to ascii
        data = bytearray(text.encode(encoding = "ascii", errors = "replace"))

        # Replace all CR from the string to CRNUL
        data.replace(b"\r", b"\r\0")
        # Replace all LF from the string to CRLF
        data.replace(b"\n", b"\r\n")

        # Filter bytes
        def isNetasciiByte(val):
            return (0x20 <= val and val <= 0x7f) or (0x07 <= val and val <= 0x13) or (val == 0x00)
        filteredData = filter(isNetasciiByte, data)

        # Store byes
        self.bufferDataIn.pushBytes(bytes(filteredData))

    # Recuperar text en el buffer del buffer de sortida
    def readText(self, length):
        if(self.mode == "netascii"):
            data = self.bufferDataOut.popBytes(length)
            return data.decode(encoding = "ascii", errors = "replace")
        else:
            return ""

    # buffer control ----------------------------------------------------------
    # Tancar el buffer d'entrada
    def bufferInClose(self):
        self.bufferDataInOpen = False

    # Consultar si el buffer d'entrada es obert
    def isBufferInOpened(self):
        return self.bufferDataInOpen

    # Consultar si el buffer de sortida te dades disponibles
    def isBufferOutWithData(self):
        return (0 < self.bufferDataOut.getNumBytes())

    # other -------------------------------------------------------------------
    # Seleccionar a quin host enviar les dades
    def setPeer(self, hostname = "localhost", welcomePort = 69, defTimeout = 1):
        # Set internal vars
        self.hostname = hostname
        self.port = welcomePort
        self.originUpdated = False

        # Create socket
        self.socket = socket(AF_INET,SOCK_DGRAM)
        self.socket.settimeout(defTimeout)
        print("Socket UDP creat per enviar missatges a [" + hostname + "]:[" + str(welcomePort) + "]")

    # Enviar error
    def _sendError(self, errorcode, errormessage):
        errorPacket = PacketTFTP()
        errorPacket.setOpcode(OpcodeTFTP.ERROR())
        errorPacket.setErrorcode(errorcode)
        errorPacket.setErrorMsg(errormessage)
        self.__sendPacket(errorPacket)

    # Enviar error i interrompre la transmissió
    def sendErrorAndStop(self, errorcode, errormessage):
        self.forceStop = True
        self._sendError(errorcode, errormessage)
        self.bufferInClose()
        self.thread.join()

    # Esperar a que finalitzi la transmissió
    def waitForTransmissionCompletion(self):
        self.thread.join()

    # Recuperar blocksize configurat
    def getBlockSize(self):
        return self.blockSize

    # Enllaçar socket intern a una adreça i port determinats
    def bind(self, listenAdress, port):
        self.socket.bind((listenAdress, port))

    # Tancar socket intern
    def closeInternalSocket(self):
        self.socket.close()

    # Recuperar mode de transmissió
    def getMode(self):
        return self.mode
