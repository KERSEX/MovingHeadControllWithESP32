#include <WiFi.h>
#include <WiFiUdp.h>

const char* ssid = "Dein_WiFi_Netzwerk";
const char* password = "Dein_WiFi_Passwort";
const char* udpAddress = "192.168.1.100";  // IP des PCs
const int udpPort = 12345;  // Port für die Kommunikation

WiFiUDP udp;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Verbinde mit WiFi...");
  }
  Serial.println("Verbunden mit WiFi");
  udp.begin(udpPort);
}

void loop() {
  int rssi = WiFi.RSSI();
  String message = String("RSSI:") + rssi;

  udp.beginPacket(udpAddress, udpPort);
  udp.print(message);
  udp.endPacket();

  delay(500);  // Alle 500ms senden
}
