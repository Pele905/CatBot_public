//Declare pin functions on Arduino
// These are the controls for every single component on the board
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <Arduino.h>
Adafruit_PWMServoDriver myServo = Adafruit_PWMServoDriver();

#define SERVOMIN 150
#define SERVOMAX 600

uint8_t servonum = 9;
uint8_t numberOfServos = 9;

#define stp1 2
#define dir1 3

#define stp2 4
#define dir2 5

#define stp3 6
#define dir3 7

#define stp4 8
#define dir4 9

#define stp5 10
#define dir5 11

#define stp6 12
#define dir6 13

#define stp7 22
#define dir7 27

#define stpActuator 24
#define dirActuator 25

#define stpNickelWheel 26
#define dirNickelWheel 23

#define relayBx1pin1 29
#define relayBx1pin2 31
#define relayBx1pin3 33
#define relayBx1pin4 35
#define relayBx1pin5 37
#define relayBx1pin6 39
#define relayBx1pin7 41
#define relayBx1pin8 43
int connecting_testing_deposition_pin = 33;


//float stepsPerMl = 1425 / 5 // Determined from calibration

//Declare variables for functions

//rune input
//was 37
//41
int pump_liqiud_mixing_deposition_Pin = 39;
int pump_liquid_deposition_waste_Pin_old = 43;
int pump_liquid_testing_waste_Pin =37;
int pump_HCl_from_wire =29;
int pump_HCl_to_wire =31;
int pump_liquid_deposition_waste_Pin = 41;

int depTime = 0;
long delayTime = 0;
int offSetSteps = 300;
int state;
int stepsToMove = 0;
String action = "";
int pumpNumber = 0;
int nSteps = 0;
String direction = "";
int cmdLength = 0;
int stringState = 0;
// 
// 1 start default 
// 2 switches anticlockwise
// 3 switches anticlockwise
// 4 default 
// 5 default
// 6 switches anticlockwise
// 7 default 
void initializeServos() {
  anticlockwiseCallback(0);

  anticlockwiseCallback(1);
  clockwiseCallback(1);

  anticlockwiseCallback(2);
  clockwiseCallback(2);

  anticlockwiseCallback(3);
  anticlockwiseCallback(4);
  anticlockwiseCallback(5);
  clockwiseCallback(5);
  anticlockwiseCallback(6);

  anticlockwiseCallback(7); // Deinitializes the deposition servo
  anticlockwiseCallback(8); // Deinitializes the testing servo
}

void setup() {
  pinMode(stp1, OUTPUT);
  pinMode(dir1, OUTPUT);
  pinMode(stp2, OUTPUT);
  pinMode(dir2, OUTPUT);
  pinMode(stp3, OUTPUT);
  pinMode(dir3, OUTPUT);
  pinMode(stp4, OUTPUT);
  pinMode(dir4, OUTPUT);
  pinMode(stp5, OUTPUT);
  pinMode(dir5, OUTPUT);
  pinMode(stp6, OUTPUT);
  pinMode(dir6, OUTPUT);
  pinMode(stp7, OUTPUT);
  pinMode(dir7, OUTPUT);
  
  // Nickel wire wheel
  pinMode(stpActuator, OUTPUT);
  pinMode(dirActuator, OUTPUT);
  pinMode(stpNickelWheel, OUTPUT);
  pinMode(dirNickelWheel, OUTPUT);

  digitalWrite(dirNickelWheel, HIGH);
  digitalWrite(dirActuator, LOW);

  //rune input
  pinMode(pump_liqiud_mixing_deposition_Pin, OUTPUT);     // Set pin 39 (relayBx2pin39) as an output
  pinMode(pump_liquid_deposition_waste_Pin, OUTPUT);     // Set pin 41 (relayBx2pin41) as an output
  
  pinMode(pump_liquid_testing_waste_Pin, OUTPUT);
  pinMode(pump_HCl_from_wire, OUTPUT);
  pinMode(pump_HCl_to_wire, OUTPUT);
  

  pinMode(relayBx1pin1, OUTPUT);
  pinMode(relayBx1pin2, OUTPUT);
  pinMode(relayBx1pin3, OUTPUT);
  pinMode(relayBx1pin4, OUTPUT);
  pinMode(relayBx1pin5, OUTPUT);
  pinMode(relayBx1pin6, OUTPUT);
  pinMode(relayBx1pin7, OUTPUT);
  pinMode(relayBx1pin8, OUTPUT);

  pinMode(connecting_testing_deposition_pin, OUTPUT);
  Serial.begin(9600);
  myServo.begin();
  myServo.setPWMFreq(60);
  delay(10);
  initializeServos();
  char *ptr; // Pointer for strtok

  
}

//Main loop
// For the purpose of this, we will use the bigeasydriver 3 and 6 to test the rotating drum system
// ... (previous code)

// ... (previous code)

void loop() {
  Serial.println("Enter pump number, number of steps, and direction (e.g., '3 100 forward refill'):");
  while (Serial.available() == 0) {
    // Wait for user input
  }


  // Read pump number
  String inputString = Serial.readString();

  int count;
  String* cmdArr = splitString(inputString, count);
  
  // Print the tokens
  
  int cmdLength = sizeof(cmdArr) / sizeof(cmdArr[0]);

  action = cmdArr[0];

  // Distributing liquid into syringe pumps 
  // In the new program, we need to use space
  stringState = "";
  if (action == "SyringePumps") {  
    
    pumpNumber = cmdArr[1].toInt();
    stepsToMove = cmdArr[2].toInt();
    direction = cmdArr[3];
    // If we 
    
    if (count == 5) {
      stringState = "refill";
    }
    Serial.print(count);
    Serial.println(stringState);
    // Set the appropriate direction pins based on the pump number
    switch (pumpNumber) {
      case 1:
        
        if (stringState == "refill") {
          anticlockwiseCallback(0);
          delay(2000);
          
          
          if (direction == "forward") {
            digitalWrite(dir1, HIGH);
          } else {
            
            digitalWrite(dir1, LOW);
          }
          distributeLiquid(stepsToMove, stp1);
          // Here we need to add code such that the liquid that we loose inside the 
          // tubing when we turn the 3 way valve corrects for it and pumps forward say the amont + 3 ml to be on the safe side
          // Finally, this added liquid should be flushed out of the chambers
          //clockwiseCallback(0);
        } else {
          clockwiseCallback(0);
          

          if (direction == "forward") {
            digitalWrite(dir1, HIGH);
          } else {
            
            digitalWrite(dir1, LOW);
          }
          distributeLiquid(stepsToMove, stp1);

        }
        
        break;

      case 2:
        
        if (stringState == "refill") {
          clockwiseCallback(1);
          delay(2000);

          if (direction == "forward") {
            digitalWrite(dir2, HIGH);
          } else {
            digitalWrite(dir2, LOW);
          }
          
          distributeLiquid(stepsToMove, stp2);
          
          //clockwiseCallback(1);
        } else {
          anticlockwiseCallback(1);

          if (direction == "forward") {
            digitalWrite(dir2, HIGH);
          } else {
            digitalWrite(dir2, LOW);
          }

          distributeLiquid(stepsToMove, stp2);
          

        }
        
        break;

      // Pump 3 has the reverse polarity and cables therefore the reverse is true
      case 3:
        if (stringState == "refill") {
          clockwiseCallback(2);
          delay(2000);

          if (direction == "forward") {
            digitalWrite(dir3, HIGH);
          } else {
            digitalWrite(dir3, LOW);
          }
          
          distributeLiquid(stepsToMove, stp3);

          //clockwiseCallback(1);
        } else {
          // Removed thew anticlockwise callback
          anticlockwiseCallback(2);

          if (direction == "forward") {
            digitalWrite(dir3, HIGH);
          } else {
            digitalWrite(dir3, LOW);
          }

          
          distributeLiquid(stepsToMove, stp3);
          //digitalWrite(dir3, LOW);
          //distributeLiquid(offSetSteps * 2, stp3); // Adding these to test temorrow to see if we can directly pump liquid into the chamber
          // Instead of pumping into mixing chamber 
        }
        break;

      case 4:
          if (stringState == "refill") {
          anticlockwiseCallback(3);
          delay(2000);

          if (direction == "forward") {
            digitalWrite(dir4, HIGH);
          } else {
            digitalWrite(dir4, LOW);
          }
          
          distributeLiquid(stepsToMove, stp4);

          //clockwiseCallback(1);
        } else {
          clockwiseCallback(3);

          if (direction == "forward") {
            digitalWrite(dir4, HIGH);
          } else {
            digitalWrite(dir4, LOW);
          }

          
          distributeLiquid(stepsToMove, stp4);
          
        }
        break;

      case 5: // We want to use pump number 5 
          if (stringState == "refill") {
          anticlockwiseCallback(4);
          delay(2000);

          if (direction == "forward") {
            digitalWrite(dir5, HIGH);
          } else {
            digitalWrite(dir5, LOW);
          }
          
          distributeLiquid(stepsToMove, stp5);

          //clockwiseCallback(1);
        } else {
          clockwiseCallback(4);

          if (direction == "forward") {
            digitalWrite(dir5, HIGH);
          } else {
            digitalWrite(dir5, LOW);
          }

          distributeLiquid(stepsToMove, stp5);
        }
        break;
        // Also 6 is wrong
      case 6:
          if (stringState == "refill") {
          clockwiseCallback(5);
          delay(2000);

          if (direction == "forward") {
            digitalWrite(dir6, LOW);
          } else {
            digitalWrite(dir6, HIGH);
          }
          
          distributeLiquid(stepsToMove, stp6);

          //clockwiseCallback(1);
        } else {
          anticlockwiseCallback(5);

          if (direction == "forward") {
            digitalWrite(dir6, LOW);
          } else {
            digitalWrite(dir6, HIGH);
          }

          distributeLiquid(stepsToMove, stp6);
        }
        break;
      case 7:
        if (stringState == "refill") {
          anticlockwiseCallback(6);
          delay(2000);

          if (direction == "forward") {
            digitalWrite(dir7, HIGH);
          } else {
            digitalWrite(dir7, LOW);
          }
          
          distributeLiquid(stepsToMove, stp7);
         
          //clockwiseCallback(1);
        } else {
          clockwiseCallback(6);

          if (direction == "forward") {
            digitalWrite(dir7, HIGH);
          } else {
            digitalWrite(dir7, LOW);
          }

          distributeLiquid(stepsToMove, stp7);
        }
        break;


      default:
        Serial.println("Invalid pump number.");
        break;
    }
    Serial.println("SyringePump movement comp");
    stringState = "";
  }
  
  // Nickel wire rolling mechanisms
  if (action == "DipWireIntoHCl") {
    combinedLinearNickelWireMotion(11650, stpNickelWheel, stpActuator);
    Serial.println("Wire Rolled into HCl");
  }
  if (action == "RollWireHClToWater") {
    combinedLinearNickelWireMotion(18975, stpNickelWheel, stpActuator);
    Serial.println("Wire Rolled from HCl to water1");
    combinedLinearNickelWireMotion(18975, stpNickelWheel, stpActuator);
    Serial.println("Wire Rolled from HCl to water");
  }
  if (action == "RollWireWaterDeposition") {
    combinedLinearNickelWireMotion(19675, stpNickelWheel, stpActuator);
    Serial.println("Wire rolled water - deposition1");
    //combinedLinearNickelWireMotion(19475 + 200 - 5142, stpNickelWheel, stpActuator); //We subtract the length of a sample which is 77 mm or 5142 steps for robots 
    combinedLinearNickelWireMotion(19675 , stpNickelWheel, stpActuator);
    Serial.println("Wire rolled water - deposition");
  }
  if (action == "RollWireWaterTesting") {
    combinedLinearNickelWireMotion(30000, stpNickelWheel, stpActuator);
    Serial.println("Wire rolled water - testing 1");
    combinedLinearNickelWireMotion(21400, stpNickelWheel, stpActuator);
    Serial.println("Wire rolled water - testing");
  }
   if (action == "RollWireHClToDeposition") {
    // In the case that we have removes one water column
    combinedLinearNickelWireMotion(18650, stpNickelWheel, stpActuator);
    Serial.println("Wire rolled HCl - deposition1");
    combinedLinearNickelWireMotion(18650, stpNickelWheel, stpActuator);
    Serial.println("Wire rolled HCl - deposition");
  }

  if (action == "RollWireDepositionToTesting_RollingWhileDepositing") {
    // combinedLinearNickelWireMotion(20050, stpNickelWheel, stpActuator); this is the old one
    combinedLinearNickelWireMotion(20025, stpNickelWheel, stpActuator);
    Serial.println("Wire rolled deposition - testing 1");
    combinedLinearNickelWireMotion(14883, stpNickelWheel, stpActuator); // We also subtract the number of steps that is equal to the length of the deposited wire 
    Serial.println("Wire rolled deposition - testing");
  }
  if (action == "RollWireDepositionToTesting_RollingWhileDepositing_Ni_calib") {
    // combinedLinearNickelWireMotion(20050, stpNickelWheel, stpActuator); this is the old one
    combinedLinearNickelWireMotion(10025, stpNickelWheel, stpActuator); // We now roll 10000 steps to dip a fresh piece of Nickel wire into solution as a first start to get the nickel calibration
    Serial.println("Wire rolled deposition - testing 1");
    combinedLinearNickelWireMotion(14883, stpNickelWheel, stpActuator); // We also subtract the number of steps that is equal to the length of the deposited wire 
    Serial.println("Wire rolled deposition - testing");
  }
  if (action == "RollWireWaterDeposition_RollingWhileDepositing") {
    combinedLinearNickelWireMotion(19675, stpNickelWheel, stpActuator);
    Serial.println("Wire rolled water - deposition1");
    combinedLinearNickelWireMotion(14533, stpNickelWheel, stpActuator); //We subtract the length of a sample which is 77 mm or 5142 steps for robots 
    Serial.println("Wire rolled water - deposition");
  }
 
  if (action == "RollWireDepositionToTesting") {
    // combinedLinearNickelWireMotion(20050, stpNickelWheel, stpActuator); this is the old one
    combinedLinearNickelWireMotion(20025, stpNickelWheel, stpActuator);
    Serial.println("Wire rolled deposition - testing 1");
    //combinedLinearNickelWireMotion(19775 + 250 - 5142, stpNickelWheel, stpActuator); // We also subtract the number of steps that is equal to the length of the deposited wire 
    //combinedLinearNickelWireMotion(20050, stpNickelWheel, stpActuator); this is the old one, we now have calibrated the new one
    combinedLinearNickelWireMotion(20025, stpNickelWheel, stpActuator);
    Serial.println("Wire rolled deposition - testing");
  }


  if (action == "RollWireWhileExperimenting") {
    nSteps = cmdArr[1].toInt();
    depTime = cmdArr[2].toInt();
 
    rollNiWireWhileExperimenting(nSteps, stpNickelWheel, stpActuator, depTime);
    Serial.println("Wire rolled X number of steps");
  }

  if (action == "RollWireNSteps") {
    nSteps = cmdArr[1].toInt();
    combinedLinearNickelWireMotion(nSteps, stpNickelWheel, stpActuator);
    Serial.println("Wire rolled X number of steps");
  }
  if (action == "ReverRollWireNSteps") {
    nSteps = cmdArr[1].toInt();
    digitalWrite(dirActuator, HIGH);
    digitalWrite(dirNickelWheel, LOW);
    combinedLinearNickelWireMotion(nSteps, stpNickelWheel, stpActuator);
    Serial.println("Wire rolled X number of steps");
    digitalWrite(dirNickelWheel, HIGH);
    digitalWrite(dirActuator, LOW);
    Serial.println("Wire rolled reverse complete");
  
  }


  
 if (action == "MoveActuatorNSteps") {
    nSteps = cmdArr[1].toInt();
    moveLinearActuator(nSteps, stpActuator);
    Serial.println("Actuator moved N steps");
  }

 if (action == "ReverseMoveActuatorNSteps") {

    digitalWrite(dirActuator, HIGH);

    nSteps = cmdArr[1].toInt();
    moveLinearActuator(nSteps, stpActuator);
    Serial.println("Actuator moved N steps");
    digitalWrite(dirActuator, LOW);
  }

if (action == "RollNiWheelNSteps") {
    nSteps = cmdArr[1].toInt();
    digitalWrite(dirNickelWheel, HIGH);

    moveNiRoll(nSteps, stpNickelWheel);

    digitalWrite(dirNickelWheel, HIGH);

    delay(500);

    Serial.println("Wire rolled reversed - testing");

  }
if (action == "ReverseRollNiWheelNSteps") {
    nSteps = cmdArr[1].toInt();
    digitalWrite(dirNickelWheel, LOW);

    moveNiRoll(nSteps, stpNickelWheel);

    digitalWrite(dirNickelWheel, HIGH);

    delay(500);

    Serial.println("Wire rolled reversed - testing");

  }



  // Pumping actions

  //RUNE INPUT periastaltic pump
  if (action == "FILL_SOL") {
   
    digitalWrite(pump_liqiud_mixing_deposition_Pin, HIGH); 
    delay(10000); // Wait for 1 second
    digitalWrite(pump_liqiud_mixing_deposition_Pin, LOW);
    Serial.println("complete evacuation");
    
  } 

  if (action == "EVAC_SOL1") {
    digitalWrite(pump_liquid_deposition_waste_Pin_old, HIGH); 
    delay(10000);
    digitalWrite(pump_liquid_deposition_waste_Pin_old, LOW);
    Serial.println("complete evacuation");
  } 

  if (action == "EVAC_SOL") {
    digitalWrite(pump_liquid_deposition_waste_Pin, HIGH); 
    delay(10000); // Wait for 1 second
    digitalWrite(pump_liquid_deposition_waste_Pin, LOW);
    Serial.println("complete evacuation");
  } 

  if (action == "EVAC_SOL_TEST") {
    digitalWrite(pump_liquid_testing_waste_Pin, HIGH); 
    delay(10000);
    digitalWrite(pump_liquid_testing_waste_Pin, LOW);
    Serial.println("complete evacuation");
  } 

  if (action == "EVAC_HCL") {
    digitalWrite(pump_HCl_from_wire, HIGH); 
    delay(15000);
    digitalWrite(pump_HCl_from_wire, LOW);
    Serial.println("complete evacuation");
  }

    if (action == "FILL_HCL") {
    digitalWrite(pump_HCl_to_wire, HIGH); 
    delay(15000);
    digitalWrite(pump_HCl_to_wire, LOW);
    Serial.println("complete evacuation");
  }

  if (action == "ActivatePotentiostatDeposition") {
    clockwiseCallback(7);
    anticlockwiseCallback(8);
    digitalWrite(connecting_testing_deposition_pin, LOW);  
    Serial.println("Deposition Potentiostat Activated");
  }

  if (action == "DeactivatePotentiostatDeposition") {
    anticlockwiseCallback(7);
    digitalWrite(connecting_testing_deposition_pin, HIGH); 
    Serial.println("Deposition Potentiostat deactivated");
  }

  if (action == "ActivatePotentiostatTesting") {
    clockwiseCallback(8);
    anticlockwiseCallback(7);
    digitalWrite(connecting_testing_deposition_pin, HIGH);  
    Serial.println("Testing potentiostat activated");
  }

  if (action == "DeactivatePotentiostatTesting") {
    anticlockwiseCallback(8);
    digitalWrite(connecting_testing_deposition_pin, LOW);  
    Serial.println("Testing potentiostat dectivated");
  }

  // inser the evacuatiuon and fill using peruiastaltic
  
  delete[] cmdArr;
  cmdLength = 0;
  delay(1000);
}


void clockwiseCallback(int servonum) {
  for (uint16_t pulselen = SERVOMIN; pulselen < SERVOMAX; pulselen++) {
    myServo.setPWM(servonum, 0, pulselen);
  }
  delay(1500);
  // Your code for clockwise motion
  // This function will be called when the servo is moving clockwise
}

void anticlockwiseCallback(int servonum) {
  for (uint16_t pulselen = SERVOMAX; pulselen > SERVOMIN; pulselen--) {
    myServo.setPWM(servonum, 0, pulselen);
  }
  delay(1500);
  // Your code for anticlockwise motion
  // This function will be called when the servo is moving anticlockwise
}

void emptyLiquidToDeposition() {
  digitalWrite(relayBx1pin1, HIGH);
  delay(1500);
  // Your code for anticlockwise motion
  // This function will be called when the servo is moving anticlockwise
}

void emptyDepositionLiquidToWaste() {
  digitalWrite(relayBx1pin2, HIGH);
  delay(1500);
  // Your code for anticlockwise motion
  // This function will be called when the servo is moving anticlockwise
}

void distributeLiquid(int stepsToMove, int stp) {
  for (int x = 0; x < stepsToMove; x++) {
    digitalWrite(stp, HIGH);
    delay(2);
    digitalWrite(stp, LOW);
    delay(2); // How long we wait, 
    // Before it was 2 
  }
  delay(1500);
}

void distributeLiquidTestingChamber(int stepsToMove, int stp) {
  for (int x = 0; x < stepsToMove; x++) {
    digitalWrite(stp, HIGH);
    delay(6);
    digitalWrite(stp, LOW);
    delay(6); // How long we wait, 
    // Before it was 2 
  }
  delay(1500);
}

void dipWireIntoHCl(int stpNickelStepper, int stpLinearActuator) {
  // Dips initial wire into the HCl chamber
  combinedLinearNickelWireMotion(11650, stpNickelStepper, stpLinearActuator);
  //combinedLinearNickelWireMotion(17200+4400, stpNickelStepper, stpLinearActuator);
}

void transportWireThroughWater(int stpNickelStepper, int stpLinearActuator) {
  combinedLinearNickelWireMotion(23717, stpNickelStepper, stpLinearActuator);
}


void transportWireHClToWater(int stpNickelStepper, int stpLinearActuator) {
  // Transports wire from the HCl chamber into the water chamber 
  //combinedLinearNickelWireMotion(4400, stpNickelStepper, stpLinearActuator);
  combinedLinearNickelWireMotion(18975, stpNickelStepper, stpLinearActuator);
}

void transportWireWaterToDeposition(int stpNickelStepper, int stpLinearActuator) {
  combinedLinearNickelWireMotion(19350, stpNickelStepper, stpLinearActuator);
}
//20k too much

void transportWireDepositionToAlkaline(int stpNickelStepper, int stpLinearActuator) {
  combinedLinearNickelWireMotion(1000, stpNickelStepper, stpLinearActuator);
}

void transportWireNSteps(int steps, int stpNickelStepper, int stpLinearActuator) {
  combinedLinearNickelWireMotion(steps, stpNickelStepper, stpLinearActuator);
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


void combinedLinearNickelWireMotion(int stepsToMove, int stpNickelStepper, int stpLinearActuator) {
  // Combined stepper with linear actuator to make sure that the Nickel wire remains in the same space
  // One step moves the wire 
  int nickelStepCounter = 0;
    for (int x = 0; x < stepsToMove; x++) {
    // One step forward with Nickel wire, 3 steps back with linear actuator
    digitalWrite(stpNickelStepper, HIGH);
    delay(1);
    digitalWrite(stpNickelStepper, LOW);
    delay(1);
    nickelStepCounter++;
    // Now that we double the nicke step counter due to lower thread pitch, we change NickelStepCounter = 100 to NickelStepCounter = 200
    // Now we changed nickel step counter to 600 that is 1/3 of what it was previously
    if (nickelStepCounter == 600) {
            // Execute 3 steps back with linear actuator
            for (int i = 0; i < 3; i++) {
                digitalWrite(stpLinearActuator, HIGH);
                delay(1);
                digitalWrite(stpLinearActuator, LOW);
                delay(1);
            }
            // Reset Nickel step counter
            nickelStepCounter = 0;
        }
  }
  delay(1500);
}

void rollNiWireWhileExperimenting(int stepsToMove, int stpNickelStepper, int stpLinearActuator, long delayTime) {
  // Combined stepper with linear actuator to make sure that the Nickel wire remains in the same space
  // One step moves the wire 
  delay(10000); // Delay so that it matches with the OCV from the Admiral squidstat
  int nickelStepCounter = 0;
    for (int x = 0; x < stepsToMove; x++) {
    // One step forward with Nickel wire, 3 steps back with linear actuator
    digitalWrite(stpNickelStepper, HIGH);
    delay(1);
    digitalWrite(stpNickelStepper, LOW);
    delay(delayTime - 1 - 6/200);
    nickelStepCounter++;
    // Now that we double the nicke step counter due to lower thread pitch, we change NickelStepCounter = 100 to NickelStepCounter = 200
    if (nickelStepCounter == 200) {
            // Execute 3 steps back with linear actuator
            for (int i = 0; i < 3; i++) {
                digitalWrite(stpLinearActuator, HIGH);
                delay(1);
                digitalWrite(stpLinearActuator, LOW);
                delay(1);
            }
            // Reset Nickel step counter
            nickelStepCounter = 0;
        }
  }
  delay(1500);
}







void moveLinearActuator(int stepsToMove, int stpLinearActuator) {

  // Combined stepper with linear actuator to make sure that the Nickel wire remains in the same space



      for (int i = 0; i < stepsToMove; i++) {

          digitalWrite(stpLinearActuator, HIGH);

          delay(2);

          digitalWrite(stpLinearActuator, LOW);

          delay(2);

      }

  delay(1500);



  }




void moveNiRoll(int stepsToMove, int stpNickelStepper) {

  // Combined stepper with linear actuator to make sure that the Nickel wire remains in the same space

  // One step moves the wire 







      for (int i = 0; i < stepsToMove; i++) {

          digitalWrite(stpNickelStepper, HIGH);

          delay(2);

          digitalWrite(stpNickelStepper, LOW);

          delay(2);

      }

  delay(1500);



  }

