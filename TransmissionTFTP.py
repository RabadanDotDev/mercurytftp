import threading
import time
from socket import *
from OpcodeTFTP import *
from PacketTFTP import *
from BytesFIFO  import *
from ExceptionTFTP  import *

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

        print("TransmissionTFTP created with blocksize: [" + str(blockSize) + "] and mode [" + mode + "].")

    def __incrementNumCurrentBlock(self):
        self.numCurrentBlock = (self.numCurrentBlock + 1) % 65536

    # send/read packet --------------------------------------------------------
    def __sendPacket(self, packet):
        while True:
            try:
                self.socket.sendto(packet.getEncoded(), (self.hostname, self.port))
                self.numPacketsSentRecv += 1
            except Exception as e:
                print("Error sending packet (" + str(self.numPacketsSentRecv) + "): " + str(e) + ". Retrying in 2 seconds...")
                time.sleep(2)
            else:
                print("Packet (" + str(self.numPacketsSentRecv) +  "º) sent: " + str(packet))
                return
    
    def __readPacket(self, expectedOpcodes):
        while True:
            # Recieve packet
            packet = PacketTFTP()

            try:
                (recievedData, origin) = self.socket.recvfrom(self.maxPacketSize)
            except OSError as o:
                packet.setOpcode(OpcodeTFTP.NULL())
                packet.setNumBlock(-1)
                print("Error on read packet: " + str(o))
                return packet

            packet.setEncoded(recievedData)

            print("Packet (" + str(self.numPacketsSentRecv) +  "º) recived: "          \
                    + str(origin[0]) + ":" + str(origin[1]) + "->" + str(packet) + " " \
                    + "Expected opcodes: " + ' '.join([o.name for o in expectedOpcodes]) + " " \
                    + "Current seq number: " + str(self.numCurrentBlock)               \
                )
            self.numPacketsSentRecv += 1

            # Reply with an error packet if the origin doesn't match
            if((origin[0] != self.hostname or origin[1] != self.port) and self.originUpdated):
                errorPacket = PacketTFTP()
                errorPacket.setErrorcode(ErrorcodeTFTP.UnknownTransferID())
                errorPacket.setErrorMsg("")
                self.__sendPacket(errorPacket)
            elif(not self.originUpdated):
                (self.hostname, self.port) = origin

            # The origin can only change in the first packet reception
            self.originUpdated = True

            # Check if the packet is an ERROR packet
            if(packet.getOpcode() == OpcodeTFTP.ERROR()):
                raise ExceptionTFTP(packet.getErrorcode().meaning + " " + packet.getErrorMsg())

            # Check if the packet is a NULL packet
            if(packet.getOpcode() == OpcodeTFTP.NULL()):
                errorPacket = PacketTFTP()
                errorPacket.setErrorcode(ErrorcodeTFTP.IlegalTFTPOperation())
                errorPacket.setErrorMsg("")
                self.__sendPacket(errorPacket)
                raise ExceptionTFTP("Malformed package recieved.")

            # Return if it matches, drop it otherwise
            if(packet.getOpcode() in expectedOpcodes):
                return packet

    # make/read Data ----------------------------------------------------------
    def __makeDATA(self):
        # Read data from buffer
        while (self.bufferDataInOpen and \
            self.bufferDataIn.getNumBytes() < self.blockSize):
            time.sleep(0.001)
        data = self.bufferDataIn.popBytes(self.blockSize)

        # Build DATA packet
        packet = PacketTFTP()
        packet.setOpcode(OpcodeTFTP.DATA())
        packet.setNumBlock(self.numCurrentBlock)
        packet.setDataEncoded(data)

        return packet

    def __readDATA(self):
        while not self.forceStop:
            # Wait for DATA packet
            packet = self.__readPacket([OpcodeTFTP.DATA()])

            # Return
            return packet

        packet = PacketTFTP()
        packet.setOpcode(OpcodeTFTP.NULL())
        packet.setNumBlock(-1)
        
    # make/read ACK -----------------------------------------------------------
    def __makeACK(self):
        # Build ACK packet
        packet = PacketTFTP()
        packet.setOpcode(OpcodeTFTP.ACK())
        packet.setNumBlock(self.numCurrentBlock)

        # Return
        return packet

    def __makeOACK(self):
        # Build OACK packet
        packet = PacketTFTP()
        packet.setOpcode(OpcodeTFTP.OACK())
        for opt in self.recognizedOptions:
            packet.setOption(opt, self.recognizedOptions[opt])

        # Return
        return packet

    def __readACK(self):
        while not self.forceStop:
            packet = self.__readPacket([OpcodeTFTP.ACK()])
            return packet.getNumBlock()

        return -1

    # send/recv dataThread ----------------------------------------------------
    def __sendData(self):
        self.numCurrentBlock = 1

        while not self.forceStop:
            # Construct next DATA packet from input buffer
            packet = self.__makeDATA()

            # Send the packet until confirmation
            self.__sendPacket(packet)
            while (self.__readACK() != self.numCurrentBlock and not self.forceStop):
                print("Wrong ACK recieved or lost, resending DATA...")
                self.__sendPacket(packet)

            if(self.forceStop):
                break

            # Calculate next sequence number
            self.__incrementNumCurrentBlock()

            # End thread if done
            if(len(packet.getDataEncoded()) < self.blockSize):
                break

    def __sendDataThread(self):
        try:
            self.__sendData()
        except Exception as e:
            print("Send data thread ended because an exception occured: " + str(e))
            self.bufferInClose()

    def __recvData(self, packetDataRequest):
        self.numCurrentBlock = 1

        while self.isBufferInOpened() and not self.forceStop:
            packet = self.__readDATA()

            # Send old ACK/dataRequest if its not the expected num     
            while (packet.getNumBlock() != self.numCurrentBlock and not self.forceStop):
                print("Wrong DATA recieved or lost, resending ACK/request...")
                self.__sendPacket(packetDataRequest)
                packet = self.__readDATA()

            if(self.forceStop):
                break

            # Store it
            self.bufferDataOut.pushBytes(packet.getDataEncoded())

            # Send ACK/dataRequest
            packetDataRequest = self.__makeACK()
            self.__sendPacket(packetDataRequest)
            self.__incrementNumCurrentBlock()

            # End thread if done
            if(len(packet.getDataEncoded()) < self.blockSize):
                self.bufferInClose()

    def __recvDataThread(self, packetDataRequest):
        try:
            self.__recvData(packetDataRequest)
        except Exception as e:
            print("Recv data thread ended because an exception occured: " + str(e))
            self.bufferInClose()

    def setPeer(self, hostname = "localhost", welcomePort = 69, defTimeout = 1):
        # Set internal vars
        self.hostname = hostname
        self.port = welcomePort
        self.originUpdated = False

        # Create socket
        self.socket = socket(AF_INET,SOCK_DGRAM)
        self.socket.settimeout(defTimeout)
        print("Created UDP socket to send messages to [" + hostname + "]:[" + str(welcomePort) + "]")

    # make PUT/GET ------------------------------------------------------------
    def makePUT(self, filename):
        # Init params
        self.dataSender = True

        # Build WRQ packet
        packet = PacketTFTP()
        packet.setOpcode(OpcodeTFTP.WRQ())
        packet.setFilename(filename)
        packet.setMode(self.mode)
        packet.setOption("blksize", self.blockSize)

        # Send WRQ
        self.__sendPacket(packet)

        # Wait for an OACK/ACK
        while True:
            pkg = self.__readPacket([OpcodeTFTP.OACK(), OpcodeTFTP.ACK()])

            if(pkg.getOpcode() == OpcodeTFTP.OACK()):
                break
            
            if(pkg.getNumBlock == 0):
                break

            self.__sendPacket(packet)

        if(pkg.getOpcode() == OpcodeTFTP.OACK()):
            opts = pkg.getOptions()
            for opt in opts:
                if (opt == "blksize"):
                    self.blockSize = int(opts["blksize"])
                else:
                    self._sendError(ErrorcodeTFTP.InvalidOptions, "Invalid response options")
                    self.bufferInClose()
                    print("Invalid options in OACK recieved")
                    return False
        else:
            self.blockSize = 512

        # Send data
        self.thread = threading.Thread(target=TransmissionTFTP.__sendDataThread, args=(self,))
        self.thread.start()

    def makeGET(self, filename):
        # Init params
        self.dataReciever = True

        # Build RRQ packet
        packet = PacketTFTP()
        packet.setOpcode(OpcodeTFTP.RRQ())
        packet.setFilename(filename)
        packet.setMode(self.mode)
        packet.setOption("blksize", self.blockSize)

        # Send RRQ
        self.__sendPacket(packet)

        # Wait for an OACK/DATA
        while True:
            pkg = self.__readPacket([OpcodeTFTP.OACK(), OpcodeTFTP.DATA()])

            if(pkg.getOpcode() == OpcodeTFTP.OACK()):
                break
            
            if(pkg.getNumBlock == 0):
                break

            self.__sendPacket(packet)

        if(pkg.getOpcode() == OpcodeTFTP.OACK()):
            opts = pkg.getOptions()
            for opt in opts:
                if (opt == "blksize"):
                    self.blockSize = int(opts["blksize"])
                else:
                    self._sendError(ErrorcodeTFTP.InvalidOptions, "Invalid response options")
                    self.bufferInClose()
                    print("Invalid options in OACK recieved")
                    return False
        else:
            self.blockSize = 512

        # Send ACK0 to begin the transmission
        self.numCurrentBlock = 0
        packet = self.__makeACK()
        self.__sendPacket(packet)

        # Recv data
        self.thread = threading.Thread(target=TransmissionTFTP.__recvDataThread, args=(self,packet,))
        self.thread.start()

    # server ------------------------------------------------------------------
    def startServerTransmission(self, dataSender):
        self.dataReciever  = not dataSender
        self.dataSender    =     dataSender
        self.originUpdated = True
        self.server        = True

        if(self.dataReciever):
            if(self.hasRecognizedOptions):
                # Send OACK
                packet = self.__makeOACK()
                self.__sendPacket(packet)
            else:
                # Send ACK0
                packet = self.__makeACK()
                self.__sendPacket(packet)

            # Start receieve data thread
            self.thread = threading.Thread(target=TransmissionTFTP.__recvDataThread, args=(self,packet,))
        else:
            if(self.hasRecognizedOptions):
                # Send OACK
                packet = self.__makeOACK()
                self.__sendPacket(packet)

                # Wait for ACK0
                while(self.__readACK() != 0 and not self.forceStop):
                    self.__sendPacket(packet)
                
                if(self.forceStop):
                    print("Error in reading ACK0")
                    self.bufferInClose()
                    
            # Start send data thread
            self.thread = threading.Thread(target=TransmissionTFTP.__sendDataThread, args=(self,))

        self.thread.start()

    # send/read data -----------------------------------------------------------
    def sendData(self, data):
        if(self.mode == "octet"):
            self.bufferDataIn.pushBytes(data)

    def readData(self, length):
        if(self.mode == "octet"):
            return self.bufferDataOut.popBytes(length)
        else:
            return bytes()

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

    def readText(self, length):
        if(self.mode == "netascii"):
            data = self.bufferDataOut.popBytes(length)
            return data.decode(encoding = "ascii", errors = "replace")
        else:
            return ""

    # buffer control ----------------------------------------------------------

    def bufferInClose(self):
        self.bufferDataInOpen = False

    def isBufferInOpened(self):
        return self.bufferDataInOpen

    def isBufferOutWithData(self):
        return (0 < self.bufferDataOut.getNumBytes())

    # other -------------------------------------------------------------------

    def _sendError(self, errorcode, errormessage):
        errorPacket = PacketTFTP()
        errorPacket.setOpcode(OpcodeTFTP.ERROR())
        errorPacket.setErrorcode(errorcode)
        errorPacket.setErrorMsg(errormessage)
        self.__sendPacket(errorPacket)

    def sendErrorAndStop(self, errorcode, errormessage):
        self.forceStop = True
        self._sendError(errorcode, errormessage)
        self.bufferInClose()
        self.thread.join()

    def waitForTransmissionCompletion(self):
        self.thread.join()

    def getBlockSize(self):
        return self.blockSize

    def bind(self, listenAdress, port):
        self.socket.bind((listenAdress, port))

    def closeInternalSocket(self):
        self.socket.close()

    def getMode(self):
        return self.mode

    def setRecognizedServerOptions(self, opts):
        self.hasRecognizedOptions = True
        self.recognizedOptions = opts
