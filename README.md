# Anleitung zum richtigen Einrichten der ESP32-Empfänger für Triangulation
Um Ihr System korrekt einzurichten und präzise Positionsergebnisse zu erhalten, müssen Sie die Empfänger-Koordinaten im Code exakt an Ihre reale Aufstellung anpassen. Hier ist eine Schritt-für-Schritt-Anleitung:

# Empfohlene Aufstellung:

Platzieren Sie die ESP32-Geräte an gegenüberliegenden Ecken des Raums
Idealerweise sollten sie erhöht angebracht werden (z.B. auf Stativen oder an der Wand)
Vermeiden Sie Hindernisse wie Möbel zwischen den Empfängern und dem Zielgerät



## 1. Positionierung der ESP32-Empfänger
Für optimale Ergebnisse sollten Sie:

Die ESP32-Empfänger in einem bekannten Abstand zueinander aufstellen
Die Positionen genau ausmessen
Eine klare Sichtlinie zwischen den Empfängern und dem zu verfolgenden Gerät gewährleisten



## 2. Koordinatensystem festlegen

### Definieren Sie den Ursprung (0,0):

Wählen Sie die Position von Empfänger 1 als Koordinatenursprung (0,0)
Alle anderen Positionen werden relativ zu diesem Punkt gemessen
```
RECEIVER1_POSITION = (0, 0)   # Position des ersten Empfängers
RECEIVER2_POSITION = (5, 0)   # Position des zweiten Empfängers (5 Meter entfernt)
```


## Definieren Sie die X-Achse:

Die X-Achse verläuft üblicherweise horizontal
Messen Sie den horizontalen Abstand zwischen den Empfängern


Definieren Sie die Y-Achse:
Die Y-Achse verläuft senkrecht zur X-Achse



## 3. Vermessen der tatsächlichen Positionen

Messen Sie mit einem Maßband den exakten Abstand zwischen beiden ESP32s
Wenn die Empfänger nicht genau auf einer Linie sind:

Messen Sie den horizontalen (X) Abstand
Messen Sie den vertikalen (Y) Abstand
