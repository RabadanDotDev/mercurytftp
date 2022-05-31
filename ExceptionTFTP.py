class ExceptionTFTP(Exception):
    def __init__(self, mesessage):
        self.message = "Excepció TFTP: " + mesessage
        super().__init__(self.message)
