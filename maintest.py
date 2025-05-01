import socket
import numpy as np
import matplotlib.pyplot as plt
import serial
import time
import serial.tools.list_ports

# === KONFIGURATION ===
UDP_PORT = 12345
#DMX_PORT = "COM4"  # <-- Hier muss dein USB-DMX-Gerät stehen, NICHT der ESP32!
BAUDRATE = 250000

# === DMX-Initialisierung ===
#dmx_data = [0] * 512
#try:
#    ser = serial.Serial(DMX_PORT, baudrate=BAUDRATE, bytesize=8, parity='N', stopbits=2)
#    print(f"[INFO] Verbunden mit DMX-Interface an {DMX_PORT}")
#except serial.SerialException as e:
#    print(f"[FEHLER] Konnte {DMX_PORT} nicht öffnen: {e}")
#    exit(1)

def send_dmx_frame(data):
    """Sendet DMX-Daten über USB-DMX Interface."""
    packet = bytes([0]) + bytes(data)
    ser.break_condition = True
    time.sleep(0.001)
    ser.break_condition = False
    time.sleep(0.001)
    ser.write(packet)

# === UDP-Setup ===
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", UDP_PORT))
print(f"[INFO] Warte auf UDP-Daten von ESP32 an Port {UDP_PORT}...")

def triangulation(rssi1, rssi2):
    freq = 2400  # MHz
    d1 = 10 ** ((27.55 - (20 * np.log10(freq)) + abs(rssi1)) / 20)
    d2 = 10 ** ((27.55 - (20 * np.log10(freq)) + abs(rssi2)) / 20)
    print(f"[TRIANGULATION] RSSI1: {rssi1}, RSSI2: {rssi2} => d1: {d1:.2f}, d2: {d2:.2f}")
    return d1, d2

def set_dmx_values(pan, tilt):
    """Berechnet DMX-Werte aus Position und sendet sie."""
    pan_value = int(np.clip(pan * 255 / 10, 0, 255))
    tilt_value = int(np.clip(tilt * 255 / 10, 0, 255))
    dmx_data[0] = pan_value
    dmx_data[1] = tilt_value
    print(f"[DMX] Pan: {pan:.2f} -> {pan_value}, Tilt: {tilt:.2f} -> {tilt_value}")
    send_dmx_frame(dmx_data)

# === Visualisierung ===
plt.ion()
fig, ax = plt.subplots()

# === Hauptschleife ===
while True:
    try:
        data, addr = sock.recvfrom(1024)
        rssi_values = data.decode("utf-8").split(":")
        
        if len(rssi_values) > 1:
            rssi1 = int(rssi_values[1])
            rssi2 = 30  # Zweiter (simulierter) Empfänger

            d1, d2 = triangulation(rssi1, rssi2)
            x = (d1 + d2) / 2
            y = (d1 - d2) / 2
            print(f"[POSITION] X: {x:.2f}, Y: {y:.2f}")

            set_dmx_values(x, y)

            # Visualisierung
            ax.clear()
            ax.plot(x, y, 'ro')
            plt.xlim(-10, 10)
            plt.ylim(-10, 10)
            plt.title("Position des Senders (Triangulation)")
            plt.pause(0.1)

    except Exception as e:
        print(f"[FEHLER] {e}")
        continue
