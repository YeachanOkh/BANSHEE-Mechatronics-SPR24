//Goal: Full functionallity using both ultrasonic sensor and get information from raspberry pi to tell Arduino Nano when to move
//Created By: Alexander Ov
//Created On: 4/22/24
//Version 1.8.2
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
  delay(3000);                                  //Delay for 5 seconds
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
  delay(500); // Pause for 2 seconds

  // Clear the buffer
  display.clearDisplay();

  display.display();
  delay(100);
}

void oledDisplay(){
  display.clearDisplay();
  display.setTextSize(1);             // Normal 1:1 pixel scale
  display.setTextColor(SSD1306_WHITE);        // Draw white text
  display.setCursor(0,0);
  display.print(F("Movement Code V1.8.2"));
  display.setCursor(0,8);
  display.print(F("Dist to BVM: "));
  display.print(front_dist);
  display.setCursor(0,16);
  display.print(F("Dist to GCS: "));
  display.print(back_dist);
  display.setCursor(0,24); 
  display.print(F("Direction: "));
  display.print(direction);
  display.display();
  delay(2);
}

//Main Looping Fucntion
void loop() {
  while(digitalRead(reset_pin) == LOW);  
  front_dist = getdistance(trigFront,echoFront);
  back_dist = getdistance(trigBack,echoBack);
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
    if(back_dist < 50){
      servoLeft.write(forward_speed-4);                    //Set left side motors postion to 90
      servoRight.write(forward_speed-4);
    }
    else if(back_dist < 70){
      servoLeft.write(forward_speed-2);                    //Set left side motors postion to 90
      servoRight.write(forward_speed-2);
    }
    else if(back_dist < 100){
      servoLeft.write(forward_speed-1);                    //Set left side motors postion to 90
      servoRight.write(forward_speed-1);
    }
    else{
      servoLeft.write(forward_speed);                    //Set left side motors postion to 90
      servoRight.write(forward_speed);
    }
    if(back_dist < 3){
      direction = 'S';                          //Set direction to none to trigger a stop
      servoLeft.write(midpoint);                    //Set left side motors postion to 90
      servoRight.write(midpoint);                   //Set right side motors postion to 90
      Serial.write('s');
    }
  }
  else if(direction == 'B')                     //Check if direction is set as backwards (GCS)
  { 
    if(front_dist < 40){
      servoLeft.write(reverse_speed+3);                    //Set left side motors postion to 90
      servoRight.write(reverse_speed+3);
    }
    else if(front_dist < 50){
      servoLeft.write(reverse_speed+2);                    //Set left side motors postion to 90
      servoRight.write(reverse_speed+2);
    }
    else if(front_dist < 100){
      servoLeft.write(reverse_speed+1);                    //Set left side motors postion to 90
      servoRight.write(reverse_speed+1);
    }
    else{
      servoLeft.write(reverse_speed);                    //Set left side motors postion to 90
      servoRight.write(reverse_speed);
    }
    if(front_dist < 5){
      direction = 'S';                          //Set direction to none to trigger a stop
      servoLeft.write(midpoint);                    //Set left side motors postion to 90
      servoRight.write(midpoint);                   //Set right side motors postion to 90
      Serial.write('s');
    }
  }
  else if(direction == 'S'){                                         //Check if direction not forward or backward
    servoLeft.write(midpoint);                    //Set left side motors postion to 90
    servoRight.write(midpoint);                   //Set right side motors postion to 90
  }
}
