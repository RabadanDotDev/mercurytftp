from OpcodeTFTP import *
from ErrorcodeTFTP import *

class PacketTFTP:
    # Common ------------------------------------------------------------------
    def __init__(self):
        self._options = {}
    
    def __str__(self):
        if(self.getOpcode() == OpcodeTFTP.NULL()):
            return  "[" + self.getOpcode().name + "]"

        if(self.getOpcode() == OpcodeTFTP.RRQ() or self.getOpcode() == OpcodeTFTP.WRQ()):
            return  "[" + self.getOpcode().name                        + "]" + \
                    "[" + '\"' + self.getFilename()             + '\"' + "]" + \
                    "[" + "0"                                          + "]" + \
                    "[" + '\"' + self.getMode()                 + '\"' + "]" + \
                    "[" + "0"                                          + "]" + \
                    self.strOptions()

        if(self.getOpcode() == OpcodeTFTP.DATA()):
            return  "[" + self.getOpcode().name                      + "]" + \
                    "[" + str(self.getNumBlock())                    + "]" + \
                    "[" + str(len(self.getDataEncoded())) + " bytes" + "]"

        if(self.getOpcode() == OpcodeTFTP.ACK()):
            return  "[" + self.getOpcode().name   + "]" + \
                    "[" + str(self.getNumBlock()) + "]"

        if(self.getOpcode() == OpcodeTFTP.ERROR()):
            return  "[" + self.getOpcode().name       + "]" + \
                    "[" + self.getErrorcode().meaning + "]" + \
                    "[" + self.getErrorMsg()          + "]" + \
                    "[" + "0"                         + "]"
        
        if(self.getOpcode() == OpcodeTFTP.OACK()):
            return  "[" + self.getOpcode().name   + "]" + \
                    self.strOptions()

    def strOptions(self):
        txt = ""
        for k in self._options:
            txt += "[\"" + k + "\"]" + "[0]" + "[\"" + self._options[k] + "\"]" + "[0]" 
        return txt

    def setEncoded(self, rawPacket):
        self.setOpcodeEncoded(rawPacket[0:2])

        if(self.getOpcode() == OpcodeTFTP.RRQ() or self.getOpcode() == OpcodeTFTP.WRQ()):
            parts = rawPacket[2:len(rawPacket)].split(b'\0')
            self.setFilenameEncoded(parts[0])
            self.setModeEncoded(parts[1])
            self.setOptionsEncodedParts(parts[2:])

        if(self.getOpcode() == OpcodeTFTP.DATA()):
            self.setNumBlockEncoded(rawPacket[2:4])
            self.setDataEncoded(rawPacket[4:len(rawPacket)])

        if(self.getOpcode() == OpcodeTFTP.ACK()):
            self.setNumBlockEncoded(rawPacket[2:4])

        if(self.getOpcode() == OpcodeTFTP.ERROR()):
            self.setErrorcodeEncoded(rawPacket[2:4])
            self.setErrorMsgEncoded(rawPacket[4:len(rawPacket)-1])
                    
        if(self.getOpcode() == OpcodeTFTP.OACK()):
            parts = rawPacket[2:len(rawPacket)].split(b'\0')
            self.setOptionsEncodedParts(parts)

    def getEncoded(self):
        if(self.getOpcode() == OpcodeTFTP.RRQ() or self.getOpcode() == OpcodeTFTP.WRQ()):
            return  self.getOpcodeEncoded() + \
                    self.getFilenameEncoded() + \
                    (0).to_bytes(1, byteorder='big') + \
                    self.getModeEncoded() + \
                    (0).to_bytes(1, byteorder='big') + \
                    self.getOptionsEncoded() + \
                    (0).to_bytes(1, byteorder='big')

        if(self.getOpcode() == OpcodeTFTP.DATA()):
            return  self.getOpcodeEncoded() + \
                    self.getNumBlockEncoded() + \
                    self.getDataEncoded()   

        if(self.getOpcode() == OpcodeTFTP.ACK()):
            return  self.getOpcodeEncoded() + \
                    self.getNumBlockEncoded()

        if(self.getOpcode() == OpcodeTFTP.ERROR()):
            return  self.getOpcodeEncoded() + \
                    self.getErrorcodeEncoded() + \
                    self.getErrorMsgEncoded() + \
                    (0).to_bytes(1, byteorder='big')

        if(self.getOpcode() == OpcodeTFTP.OACK()):
            return  self.getOpcodeEncoded() + \
                    self.getOptionsEncoded() + \
                    (0).to_bytes(1, byteorder='big')

    # Opcode ------------------------------------------------------------------
    def setOpcode(self, opcode):
        self._opcode = opcode

    def getOpcode(self):
        return self._opcode

    def setOpcodeEncoded(self, opcode):
        self._opcode = OpcodeTFTP.from_int(int.from_bytes(opcode, byteorder='big'))

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
        self._options[optionName] = optionVal

    def getOption(self, optionName):
        try:
            return self._options[optionName]
        except KeyError:
            return ""

    def getOptions(self):
        return self._options

    def setOptionEncoded(self, optionNameEncoded, optionValEncoded):
        self._options[optionNameEncoded.decode(encoding='ascii')] = optionValEncoded.decode(encoding="ascii")

    def setOptionsEncodedParts(self, encodedParts):
        it = iter(encodedParts)
        for optionNameEncoded, optionValEncoded in zip(it, it):
            self.setOptionEncoded(optionNameEncoded, optionValEncoded)

    def getOptionEncoded(self, optionName):
        try:
            return (self._options[optionName] + '\0').encode(encoding='ascii', errors="ignore")
        except KeyError:
            return bytes()

    def getOptionsEncoded(self):
        # Encode options and values
        opsEncoded = [[op.encode(), self._options[op].encode()] for op in self._options]
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

    # Error -------------------------------------------------------------------
    def setErrorcode(self, errorcode):
        self._errorcode = errorcode
    
    def setErrorcodeEncoded(self, errorcodeEncoded):
        self._errorcode = ErrorcodeTFTP.from_int(int.from_bytes(errorcodeEncoded, byteorder='big'))

    def getErrorcode(self):
        return self._errorcode
    
    def getErrorcodeEncoded(self):
        return (self._errorcode.value).to_bytes(2, byteorder='big')
    
    def setErrorMsg(self, msg):
        self._errorMsg = msg
    
    def getErrorMsg(self):
        return self._errorMsg

    def setErrorMsgEncoded(self, msgEncoded):
        self._errorMsg = msgEncoded.decode(encoding='ascii', errors="ignore")

    def getErrorMsgEncoded(self):
        return self._errorMsg.encode(encoding='ascii', errors="ignore")
    

