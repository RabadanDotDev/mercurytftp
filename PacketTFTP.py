from OpcodeTFTP import *

class PacketTFTP:
    # Common ------------------------------------------------------------------
    def __init__(self):
        self.options = {}
    
    def __str__(self):
        if(self.getOpcode() == OpcodeTFTP.NULL()):
            return  "[" + self.getOpcode().name + "]"

        if(self.getOpcode() == OpcodeTFTP.RRQ() or self.getOpcode() == OpcodeTFTP.WRQ()):
            return  "[" + self.getOpcode().name                        + "]" + \
                    "[" + '\"' + self.getFilename()             + '\"' + "]" + \
                    "[" + "0"                                          + "]" + \
                    "[" + '\"' + self.getMode()                 + '\"' + "]" + \
                    "[" + "0"                                          + "]" + \
                    "[" + '\"' + self.getNonStandardBlockSize() + '\"' + "]" + \
                    "[" + "0"                                          + "]"

        if(self.getOpcode() == OpcodeTFTP.DATA()):
            return  "[" + self.getOpcode().name                      + "]" + \
                    "[" + str(self.getNumBlock())                    + "]" + \
                    "[" + str(len(self.getDataEncoded())) + " bytes" + "]"

        if(self.getOpcode() == OpcodeTFTP.ACK()):
            return  "[" + self.getOpcode().name   + "]" + \
                    "[" + str(self.getNumBlock()) + "]"

    def setEncoded(self, rawPacket):
        self.setOpcodeEncoded(rawPacket[0:2])

        if(self.getOpcode() == OpcodeTFTP.RRQ() or self.getOpcode() == OpcodeTFTP.WRQ()):
            parts = rawPacket[2:len(rawPacket)].split(b'\0')
            self.setFilenameEncoded(parts[0])
            self.setModeEncoded(parts[1])
            self.setNonStandardBlockSizeEncoded(parts[2])

        if(self.getOpcode() == OpcodeTFTP.DATA()):
            self.setNumBlockEncoded(rawPacket[2:4])
            self.setDataEncoded(rawPacket[4:len(rawPacket)])

        if(self.getOpcode() == OpcodeTFTP.ACK()):
            self.setNumBlockEncoded(rawPacket[2:4])

    def getEncoded(self):
        if(self.getOpcode() == OpcodeTFTP.RRQ() or self.getOpcode() == OpcodeTFTP.WRQ()):
            return  self.getOpcodeEncoded() + \
                    self.getFilenameEncoded() + \
                    (0).to_bytes(1, byteorder='big') + \
                    self.getModeEncoded() + \
                    (0).to_bytes(1, byteorder='big') + \
                    self.getNonStandardBlockSizeEncoded() + \
                    (0).to_bytes(1, byteorder='big')

        if(self.getOpcode() == OpcodeTFTP.DATA()):
            return  self.getOpcodeEncoded() + \
                    self.getNumBlockEncoded() + \
                    self.getDataEncoded()   

        if(self.getOpcode() == OpcodeTFTP.ACK()):
            return  self.getOpcodeEncoded() + \
                    self.getNumBlockEncoded()

    # Opcode ------------------------------------------------------------------
    def setOpcode(self, opcode):
        self._opcode = opcode

    def getOpcode(self):
        return self._opcode

    def setOpcodeEncoded(self, opcode):
        self._opcode= OpcodeTFTP.from_int(int.from_bytes(opcode, byteorder='big'))

    def getOpcodeEncoded(self):
        return self._opcode.value.to_bytes(2, byteorder='big')

    # Filename ----------------------------------------------------------------
    def setFilename(self, filename):
        filenameAsciiConverted = filename.encode(encoding='ascii', errors="ignore").decode(encoding='ascii')
        self._filename = filenameAsciiConverted

    def getFilename(self):
        return self._filename

    def setFilenameEncoded(self, filename):
        self._filename = filename.decode(encoding='ascii', errors="ignore")

    def getFilenameEncoded(self):
        return self._filename.encode(encoding='ascii', errors="ignore")
    
    # Mode --------------------------------------------------------------------
    def setMode(self, mode):
        modeAsciiConverted = mode.encode(encoding='ascii', errors="ignore").decode(encoding='ascii')
        self._mode = modeAsciiConverted
    
    def getMode(self):
        return self._mode

    def setModeEncoded(self, mode):
        self._mode = mode.decode(encoding='ascii', errors="ignore")

    def getModeEncoded(self):
        return self._mode.encode(encoding='ascii', errors="ignore")

    # setOption ---------------------------------------------------------------
    def setOption(self, optionName, optionVal):
        self.options[optionName] = optionVal

    def getOption(self, optionName):
        try:
            return self.options[optionName]
        except KeyError:
            return ""

    def getOptions(self):
        return self.options

    def setOptionsEncodedParts(self, encodedParts):
        encodedParts = 

    def getOptionEncoded(self, optionName):
        try:
            return (self.options[optionName] + '\0').encode(encoding='ascii', errors="ignore")
        except KeyError:
            return bytes()

    def getOptionsEncoded(self):
        # Encode options and values
        opsEncoded = [[op.encode(), self.options[op].encode()] for op in self.options]
        # Join options and values
        opsEncoded = [b'\0'.join(pair) for pair in opsEncoded]
        # Join all options and return
        return b'\0'.join(opsEncoded)
        

    # NumBlock  ---------------------------------------------------------------
    def setNumBlock(self, numBlock):
        self._numBlock = numBlock

    def getNumBlock(self):
        return self._numBlock

    def setNumBlockEncoded(self, numBlock):
        self._numBlock = int.from_bytes(numBlock, byteorder='big')

    def getNumBlockEncoded(self):
        return self._numBlock.to_bytes(2, byteorder='big')

    # Data  -------------------------------------------------------------------
    def setDataEncoded(self, data):
        self._data = data

    def getDataEncoded(self):
        return self._data
