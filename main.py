import socket
import numpy as np
import matplotlib.pyplot as plt
import ola
from ola.ClientWrapper import ClientWrapper

# UDP-Empfang
UDP_IP = "0.0.0.0"  # Alle IPs des PCs
UDP_PORT = 12345
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

# OLA Client für DMX
client = ola.ClientWrapper()

# DMX Universum
universe = 1
dmx_data = [0] * 512  # Ein DMX-Kanal reicht bis 512, also 512 Werte

def triangulation(rssi1, rssi2):
    d1 = 10 ** ((27.55 - (20 * np.log10(2400)) + abs(rssi1)) / 20)
    d2 = 10 ** ((27.55 - (20 * np.log10(2400)) + abs(rssi2)) / 20)
    return d1, d2

def set_dmx_values(pan, tilt):
    # Skaliere Pan und Tilt auf DMX-Werte (0-255)
    dmx_data[0] = int(np.clip(pan * 255 / 10, 0, 255))  # Pan (horizontal)
    dmx_data[1] = int(np.clip(tilt * 255 / 10, 0, 255))  # Tilt (vertikal)

    client.SendDmx(universe, dmx_data)

# Visualisierung vorbereiten
plt.ion()
fig, ax = plt.subplots()

while True:
    data, addr = sock.recvfrom(1024)  # Puffergröße
    rssi_values = data.decode("utf-8").split(":")
    
    if len(rssi_values) > 1:
        rssi1 = int(rssi_values[1])  # RSSI-Wert des ersten Empfängers
        rssi2 = 30  # Beispiel-RSSI-Wert für den zweiten Empfänger (wird im echten Setup gemessen)

        # Beispielhafte Triangulation
        d1, d2 = triangulation(rssi1, rssi2)

        # Berechne die Position des georteten ESP32
        x = (d1 + d2) / 2
        y = (d1 - d2) / 2

        # Berechne die DMX-Werte für Pan und Tilt
        set_dmx_values(x, y)

        # Visualisierung der Position
        ax.clear()
        ax.plot(x, y, 'ro')  # Plot der Position
        plt.xlim(-10, 10)
        plt.ylim(-10, 10)
        plt.pause(0.1)

# Warten auf DMX-Daten
client.Run()
