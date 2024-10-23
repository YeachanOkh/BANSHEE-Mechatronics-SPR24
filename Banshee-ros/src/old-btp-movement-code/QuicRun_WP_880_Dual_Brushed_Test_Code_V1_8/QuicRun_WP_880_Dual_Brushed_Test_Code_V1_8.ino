//Goal: Full functionallity using both ultrasonic sensor and get information from raspberry pi to tell Arduino Nano when to move
//Created By: Alexander Ov
//Created On: 4/08/24
//Version 1.8
//

#include "BTP.h"
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 32 // OLED display height, in pixels
#define OLED_RESET     -1 // Reset pin # (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3C ///< See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

#define NUMFLAKES     10 // Number of snowflakes in the animation example
void oledDisplay();

const int reset_pin = 13;
void setup() {
  //Serial communication startup
  Serial.begin(9600);                           //Set baudrate to 9600

  //Servo attachment
  servoLeft.attach(left_servos, 1000, 2000);    //Attaches the motor driver on pin 9 to the servoLeft object (pin, min pulse width, max pulse width in microseconds)
  servoRight.attach(right_servos, 1000, 2000);  //Attaches the motor driver on pin 10 to the servoRight object (pin, min pulse width, max pulse width in microseconds)

  //Pin IO Setup
  pinMode(blue_led, OUTPUT);                    //LED pin declerartion as OUTPUT
  pinMode(green_led, OUTPUT);                   //LED pin declerartion as OUTPUT
  pinMode(trigFront, OUTPUT);                   //trigFront pin declerartion as OUTPUT
  pinMode(echoFront, INPUT);                    //echoFront pin declerartion as OUTPUT
  pinMode(trigBack, OUTPUT);                    //trigFront pin declerartion as OUTPUT
  pinMode(echoBack, INPUT);                     //echoFront pin declerartion as OUTPUT
  pinMode(power, OUTPUT);                       //power pin declerartion as OUTPUT
  pinMode(reset_pin, INPUT);
  //LED start up
  digitalWrite(blue_led,HIGH);                  //Turn on LED for set up
  digitalWrite(green_led,HIGH);                 //Turn on LED for reverse movement state
  digitalWrite(power, HIGH);                    //Turn on power for set up

  //ESC safety start up
  servoLeft.write(midpoint);                    //Set left side motors postion to 90
  servoRight.write(midpoint);                   //Set right side motors postion to 90
  delay(5000);                                  //Delay for 5 seconds
  digitalWrite(blue_led,LOW);                   //Turn off LED for set up
  digitalWrite(green_led,LOW);                  //Turn on LED for reverse movement state
  direction = 'S';                              //Set direction var to forward (BVM)

  //default_mode(distanceBack);                   //Reset Pod to the start point (GCS)
    // SSD1306_SWITCHCAPVCC = generate display voltage from 3.3V internally
  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed, loop forever
  }

  // Show initial display buffer contents on the screen --
  // the library initializes this with an Adafruit splash screen.
  display.display();
  delay(2000); // Pause for 2 seconds

  // Clear the buffer
  display.clearDisplay();

  // Draw a single pixel in white
  display.drawPixel(10, 10, SSD1306_WHITE);

  // Show the display buffer on the screen. You MUST call display() after
  // drawing commands to make them visible on screen!
  display.display();
  delay(2000);
}

void oledDisplay(){
  display.clearDisplay();
  display.setTextSize(1);             // Normal 1:1 pixel scale
  display.setTextColor(SSD1306_WHITE);        // Draw white text
  display.setCursor(0,0);
  display.print(F("Movement Code V1.8"));
  display.setCursor(0,8);
  display.print(F("Dist to BVM: "));
  display.print(distance);
  display.setCursor(0,16);
  display.print(F("Dist to GCS: "));
  display.print(distanceBack);
  display.setCursor(0,24); 
  display.print(F("Direction: "));
  display.print(direction);
  display.display();
  display.display();
  delay(2);
}

//Main Looping Fucntion
void loop() {
  while(digitalRead(reset_pin) == LOW);  
  distance = getdistance(trigFront,echoFront);
  distanceBack = getdistance(trigBack,echoBack);
  oledDisplay();

  if (Serial.available()>0) {
    int mode = Serial.read();
    switch(mode) {
      case 'b':                       //Mode 1: Pod moving to the right
        direction = 'B';        
        break;
      case 'g':                       //Mode 2: Pod moving to the left
        direction = 'G';
        break;
      default:
        break;
    }
  }


  if(direction == 'G')                          //Check if direction is set as forward
  {
    digitalWrite(blue_led,HIGH);                //Turn on LED for forward movement state
    digitalWrite(green_led,LOW);                //Turn on LED for reverse movement state
    servoLeft.write(midpoint);                    //Set left side motors postion to 90
    servoRight.write(midpoint);
    while(true){
      distance = getdistance(trigFront,echoFront);
      distanceBack = getdistance(trigBack,echoBack);
      oledDisplay();

      if(distanceBack > 220){
        move(forward_speed);
        distance = getdistance(trigFront,echoFront);
        distanceBack = getdistance(trigBack,echoBack);
      }
      else if(distanceBack <= 220 && distanceBack > 25 ){
        distance = getdistance(trigFront,echoFront);
        distanceBack = getdistance(trigBack,echoBack);
        gradientControl(midpoint);                   //Set right side motors postion to 90
        if(distanceBack<=70) delay(1000);
        else if(distanceBack<=180) delay(500);
        gradientControl(forward_speed);
        for(int i = 0; i <= 500; i++){
          distance = getdistance(trigFront,echoFront);
          distanceBack = getdistance(trigBack,echoBack);
          delay(1);
          if(distanceBack <= 180) break;
        }
      }
      else if(distanceBack <= 25)                       //Check if the distance is less than or equal to 10 cm  from the front
      {
        distance = getdistance(trigFront,echoFront);
        distanceBack = getdistance(trigBack,echoBack);
        direction = 'S';                          //Set direction to none to trigger a stop
        servoLeft.write(midpoint);                    //Set left side motors postion to 90
        servoRight.write(midpoint);                   //Set right side motors postion to 90
        // for(int i = 0; i <=10; i++){
        Serial.write('s');
        break;
      }
      // delay(50);
      // gradientControl(midpoint);                   //Set right side motors postion to 90
    }
  }
  else if(direction == 'B')                     //Check if direction is set as backwards (GCS)
  {   
    digitalWrite(blue_led,LOW);                 //Turn on LED for reverse movement state
    digitalWrite(green_led,HIGH);               //Turn on LED for reverse movement state   
    int toggle = 0;
    while(true){
      distance = getdistance(trigFront,echoFront);
      distanceBack = getdistance(trigBack,echoBack);
      oledDisplay();
      if(distance > 200){
        if(toggle == 0){
          gradientControl(midpoint);
          delay(1000);
          toggle = 1;
        }
        gradientControl(reverse_speed);
        distance = getdistance(trigFront,echoFront);
        distanceBack = getdistance(trigBack,echoBack);
      }
      else if(distance <= 200 && distance > 25){
        distance = getdistance(trigFront,echoFront);
        distanceBack = getdistance(trigBack,echoBack);
        gradientControl(midpoint);
        delay(500);
        gradientControl(reverse_speed);
        for(int i = 0; i <= 500; i++){
          distance = getdistance(trigFront,echoFront);
          distanceBack = getdistance(trigBack,echoBack);
          delay(1);
          if(distance <= 130) break;
        }
      }
      //reverse(reverse_speed);
      
      else if(distance <= 25)                           //Check if the distance is less than or equal to 10 cm from the back
      {
        distance = getdistance(trigFront,echoFront);
        distanceBack = getdistance(trigBack,echoBack);
        is_reverse = false;
        direction = 'S';                          //Set direction to none to trigger a stop
        Serial.write('s');
        break;
      }
      // delay(50);
      // gradientControl(midpoint);                   //Set right side motors postion to 90
    }
  }
  else if(direction == 'S'){                                         //Check if direction not forward or backward
    digitalWrite(blue_led,LOW);                 //Turn on LED for reverse movement state
    digitalWrite(green_led,LOW);               //Turn on LED for reverse movement state
    servoLeft.write(midpoint);                    //Set left side motors postion to 90
    servoRight.write(midpoint);                   //Set right side motors postion to 90
  }
}
