#include <MQ2.h>
#include <Wire.h>
#include "DHT.h"
#define DHTTYPE DHT11
#define DHTPIN 2
#define CLK 3
#define DT 4
#define SW 5

int Analog_Input = A0;
int lpg, co, smoke;
int SAMPLE_FREQUENCY = 10000;

MQ2 mq2(Analog_Input);
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  
  Serial.begin(9600);

  mq2.begin();
  dht.begin();
}

void loop() {

  delay(SAMPLE_FREQUENCY);
  dhtsense();
  mq2sense();
  
  Serial.print("LPG:");
  Serial.print(lpg);
  Serial.print(" CO:");
  Serial.print(co);
  Serial.print("SMOKE:");
  Serial.print(smoke);
  Serial.print(" PPM");

}

void dhtsense(){
  float h = dht.readHumidity();
  // Read temperature as Celsius (the default)
  float t = dht.readTemperature();
  // Read temperature as Fahrenheit (isFahrenheit = true)
  float f = dht.readTemperature(true);

  // Check if any reads failed and exit early (to try again).
  if (isnan(h) || isnan(t) || isnan(f)) {
    Serial.println(F("Failed to read from DHT sensor!"));
    return;
  }

  // Compute heat index in Fahrenheit (the default)
  float hif = dht.computeHeatIndex(f, h);
  // Compute heat index in Celsius (isFahreheit = false)
  float hic = dht.computeHeatIndex(t, h, false);

  Serial.print(F("Humidity: "));
  Serial.print(h);
  Serial.print(F("%  Temperature: "));
  Serial.print(t);
  Serial.print(F("°C "));
  Serial.print(f);
  Serial.print(F("°F  Heat index: "));
  Serial.print(hic);
  Serial.print(F("°C "));
  Serial.print(hif);
  Serial.println(F("°F"));
  
}

void mq2sense(){
  float* values= mq2.read(true); //set it false if you don't want to print the values in the Serial
  //lpg = values[0];
  lpg = mq2.readLPG();
  //co = values[1];
  co = mq2.readCO();
  //smoke = values[2];
  smoke = mq2.readSmoke();
}
