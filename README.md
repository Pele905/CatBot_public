# CatBot_public
Code for autonomous catalyst synthesis and testing platform (CatBot)


This project was developed and tested with the following versions:

- **Python:** 3.10
- **Arduino IDE:** 2.3.2

Startup guide:

The code for controlling Robot consists of the following parts:
  1) A roll to roll system, controlled through Nickel_wire_control_PA.py
  2) A liquid distribution system containing Liquid_distribution_control_PA.py
  3) A temperature control system controlled through temperature_control_PA.py
  4) A master script calling on these 3 subprocesses together
     
In order to

 For example, temperature_control_PA.py uses hard-coded calibration
data and Serial port constructor values which will need to be updated on
a new system

To run an experiment, the user needs to change the following aspects
1)  Ensure that the COM ports of the liquid distribution system and temperature measurement systems are correct when calling and initializing the robot:
  Robot_test = CatBot(serialcomm_temp='COM4', 
                      serialcomm_liquid='COM6') # Ensure these are correct COM port
2) In Python/temperature_control_PA.py a hard-coded calibration is used for setting the correct temperature in the following functions:
      set_temperature_both_chambers
       set_temperature_deposition
   set_temperature_testing
    
     The calibration which depends on temperature can be found for the function is this:
   get_temperature_correction_dep()
   This should be changed depending on the setup





       


