#include <WiFi.h>
#include <WiFiUdp.h>

// KONFIGURATION - Ändern Sie diese Werte
const char* ssid = "Dein_WiFi_Netzwerk";
const char* password = "Dein_WiFi_Passwort";
const char* udpAddress = "192.168.1.100";  // IP des PCs
const int udpPort = 12345;                 // Port für die Kommunikation
const int receiverID = #;                  // 1 für ersten Empfänger, 2 für zweiten

WiFiUDP udp;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Verbinde mit WiFi...");
  }
  
  Serial.println("Verbunden mit WiFi");
  Serial.print("Receiver ID: ");
  Serial.println(receiverID);
  Serial.print("IP-Adresse: ");
  Serial.println(WiFi.localIP());
  
  udp.begin(udpPort);
}

void loop() {
  int rssi = WiFi.RSSI();
  // Format: ID:RSSI
  String message = String("RX") + receiverID + ":" + rssi;

  udp.beginPacket(udpAddress, udpPort);
  udp.print(message);
  udp.endPacket();

  Serial.println(message);  // Debug-Ausgabe
  delay(500);               // Alle 500ms senden
}