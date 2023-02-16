import socket

f = open("IndoorMonitor.ino", "a")

f.write("#include<WiFiNINA.h>\n")
f.write("#include <ArduinoMqttClient.h>\n")
f.write("#include <ArduinoHttpClient.h>\n")
f.write("#include <ArduinoJson.h>\n")
f.write("#include <MQ2.h>\n")
f.write("#include \"DHT.h\"\n")

f.write("#define DHTTYPE DHT11\n")
f.write("#define DHTPIN 2\n")

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))

f.write("#define DOCKERADDR \"" + s.getsockname()[0] +"\"\n")

s.close()

f.write("int Analog_Input = A0;\n")

f.write("float MAX_GAS_VALUE =1;\n")
f.write("float MIN_GAS_VALUE = 0.5;\n")
f.write("long SAMPLE_FREQUENCY = 5000;\n")
f.write("bool PROTOCOL = true;\n")

f.write("float lpg, co, smoke;\n")
f.write("float h, t;\n")
f.write("int aqi;\n")
f.write("float measureWindow[5] = { };\n")

f.write("MQ2 mq2(Analog_Input);\n")
f.write("DHT dht(DHTPIN, DHTTYPE);\n")

f.write("const char* settings_topic = \"set\";\n")
f.write("const char* sense_topic = \"sensedData\";\n")

f.write("const char broker[] = DOCKERADDR;\n")
f.write("int        port     = 1883;\n")

f.write("WiFiClient wifi;\n")
f.write("WiFiClient wifi2;\n")
f.write("int status = WL_IDLE_STATUS;\n")
f.write("MqttClient mqttClient(wifi);\n")
f.write("HttpClient httpClient = HttpClient(wifi2, DOCKERADDR, 8080);\n")

f.write("void setup() {\n")
  
f.write("  while(!Serial){\n")
f.write("    ;\n")
f.write("  }\n")
  
f.write("  Serial.begin(9600);\n")
f.write("  Serial.println(\"OK\");\n")
f.write("  Serial.println(\"Connessione...\");\n")
  
f.write("  while (status != WL_CONNECTED){\n")
f.write("    status = WiFi.begin(\"Vodafone-34348811\",\"M0zz4r3ll1n0\");\n")
f.write("    Serial.print(\".\");\n")
f.write("    delay(1000);\n")
f.write("  }\n")
  
f.write("  Serial.println(\"Connected to WiFi!\");\n")

f.write("  mqttClient.setUsernamePassword(\"admin\",\"admin\");\n")

f.write("  if (!mqttClient.connect(broker, port)) {\n")
f.write("      Serial.print(\"MQTT connection failed! Error code = \");\n")
f.write("      Serial.println(mqttClient.connectError());\n")
  
f.write("      while (1);\n")
f.write("    }\n")
  
f.write("  Serial.println(\"You're connected to the MQTT broker!\");\n")
f.write("  Serial.println();\n")

f.write("  mq2.begin();\n")
f.write("  dht.begin();\n")

f.write("  mqttClient.onMessage(onMqttMessage);\n")
f.write("  mqttClient.subscribe(settings_topic);\n")

f.write("}\n")

f.write("void loop() {\n")

f.write("  if (!mqttClient.connected()) {\n")
f.write("    Serial.println(\"MQTT connection lost\");\n")
f.write("    if (!mqttClient.connect(broker, port)) {\n")
f.write("      Serial.print(\"MQTT reconnection error \");\n")
f.write("      Serial.println(mqttClient.connectError());\n")
f.write("    }else{\n")
f.write("      Serial.println(\"MQTT reconnected! \");\n")
f.write("      mqttClient.onMessage(onMqttMessage);\n")
f.write("      mqttClient.subscribe(settings_topic);\n")
f.write("   }\n")
f.write("  }\n")
  
f.write("  mqttClient.poll();\n")
f.write("  delay(SAMPLE_FREQUENCY);\n")

f.write("  dhtsense();\n")
f.write("  mq2sense();\n")
f.write("  updateAQI();\n")

f.write("  StaticJsonDocument<200> doc;\n")
f.write("  char json_string[200];\n")

f.write("  doc[\"r\"] = WiFi.RSSI();\n")
f.write("  doc[\"i\"] = \"a57\";\n")
f.write("  doc[\"p\"][\"la\"] = \"45.465\";\n")
f.write("  doc[\"p\"][\"lo\"] = \"9.185\";\n")
f.write("  doc[\"a\"][\"h\"] = h;\n")
f.write("  doc[\"a\"][\"tm\"]   = t;\n")
f.write("  doc[\"a\"][\"co\"] = co;\n")
f.write("  doc[\"aq\"] = aqi;\n")

f.write("  serializeJson(doc, json_string);\n")
f.write("  Serial.println(json_string);\n")

f.write("  if(PROTOCOL){\n")
f.write("    sendWithMQTT(json_string);\n")
f.write("  }else{\n")
f.write("    sendWithHTTP(json_string);\n")
f.write("  }\n")
   
f.write("}\n")

f.write("void sendWithMQTT(char* json_string){\n")
f.write("  mqttClient.beginMessage(sense_topic);\n")
f.write("  mqttClient.print(json_string);\n")
f.write("  mqttClient.endMessage();\n")
f.write("  Serial.println(\"Sent with MQTT\");\n")
f.write("}\n")
f.write("void sendWithHTTP(char* json_string){\n")

f.write("  String jsonToString = String(json_string);\n")
  
f.write("  httpClient.beginRequest();\n")
f.write("  httpClient.post(\"/telegraf\");\n")
f.write("  httpClient.sendHeader(\"Content-Type\", \"application/json\");\n")
f.write("  httpClient.sendHeader(\"Content-Length\", jsonToString.length());\n")
f.write("  httpClient.sendHeader(\"X-Custom-Header\", \"custom-header-value\");\n")
f.write("  httpClient.beginBody();\n")
f.write("  httpClient.print(jsonToString);\n")
f.write("  httpClient.endRequest();\n")

f.write("  int statusCode = httpClient.responseStatusCode();\n")
f.write("  String response = httpClient.responseBody();\n")

f.write("  Serial.println(\"Sent with HTTP\");\n")

f.write("}\n")

f.write("void onMqttMessage(int messageSize) {\n")

f.write("  char message[messageSize+1];\n")

f.write("  int i = 0;\n")
f.write("  while (mqttClient.available()) {\n")
f.write("    message[i] = (char)mqttClient.read();\n")
f.write("    i++;\n")
f.write("  }\n")
f.write("  message[i] = 0;\n")

f.write("  Serial.println(message);\n")

f.write("  StaticJsonDocument <256> doc;\n")
f.write("  deserializeJson(doc,message);\n")

f.write("  MAX_GAS_VALUE = doc[\"max\"];\n")
f.write("  MIN_GAS_VALUE = doc[\"min\"];\n")
f.write("  SAMPLE_FREQUENCY = (long)doc[\"samp\"];\n")
f.write("  PROTOCOL = doc[\"p\"];\n")

f.write("  Serial.println();\n")

f.write("}\n")

f.write("void updateAQI(){\n")

f.write("  measureWindow[0] = measureWindow[1];\n")
f.write("  measureWindow[1] = measureWindow[2];\n")
f.write("  measureWindow[2] = measureWindow[3];\n")
f.write("  measureWindow[3] = measureWindow[4];\n")

f.write("  measureWindow[4] = co;\n")
  
f.write("  float avg=0;\n")
f.write("  for(int i=0; i < 5; i++){\n")
f.write("    avg+=measureWindow[i];\n")
f.write("  }\n")
f.write("  avg = avg / 5;\n")
  
f.write("  if(avg >= MAX_GAS_VALUE ){\n")
f.write("   aqi = 0;\n")
f.write("  }else if(avg >= MIN_GAS_VALUE && avg < MAX_GAS_VALUE){\n")
f.write("    aqi = 1;\n")
f.write("  }else{\n")
f.write("    aqi = 2;\n")
f.write("  }\n")
  
f.write("}\n")

f.write("void dhtsense(){\n")
  
f.write("  h = dht.readHumidity();\n")
f.write("  t = dht.readTemperature();\n")

f.write("  if (isnan(h) || isnan(t)) {\n")
f.write("    Serial.println(F(\"Failed to read from DHT sensor!\"));\n")
f.write("    return;\n")
f.write(" }\n")

f.write("  float hic = dht.computeHeatIndex(t, h, false);\n")

  
f.write("}\n")

f.write("void mq2sense(){\n")
  
f.write("  float* values= mq2.read(false);\n")
f.write("  lpg = mq2.readLPG();\n")
f.write("  co = mq2.readCO();\n")
f.write("  smoke = mq2.readSmoke();\n")
  
f.write("}\n")

f.write("String prefixZero(uint8_t numero) {\n")
f.write("  if (numero < 10) {\n")
f.write("    return \"0\" + String(numero);\n")
f.write(" }\n")
f.write("  return String(numero);\n")
f.write(" }\n")
f.close()
