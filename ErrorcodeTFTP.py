
# Clase auxiliar per definir els codis d'error y els seu texts
class ErrorcodeTFTP:
    def __init__(self, value, meaning):
        self.value = value
        self.meaning = meaning
    
    def __eq__(self, other):
        return self.value == other.value

    @staticmethod
    def NULL():
        return ErrorcodeTFTP(0, "No definit, mirar missatge d'error (si n'hi ha).")

    @staticmethod
    def FileNotFound():
        return ErrorcodeTFTP(1, "Fitxer no trobat.")

    @staticmethod
    def AccessViolation():
        return ErrorcodeTFTP(2, "Access denegat.")
        
    @staticmethod
    def DiskFull():
        return ErrorcodeTFTP(3, "Disc ple.")
        
    @staticmethod
    def IlegalTFTPOperation():
        return ErrorcodeTFTP(4, "Operació TFTP no vàlida.")

    @staticmethod
    def UnknownTransferID():
        return ErrorcodeTFTP(5, "ID de transmissió desconegut.")

    @staticmethod
    def AlreadyExists():
        return ErrorcodeTFTP(6, "El fitxer ja existeix.")

    @staticmethod
    def NoSuchUser():
        return ErrorcodeTFTP(7, "Usuari inexistent.")

    @staticmethod
    def InvalidOptions():
        return ErrorcodeTFTP(8, "Opcions no vàlides.")

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
