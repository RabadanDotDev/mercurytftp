
class ErrorcodeTFTP:
    def __init__(self, value, meaning):
        self.value = value
        self.meaning = meaning
    
    def __eq__(self, other):
        return self.value == other.value

    @staticmethod
    def NULL():
        return ErrorcodeTFTP(0, "Not defined, see error message (if any).")

    @staticmethod
    def FileNotFound():
        return ErrorcodeTFTP(1, "File not found.")

    @staticmethod
    def AccessViolation():
        return ErrorcodeTFTP(2, "Access violation.")
        
    @staticmethod
    def DiskFull():
        return ErrorcodeTFTP(3, "Disk full or allocation exceeded.")
        
    @staticmethod
    def IlegalTFTPOperation():
        return ErrorcodeTFTP(4, "Illegal TFTP operation.")

    @staticmethod
    def UnknownTransferID():
        return ErrorcodeTFTP(5, "Unknown transfer ID.")

    @staticmethod
    def AlreadyExists():
        return ErrorcodeTFTP(6, "File already exists.")

    @staticmethod
    def NoSuchUser():
        return ErrorcodeTFTP(7, "No such user.")

    @staticmethod
    def from_int(v):
        if(v == 1):
            return ErrorcodeTFTP.FileNotFound()
        if(v == 2):
            return ErrorcodeTFTP.AccessViolation()
        if(v == 3):
            return ErrorcodeTFTP.DiskFull()
        if(v == 4):
            return ErrorcodeTFTP.IlegalTFTPOperation()
        if(v == 5):
            return ErrorcodeTFTP.UnknownTransferID()
        if(v == 6):
            return ErrorcodeTFTP.AlreadyExists()
        if(v == 7):
            return ErrorcodeTFTP.NoSuchUser()
        
        ErrorcodeTFTP.NULL()
