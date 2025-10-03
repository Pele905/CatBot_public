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
import threading 
# Add the parent directory to the system path as this is running in a subdirectory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
analysis_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', "Live_data_analysis"))
sys.path.append(analysis_path)
from Catbot_control_master import CatBot
from experimental_protocols import coated_wire_testing_protocol_1
from experiment_class import Experiment
from time import time

# Initialize the robot, 
# Important, when initializing robot, the serialcomms for temperature and liquid needs to be changed according to the users computer
Robot_test = CatBot(serialcomm_temp='COM4',
                    serialcomm_liquid='COM6') 

# Wait top ensure robot is ready to recieve commands
time.sleep(15)

# Define the deposition solution in your experimental pumps:
stock_solutions = {"H2SO4": {"Pump": 4, "Concentration [mol/L]" : 1}, 
                    'NiSO4' : {"Pump": 6, "Concentration [mol/L]" : 0.4},
                    "H2O": {"Pump": 3}} 

Robot_test.stock_solutions = stock_solutions


# Define the output data folder, where the data will be stored
output_data_folder = r"C:\Users\Catbot-adm\Desktop\EC_data_CatBot\Ni_Mo_optimization"


# Define both a testing experiment, and give the testing experiment a name
# The experiment is of type AisExperiment, the name ins a string
testing_experiment, testing_protocol_name = coated_wire_testing_protocol_1()

# Define the experiment
experiment_example_1 = Experiment(
    experimental_params={
        "Temperature_deposition [C]": 50, # Deposition temperature (°C, float)
        "Temperature_testing [C]": 80, # Testing chamber temperature (°C, float)
        "Testing liquid KOH [w %]": 30, # KOH concentration in testing solution (wt %, float)
        "Deposition composition": {"NiSO4": 0.1275}, # Deposition bath composition [M] (dict: species → float)
        "Roll while depositing": True, # Roll wire during deposition (bool)
        "Testing protocol": {"testing protocol name": testing_protocol_name,"protocol": testing_experiment}, # Testing protocol details (dict: name + procedure)
        "Deposition time [s]": 129, # Deposition time (s, float)
        "Deposition current density [mA/cm2]": 70.99, # Current density during deposition (mA/cm², float)
        "Wire type": "Ni 99.8 %", # Wire material and purity (string)
        "Filename testing data": "", # File to save testing data (string, optional)
        "Filename deposition data": "", # File to save deposition data (string, optional)
        "Filename temperature data": "", # File to save temperature data (string, optional)
        "Filename folder": "", # Custom output folder (string, optional)
        "General comments": "No comment", # Free-text experiment notes (string)
        "Clean after testing": True, # Flush testing chamber with water after experiment (bool)
        "Maintain KOH after testing": False, # Keep/reuse KOH solution after test (bool)
        "HCl dipping time [s]": 900, # Wire pretreatment in HCl (s, float)
        "HCl cleaning concentration [mol / L]": 3, # HCl cleaning solution concentration (mol/L, float)
        "KOH filling volume [ml]": 10.9, # KOH volume used in testing chamber (mL, float)
        "Deposition filling volume [ml]": 15, # Deposition solution volume (mL, float)
        "Experiment name": "", # Optional experiment name (string)
        "KOH batch": "Batch fabricated 04.11 Pre electrolyzed 100 h 30 wt %", # Batch ID / preparation details for KOH (string)
        "Repeat experiment n cycles": 1, # Number of repetitions of the experiment (int)
        "Cleaning waiting time testing [s]": 60, # Dwell time for cleaning solution in testing chamber (s, float)
        "Cleaning waiting time deposition [s]": 60, # Dwell time for cleaning solution in deposition chamber (s, float)
        "Cleaning cycles testing chamber": 2, # Number of cleaning cycles for testing chamber (int)
        "Cleaning cycles deposition chamber": 2, # Number of cleaning cycles for deposition chamber (int)
        "Deposition batch": "Electrolyte 1 NiSO4 0.4 M with 0.4 M NaCitrate + 0.3 M NaCl Fabricated 21.11.24" # Stock solution used for deposition (string)
    }
)

# Execute the pre-defined experiment
Robot_test.run_complete_experiment(experiment=experiment_example_1, 
                                empty_after_deposition=True, 
                                keep_wire_stationary=False, 
                                evacuate_chambers_before_starting=True, 
                                output_data_folder=output_data_folder)


time.sleep(5)
# Set the temperature low after finishing an experiment for safety 
Robot_test.set_temperature_both_chambers(filename="cooldown_T.json",
                                         temperature_dep_electrolyte=30,
                                           temperature_KOH=30)


       


