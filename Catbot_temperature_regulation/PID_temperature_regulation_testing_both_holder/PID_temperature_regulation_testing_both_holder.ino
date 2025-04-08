//void setup() {
  // put your setup code here, to run once:

//}

#include <SD.h> 
#include <Adafruit_MAX31865.h>
File dataFile;

//including the pins for the peletier element
const int pwm_deposition = 51; // pin 10 as pwm
const int dir_deposition = 53;  // pin 9 as dir
const int pwm_testing = 47;
const int dir_testing = 49;




float safety_shutdown = 0;
//PID constants
////////////////////////////////////////////////////////// kp was 90 kd was 80  new kp was 150 TRY 50 Try 90 
//kd from 120 try at 200
//ki from 30 to 50  (90 too high)
int kp = 100;   int ki = 270;   int kd = 0; //200;

//////////////////////////////////////////////////////////
int PID_p_dep = 0;    int PID_i_dep = 0; 
int PID_p_test = 0;    int PID_i_test = 0; 

float set_temperature_test = 0;
float set_temperature_dep = 0;

float temperature_read_dep = 0.0;
float temperature_read_test = 0.0;
float PID_error_dep = 0;
float PID_error_test = 0;

float previous_error_dep = 0;
float previous_error_test = 0;

float PID_value_dep = 0;
float PID_value_test = 0;

 int num_sensors_func(){
  int num_sensors = 4;
  return num_sensors;
 }

#define RREF 430
// The 'nominal' 0-degrees-C resistance of the sensor
// 100.0 for PT100, 1000.0 for PT1000 wassss 100
#define RNOMINAL 100.0
// The input channels used in descending order (Channel 1 is digital input 10, channel 2 is digital input 9 etc.)
Adafruit_MAX31865 depTemp = Adafruit_MAX31865(10, 11, 12, 13); // Deposition temperature //the pins correspond to (Cs, DI, DO, CLK)
Adafruit_MAX31865 cuDepTemp = Adafruit_MAX31865(9, 11, 12, 13);
Adafruit_MAX31865 tstTemp = Adafruit_MAX31865(8, 11, 12, 13);
Adafruit_MAX31865 cuTstTemp = Adafruit_MAX31865(7, 11, 12, 13);


void setup() {
int num_sensors;
//for the PID


num_sensors = num_sensors_func();
Serial.begin(115200); // There is another number for this in the peletier code
//this is for the peletier output
  pinMode(pwm_deposition,OUTPUT); //declare pin pwm as OUTPUT
  pinMode(dir_deposition,OUTPUT); //declare pin dir as OUTPUT
  pinMode(pwm_testing, OUTPUT);
  pinMode(dir_testing, OUTPUT);

  if (num_sensors >= 1){
  tstTemp.begin(MAX31865_2WIRE); // set to 2WIRE or 4WIRE as necessary
  }
  if (num_sensors >= 2){
  cuDepTemp.begin(MAX31865_4WIRE); // set to 2WIRE or 4WIRE as necessary
  }
  if (num_sensors >= 3){
  depTemp.begin(MAX31865_4WIRE); // set to 2WIRE or 4WIRE as necessary
  }
  if (num_sensors >= 4){
  cuTstTemp.begin(MAX31865_4WIRE); // set to 2WIRE or 4WIRE as necessary
}

}


String heating_holder = "";

void loop() {

  int num_sensors;
  int temp_time = 0;
  double temp_dep = 0;
  double temp_test = 0;
  unsigned long current_time = millis() / 1000;
  int count = 2;
  
  // Initialize timespan_total


if (Serial.available() > 0) {
  previous_error_dep = 0;
  PID_error_dep = 0;
  String inputString = Serial.readString();

  String* cmdArr = splitString(inputString, count);
  
  // Split the command into (Alkaline/deposition) and then testing

  //heating_holder = cmdArr[0];
  temp_dep = cmdArr[1].toFloat();

  temp_test = cmdArr[3].toFloat();

  set_temperature_test = temp_test; // temp_test
  set_temperature_dep = temp_dep; //
  Serial.println("Temp Set");
  delay(1000);
    // Read and discard the newline character
  while (Serial.available() > 0 && Serial.read() != '\n') {}

  }
  
  num_sensors = num_sensors_func();
    if (num_sensors >= 1){
    Serial.print("Test electrolyte T: "); Serial.print(tstTemp.temperature(RNOMINAL, RREF));
    }
    if (num_sensors >= 2){
    Serial.print("Copper chamber testing T: "); Serial.print(cuTstTemp.temperature(RNOMINAL, RREF));
    }
    if (num_sensors >= 3){
    Serial.print("Deposition electrolyte T: "); Serial.print(depTemp.temperature(RNOMINAL, RREF));
    }
    if (num_sensors >= 4){
    Serial.print("Copper chamber deposition T: "); Serial.print(cuDepTemp.temperature(RNOMINAL, RREF));
    }

      digitalWrite(dir_testing, HIGH);
      digitalWrite(dir_deposition,HIGH);

      temperature_read_dep = cuDepTemp.temperature(RNOMINAL, RREF); //+ safety_shutdown; // Temperature read of the alkaline testing holder
  
      // In future production, the temperature read should just be the temperature inside the deposition chamber
      temperature_read_test = cuTstTemp.temperature(RNOMINAL, RREF); // + safety_shutdown; Temoerature read should be switched to the correct one of course 
  

      // Constant bias error correction from Python:
      float bias_dep = 0.016 * set_temperature_dep - 0.462;
      PID_error_dep = set_temperature_dep + (bias_dep) - temperature_read_dep; 
      //Calculate the P value
      PID_p_dep = kp * PID_error_dep; //0.01*kp * PID_error;
      //Calculate the I value in a range on +-3
      PID_i_dep = 0.01*PID_i_dep + (ki * PID_error_dep);


      // Temperature set in testing chamber 
      float bias_test = 0.016 * set_temperature_test - 0.462;
      PID_error_test = set_temperature_test + (bias_test) - temperature_read_test;
      //Calculate the P value
      PID_p_test = kp * PID_error_test; //0.01*kp * PID_error;
      //Calculate the I value in a range on +-3
      PID_i_test = 0.01*PID_i_test + (ki * PID_error_test);






      PID_value_dep = PID_p_dep + PID_i_dep; // we dont control using the derivative anyways 
      previous_error_dep = PID_error_dep;

      PID_value_test = PID_p_test + PID_i_test + ((2.378 + 0.92 * set_temperature_test) - tstTemp.temperature(RNOMINAL, RREF)) * 10; // Added KOH temperature correction 
      previous_error_test = PID_error_test;

    //We define PWM range between 0 and 255
      if(PID_value_dep < 0)
      {    PID_value_dep = 0;    }
      if(PID_value_dep > 255)  
      {    PID_value_dep = 255;  }
  
      if(PID_value_test < 0)
      {    PID_value_test = 0;    }
      if(PID_value_test > 255)  
      {    PID_value_test = 255;  }
  
      analogWrite(pwm_testing,PID_value_test);
      
      analogWrite(pwm_deposition,PID_value_dep);
      
      
    Serial.print("Heating power dep "); Serial.print(PID_value_dep);
    Serial.print("Heating power test "); Serial.print(PID_value_test);
    
  
  Serial.println();
  delay(2000);


}

String* splitString(String inputString, int& count) {
  // Count the number of spaces in the input string
  int spaceCount = 0;
  for (int i = 0; i < inputString.length(); i++) {
    if (inputString.charAt(i) == ' ') {
      spaceCount++;
    }
  }
  
  // Allocate memory for the array of tokens
  String* tokens = new String[spaceCount + 1]; // Add 1 for the last token
  int tokenIndex = 0;
  int startIndex = 0;
  
  // Loop through the characters in the input string
  for (int i = 0; i < inputString.length(); i++) {
    if (inputString.charAt(i) == ' ') {
      // Extract the substring between startIndex and i
      tokens[tokenIndex++] = inputString.substring(startIndex, i);
      startIndex = i + 1;
    }
  }
  
  // Extract the last token
  tokens[tokenIndex] = inputString.substring(startIndex);
  
  // Set the count of tokens
  count = spaceCount + 1;
  
  // Return the array of tokens
  return tokens;
}


