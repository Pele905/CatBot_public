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



## Full Example

This script shows how to initialize **CatBot**, configure an experiment, and run it.  
Update the COM ports and output folder before running.  

```python
import sys
import os
import time
from Catbot_control_master import CatBot
from utils import *
from experimental_protocols import coated_wire_testing_protocol_1
from experiment_class import Experiment

# --- Initialization ---
# Initialize CatBot (update COM ports to match your system)
Robot = CatBot(serialcomm_temp='COM4', serialcomm_liquid='COM6')
time.sleep(15)  # wait to ensure connection

# Define output folder
output_data_folder = r"C:\Users\YourName\Desktop\EC_data"

# Load a testing protocol
testing_experiment, testing_protocol_name = coated_wire_testing_protocol_1()

# --- Experiment Definition ---
experiment = Experiment(
    experimental_params={
        "Temperature_deposition [C]": 50, # Deposition temperature (°C)
        "Temperature_testing [C]": 80, # Testing chamber temperature (°C)
        "Testing liquid KOH [w %]": 30, # KOH concentration (wt %)
        "Deposition composition": {"NiSO4": 0.1275}, # Deposition bath composition [M]
        "Roll while depositing": True, # Roll wire during deposition
        "Testing protocol": {"testing protocol name": testing_protocol_name, "protocol": testing_experiment},
        "Deposition time [s]": 129, # Deposition time (s)
        "Deposition current density [mA/cm2]": 70.99, # Current density (mA/cm²)
        "Wire type": "Ni 99.8 %", # Wire material and purity
        "Filename testing data": "", # File to save testing data
        "Filename deposition data": "", # File to save deposition data
        "Filename temperature data": "", # File to save temperature data
        "Filename folder": "", # Custom output folder
        "General comments": "No comment", # Free-text notes
        "Clean after testing": True, # Flush chamber after experiment
        "Maintain KOH after testing": False, # Keep/reuse KOH solution
        "HCl dipping time [s]": 900, # Pretreatment in HCl (s)
        "HCl cleaning concentration [mol / L]": 3, # HCl concentration (mol/L)
        "KOH filling volume [ml]": 10.9, # Volume of KOH (mL)
        "Deposition filling volume [ml]": 15, # Volume of deposition solution (mL)
        "Experiment name": "", # Optional name
        "KOH batch": "Batch fabricated 04.11 Pre electrolyzed 100 h 30 wt %", # Batch details
        "Repeat experiment n cycles": 1, # Number of repetitions
        "Cleaning waiting time testing [s]": 60, # Dwell time for cleaning solution (testing chamber)
        "Cleaning waiting time deposition [s]": 60, # Dwell time for cleaning solution (deposition chamber)
        "Cleaning cycles testing chamber": 2, # Cleaning cycles (testing chamber)
        "Cleaning cycles deposition chamber": 2, # Cleaning cycles (deposition chamber)
        "Deposition batch": "Electrolyte 1 NiSO4 0.4 M with 0.4 M NaCitrate + 0.3 M NaCl Fabricated 21.11.24" # Stock solution
    }
)

# --- Run Experiment ---
Robot.run_complete_experiment(
    experiment=experiment, 
    empty_after_deposition=True, 
    keep_wire_stationary=False, 
    evacuate_chambers_before_starting=True, 
    output_data_folder=output_data_folder
)

# --- Shutdown (Safety) ---
time.sleep(5)
Robot.set_temperature_both_chambers(
    filename="bs.json",
    temperature_dep_electrolyte=30,
    temperature_KOH=30
)




       


