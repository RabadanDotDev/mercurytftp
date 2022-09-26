# MercuryTFTP
🌏 [**Català**](https://github.com/RabadanDotDev/mercurytftp/blob/main/README.md),
[**English**](https://github.com/RabadanDotDev/mercurytftp/blob/main/README.en.md)

## Descripció
MercuryTFTP és un client i servidor escrit en Python i desenvolupat com a projecte de l'assignatura de xarxes d'ordinadors (XACO) de la Universitat Politècnica de Catalunya Barcelona Tech (UPC) que permet realitzar transmissions interoperables utilitzant el protocol TFTP. Compleix amb les RFC:
- [**RFC 1350**](https://tools.ietf.org/html/rfc1350) (The TFTP Protocol (Revision 2)),
- [**RFC 2347**](https://tools.ietf.org/html/rfc2347) (TFTP Option Extension)
- [**RFC 2348**](https://tools.ietf.org/html/rfc2348) (TFTP Blocksize Option).

## Utilització bàsica
### Servidor
Clonar el directori, crear una carpeta per contenir els arxius i executar.
```sh
git clone https://github.com/RabadanDotDev/mercurytftp.git
mkdir ./mercurytftp/server_files
cd mercurytftp/server_files
python3 ../server.py
```

### Client
Clonar el directori, crear una carpeta per contenir els arxius i executar.
```sh
git clone https://github.com/RabadanDotDev/mercurytftp.git
mkdir ./mercurytftp/client_files
cd mercurytftp/client_files
python3 ../client.py
```
Es demanarà el nom del servidor (per defecte testxaco.rabadan.dev), el port, la comanda a fer (GET o PUT), el mode de transmissió (octet o netascii) i el nom del fitxer a transferir.
