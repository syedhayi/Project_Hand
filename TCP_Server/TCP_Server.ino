#include <ESP8266WiFi.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// called this way, it uses the default address 0x40
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define SERVOMIN  125 // this is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX  575 // this is the 'maximum' pulse length count (out of 4096)

int port = 8888;
WiFiServer server(port);

const char *ssid = "XXXXXXXXXXXX";        //ssid of your WIFI
const char *password = "XXXXXXXXXXXXXX";  //password of your WIFI

int Array_[5], r=0, t=0;

void setup() 
{ Serial.begin(115200);
  pwm.begin();  
  pwm.setPWMFreq(60);  
  Serial.println();
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password); //Connect to wifi
   
  // Wait for connection  
  Serial.println("Connecting to Wifi");
  while (WiFi.status() != WL_CONNECTED) {   
    delay(500);
    Serial.print(".");
    delay(500);
  }

  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());  
  server.begin();
  Serial.print("Connected to IP:");
  Serial.print(WiFi.localIP());
  Serial.print(" on port ");
  Serial.println(port);
}

void loop() 
{
  WiFiClient client = server.available();  
  if (client) {
    if(client.connected())
    {
      Serial.println("Client Connected");
    }   
    while(client.connected()){      
      while(client.available()>0){
         // read data from the connected client                 
         String _receiveData = client.readStringUntil(';'); //receive data until ';', it creates a string of data till the ';'///
         Serial.println(_receiveData); 
             
          ////////////split the received string (5 finger's angle) leaving ',' out and convert it to int array/////////               
            for (int i=0; i < _receiveData.length(); i++)
            {if(_receiveData.charAt(i) == ',') 
              { Array_[t] = _receiveData.substring(r, i).toInt(); 
                r=(i+1); 
                t++;                
              }
            }       

          /////////////set pwm to the servos///////////////
            pwm.setPWM(15, 0, angleToPulse(Array_[0]) );
            pwm.setPWM(14, 0, angleToPulse(Array_[1]) );
            pwm.setPWM(13, 0, angleToPulse(Array_[2]) );
            pwm.setPWM(12, 0, angleToPulse(abs(180-Array_[3])) );
            pwm.setPWM(11, 0, angleToPulse(abs(180-Array_[4])) );
            r = 0;
            t =0;   
            }    
        }
        client.stop();   
        }
}

int angleToPulse(int ang){
  // map angle of 0 to 180 to Servo min and Servo max 
   int pulse = map(ang,0, 180, SERVOMIN,SERVOMAX);
   return pulse;
}
