#include<WiFiNINA.h>
#include <ArduinoMqttClient.h>
#include <ArduinoHttpClient.h>
#include <ArduinoJson.h>
#include <MQ2.h>
#include "DHT.h"

#define DHTTYPE DHT11
#define DHTPIN 2

int Analog_Input = A0;

float MAX_GAS_VALUE =1;
float MIN_GAS_VALUE = 0.5;
int SAMPLE_FREQUENCY = 5000;
bool PROTOCOL = true;

float lpg, co, smoke;
float h, t;
int aqi;
float measureWindow[5] = { };

MQ2 mq2(Analog_Input);
DHT dht(DHTPIN, DHTTYPE);

const char* settings_topic = "set";
const char* sense_topic = "sensedData";

const char broker[] = "192.168.0.166";
int        port     = 1883;

WiFiClient wifi;
WiFiClient wifi2;
int status = WL_IDLE_STATUS;
MqttClient mqttClient(wifi);
HttpClient httpClient = HttpClient(wifi2, "192.168.0.166", 8080);

String mqttPonteBaseUrl="http://192.168.0.166:1883/resources/";
String mqttTopic="mode";


void setup() {
  
  while(!Serial){
    ;
  }
  
  Serial.begin(9600);
  Serial.println("OK");
  Serial.println("Connessione...");
  
  while (status != WL_CONNECTED){
    status = WiFi.begin("Vodafone-34348811","M0zz4r3ll1n0");
    Serial.print(".");
    delay(1000);
  }
  
  Serial.println("Connected to WiFi!");

  mqttClient.setUsernamePassword("admin","admin");

  if (!mqttClient.connect(broker, port)) {
      Serial.print("MQTT connection failed! Error code = ");
      Serial.println(mqttClient.connectError());
  
      while (1);
    }
  
  Serial.println("You're connected to the MQTT broker!");
  Serial.println();

  mq2.begin();
  dht.begin();

  mqttClient.onMessage(onMqttMessage);
  mqttClient.subscribe(settings_topic);

}

void loop() {
  
  mqttClient.poll();
  delay(SAMPLE_FREQUENCY);

  dhtsense();
  mq2sense();
  updateAQI();

  StaticJsonDocument<200> doc;
  char json_string[200];

  doc["r"] = WiFi.RSSI();
  doc["i"] = "a57";
  doc["p"]["la"] = "45.465";
  doc["p"]["lo"] = "9.185";
  doc["a"]["h"] = h;
  doc["a"]["tm"]   = t;
  doc["a"]["co"] = co;
  doc["aq"] = aqi;

  serializeJson(doc, json_string);
  Serial.println(json_string);

  if(PROTOCOL){
    sendWithMQTT(json_string);
  }else{
    sendWithHTTP(json_string);
  }
  
  //Serial.print(MAX_GAS_VALUE);
  //Serial.print("\n");
  //Serial.print(MIN_GAS_VALUE);
  //Serial.print("\n");
  //Serial.print(SAMPLE_FREQUENCY);
  //Serial.print("\n");
   
}

void sendWithMQTT(char* json_string){
  mqttClient.beginMessage(sense_topic);
  mqttClient.print(json_string);
  mqttClient.endMessage();
  Serial.println("Sent with MQTT");
}
void sendWithHTTP(char* json_string){

  String jsonToString = String(json_string);
  
  httpClient.beginRequest();
  httpClient.post("/telegraf");
  httpClient.sendHeader("Content-Type", "application/json");
  httpClient.sendHeader("Content-Length", jsonToString.length());
  httpClient.sendHeader("X-Custom-Header", "custom-header-value");
  httpClient.beginBody();
  httpClient.print(jsonToString);
  httpClient.endRequest();

  // read the status code and body of the response
  int statusCode = httpClient.responseStatusCode();
  String response = httpClient.responseBody();

  Serial.println("Sent with HTTP");

  //Serial.print("Status code: ");
  //Serial.println(statusCode);
  //Serial.print("Response: ");
  //Serial.println(response);
}

void onMqttMessage(int messageSize) {

  char message[messageSize+1];

  // use the Stream interface to print the contents
  int i = 0;
  while (mqttClient.available()) {
    message[i] = (char)mqttClient.read();
    i++;
  }
  message[i] = 0;

  Serial.println(message);

  StaticJsonDocument <256> doc;
  deserializeJson(doc,message);

  MAX_GAS_VALUE = doc["max"];
  MIN_GAS_VALUE = doc["min"];
  SAMPLE_FREQUENCY = (int)doc["samp"];
  PROTOCOL = doc["p"];

  Serial.println();

}

void updateAQI(){

  measureWindow[0] = measureWindow[1];
  measureWindow[1] = measureWindow[2];
  measureWindow[2] = measureWindow[3];
  measureWindow[3] = measureWindow[4];

  measureWindow[4] = co;
  
  float avg=0;
  for(int i=0; i < 5; i++){
    avg+=measureWindow[i];
  }
  avg = avg / 5;
  
  if(avg >= MAX_GAS_VALUE ){
    aqi = 0;
  }else if(avg >= MIN_GAS_VALUE && avg < MAX_GAS_VALUE){
    aqi = 1;
  }else{
    aqi = 2;
  }
  
}

void dhtsense(){
  
  h = dht.readHumidity();
  t = dht.readTemperature();

  // Check if any reads failed and exit early (to try again).
  if (isnan(h) || isnan(t)) {
    Serial.println(F("Failed to read from DHT sensor!"));
    return;
  }

  // Compute heat index in Celsius (isFahreheit = false)
  float hic = dht.computeHeatIndex(t, h, false);

  
}

void mq2sense(){
  
  float* values= mq2.read(false); //set it false if you don't want to print the values in the Serial
  //lpg = values[0];
  lpg = mq2.readLPG();
  //co = values[1];
  co = mq2.readCO();
  //smoke = values[2];
  smoke = mq2.readSmoke();
  
}

String prefixZero(uint8_t numero) {
  if (numero < 10) {
    return "0" + String(numero);
  }
  return String(numero);
}
