# CatBot_public
Code for autonomous catalyst synthesis and testing platform (CatBot)


This project was developed and tested with the following versions:

- **Python:** 3.10.11
- **Arduino IDE:** 2.3.2


Structure:
The CatBot control code is organized into the following modules:

1) **Roll-to-roll system** – manages wire movement and deposition; implemented in `Nickel_wire_control_PA.py`  
2) **Liquid distribution system** – controls pumps and fluid handling; implemented in `Liquid_distribution_control_PA.py`  
3) **Temperature control system** – maintains temperatures in the chambers; implemented in `temperature_control_PA.py`  
4) **Potentiostat control system** – connects the potentiostat as well as maintaining electrical connection; implemented in `potentiostat_switching_control_PA.py` and `admiral_experimental_setups.py`
6) **Master control script** – coordinates the four subsystems to run complete experiments including electrodeposition and subsequent testing

     
Before starting

 For example, temperature_control_PA.py uses hard-coded calibration
data and Serial port constructor values which will need to be updated on
a new system

## 1. Serial Port (COM Port) Configuration

The primary scripts use specific, hard-coded COM ports to communicate with the liquid distribution and temperature control systems.
Note that the liquid distribution system also hands wire rolling as well as potentiostat connections. COM ports can be located by navigating to "Device Manager" in Windows, and then 
scrolling down to reveal "ports (COM & LPT)".

* **Action:** Update the `serialcomm_temp` and `serialcomm_liquid` parameters below to use the correct COM ports assigned by your operating system.

```python
# UPDATE THESE VALUES
Robot_test = CatBot(
    serialcomm_temp='COM4',    # <- Verify and update the COM port for the temperature system
    serialcomm_liquid='COM6'   # <- Verify and update the COM port for the liquid system
)
```
The same should be done about the COM port for the potentiostat that is connected to your computer. 

```python
self.run_deposition_experiment(deposition_current_density=deposition_current_density_mA, 
                                            deposition_time=deposition_time, 
                                            filename=filename_deposition_data, 
                                            roll_while_depositing = roll_while_depositing, 
                                            squidstat_name="Plus2254", 
                                            COM_port="COM9") # Change the COM port to match your computers COM port
```
and 
```python
run_specified_experiment(filename=filename_calibration_data, 
                                        app=self.app, 
                                        experiment=nickel_calibration_exp,
                                        COM_port="COM9",
                                        squidstat_name="Plus2254")  # Change the COM port to match your computers COM port
```
### 2. Temperature Calibration Data

The file `Python/temperature_control_PA.py` relies on a **hard-coded calibration** curve to ensure accurate temperature setting. This calibration is specific to the hardware setup and must be verified or updated for your system. In our setup, we observed a temperature offset when the temperature was higher than 30 °C. We found empirically that adding (1 / 0.96) × 0.0834 = 0.086 °C/°C, to the set temperature i.e., increasing it by 0.086 °C for every degree yielded the correct actual temperature.

To calibrate the temperature settings of your setup, select a series of setpoints, for example, 30, 40, 50, 60, 70, and 80 °C and measure the temperature offset (ΔT) at each point.
The temperature offset ΔT should vary linearly with the set temperature. The slope of this relationship indicates how much you need to adjust the set temperature to achieve the actual desired temperature.

* **Calibration Function:** The relevant calibration logic is contained within the functions:
    ```python
    def get_temperature_correction_dep(T):
    '''
        Function that adds the correct offset to the temperature to ensure that
        the liquid electrolyte obtains the correct temperature.
        Corrections are based on the following data.
    '''
    if T > 29.75:
        delta_T = round((1 / 0.96) * 0.0834 * (T - 29.75), 2)  
        return delta_T
    return 0

    def get_temperature_correction_test(T):
    '''
        Function that adds the correct offset to the temperature to ensure that
        the liquid electrolyte obtains the correct temperature.
        Corrections are based on the following data.
    '''
    if T > 29.75:
        delta_T = round((1 / 0.96) * 0.0834 * (T - 29.75), 2)  
        return delta_T
    return 0
    ```
    These functions adds a constant linear shift depending on temperature such that the set temperature equals the temperature in the chamber
* **Impact:** The data provided by this function is consumed by the main temperature control methods:
    * `set_temperature_both_chambers`
    * `set_temperature_deposition`
    * `set_temperature_testing`

Update the `get_temperature_correction_dep()` and `get_temperature_correction_test()` functions based on your current setup's temperature readings.
This might mean changing the slope of the temperature offset.



## Full Example

This script shows how to initialize **CatBot**, configure an experiment, and run it. The script can also be found under Python/ExperimentRunningScripts/run_arbitrary_experiment.py 
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
import time

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
output_data_folder = r"path/to/output"

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
```
Experimental Parameters
Parameter	Description	Type	Example / Default	Typical Range / Notes
Temperature_deposition [C]	Deposition temperature	float	50	~20–90 °C
Temperature_testing [C]	Testing chamber temperature	float	80	~20–90 °C
Testing liquid KOH [w %]	KOH concentration in testing solution	float	30	10–40 wt %
Deposition composition	Deposition bath composition (species → molarity)	dict[str → float]	{ "NiSO4": 0.1275 }	Typically 0.01–0.5 M
Roll while depositing	Roll wire during deposition	bool	True	Enables moving substrate during deposition
Testing protocol	Testing procedure and metadata	dict	{ "testing protocol name": ..., "protocol": ... }	Defines test sequence
Deposition time [s]	Deposition duration	float	129	Depends on desired thickness
Deposition current density [mA/cm2]	Deposition current density	float	70.99	~1–200 mA/cm²
Wire type	Wire material and purity	str	"Ni 99.8 %"	e.g., Ni, Cu, Mo
Filename testing data	Output file for testing data	str	""	Optional
Filename deposition data	Output file for deposition data	str	""	Optional
Filename temperature data	Output file for temperature log	str	""	Optional
Filename folder	Custom output folder path	str	""	Optional
General comments	Free-text notes about experiment	str	"No comment"	Optional
Clean after testing	Flush testing chamber with water	bool	True	Recommended
Maintain KOH after testing	Keep/reuse KOH solution	bool	False	True only if same batch reused
HCl dipping time [s]	Wire pretreatment duration in HCl	float	900	30–1800 s typical
HCl cleaning concentration [mol / L]	HCl concentration for cleaning	float	3	0.1–5 mol/L
KOH filling volume [ml]	Volume of KOH solution in testing chamber	float	10.9	Depends on cell volume
Deposition filling volume [ml]	Volume of deposition solution	float	15	Depends on chamber size
Experiment name	Optional experiment name	str	""	Free text
KOH batch	Batch ID / preparation notes	str	"Batch fabricated 04.11 Pre electrolyzed 100 h 30 wt %"	Record provenance
Repeat experiment n cycles	Number of experiment repetitions	int	1	≥ 1
Cleaning waiting time testing [s]	Dwell time for cleaning solution (testing chamber)	float	60	10–120 s typical
Cleaning waiting time deposition [s]	Dwell time for cleaning solution (deposition chamber)	float	60	10–120 s typical
Cleaning cycles testing chamber	Number of cleaning cycles (testing chamber)	int	2	1–5
Cleaning cycles deposition chamber	Number of cleaning cycles (deposition chamber)	int	2	1–5
Deposition batch	Stock electrolyte used for deposition	str	"Electrolyte 1 NiSO4 0.4 M with 0.4 M NaCitrate + 0.3 M NaCl Fabricated 21.11.24"	Record preparation details

       


