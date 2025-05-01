import socket
import numpy as np
import matplotlib.pyplot as plt
import serial
import time
import serial.tools.list_ports
from datetime import datetime

# === KONFIGURATION ===
UDP_PORT = 12345
DMX_PORT = "COM4"  # <-- Hier muss dein USB-DMX-Gerät stehen, NICHT der ESP32!
BAUDRATE = 250000

# Konfiguration für Triangulation und Positionierung
FREQUENCY_MHZ = 2400  # Frequenz in MHz
# Empfänger-Positionen (in Meter) im 2D-Raum
RECEIVER1_POSITION = (0, 0)   # Position des ersten Empfängers
RECEIVER2_POSITION = (5, 0)   # Position des zweiten Empfängers (5 Meter entfernt)
# Parameter für RSSI-zu-Distanz Konversion
RSSI_REF = -50  # RSSI-Wert in 1 Meter Entfernung
N_FACTOR = 2.0  # Path-Loss Exponent (normalerweise zwischen 2-4)
# Filter-Parameter
ALPHA = 0.3     # Gewichtungsfaktor für gleitenden Durchschnitt (0-1)

# === DMX-Initialisierung ===
dmx_data = [0] * 512
try:
    ser = serial.Serial(DMX_PORT, baudrate=BAUDRATE, bytesize=8, parity='N', stopbits=2)
    print(f"[INFO] Verbunden mit DMX-Interface an {DMX_PORT}")
except serial.SerialException as e:
    print(f"[FEHLER] Konnte {DMX_PORT} nicht öffnen: {e}")
    print("[INFO] Fahre ohne DMX-Interface fort (nur Visualisierung)")
    ser = None

def send_dmx_frame(data):
    """Sendet DMX-Daten über USB-DMX Interface."""
    if ser is None:
        return
        
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

def log_message(category, message):
    """Formatierte Log-Ausgabe mit Zeitstempel."""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] [{category}] {message}")

def rssi_to_distance(rssi):
    """
    Verbesserte RSSI-zu-Distanz Konvertierung mit Log-Distance Path Loss Model.
    """
    # Log-Distance Path Loss Model: d = 10^((RSSI_ref - RSSI)/(10*N))
    if rssi == 0:  # Ungültiger RSSI-Wert
        return float('inf')
    distance = 10 ** ((RSSI_REF - abs(rssi)) / (10 * N_FACTOR))
    return distance

def triangulate_position(rssi1, rssi2):
    """
    Berechnet die Position basierend auf RSSI-Werten von zwei Empfängern
    unter Verwendung eines verbesserten Triangulationsalgorithmus.
    """
    # Distanzen berechnen
    d1 = rssi_to_distance(rssi1)
    d2 = rssi_to_distance(rssi2)
    
    log_message("TRIANGULATION", f"RSSI1: {rssi1}, RSSI2: {rssi2} => d1: {d1:.2f}m, d2: {d2:.2f}m")
    
    # Einfache Triangulation für zwei Empfänger auf einer Linie
    # Wenn beide Empfänger auf der X-Achse liegen (y=0)
    rx1_x, rx1_y = RECEIVER1_POSITION
    rx2_x, rx2_y = RECEIVER2_POSITION
    
    # Berechne X-Position durch gewichtete Mittelung
    if d1 + d2 > 0:
        x = (rx1_x * d2 + rx2_x * d1) / (d1 + d2)
    else:
        x = (rx1_x + rx2_x) / 2  # Fallback
    
    # Berechne Y-Position durch Pythagoras
    # Wir verwenden die präzisere Entfernung für die Y-Berechnung
    more_accurate_d = d1 if abs(rssi1) < abs(rssi2) else d2
    reference_x = rx1_x if more_accurate_d == d1 else rx2_x
    
    y_squared = max(0, (more_accurate_d**2 - (x - reference_x)**2))
    y = np.sqrt(y_squared)
    
    # Im realen Setup könnten wir nicht wissen, ob y positiv oder negativ ist
    # Hier nehmen wir an, dass der Sender immer im positiven Y-Bereich ist
    
    return x, y

# Variablen für gleitenden Durchschnitt
last_x, last_y = 0, 0
first_reading = True

def set_dmx_values(x, y):
    """
    Berechnet DMX-Werte aus Position und sendet sie.
    Skaliert die Werte auf den DMX-Bereich (0-255).
    """
    # Anpassung der Skalierung basierend auf Ihrem Setup
    # Annahme: X von 0-10 auf DMX 0-255, Y von 0-10 auf DMX 0-255
    pan_value = int(np.clip(x * 255 / 10, 0, 255))
    tilt_value = int(np.clip(y * 255 / 10, 0, 255))
    
    dmx_data[0] = pan_value
    dmx_data[1] = tilt_value
    
    log_message("DMX", f"Position: ({x:.2f}, {y:.2f}) -> DMX: (Pan: {pan_value}, Tilt: {tilt_value})")
    send_dmx_frame(dmx_data)

# === Visualisierung ===
plt.ion()
fig, ax = plt.subplots(figsize=(10, 8))
historical_positions = []  # Für die Anzeige der Bewegungsspur

# === Hauptschleife ===
try:
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            message = data.decode("utf-8")
            log_message("UDP", f"Empfangen von {addr}: {message}")
            
            rssi_values = message.split(":")
            
            if len(rssi_values) > 1:
                try:
                    rssi1 = int(rssi_values[1])
                    # Zweiter Empfänger (in einer realen Umgebung würden Sie
                    # tatsächliche Werte von einem zweiten ESP32 erhalten)
                    # Für Testzwecke: simulierter Wert, der von rssi1 abhängt
                    rssi2 = min(-30, rssi1 + 10)  # Simuliere einen zweiten Empfänger
                    
                    # Position berechnen
                    x, y = triangulate_position(rssi1, rssi2)
                    
                    # Filtern mit gleitendem Durchschnitt
                    if not first_reading:
                        x = ALPHA * x + (1 - ALPHA) * last_x
                        y = ALPHA * y + (1 - ALPHA) * last_y
                    else:
                        first_reading = False
                        
                    last_x, last_y = x, y
                    
                    log_message("POSITION", f"X: {x:.2f}, Y: {y:.2f}")
                    
                    # DMX-Werte setzen
                    set_dmx_values(x, y)
                    
                    # Positionen für die Visualisierung speichern (letzte 20 Positionen)
                    historical_positions.append((x, y))
                    if len(historical_positions) > 20:
                        historical_positions.pop(0)
                    
                    # Visualisierung
                    ax.clear()
                    
                    # Empfänger anzeigen
                    ax.plot(*RECEIVER1_POSITION, 'bs', markersize=10, label='Empfänger 1')
                    ax.plot(*RECEIVER2_POSITION, 'gs', markersize=10, label='Empfänger 2')
                    
                    # Bewegungsspur anzeigen
                    if len(historical_positions) > 1:
                        hist_x, hist_y = zip(*historical_positions)
                        ax.plot(hist_x, hist_y, 'b-', alpha=0.5)
                    
                    # Aktuelle Position anzeigen
                    ax.plot(x, y, 'ro', markersize=8, label='Sender')
                    
                    # Distanzkreise um die Empfänger zeichnen
                    circle1 = plt.Circle(RECEIVER1_POSITION, rssi_to_distance(rssi1), 
                                        color='blue', fill=False, alpha=0.3)
                    circle2 = plt.Circle(RECEIVER2_POSITION, rssi_to_distance(rssi2), 
                                        color='green', fill=False, alpha=0.3)
                    ax.add_patch(circle1)
                    ax.add_patch(circle2)
                    
                    # Plot-Eigenschaften setzen
                    ax.set_xlim(-2, 12)
                    ax.set_ylim(-2, 12)
                    ax.set_xlabel('X-Position (Meter)')
                    ax.set_ylabel('Y-Position (Meter)')
                    ax.set_title("Sender-Position (Triangulation)")
                    ax.grid(True)
                    ax.legend()
                    
                    plt.tight_layout()
                    plt.pause(0.1)
                    
                except ValueError as ve:
                    log_message("FEHLER", f"Konnte RSSI-Werte nicht konvertieren: {ve}")
                    
        except Exception as e:
            log_message("FEHLER", f"{e}")
            time.sleep(0.5)  # Kurze Pause bei Fehlern
            continue

except KeyboardInterrupt:
    log_message("INFO", "Programm durch Benutzer beendet")
    if ser is not None:
        ser.close()
        log_message("INFO", "DMX-Interface geschlossen")
    sock.close()
    log_message("INFO", "UDP-Socket geschlossen")
    plt.close()