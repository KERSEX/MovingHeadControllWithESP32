#include <WiFi.h>
#include <WiFiUdp.h>

// KONFIGURATION - Ändern Sie diese Werte
const char* ssid = "Dein_WiFi_Netzwerk"; // Wifi Name
const char* password = "Dein_WiFi_Passwort"; //Wifi Password
const char* udpAddress = "192.168.1.100";  // IP from PC 
const int udpPort = 12345;                 // Port for Communication
const int receiverID = 1;                  // 1 for the first, 2 for the second

WiFiUDP udp;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000); // Just Delay 
    Serial.println("Verbinde mit WiFi..."); // The ESP32 want WiFi Connection
  }
  
  Serial.println("Verbunden mit WiFi"); // The ESP32 is connectet with WiFi
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

  Serial.println(message);  // Debug Message
  delay(500);               // All 0.5 Seconds a Signal 
}