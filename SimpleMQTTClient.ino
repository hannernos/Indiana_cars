/*
  SimpleMQTTClient.ino
  The purpose of this exemple is to illustrate a simple handling of MQTT and Wifi connection.
  Once it connects successfully to a Wifi network and a MQTT broker, it subscribe to a topic and send a message to it.
  It will also send a message delayed 5 seconds later.
*/

#include "EspMQTTClient.h"
#define VRX_PIN  36 // ESP32 pin GIOP36 (ADC0) connected to VRX pin
#define VRY_PIN  39 // ESP32 pin GIOP39 (ADC0) connected to VRY pin

#define LEFT_THRESHOLD  1000
#define RIGHT_THRESHOLD 3000
#define UP_THRESHOLD    1000
#define DOWN_THRESHOLD  3000

#define COMMAND_NO     0x00
#define COMMAND_LEFT   0x01
#define COMMAND_RIGHT  0x02
#define COMMAND_UP     0x04
#define COMMAND_DOWN   0x08

int valueX = 0; // to store the X-axis value
int valueY = 0; // to store the Y-axis value
int command = COMMAND_NO;

EspMQTTClient client(
  "wifi_name",
  "wifi_pwd",
  "ip",  // MQTT Broker server ip
  "MQTTUsername",   // Can be omitted if not needed
  "MQTTPassword",   // Can be omitted if not needed
  "TestClient",     // Client name that uniquely identify your device
  1883              // The MQTT port, default to 1883. this line can be omitted
);

char *topic = "RC/dir";

void tx(){
  client.publish(topic,"abc123");
}

void setup()
{
  Serial.begin(115200);

  
  // Optional functionalities of EspMQTTClient
  client.enableDebuggingMessages(); // Enable debugging messages sent to serial output
  client.enableHTTPWebUpdater(); // Enable the web updater. User and password default to values of MQTTUsername and MQTTPassword. These can be overridded with enableHTTPWebUpdater("user", "password").
  client.enableOTA(); // Enable OTA (Over The Air) updates. Password defaults to MQTTPassword. Port is the default OTA port. Can be overridden with enableOTA("password", port).
  client.enableLastWillMessage("TestClient/lastwill", "I am going offline");  // You can activate the retain flag by setting the third parameter to true
}

// This function is called once everything is connected (Wifi and MQTT)
// WARNING : YOU MUST IMPLEMENT IT IF YOU USE EspMQTTClient
void onConnectionEstablished()
{
  // Subscribe to "mytopic/test" and display received message to Serial
  client.subscribe(topic, [](const String & payload) {
    Serial.println(payload);
  });
}

void loop()
{

  valueX = analogRead(VRX_PIN);
  valueY = analogRead(VRY_PIN);

  // converts the analog value to commands
  // reset commands
  command = COMMAND_NO;


//test code
  Serial.print("x = ");
  Serial.print(valueX);
  Serial.print(", y = ");
  Serial.println(valueY);
  // check left/right commands
  if (valueX < LEFT_THRESHOLD)
    command = command | COMMAND_LEFT;
  else if (valueX > RIGHT_THRESHOLD)
    command = command | COMMAND_RIGHT;

  // check up/down commands
  if (valueY < UP_THRESHOLD)
    command = command | COMMAND_UP;
  else if (valueY > DOWN_THRESHOLD)
    command = command | COMMAND_DOWN;

  // NOTE: AT A TIME, THERE MAY BE NO COMMAND, ONE COMMAND OR TWO COMMANDS



  // print command to serial and process command
//client.publish(topic_hu,String(event.relative_humidity));
  if (command & COMMAND_LEFT) {
    client.publish(topic,"left");
    // TODO: add your task here
  }

  if (command & COMMAND_RIGHT) {
    client.publish(topic,"right");
    // TODO: add your task here
  }

  if (command & COMMAND_UP) {
    client.publish(topic,"go");
    // TODO: add your task here
  }

  if (command & COMMAND_DOWN) {
    client.publish(topic,"back");
    // TODO: add your task here
  }


  //tx();
  client.loop();
  delay(500);

}