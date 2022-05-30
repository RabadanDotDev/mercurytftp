class ExceptionTFTP(Exception):
    def __init__(self, mesessage):
        self.message = "TFTP exception: " + mesessage
        super().__init__(self.message)
