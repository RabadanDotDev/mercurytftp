from OpcodeTFTP import *
from ErrorcodeTFTP import *

# Classe per facilitar la creació y repcepció de paquets TFTP
class PacketTFTP:
    # Common ------------------------------------------------------------------
    def __init__(self):
        self._options = {}

    # Obtenir string que representa el paquet. Assumeix que el paquet esta ben 
    # format si el opcode no es NULL.
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

    # Obtenir string de la llista d'opcions com s'afegiria al RRQ/WRQ
    def strOptions(self):
        txt = ""
        for k in self._options:
            txt += "[\"" + k + "\"]" + "[0]" + "[\"" + self._options[k] + "\"]" + "[0]" 
        return txt

    # Definir el paquet segons bytes rebuts. Si el opcode es correcte, asumeix 
    # que la resta del paquet també ho es
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

    # Obtenir el paquet codificat en binari. Assumeix que el paquet esta ben 
    # format si el opcode no es NULL.
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
    # Seleccionar el codi d'operació del paquet
    def setOpcode(self, opcode):
        self._opcode = opcode

    # Recuperar el codi d'operació del paquet
    def getOpcode(self):
        return self._opcode

    # Seleccionar el codi d'operació a partir de la versió codificada bytes d'aquest
    def setOpcodeEncoded(self, opcode):
        self._opcode = OpcodeTFTP.from_int(int.from_bytes(opcode, byteorder='big'))

    # Recuperar el codi d'operació del paquet en forma codificada
    def getOpcodeEncoded(self):
        return self._opcode.value.to_bytes(2, byteorder='big')

    # Filename ----------------------------------------------------------------
    # Seleccionar el nom d'arxiu per un RRQ/WRQ
    def setFilename(self, filename):
        filenameAsciiConverted = filename.encode(encoding='ascii', errors="ignore").decode(encoding='ascii')
        self._filename = filenameAsciiConverted

    # Obtenir el nom de l'arxiu seleccionat
    def getFilename(self):
        return self._filename

    # Seleccionar el nom d'arxiu per un RRQ/WRQ a partir de la versió 
    # codificada d'aquest
    def setFilenameEncoded(self, filename):
        self._filename = filename.decode(encoding='ascii', errors="ignore")

    # Recuperar el nom de l'arxiu seleccionat en forma codificada
    def getFilenameEncoded(self):
        return self._filename.encode(encoding='ascii', errors="ignore")
    
    # Mode --------------------------------------------------------------------
    # Seleccionar el mode de transmissió per un RRQ/WRQ
    def setMode(self, mode):
        modeAsciiConverted = mode.encode(encoding='ascii', errors="ignore").decode(encoding='ascii')
        self._mode = modeAsciiConverted
    
    # Recuperar el mode de transmissió seleccionat
    def getMode(self):
        return self._mode

    # Seleccionar el mode de transmissió per un RRQ/WRQ a partir de la versió 
    # codificada d'aquest
    def setModeEncoded(self, mode):
        self._mode = mode.decode(encoding='ascii', errors="ignore")

    # Recuperar  el mode de transmissió seleccionat en forma codificada
    def getModeEncoded(self):
        return self._mode.encode(encoding='ascii', errors="ignore")

    # setOption ---------------------------------------------------------------
    # Seleccionar/definir el valor d'una opció
    def setOption(self, optionName, optionVal):
        self._options[optionName] = str(optionVal)

    # Recuperar el valor d'una opció
    def getOption(self, optionName):
        try:
            return self._options[optionName]
        except KeyError:
            return ""

    # Recuperar totes les opcions definides
    def getOptions(self):
        return self._options

    # Seleccionar/definir el valor d'una opció a partir de la versió codificada 
    # d'aquest
    def setOptionEncoded(self, optionNameEncoded, optionValEncoded):
        self._options[optionNameEncoded.decode(encoding='ascii')] = optionValEncoded.decode(encoding="ascii")

    # Seleccionar/definir el valor d'una opció a partir de una llista de opcions
    # codificades
    def setOptionsEncodedParts(self, encodedParts):
        it = iter(encodedParts)
        for optionNameEncoded, optionValEncoded in zip(it, it):
            self.setOptionEncoded(optionNameEncoded, optionValEncoded)

    # Recuperar el valor d'una opció en forma codificada
    def getOptionEncoded(self, optionName):
        try:
            return (self._options[optionName] + '\0').encode(encoding='ascii', errors="ignore")
        except KeyError:
            return bytes()

    # Recuperar el valor de totes les opcions en forma codificada separades per '\0'
    def getOptionsEncoded(self):
        # Encode options and values
        opsEncoded = [[op.encode(), self._options[op].encode()] for op in self._options]
        # Join options and values
        opsEncoded = [b'\0'.join(pair) for pair in opsEncoded]
        # Join all options and return
        return b'\0'.join(opsEncoded)

    # NumBlock  ---------------------------------------------------------------
    # Seleccionar el número de bloc d'un ACK/DATA/OACK
    def setNumBlock(self, numBlock):
        self._numBlock = numBlock

    # Recuperar el número de bloc d'un ACK/DATA/OACK
    def getNumBlock(self):
        return self._numBlock

    # Seleccionar el número de bloc d'un ACK/DATA/OACK a partir de la versió 
    # codificada
    def setNumBlockEncoded(self, numBlock):
        self._numBlock = int.from_bytes(numBlock, byteorder='big')

    # Recuperar el número de bloc d'un ACK/DATA/OACK en forma codificada
    def getNumBlockEncoded(self):
        return self._numBlock.to_bytes(2, byteorder='big')

    # Data  -------------------------------------------------------------------
    # Introducció de dades d'un paquet DATA
    def setDataEncoded(self, data):
        self._data = data

    # Recuperació de dades d'un paquet DATA
    def getDataEncoded(self):
        return self._data

    # Error -------------------------------------------------------------------
    # Selecció del errorcode d'un paquet ERROR
    def setErrorcode(self, errorcode):
        self._errorcode = errorcode
    
    # Selecció del errorcode d'un paquet ERROR a partir de la versió codificada
    def setErrorcodeEncoded(self, errorcodeEncoded):
        self._errorcode = ErrorcodeTFTP.from_int(int.from_bytes(errorcodeEncoded, byteorder='big'))

    # Recuperació del errorcode d'un paquet ERROR
    def getErrorcode(self):
        return self._errorcode
    
    # Recuperació del errorcode d'un paquet ERROR en forma codificada
    def getErrorcodeEncoded(self):
        return (self._errorcode.value).to_bytes(2, byteorder='big')
    
    # Introducció del missatge d'un paquet ERROR
    def setErrorMsg(self, msg):
        self._errorMsg = msg
    
    # Recuperació del missatge d'un paquet ERROR
    def getErrorMsg(self):
        return self._errorMsg

    # Introducció del missatge d'un paquet ERROR a partir de la versió 
    # codificada
    def setErrorMsgEncoded(self, msgEncoded):
        self._errorMsg = msgEncoded.decode(encoding='ascii', errors="ignore")

    # Recuperació del missatge d'un paquet d'ERROR en forma codificada
    def getErrorMsgEncoded(self):
        return self._errorMsg.encode(encoding='ascii', errors="ignore")
    

