# MercuryTFTP
🌏 [**Català**](https://github.com/RabadanDotDev/mercurytftp/blob/main/README.md),
[**English**](https://github.com/RabadanDotDev/mercurytftp/blob/main/README.en.md)

## Description
MercuryTFTP is a client and server written in Python and developed as a project of the subject of computer networking (XACO) of the Universitat Politècnica de Catalunya Barcelona Tech (UPC) that allows interoperable transmissions using the TFTP protocol. Complies with the following RFCs:
- [**RFC 1350**](https://tools.ietf.org/html/rfc1350) (The TFTP Protocol (Revision 2)),
- [**RFC 2347**](https://tools.ietf.org/html/rfc2347) (TFTP Option Extension)
- [**RFC 2348**](https://tools.ietf.org/html/rfc2348) (TFTP Blocksize Option).

## Basic usage
### Server
Clone the directory, create a folder where the files will be stored and run.
```sh
git clone https://github.com/RabadanDotDev/mercurytftp.git
mkdir ./mercurytftp/server_files
cd mercurytftp/server_files
python3 ../server.py
```

### Client
Clone the directory, create a folder where the files will be stored and run.
```sh
git clone https://github.com/RabadanDotDev/mercurytftp.git
mkdir ./mercurytftp/client_files
cd mercurytftp/client_files
python3 ../client.py
```
The following will be requested (in Catalan): the name of the server (by default, testxaco.rabadan.dev), the port, the command to be made (GET or PUT), the transmission mode (octet or netascii) and the name of the file to be transferred.
