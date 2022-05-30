
class OpcodeTFTP:
    def __init__(self, value, name):
        self.value = value
        self.name = name
    
    def __eq__(self, other):
        return self.value == other.value

    @staticmethod
    def NULL():
        return OpcodeTFTP(0, "NULL")

    @staticmethod
    def RRQ():
        return OpcodeTFTP(1, "RRQ")

    @staticmethod
    def WRQ():
        return OpcodeTFTP(2, "WRQ")
        
    @staticmethod
    def DATA():
        return OpcodeTFTP(3, "DATA")
        
    @staticmethod
    def ACK():
        return OpcodeTFTP(4, "ACK")

    @staticmethod
    def ERROR():
        return OpcodeTFTP(5, "ERROR")

    @staticmethod
    def OACK():
        return OpcodeTFTP(6, "OACK")

    @staticmethod
    def from_int(v):
        if(v == 1):
            return OpcodeTFTP.RRQ()
        if(v == 2):
            return OpcodeTFTP.WRQ()
        if(v == 3):
            return OpcodeTFTP.DATA()
        if(v == 4):
            return OpcodeTFTP.ACK()
        if(v == 5):
            return OpcodeTFTP.ERROR()
        if(v == 6):
            return OpcodeTFTP.OACK()
        
        OpcodeTFTP.NULL()
