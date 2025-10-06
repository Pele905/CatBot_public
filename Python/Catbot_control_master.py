import serial 
import threading 

from PySide2.QtWidgets import QApplication

from temperature_control_PA import (set_temperature_deposition, 
                                    set_temperature_testing, 
                                    set_temperature_both_chambers, 
                                    check_convergence_periodically, 
                                    save_png_continuously)

from utils import calculate_volumes
from datetime import datetime

from Liquid_distribution_control_PA import (
    pump_liquids_syringe, 
    pump_liquid_testing_waste, pump_liquid_deposition_waste, 
    pump_liqiud_mixing_deposition, 
    pump_liquid_mixing_test, 
    pump_HCl_from_cleaning_station_to_holder, 
    pump_HCl_into_cleaning_station,
    set_liquids_syringe)

from Nickel_wire_control_PA import (
    roll_wire_deposition_testing,
    roll_wire_water_deposition,
    roll_wire_HCl_to_water,
    roll_wire_N_steps, 
    roll_wire_while_depositing, 
    reset_wheel_to_start, 
    reset_actuator
)
from admiral_experimental_setups import (run_specified_experiment, 
                                         run_new_testing_protocol, 
                                         run_CV_stability_wait_tests,
                                         run_testing_protocol_coated_wires, 
                                         run_GEIS, 
                                         run_OCP, 
                                         )

from experimental_protocols import deposition_experiment
from potentiostat_switching_control_PA import (activate_potentiostat_deposition, 
                                               activate_potentiostat_testing, 
                                               deactivate_potentiostat_deposition, 
                                               deactivate_potentiostat_testing)

import os
from experiment_class import Experiment
import json
import time
# Class that manages all robot components and provides functionality 
# for configuring and running experiments
class CatBot:
    """
        Orchestrates all modules required to run an experiment, coordinating hardware and software components.

        Responsibilities:
            - Controls temperature settings for the experiment.
            - Executes electrochemical experiments via by connection to potentiostat as well as ensuring proper electrical connections
            - Manages liquid handling operations.
            - Manages rolling the wire through different stages
            - Integrates all modules to run experiments smoothly and reliably.
    """
    def __init__(self, serialcomm_liquid = None, serialcomm_temp = None, stock_solutions = None):

        self.reload = False 
        self.app = QApplication([])
        self.log = {}
        if serialcomm_liquid == None:
            self.serialcomm_liquid = serial.Serial('COM3', 9600, timeout=2) 
            time.sleep(1)
            self.serialcomm_temp = serial.Serial('COM5', 115200, timeout=5)

        else:
            try:
                self.serialcomm_temp = serial.Serial(serialcomm_temp, 115200, timeout=5)
                time.sleep(1)
                self.serialcomm_liquid = serial.Serial(serialcomm_liquid, 9600, timeout=2)
                time.sleep(1)
            except Exception as e:
                print("Failed to connect to all COM ports")
                print(e)


        
        
        # The stock solution inside the different syringe pumps 
        if stock_solutions == None:
            self.stock_solutions = {"H2SO4": {"Pump": 4, "Concentration [mol/L]" : 1}, 
                                    'NiSO4' : {"Pump": 6, "Concentration [mol/L]" : 0.4},
                            "H2O": {"Pump": 3}} 
            
            self.pumping_liquids = {
                                "H2O": {"Pump": 3, "amount ml" : 0},
                                "H2SO4": {"Pump": 4, "amount ml" : 0},
                                "H2O": {"Pump": 5, "amount ml" : 0},
                                "NiSO4": {"Pump": 6, "amount ml" : 0}, 
                                "H2O": {"Pump": 7, "amount ml" : 0}, 
         }
        else:
            self.stock_solutions = stock_solutions
        
        # Cleaning liquids command for deposition chamber
        self.cleaning_liquids_command_dep = {
                                "Cleaning solution": {"Pump": 3, "amount ml" : 15.5},
         } 
        self.cleaning_liquids_command_test = {"KOH": {"Pump": 1, "amount ml" : 0}, 
                                "H2O": {"Pump": 2, "amount ml" : 12}}


        self.testing_liquid_command = {"KOH": {"Pump": 1, "amount ml" : 10.9}, 
                                "H2O": {"Pump": 2, "amount ml" : 0}, # We just measured the 
                                # amount  of liquid that we need to fill up the testing chamber
                                # until we reach the lower end of the 
         }
        self.fill_testing_tubing_command = {"KOH": {"Pump": 1, "amount ml" : 4}, 
                                "H2O": {"Pump": 2, "amount ml" : 4},}
        
        self.fill_deposition_tubing_command = {} # Should be called whenever we want to fill testing tubing

        self.temp_test = 30
        self.liquid_max = 15 # Max amount of liquid to distribute into the holder 
        self.syringe_pump_status = []

    def get_experiment_from_ML():
        # Call, and get library from ML 
        return 
    def set_temperature_dep_chamber(self, temperature, filename, convergence_setter = "Temp Electrolyte"):
        # Plot the data as well
        if hasattr(self, 'dep_thread') and self.dep_thread.is_alive():
            self.stop_event.set()
            self.dep_thread.join(10)
        if hasattr(self, 'convergence_thread_dep') and self.convergence_thread_dep.is_alive():
            self.stop_event.set()
            self.convergence_thread_dep.join(10)
        if hasattr(self, 'video_thread_dep') and self.video_thread_dep.is_alive():
            self.stop_event.set()
            self.video_thread.join(10)

        self.stop_event = threading.Event()
        self.dep_thread = threading.Thread(target=set_temperature_deposition, 
                                      args=(temperature, filename, self.serialcomm_temp,None, self.stop_event))
        self.dep_thread.daemon = True
        self.dep_thread.start()
        time.sleep(10) # Wait a few seconds 
        window_size = 50 # Window size for the temperature convergence is 100 s 
        interval = 10 # Interval for checking the temperature convergence is 10 s


        self.convergence_event_dep = threading.Event()
        self.convergence_thread_dep = threading.Thread(target=check_convergence_periodically,
                                        args = (interval, window_size, 
                                        filename, temperature, self.convergence_event_dep, convergence_setter))

        self.convergence_thread_dep.daemon = True
        self.convergence_thread_dep.start()
        time.sleep(5)

        self.video_thread_dep = threading.Thread(target=save_png_continuously, 
                                      args=(filename, 'deposition', self.stop_event))
        self.video_thread_dep.daemon = True
        self.video_thread_dep.start()
        
        #self.convergence_event_dep.wait()
        
    def set_temperature_both_chambers(self, filename, temperature_KOH = 30, temperature_dep_electrolyte = 30):
        if hasattr(self, 'temp_thread') and self.temp_thread.is_alive():
            self.stop_event_temp_thread.set()
            self.temp_thread.join()
            print('Killing thread temp')
        
        if hasattr(self, 'convergence_thread_test') and self.convergence_thread_test.is_alive():
            self.convergence_event_test.set()
            self.convergence_thread_test.join() # The error seems to be closing 
            print('Killing convergence thread test')
        if hasattr(self, 'convergence_thread_dep') and self.convergence_thread_dep.is_alive():
            self.convergence_event_dep.set()
            self.convergence_thread_dep.join()
            print('Killing convergence thread dep')

        if hasattr(self, 'video_thread') and self.video_thread.is_alive():
            self.stop_event_video.set()
            self.video_thread.join()
            print('Killing video thread test')
        
        print("We get to final part")
        self.stop_event_temp_thread = threading.Event()


        self.temp_thread = threading.Thread(target=set_temperature_both_chambers, 
                                      args=(temperature_dep_electrolyte,
                                             temperature_KOH, 
                                             filename, 
                                             self.serialcomm_temp,
                                               None,
                                                 self.stop_event_temp_thread))
        self.temp_thread.daemon = True
        self.temp_thread.start()
        time.sleep(10) # Wait a few seconds 
        window_size = 100 # Window size for the temperature convergence is 100 s 
        interval = 10 # Interval for checking the temperature convergence is 10 s

        self.convergence_event_test = threading.Event()
        self.convergence_thread_test = threading.Thread(target=check_convergence_periodically,
                                        args = (interval, window_size, 
                                        filename, temperature_KOH, self.convergence_event_test, 'Temp KOH', "KOH - Testing"))
        
        self.convergence_thread_test.daemon = True
        self.convergence_thread_test.start()

        self.convergence_event_dep = threading.Event()
        self.convergence_thread_dep = threading.Thread(target=check_convergence_periodically,
                                        args = (interval, window_size, 
                                        filename, temperature_dep_electrolyte, self.convergence_event_dep, "Temp Electrolyte", "Electrolyte - deposition"))
        

        self.convergence_thread_dep.daemon = True
        self.convergence_thread_dep.start()
        time.sleep(5)
        print("We get here")
        self.stop_event_video = threading.Event()
        self.video_thread = threading.Thread(target=save_png_continuously, 
                                      args=(filename,"both", self.stop_event_video))
        self.video_thread.daemon = True
        self.video_thread.start()
        time.sleep(5)
        print("This whole thing finishes")
        return     
    def set_temperature_testing_chamber(self, temperature, filename, convergence_setter = "Temp KOH"):
        '''
            Sets the temperature of the testing chamber, and chooses whether we use the KOH temperature, 
            or the copper temperature as convergence criteria 
        '''
        # Kills the threads so as to not overload the system   
        if hasattr(self, 'test_thread') and self.test_thread.is_alive():
            self.stop_event.set()
            self.test_thread.join()
            print('Killing thread test')
        if hasattr(self, 'convergence_thread_test') and self.convergence_thread_test.is_alive():
            self.stop_event.set()
            self.convergence_thread_test.join()
            print('Killing convergence thread test')
        if hasattr(self, 'video_thread_test') and self.video_thread_test.is_alive():
            self.stop_event.set()
            self.video_thread_test.join()
            print('Killing video thread test')
        self.stop_event = threading.Event()
        self.test_thread = threading.Thread(target=set_temperature_testing, 
                                      args=(temperature, filename, self.serialcomm_temp, None, self.stop_event))
        self.test_thread.daemon = True
        self.test_thread.start()
        time.sleep(10) # Wait a few seconds 
        window_size = 100 # Window size for the temperature convergence is 100 s 
        interval = 10 # Interval for checking the temperature convergence is 10 s

        self.convergence_event_test = threading.Event()
        self.convergence_thread_test = threading.Thread(target=check_convergence_periodically,
                                        args = (interval, window_size, 
                                        filename, temperature, self.convergence_event_test, convergence_setter))
        self.convergence_thread_test.daemon = True
        self.convergence_thread_test.start()
        time.sleep(5)
        print("We get here")
        self.video_thread_test = threading.Thread(target=save_png_continuously, 
                                      args=(filename, 'testing', self.stop_event))
        self.video_thread_test.daemon = True
        self.video_thread_test.start()
        time.sleep(5)
        print("This whole thing finishes")
    def write_experimental_params_to_dict(self,
                                         temperature_deposition,
                                         temperature_testing,
                                         KOH_concentration,
                                         HCl_dipping_time_s,
                                           syringe_pump_concentrations, 
                                           deposition_time, 
                                           deposition_current_density,
                                        experiment_name = "testing_1",
                                         filename = "",
                                         HCl_concentration = 3, 
                                         wire_type = "Ni 99.8 %",
                                         KOH_batch = "",
                                         KOH_filling_volume = "",
                                         deposition_filling_volume = "",
                                        retained_electrolyte = False,
                                        cleaning_cycles_testing = 2,
                                        cleaning_cycles_deposition = 2,
                                        cleaning_waiting_time_testing_s = 60,
                                        cleaning_waiting_time_deposition_s = 60,
                                        deposition_batch = "",
                                        experiment_cycle_number = 1,
                                        roll_while_depositing = True,
                                        protocol_name = "1",
                                         general_comment = "72 hours pre electrolyzed + 24 hours previously. Pumping through system. Also changed the counter and zirfon on 28/10 and cleaned the whole chamber",
                                         reference_electrode_shift = -1128, 
                                         pumped_volumes = {""}):
        '''
            This function here takes as input 
            1) Temperature
            2) Syringe_pump_concentrations
            3) Deposition time
            4) Deposition dict
            These are then turned into a dictionary, with a specified keyword 
            If append is true, we append the existing data onto an already existing dictionary
        '''
        retained_electrolyte_str = "True" if retained_electrolyte == True else "False"
        current_time = datetime.now()
        timestamp = current_time.strftime("%d.%m.%Y at %H:%M")
        
        experimental_parameter_dict = {experiment_name : {'deposition_time_s' : deposition_time,
                                   'deposition_current_density_cm2' : deposition_current_density, 
                                   'Deposition_T_K' : temperature_deposition,
                                   'Concentrations [mol/L]' : syringe_pump_concentrations,
                                   'KOH concentration [wt %]' : KOH_concentration, 
                                   'HCl dipping time [s]' : HCl_dipping_time_s,
                                   'HCl concentration [mol/L]' : HCl_concentration,
                                   'Testing_T_K' : temperature_testing,
                                   "general comment" : general_comment,
                                    "wire type" : wire_type,
                                    "KOH batch" : KOH_batch,
                                    "Deposition batch" : deposition_batch,
                                    "KOH filling volume" : KOH_filling_volume, 
                                    "Deposition filling volume" : deposition_filling_volume,
                                    "Retained electrolyte" : retained_electrolyte_str,
                                    "Water cleaning cycles after testing" : cleaning_cycles_testing,
                                    "Water cleaning cycles after deposition" : cleaning_cycles_deposition,
                                    "Water cleaning time testing [s]" : cleaning_waiting_time_testing_s,
                                    "Water cleaning time deposition [s]" : cleaning_waiting_time_deposition_s,
                                    "Experiment start time" : timestamp, 
                                    "Experiment cycle number" : experiment_cycle_number,
                                    "Roll while depositing" : roll_while_depositing, 
                                    "Protocol" : protocol_name,
                                    "Wire rolling sequence" : "",
                                    "Reference shift vs RHE [mV]" : reference_electrode_shift,
                                    "Pumped volumes [ml]" : pumped_volumes
                                   }}
        
        print(experimental_parameter_dict)
        if os.path.exists(filename):
            with open(filename, 'r') as json_file:
                existing_data = json.load(json_file)
            
            # Update the existing dictionary with the new data
            existing_data.update(experimental_parameter_dict)
            
            # Save the updated dictionary back to the file
            with open(filename, 'w') as json_file:
                json.dump(existing_data, json_file, indent=4)

        else:
            with open(filename, 'w') as json_file:
                json.dump(experimental_parameter_dict, json_file, indent=4)
        
    def write_testing_results_to_dict(self, testing_file):
        '''
            This function here takes as input the file containing all the testing data
            and subsequently turns it into a dictionary, containing 
            ECSA, Overpotential at 100 mA/cm2, Overpotential at 50 mA/cm2, Overpotential at 10 mA/cm2, impedance, stability
            These are then turned into a dictionary, with a specified keyword 
        '''
        return 
    
    def pump_liquids(self, data_logger_file = None, pump_data_dict = {}, chamber = "deposition"):
        '''
            Pumps all the liquids from the pump_data_dict into the testing / deposition chambers
        '''
        if data_logger_file == None:
            data_logger_file = "datalogger.json"
        while pump_liquids_syringe(pump_data_dict, 
                                   serialcomm = self.serialcomm_liquid, 
                                   data_logger_file = data_logger_file, 
                                   save_history = True, chamber = chamber) != True:
            confirmation = False
        confirmation = True
        return confirmation
    
    def pump_KOH_into_testing_chamber(self, 
                                  data_logger_file = None, 
                                  amount_ml = None, 
                                  concentration = 30, 
                                  ):
        '''
            Pumps desired amount of KOH into the testing mixing chamber 
            We have no changed this function such that we no longer need the testing mixing chamber
            Instead, we pup liquid directly into the chambers 
            Give an amount of ml KOH you want to pump into the chamber
        '''

        if data_logger_file == None:
            data_logger_file = "datalogger.json"
        
        # Concentration 
        if concentration > 30:
            print("Concentration exceeds the KOH concentration of 30 wt %")
            return ValueError
        
        pumping_liquid_command = {"KOH": {"Pump": 1, "amount ml" : amount_ml}, 
                            "H2O": {"Pump": 2, "amount ml" : 0}}
        
        while pump_liquids_syringe(pumping_liquid_command, 
                                serialcomm = self.serialcomm_liquid, 
                                data_logger_file = data_logger_file, 
                                save_history = True, chamber="testing") != True:
            confirmation = False
        
        confirmation = True
        return confirmation
    
    
    def initialize_testing_setup(self, data_logger_file = None):
        if data_logger_file == None:
            data_logger_file = "datalogger.json"
        
        while pump_liquids_syringe(self.fill_testing_tubing_command, 
                                   serialcomm = self.serialcomm_liquid, 
                                   data_logger_file = data_logger_file, 
                                   save_history = True) != True:
            confirmation = False
        confirmation = True
        return confirmation

    def pump_liqiud_mixing_deposition(self):
        pump_liqiud_mixing_deposition(serialcomm = self.serialcomm_liquid)
        return

    def pump_liquid_deposition_waste(self):
        pump_liquid_deposition_waste(serialcomm = self.serialcomm_liquid)
        return    
    

    def roll_while_experimentation(self):
        return 
    
    def pump_liquid_mixing_test(self):
        pump_liquid_mixing_test(serialcomm = self.serialcomm_liquid)
        return

    def pump_liquid_testing_waste(self):
        pump_liquid_testing_waste(serialcomm = self.serialcomm_liquid)
        return


    def pump_syringes_to_set(self):
       
        while set_liquids_syringe(self.cleaning_liquids_command, 
                                   serialcomm = self.serialcomm_liquid, 
                                   ) != True:
            confirmation = False
        return True

    def initialize_potentiostat_deposition(self):
        '''
            Calls on the servo motor to make electrical connection between the potentiostat and the deposition chamber
            and also connects the counter using a relay switch 
        '''
        activate_potentiostat_deposition(serialcomm=self.serialcomm_liquid)
        print("Potentiostat connected to deposition chamber")
         
    
    def uninitialize_potentiostat_deposition(self):
        '''
            Calls on the servo motor to disengage electrical connection between the potentiostat and the deposition chamber 
        '''
        deactivate_potentiostat_deposition(serialcomm = self.serialcomm_liquid) 
        print("Potentiostat disconnected to deposition chamber")

    def initialize_potentiostat_testing(self):
        '''
            Calls on the servo motor to make electrical connection between the potentiostat and the testing chamber
            and also connects the counter using a relay switch 
        '''
        activate_potentiostat_testing(serialcomm=self.serialcomm_liquid)
        print("Potentiostat connected to testing chamber")
        return 

    def uninitialize_potentiostat_testing(self):
        '''
            Calls on the servo motor to disengage electrical connection between the
            potentiostat and the testing chamber 
        '''
        deactivate_potentiostat_testing(serialcomm = self.serialcomm_liquid) 
        print("Potentiostat disconnected to testing chamber")



    def clean_deposition_chamber(self, data_logger_file = None, initialization_df = None,
                                 waiting_time=60, cleaning_cycles = 2):
        if data_logger_file == None:
            data_logger_file = "datalogger.json"
        confirmation = False 

        for _ in range(cleaning_cycles):
            #pump_data_dict, serialcomm = self.serialcomm_liquid, data_logger_file = data_logger_file, save_history = True
            while pump_liquids_syringe(self.cleaning_liquids_command_dep, 
                                    serialcomm = self.serialcomm_liquid, 
                                    data_logger_file = data_logger_file, 
                                    save_history = True, chamber = "deposition") != True:
                confirmation = False
            time.sleep(1)
            #self.pump_liquid_mixing_test() # We no longer use the mixing chamber for testing
            time.sleep(waiting_time)
            self.pump_liquid_deposition_waste()

        return True
    
    def clean_testing_chamber(self, data_logger_file = None, waiting_time = 60, cleaning_cycles = 2):
        '''
            Pumps water into the testing chamber cleaning_cycles times, and waits
        '''
        if data_logger_file == None:
            data_logger_file = "datalogger.json"
        confirmation = False 
        for cleaning_cycle in range(cleaning_cycles):
            while pump_liquids_syringe(self.cleaning_liquids_command_test, 
                                    serialcomm = self.serialcomm_liquid, 
                                    data_logger_file = data_logger_file, 
                                    save_history = True) != True:
                confirmation = False
            time.sleep(1)
            #self.pump_liquid_mixing_test() # We no longer use the mixing chamber for testing
            time.sleep(waiting_time)
            self.pump_liquid_testing_waste()
        return True
    #def clean_deposition_chamber(self, data_logger_file = None, initialization_df = None):

    
    def run_deposition_experiment(self, deposition_current_density=1, deposition_time=20, 
                                  filename="", COM_port="COM11", app = None, roll_while_depositing = True,
                                  squidstat_name = ""):
        
        '''
            Executes deposition experiment with the wire as a working electrode. 
        '''
        print("Rolling while depositing is set to : ", roll_while_depositing)
        if roll_while_depositing:

            # Make function for rolling the substrate while depositing 
            
            if hasattr(self, 'wire_rolling_thread') and self.wire_rolling_thread.is_alive():
                self.wire_rolling_thread.join()
            print('Killing thread rolling')

            self.wire_rolling_thread = threading.Thread(target=roll_wire_while_depositing, 
                                                args=(self.serialcomm_liquid,
                                                        deposition_time))
            self.wire_rolling_thread.daemon = True
            self.wire_rolling_thread.start()
            print("Wire rolling thread has started")
            deposition_experiment_test = deposition_experiment(deposition_time_s=deposition_time * 2, 
                                                               deposition_current_density_mA_cm2=deposition_current_density, 
                                                               )
            print("Started wire rolling thread")
            
            run_specified_experiment(filename=filename, app=self.app, experiment=deposition_experiment_test, 
                                     squidstat_name=squidstat_name,
                                       COM_port=COM_port)
            
            

        else:
            deposition_experiment_test = deposition_experiment(deposition_time=deposition_time * 2, 
                                                    deposition_current_density=deposition_current_density)
            
            run_specified_experiment(filename=filename, app=self.app, experiment=deposition_experiment_test, squidstat_name=squidstat_name, 
                                     COM_port=COM_port)
        
    
    
    def run_testing_protocol(self, filename = "", app = None):
        '''
            Function that sends direct orders to the admiral potentiostat to execute our testing protocol 
        '''
        run_new_testing_protocol(filename=filename, app = app)
        return 
    
    def run_CV_stability_wait_tests(self, filename = "", app = None, CV_wait_time = 30, wait_at_cutoff = 65):
        '''
            Run CV stability tests, where we wait at a certain cutoff for x amount of minutes
        '''
        run_CV_stability_wait_tests(filename=filename, 
                                    app = app, 
                                    CV_wait_time = CV_wait_time,
                                    wait_at_cutoff = wait_at_cutoff)

    
    def run_testing_protocol_coated_wires(self, filename = "", app = None):
        run_testing_protocol_coated_wires(filename=filename, app=app)
        return 

    def reset_Nickel_roll(self, data_logger_file = ""):
        reset_wheel_to_start(serialcomm=self.serialcomm_liquid, 
                             data_logger_file=data_logger_file)
    
    def dip_wire_into_HCl(self, dipping_time = 0, update_parameter_dict = False, parameter_dict_path = ""):
        '''
            Dips wire into HCl chamber and fills it with  HCl
        '''
        #steps_rolled = 1#roll_wire_into_HCl(self.serialcomm_liquid)
        if dipping_time != 0:
            pump_HCl_into_cleaning_station(serialcomm=self.serialcomm_liquid)
            time.sleep(dipping_time)
            pump_HCl_from_cleaning_station_to_holder(self.serialcomm_liquid)
        
        if os.path.exists(parameter_dict_path) and update_parameter_dict == True:
            with open(parameter_dict_path, 'r') as json_file:
                existing_data = json.load(json_file)
            
            filename = list(existing_data.keys())[0]
            # We no longer need to roll wire into HCl, as we are pumping HCl
            existing_data[filename]["Wire rolling sequence"] += f" -> Dipped wire into HCl steps: 0"
            
            with open(parameter_dict_path, 'w') as json_file:
                json.dump(existing_data, json_file, indent=4)

    
    def roll_wire_deposition_testing(self, through = True, update_parameter_dict = False, parameter_dict_path = "", calibrate_ref = False):
        '''
            Rolls wire from the deposition chamber to the testing chamber
        '''
        steps_rolled = roll_wire_deposition_testing(self.serialcomm_liquid, 
                                                    through=through,
                                                    calibrate_ref=calibrate_ref)
        
        if os.path.exists(parameter_dict_path) and update_parameter_dict == True:
            with open(parameter_dict_path, 'r') as json_file:
                existing_data = json.load(json_file)
            filename = list(existing_data.keys())[0]
            existing_data[filename]["Wire rolling sequence"] += f" -> Rolled wire deposition testing steps: {steps_rolled}"
            
            with open(parameter_dict_path, 'w') as json_file:
                json.dump(existing_data, json_file, indent=4)
        
    def roll_wire_HCl_to_water(self, update_parameter_dict = False, parameter_dict_path = ""):
        '''
            Rolls wire from the HCl chamber to the water chamber
        '''
        steps_rolled = roll_wire_HCl_to_water(self.serialcomm_liquid)
        if os.path.exists(parameter_dict_path) and update_parameter_dict == True:
            with open(parameter_dict_path, 'r') as json_file:
                existing_data = json.load(json_file)
            filename = list(existing_data.keys())[0]
            existing_data[filename]["Wire rolling sequence"] += f" -> Rolled wire HCl to water steps: {steps_rolled}"
            
            with open(parameter_dict_path, 'w') as json_file:
                json.dump(existing_data, json_file, indent=4)
    
    def roll_wire_water_deposition(self, through = True, update_parameter_dict = False, parameter_dict_path = ""):
        '''
            Rolls wire from the water chamber into the deposition chamber. 
        '''
        steps_rolled = roll_wire_water_deposition(self.serialcomm_liquid, through = through)
        if os.path.exists(parameter_dict_path) and update_parameter_dict == True:
            with open(parameter_dict_path, 'r') as json_file:
                existing_data = json.load(json_file)
            filename = list(existing_data.keys())[0]
            existing_data[filename]["Wire rolling sequence"] += f" -> Rolled wire water to deposition steps: {steps_rolled}"
            
            with open(parameter_dict_path, 'w') as json_file:
                json.dump(existing_data, json_file, indent=4)

    def reset_actuator_to_start(self):
        reset_actuator(serialcomm=self.serialcomm_liquid, 
                       data_logger_file="datalogger_wire_roll.json")
        
    def turn_off_heating(self, chamber = "deposition"):
        '''
            Function that turns off the heating of the deposition/testing chamber
        '''
        if chamber == "deposition":
            self.serialcomm_temp.write("Deposition 0".encode())
        else:
            self.serialcomm_temp.write("Testing 0".encode())
        time.sleep(1)
        return True

    def check_setup_working(self, 
    
                               temp_testing = 30, 
                               filename_temp_testing_data = "data.json",
                               filename_testing_data = "data.csv"):
        '''
            Script to run prior to running any experiments to make sure
            that we can set both temperature, as well as ensure that the Admiral is 
            properly connected
        '''
        time.sleep(10)
        self.set_temperature_testing_chamber(filename=filename_temp_testing_data, 
                temperature=temp_testing)
        time.sleep(10)
        self.initialize_potentiostat_testing()

        self.run_fast_test(filename=filename_testing_data, app=self.app)
        return 
    def run_retain_electrolyte_test(self, temp_testing = 0, 
                               filename_temp_testing_data = "",
                               KOH_concentration = 30,
                               HCl_dipping_time = 15,
                               filename_testing_data = "",
                               initialize_testing_setup = False,
                               squidstat_error = False,
                               servo_initialization_error = False,
                               experimental_protocol = {"protocol_name" : "second_protocol", 
                                                        "parameters": {"waiting_time_CVs": None, "wait_at_cutoff": None,"XPS_cutoff_cycle": None}},
                               
                               experiment = None):
        
        if initialize_testing_setup == True: # Fills tubes if you use arduino script to fill syringe pumps 
            # this function essentially fills up the water and liquid tubings with the needed amount of liquid
            # This is then emptied later 
            
            #self.initialize_testing_setup()
            time.sleep(1)
            self.pump_liquid_testing_waste()
            self.pump_KOH_into_testing_chamber()
        
        self.write_experimental_params_to_dict(temperature_deposition="Room temperature",
                                               temperature_testing=temp_testing,
                                               KOH_concentration=KOH_concentration,
                                               HCl_dipping_time=HCl_dipping_time,
                                               syringe_pump_concentrations={"NiSO4": 0.33,'MnSO4': 0.33, 'FeSO4': 0.33},
                                               deposition_time=0,
                                               deposition_current_density=0,
                                               experiment_name=filename_testing_data.split(".csv")[0],
                                               filename=filename_testing_data.split("csv")[0] + "_parameter_dict.json")
        time.sleep(1)
        #self.set_temperature_testing_chamber(filename=filename_temp_testing_data, 
        #                temperature=temp_testing)
        self.set_temperature_both_chambers(filename=filename_temp_testing_data, temperature_KOH=temp_testing,
                                           temperature_dep_electrolyte=20)
        
        #self.pump_liquid_testing_waste() # In case that you already have liquid filled into chamber, 
        time.sleep(1) # No matter what this should always be there 
       
        self.dip_wire_into_HCl()
        time.sleep(HCl_dipping_time * 60)

        # By now changing the order in which we do our experiments, we can now effectively 
        # allow the wire to be rolled in to testing chamber exactly when it is needed
        self.roll_wire_HCl_to_water()
        time.sleep(1)
        #self.roll_wire_water_deposition()
        self.roll_wire_water_deposition()
        # Now temperature is converged, bring the Nickel wire into the chamber 
        while not self.convergence_event_test.is_set():
            print("Waiting for temperature to converge")
            time.sleep(5)
        
        self.convergence_thread_test.join()
        time.sleep(1)
        
        #self.roll_wire_waiting_deposition()
        time.sleep(1)
        self.roll_wire_deposition_testing()
       
        time.sleep(1)

        self.initialize_potentiostat_testing() # Connect the potentiostat using the servo motor
        
        time.sleep(5)

        run_specified_experiment(filename=filename_testing_data, app = self.app,
                                  experiment=experiment)
        
        time.sleep(1)

        print("Threads closed") 
        #self.serialcomm_temp.write("Testing 0".encode()) # Turn off temperature regulation
        
        time.sleep(1)
       
        self.uninitialize_potentiostat_testing()
        
    def run_testing_experiment(self, temp_testing = 0, 
                               filename_temp_testing_data = "",
                               KOH_concentration = 30,
                               HCl_dipping_time = 15,
                               filename_testing_data = "",
                               initialize_testing_setup = False,
                               squidstat_error = False,
                               servo_initialization_error = False,
                               experiment = None, 
                               clean_testing_holder = True
                               ):
        '''
            Runs an experiment without applying a coating onto the Nickel wire electrode.
        '''
        if initialize_testing_setup == True: # Fills tubes if you use arduino script to fill syringe pumps 
            # this function essentially fills up the water and liquid tubings with the needed amount of liquid
            # This is then emptied later 
            
            self.initialize_testing_setup()
            time.sleep(1)
            self.pump_liquid_testing_waste()
        
        self.write_experimental_params_to_dict(temperature_deposition="Room temperature",
                                               temperature_testing=temp_testing,
                                               KOH_concentration=KOH_concentration,
                                               HCl_dipping_time=HCl_dipping_time,
                                               syringe_pump_concentrations={"NiSO4": 0.33,'MnSO4': 0.33, 'FeSO4': 0.33},
                                               deposition_time=0,
                                               deposition_current_density=0,
                                               experiment_name=filename_testing_data.split(".csv")[0],
                                               filename=filename_testing_data.split("csv")[0] + "_parameter_dict.json")
        time.sleep(1)
        #self.set_temperature_testing_chamber(filename=filename_temp_testing_data, 
        #                temperature=temp_testing)
        self.set_temperature_both_chambers(filename=filename_temp_testing_data, temperature_KOH=temp_testing,
                                           temperature_dep_electrolyte=20)
        
        self.pump_liquid_testing_waste() # In case that you already have liquid filled into chamber, 
        time.sleep(1) # No matter what this should always be there 
        self.pump_KOH_into_testing_chamber()
        self.dip_wire_into_HCl()
        time.sleep(HCl_dipping_time * 60)

        # By now changing the order in which we do our experiments, we can now effectively 
        # allow the wire to be rolled in to testing chamber exactly when it is needed
        self.roll_wire_HCl_to_water()
        time.sleep(1)
        self.roll_wire_water_deposition(through=False)
        
        # Now temperature is converged, bring the Nickel wire into the chamber 
        while not self.convergence_event_test.is_set():
            print("Waiting for temperature to converge")
            time.sleep(5)
        
        self.convergence_thread_test.join()
        time.sleep(1)
        
        self.roll_wire_deposition_testing(through=False)

        time.sleep(1)

        self.initialize_potentiostat_testing() # Connect the potentiostat using the servo motor
        
        # Run experiment
        run_specified_experiment(filename=filename_testing_data, app = self.app,
                                  experiment=experiment)
        print("Threads closed") 
        #self.serialcomm_temp.write("Testing 0".encode()) # Turn off temperature regulation
        self.pump_liquid_testing_waste()
        time.sleep(1)
        if clean_testing_holder:

            self.clean_testing_chamber()
        self.uninitialize_potentiostat_testing()
        
    def run_OCP(self, filename = "", app = None, time = 20):
        run_OCP(filename=filename, app = app, time=time)

    def run_GEIS(self, filename = "123.csv", app = None, current = 1):
        '''
            Run GEIS, with specific current. Saves the data in filename
        '''
        run_GEIS(filename=filename, app=self.app, current=current)
    
    def evacuate_all_tubings(self, evacuation_volume = 4):
        '''
            Function that evacuates volume in all tubings to ensure that there are no airbubbles when starting an experiment
        '''
        evacuate_tubings_command = {"0": {"Pump": 1, "amount ml" : evacuation_volume}, 
                                "1": {"Pump": 2, "amount ml" : evacuation_volume},
                                "2": {"Pump": 3, "amount ml" : evacuation_volume},
                                "3": {"Pump": 4, "amount ml" : evacuation_volume},
                                "4": {"Pump": 5, "amount ml" : evacuation_volume},
                                "5": {"Pump": 6, "amount ml" : evacuation_volume},
                                "6": {"Pump": 7, "amount ml" : evacuation_volume}}
        self.pump_liquids(pump_data_dict=evacuate_tubings_command, 
                            chamber="deposition")
        self.pump_liquid_testing_waste()
        time.sleep(1)
        self.pump_liquid_deposition_waste()
        print("Tubings evacuted")
        return 

    def run_complete_experiment(self, 
                                experiment: Experiment, # You can also just give it this
                               temp_deposition=None, 
                               temp_testing=None, 
                               filename_dep_data=None,
                               filename_temperature_data=None,
                               filename_testing_data=None,
                               deposition_current_density_mA=None,
                               deposition_time=None, 
                               parameter_dict_filename="parameter_saving_test.json",
                               liquid_concentrations=None,
                               experiment_name=None,
                               KOH_concentration=None, 
                               HCl_dipping_time=None, 
                               testing_experiment=None,
                               roll_while_depositing=None,
                               pump_liquids_KOH=True, 
                               pump_liquids_dep=True,
                               testing_protocol=None,
                               wire_type=None,
                               filename_folder=None,
                               comments=None,
                               testing_chamber_cleaning_cycles=None,
                               maintain_KOH_after_testing=None,
                               KOH_filling_volume_ml=10.9,
                               deposition_filling_volume_ml=15,
                               KOH_batch="04_11_pre_electrolyzed_96_h",
                               repeat_experiment_n_times=1,
                               evacuate_chambers_before_starting = True, 
                               empty_after_deposition = True,
                               keep_wire_stationary = False,
                               output_data_folder = "", 
                               filename_keywords = "",
                               reference_electrode_shift = -1128, 
                               nickel_calibration_exp = None
                       ):
        '''
            Runs a full experiment sequence in one go. 

            This includes:
            1. Electrode cleaning (HCl pretreatment and cleaning in water)
            2. Electrodeposition (setting deposition chamber temperature, pumping deposition solution, and applying current density)
            3. Electrochemical testing (setting testing chamber temperature, filling with KOH, and running the defined testing protocol)
        '''


        calibrate_ref = False
        # Extract all parameters from the experimental params
        if experiment.experimental_params != {}:
            temp_deposition = experiment.dep_temperature
            temp_testing = experiment.testing_temperature
            filename_dep_data = experiment.filename_depositon_data
            filename_temperature_data = experiment.filename_temperature_data
            filename_testing_data = experiment.filename_testing_data
            deposition_current_density_mA = experiment.dep_current_density_mA_cm2
            deposition_time = experiment.deposition_time_s
            liquid_concentrations = experiment.deposiotion_composition_mol_l
            KOH_concentration = experiment.KOH_concentration_wp
            HCl_dipping_time_s = experiment.HCl_dipping_time_s
            roll_while_depositing = experiment.roll_while_depositing
            testing_protocol = experiment.testing_protocol["protocol"]
            testing_protocol_name = experiment.testing_protocol["testing protocol name"]
            wire_type = experiment.wire_type
            comments = experiment.comments
            testing_chamber_cleaning_cycles = experiment.testing_chamber_cleaning_cycles
            maintain_KOH_after_testing = experiment.maintain_KOH_after_testing
            KOH_filling_volume_ml = experiment.KOH_filling_volume_ml
            deposition_filling_volume_ml = experiment.deposition_filling_volume_ml
            KOH_batch = experiment.KOH_batch
            repeat_experiment_n_times = experiment.repeat_experiment_n_times
            cleaning_waiting_time_testing_chamber_s = experiment.cleaning_waiting_time_testing_s
            cleaning_waiting_time_deposition_chamber_s = experiment.cleaning_waiting_time_deposition_s
            cleaning_cycles_deposition_chamber = experiment.deposition_chamber_cleaning_cycles
            cleaning_cycles_testing_chamber = experiment.testing_chamber_cleaning_cycles
            deposition_batch = experiment.deposition_batch
            HCl_cleaning_concentration = experiment.HCl_cleaning_conc
        
        maintain_KOH_after_testing_str = "True" if maintain_KOH_after_testing == True else "False"
        roll_while_depositing_str = "True" if roll_while_depositing else "False"
        print(deposition_time, "This is deposition time")
        if evacuate_chambers_before_starting:
            self.pump_liquid_deposition_waste()
        
       
        for _ in range(repeat_experiment_n_times):
            
            # Calculate the amount in ml of each solution to ensure the correct concentration of different metals in the deposition liquid
            self.pumping_liquids = calculate_volumes(self.stock_solutions, 
                                        liquid_concentrations, 
                                        chamber_volume=deposition_filling_volume_ml)
            
            experiment.make_folder_based_on_parameters()
            experiment.set_experiment_name_based_on_experiment()
            experiment.set_deposition_filename_from_parameters()
            experiment.set_testing_filename_from_parameters()
            print(experiment.filename_folder, "This is filename folder")
            
            #experiment_subfolder_path = experiment.make_folder_for_subexperiment(return_folder = True)
            
           # If we specify the output folder, the data is instead stored under output data folder
            if output_data_folder != "":
                num_experiments = len(os.listdir(output_data_folder))
                
                current_time = datetime.now()
                timestamp = current_time.strftime("%d_%m_%Y_%H_%M_")

                experiment_output_folder = os.path.join(output_data_folder, f"{timestamp}_exp_{num_experiments + 1}")

                os.mkdir(experiment_output_folder)
                filename_testing_data = os.path.join(experiment_output_folder, 
                                                                f"Testing_data_{timestamp}_exp_{num_experiments + 1}.csv")
                
                filename_deposition_data = os.path.join(experiment_output_folder, 
                                                                   filename_keywords + f"dep_data_{timestamp}_exp_{num_experiments + 1}.csv")

                
                filename_temperature_data = os.path.join(experiment_output_folder, 
                                                        "temperature_data.json")
                
                filename_calibration_data = os.path.join(experiment_output_folder, f"Nickel_calibration_data_{timestamp}_exp_{num_experiments + 1}.csv")
                parameter_dict_filename = experiment.get_parameter_dict_name()
                parameter_dict_abs_path = os.path.join(experiment_output_folder, parameter_dict_filename)

                experiment.filename_depositon_data = filename_deposition_data
                experiment.filename_testing_data = filename_testing_data


            else:
                filename_testing_data = os.path.join(experiment_subfolder_path,
                                                    experiment.filename_testing_data)
                
                filename_deposition_data = os.path.join(experiment_subfolder_path,
                                                    
                                                    experiment.filename_depositon_data)
                
                filename_temperature_data = os.path.join(experiment_subfolder_path, 
                                                        "temperature_data.json")
                
                print(os.path.exists(experiment_subfolder_path), " It  does exsgstæfjs")
                parameter_dict_filename = experiment.get_parameter_dict_name()
                parameter_dict_abs_path = os.path.join(experiment_subfolder_path, parameter_dict_filename)
            try:
                # Write all the experimental parameters to a dictionary. 
                # The parameters are defined in the Experiment()
                self.write_experimental_params_to_dict(temperature_deposition=temp_deposition,
                                        temperature_testing=temp_testing,
                                        KOH_concentration=KOH_concentration,
                                        HCl_dipping_time_s=HCl_dipping_time_s,
                                        syringe_pump_concentrations=liquid_concentrations,
                                        deposition_time=deposition_time,
                                        deposition_current_density=deposition_current_density_mA,
                                        experiment_name=experiment.experiment_name,
                                        filename=parameter_dict_abs_path,
                                        general_comment = comments, 
                                        wire_type=wire_type, 
                                        KOH_batch=KOH_batch, 
                                        deposition_filling_volume=deposition_filling_volume_ml,
                                        KOH_filling_volume = KOH_filling_volume_ml, 
                                        cleaning_waiting_time_testing_s = cleaning_waiting_time_testing_chamber_s, 
                                        cleaning_waiting_time_deposition_s = cleaning_waiting_time_deposition_chamber_s, 
                                        cleaning_cycles_deposition=cleaning_cycles_deposition_chamber, 
                                        cleaning_cycles_testing=cleaning_cycles_testing_chamber, 
                                        experiment_cycle_number=experiment.experiment_count,
                                        retained_electrolyte=maintain_KOH_after_testing_str, 
                                        deposition_batch=deposition_batch, 
                                        HCl_concentration= HCl_cleaning_concentration,
                                        roll_while_depositing = roll_while_depositing_str,
                                        protocol_name=testing_protocol_name, 
                                        reference_electrode_shift = -reference_electrode_shift, 
                                        pumped_volumes=self.pumping_liquids
                                        )
            except:
                pass
            if maintain_KOH_after_testing and experiment.experiment_count == 1:
                
                self.pump_liquid_testing_waste()
                time.sleep(1)
                self.pump_KOH_into_testing_chamber(amount_ml=KOH_filling_volume_ml)

            if maintain_KOH_after_testing == False:
                
                self.pump_liquid_testing_waste()
                time.sleep(1)
                self.pump_KOH_into_testing_chamber(amount_ml=KOH_filling_volume_ml)
            
            time.sleep(1)
            
            print(self.pumping_liquids)
            # Pump the deposition solution into the deposition chamber
            self.pump_liquids(pump_data_dict=self.pumping_liquids, 
                            chamber="deposition")
            
            time.sleep(1)
            # Set the temperature in deposition and testing chamber
            self.set_temperature_both_chambers(filename=filename_temperature_data, 
                                temperature_KOH=temp_testing,
                                temperature_dep_electrolyte=temp_deposition)
            time.sleep(1)
            
            # Setting the temperature of both chambers
            # Calls the function that fills the chamber with HCl and also dips it for x amount of seconds 
            if keep_wire_stationary == False:
                self.dip_wire_into_HCl(dipping_time=HCl_dipping_time_s, 
                                    update_parameter_dict = True, 
                                    parameter_dict_path=parameter_dict_abs_path)
                time.sleep(1)
                self.roll_wire_HCl_to_water(update_parameter_dict = True, 
                                    parameter_dict_path=parameter_dict_abs_path)
            time.sleep(1)
            # Ensure that we actually do deposition. 
            # If we dont, then we are investigating a bare nickel wire
            if deposition_current_density_mA != 0 and deposition_time != 0:
                start_time = time.time()
                convergence_time = 0
                # Waiting for convergence in deposition chamber before rolling wire into the chamber
                while not self.convergence_event_dep.is_set():
                    print("Waiting for temperature to converge deposition chamber")
                    convergence_time = time.time() - start_time
                    if convergence_time > 6000:
                        self.convergence_event_dep.set()
                    time.sleep(5)
                
                self.convergence_thread_dep.join()
                
                time.sleep(1)
                if keep_wire_stationary == False:
                    self.roll_wire_water_deposition(through=roll_while_depositing, update_parameter_dict = True, 
                                                    parameter_dict_path=parameter_dict_abs_path)
                time.sleep(1)
                
                self.initialize_potentiostat_deposition() # Connect the potentiostat to the wire (working electrode) and the counter electrode

                # Execute the deposition experiment
                self.run_deposition_experiment(deposition_current_density=deposition_current_density_mA, 
                                            deposition_time=deposition_time, 
                                            filename=filename_deposition_data, 
                                            roll_while_depositing = roll_while_depositing, 
                                            squidstat_name="Plus2254", 
                                            COM_port="COM9") # Check on your own computer to see that potentiostat connects to the correct COM port

                
                self.pump_liquid_deposition_waste() # Pump the deposition liquid into the waste bin
                time.sleep(1)
                self.uninitialize_potentiostat_deposition() # Disconnect the potentiostat to the wire (working electrode) and the counter electrode 
                time.sleep(1)
                # Clean the deposition chamber with water
                self.clean_deposition_chamber(waiting_time=cleaning_waiting_time_deposition_chamber_s, 
                                              cleaning_cycles=cleaning_cycles_deposition_chamber)
            else:
                if keep_wire_stationary == False:
                    self.roll_wire_water_deposition(through=roll_while_depositing, update_parameter_dict = True, 
                                    parameter_dict_path=parameter_dict_abs_path)
                time.sleep(1)
            
            convergence_time = 0
            start_time = time.time()
            # Wait for temperature to converge in testing chamber
            while not self.convergence_event_test.is_set():
                print("Waiting for temperature to converge testing")
                convergence_time = time.time() - start_time
                if convergence_time > 7200:
                    self.convergence_event_test.set()
                time.sleep(5)
            
            self.convergence_thread_test.join()
            time.sleep(1)
            # Here run a calibration scan for the bare nickel wire if we chose to give it 
            if nickel_calibration_exp != None:
                roll_wire_N_steps(serialcomm=self.serialcomm_liquid, 
                                  N_steps=10000) # Roll fresh piece of Nickel wire into testing chamber
                self.initialize_potentiostat_testing()
                run_specified_experiment(filename=filename_calibration_data, 
                                        app=self.app, 
                                        experiment=nickel_calibration_exp,
                                        COM_port="COM9",
                                        squidstat_name="Plus2254")
                self.uninitialize_potentiostat_testing()
                calibrate_ref = True
                time.sleep(20)
            
            # If we dont run a calibration experiment with a bare nickel wire piece, roll the coated electrode into the testing chamber
            if keep_wire_stationary == False:
                self.roll_wire_deposition_testing(through=roll_while_depositing, update_parameter_dict = True, 
                                       parameter_dict_path=parameter_dict_abs_path, calibrate_ref=calibrate_ref)

            time.sleep(1)

            self.initialize_potentiostat_testing() # Connect the potentiostat to the wire (working electrode), the counter electrode and the reference electrode in the testing chamber
            
            time.sleep(5)
            # Execute the defined electrochemical experiment
            run_specified_experiment(filename=filename_testing_data, 
                                    app=self.app, 
                                    experiment=testing_protocol, squidstat_name="Plus2254", 
                                    COM_port="COM9") # Here please change the COM-port to match your own computer, and also ensure that the squidstat is of the same type, with the same name

            time.sleep(1)
            
            # Clean the testing chamber
            if maintain_KOH_after_testing == False:
                self.pump_liquid_testing_waste()
                time.sleep(1)
                self.clean_testing_chamber(waiting_time = cleaning_waiting_time_testing_chamber_s,
                                        cleaning_cycles=testing_chamber_cleaning_cycles)
            
            self.uninitialize_potentiostat_testing() # Disconnect the potentiostat to the wire (working electrode), the counter electrode and the reference electrode in the testing chamber
            experiment.update_experiment_count() # Update the experiment count (+1)
            

    def close_connection(self):
        try:

            self.serialcomm_liquid.close()
            #self.serialcomm_temp.close()
        except Exception as e:
            print(e)
            print("Failed to disconnect serial ports")
            
def main():
    print("")
if __name__ == "__main__":
    main()
