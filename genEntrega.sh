#!/usr/bin/env sh

cat BytesFIFO.py separator.txt OpcodeTFTP.py separator.txt PacketTFTP.py separator.txt TransmissionTFTP.py separator.txt client.py | grep -vE "(^from.*|#\!|import .*)" | cat header.txt separator.txt  - > TFTPClient_Rabadan-Raul_Perez-Jaume_entrega_4.py
chmod +x TFTPClient_Rabadan-Raul_Perez-Jaume_entrega_4.py

cat BytesFIFO.py separator.txt OpcodeTFTP.py separator.txt PacketTFTP.py separator.txt TransmissionTFTP.py separator.txt ServerTFTP.py separator.txt server.py | grep -vE "(^from.*|#\!|import .*)" | cat header.txt separator.txt  - > TFTPServidor_Rabadan-Raul_Perez-Jaume_entrega_4.py
chmod +x TFTPServidor_Rabadan-Raul_Perez-Jaume_entrega_4.py
