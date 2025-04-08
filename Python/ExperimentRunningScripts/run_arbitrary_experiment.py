import sys
import os
import threading 
# Add the parent directory to the system path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
analysis_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', "Live_data_analysis"))
sys.path.append(analysis_path)
# Now you can import from the parent directory
from Catbot_control_master import *
from utils import *
from experimental_protocols import *
from experiment_class import *
from Live_data_analysis import live_data_analysis_after_testing as data_analysis

Robot_test = CatBot(serialcomm_temp='COM4',
                    serialcomm_liquid='COM6') # Initialize a catbot with two different serialcomms 

time.sleep(15)
# Testing experiment that you want to run
EC_data_path = "C:\\Users\\Catbot-adm\\Desktop\\CatBot\\Python\\Electrochemical_data\\Electrochemical_data_second_phase\\Data_dicts"

ECSA_dict_path = os.path.join(EC_data_path, "CV_ECSA_dict_all_data.json")
CP_dict_name_path = os.path.join(EC_data_path, "CP_datadict_all_data.json")
CV_cycling_stability_dict_path = os.path.join(EC_data_path, "CV_cycling_stability_dict_all_data.json")
EIS_dict_path = os.path.join(EC_data_path, "EIS_dict_all_data.json")
LSV_dict_path = os.path.join(EC_data_path, "LSV_dict_all_data.json")

testing_experiment, testing_protocol_name = coated_wire_testing_protocol_1()





experiment_ML_set_4_nr_1 = Experiment(experimental_params={"Temperature_deposition [C]" : 79, 
              "Temperature_testing [C]" : 80,
              "Testing liquid KOH [w %]": 30, 
                "Deposition composition" : {"NiSO4": 0.1275},
                "Roll while depositing" : True, 
                "Testing protocol" : {"testing protocol name" : testing_protocol_name, "protocol" : testing_experiment},
                "Deposition time [s]" : 129, 
                "Deposition current density [mA/cm2]" : 70.99, 
                "Wire type" : "Ni 99.8 %",
                "Filename testing data" : "",
                "Filename deposition data" : "", 
                "Filename temperature data" : "",
                "Filename folder" : "", 
                "General comments" : "No comment",
                "Clean after testing" : True, 
                "Maintain KOH after testing" : False, # This is to do retained electrolyte experiments 
                "Optimize using ML" : False, 
                "HCl dipping time [s]" : 900,
                "HCl cleaning concentration [mol / L]" : 3, 
                "KOH filling volume [ml]" : 10.9,
                "Deposition filling volume [ml]" : 15,
                "Experiment name" : "", 
                "KOH batch" : "Batch fabricated 04.11 Pre electrolyzed 100 h 30 wt %", 
                "Repeat experiment n cycles" : 1, # How many times you want to repeat the experiment 
                "Cleaning waiting time testing [s]" : 60, 
                "Cleaning waiting time deposition [s]" : 60, 
                "Cleaning cycles testing chamber" : 2, 
                "Cleaning cycles deposition chamber" : 2, 
                "Deposition batch" : "Electrolyte 1 NiSO4 0.4 M with 0.4 M NaCitrate + 0.3 M NaCl Fabricated 21.11.24", 
                "HCl concentration [mol / L]" : 3})


experiment_ML_set_4_nr_2 = Experiment(experimental_params={"Temperature_deposition [C]" : 79, 
              "Temperature_testing [C]" : 80,
              "Testing liquid KOH [w %]": 30, 
                "Deposition composition" : {"NiSO4": 0.2902},
                "Roll while depositing" : True, 
                "Testing protocol" : {"testing protocol name" : testing_protocol_name, "protocol" : testing_experiment},
                "Deposition time [s]" : 96.5, 
                "Deposition current density [mA/cm2]" : 62.6, 
                "Wire type" : "Ni 99.8 %",
                "Filename testing data" : "",
                "Filename deposition data" : "", 
                "Filename temperature data" : "",
                "Filename folder" : "", 
                "General comments" : "No comment",
                "Clean after testing" : True, 
                "Maintain KOH after testing" : False, # This is to do retained electrolyte experiments 
                "Optimize using ML" : False, 
                "HCl dipping time [s]" : 900,
                "HCl cleaning concentration [mol / L]" : 3, 
                "KOH filling volume [ml]" : 10.9,
                "Deposition filling volume [ml]" : 15,
                "Experiment name" : "", 
                "KOH batch" : "Batch fabricated 04.11 Pre electrolyzed 100 h 30 wt %", 
                "Repeat experiment n cycles" : 1, # How many times you want to repeat the experiment 
                "Cleaning waiting time testing [s]" : 60, 
                "Cleaning waiting time deposition [s]" : 60, 
                "Cleaning cycles testing chamber" : 2, 
                "Cleaning cycles deposition chamber" : 2, 
                "Deposition batch" : "Electrolyte 1 NiSO4 0.4 M with 0.4 M NaCitrate + 0.3 M NaCl Fabricated 21.11.24", 
                "HCl concentration [mol / L]" : 3})


experiment_ML_set_4_nr_3 = Experiment(experimental_params={"Temperature_deposition [C]" : 28.4, 
              "Temperature_testing [C]" : 80,
              "Testing liquid KOH [w %]": 30, 
                "Deposition composition" : {"NiSO4": 0.2387},
                "Roll while depositing" : True, 
                "Testing protocol" : {"testing protocol name" : testing_protocol_name, "protocol" : testing_experiment},
                "Deposition time [s]" : 162.8, 
                "Deposition current density [mA/cm2]" : 66.2, 
                "Wire type" : "Ni 99.8 %",
                "Filename testing data" : "",
                "Filename deposition data" : "", 
                "Filename temperature data" : "",
                "Filename folder" : "", 
                "General comments" : "No comment",
                "Clean after testing" : True, 
                "Maintain KOH after testing" : False, # This is to do retained electrolyte experiments 
                "Optimize using ML" : False, 
                "HCl dipping time [s]" : 900,
                "HCl cleaning concentration [mol / L]" : 3, 
                "KOH filling volume [ml]" : 10.9,
                "Deposition filling volume [ml]" : 15,
                "Experiment name" : "", 
                "KOH batch" : "Batch fabricated 04.11 Pre electrolyzed 100 h 30 wt %", 
                "Repeat experiment n cycles" : 1, # How many times you want to repeat the experiment 
                "Cleaning waiting time testing [s]" : 60, 
                "Cleaning waiting time deposition [s]" : 60, 
                "Cleaning cycles testing chamber" : 2, 
                "Cleaning cycles deposition chamber" : 2, 
                "Deposition batch" : "Electrolyte 1 NiSO4 0.4 M with 0.4 M NaCitrate + 0.3 M NaCl Fabricated 21.11.24", 
                "HCl concentration [mol / L]" : 3})

######################################################################################################################################################
experiment_ML_set_4_nr_4 = Experiment(experimental_params={"Temperature_deposition [C]" : 79, 
              "Temperature_testing [C]" : 80,
              "Testing liquid KOH [w %]": 30, 
                "Deposition composition" : {"NiSO4": 0.4},
                "Roll while depositing" : True, 
                "Testing protocol" : {"testing protocol name" : testing_protocol_name, "protocol" : testing_experiment},
                "Deposition time [s]" : 201.7, 
                "Deposition current density [mA/cm2]" : 96.3, 
                "Wire type" : "Ni 99.8 %",
                "Filename testing data" : "",
                "Filename deposition data" : "", 
                "Filename temperature data" : "",
                "Filename folder" : "", 
                "General comments" : "No comment",
                "Clean after testing" : True, 
                "Maintain KOH after testing" : False, # This is to do retained electrolyte experiments 
                "Optimize using ML" : False, 
                "HCl dipping time [s]" : 900,
                "HCl cleaning concentration [mol / L]" : 3, 
                "KOH filling volume [ml]" : 10.9,
                "Deposition filling volume [ml]" : 15,
                "Experiment name" : "", 
                "KOH batch" : "Batch fabricated 04.11 Pre electrolyzed 100 h 30 wt %", 
                "Repeat experiment n cycles" : 1, # How many times you want to repeat the experiment 
                "Cleaning waiting time testing [s]" : 60, 
                "Cleaning waiting time deposition [s]" : 60, 
                "Cleaning cycles testing chamber" : 2, 
                "Cleaning cycles deposition chamber" : 2, 
                "Deposition batch" : "Electrolyte 1 NiSO4 0.4 M with 0.4 M NaCitrate + 0.3 M NaCl Fabricated 21.11.24", 
                "HCl concentration [mol / L]" : 3})



experiment_ML_set_4_nr_5 = Experiment(experimental_params={"Temperature_deposition [C]" : 28.4, 
              "Temperature_testing [C]" : 80,
              "Testing liquid KOH [w %]": 30, 
                "Deposition composition" : {"NiSO4": 0.4},
                "Roll while depositing" : True, 
                "Testing protocol" : {"testing protocol name" : testing_protocol_name, "protocol" : testing_experiment},
                "Deposition time [s]" : 173.4, 
                "Deposition current density [mA/cm2]" : 10.1, 
                "Wire type" : "Ni 99.8 %",
                "Filename testing data" : "",
                "Filename deposition data" : "", 
                "Filename temperature data" : "",
                "Filename folder" : "", 
                "General comments" : "No comment",
                "Clean after testing" : True, 
                "Maintain KOH after testing" : False, # This is to do retained electrolyte experiments 
                "Optimize using ML" : False, 
                "HCl dipping time [s]" : 900,
                "HCl cleaning concentration [mol / L]" : 3, 
                "KOH filling volume [ml]" : 10.9,
                "Deposition filling volume [ml]" : 15,
                "Experiment name" : "", 
                "KOH batch" : "Batch fabricated 04.11 Pre electrolyzed 100 h 30 wt %", 
                "Repeat experiment n cycles" : 1, # How many times you want to repeat the experiment 
                "Cleaning waiting time testing [s]" : 60, 
                "Cleaning waiting time deposition [s]" : 60, 
                "Cleaning cycles testing chamber" : 2, 
                "Cleaning cycles deposition chamber" : 2, 
                "Deposition batch" : "Electrolyte 1 NiSO4 0.4 M with 0.4 M NaCitrate + 0.3 M NaCl Fabricated 21.11.24", 
                "HCl concentration [mol / L]" : 3})


experiment_ML_set_4_nr_6 = Experiment(experimental_params={"Temperature_deposition [C]" : 28.4, 
              "Temperature_testing [C]" : 80,
              "Testing liquid KOH [w %]": 30, 
                "Deposition composition" : {"NiSO4": 0.3629},
                "Roll while depositing" : True, 
                "Testing protocol" : {"testing protocol name" : testing_protocol_name, "protocol" : testing_experiment},
                "Deposition time [s]" : 312, 
                "Deposition current density [mA/cm2]" : 78.8, 
                "Wire type" : "Ni 99.8 %",
                "Filename testing data" : "",
                "Filename deposition data" : "", 
                "Filename temperature data" : "",
                "Filename folder" : "", 
                "General comments" : "No comment",
                "Clean after testing" : True, 
                "Maintain KOH after testing" : False, # This is to do retained electrolyte experiments 
                "Optimize using ML" : False, 
                "HCl dipping time [s]" : 900,
                "HCl cleaning concentration [mol / L]" : 3, 
                "KOH filling volume [ml]" : 10.9,
                "Deposition filling volume [ml]" : 15,
                "Experiment name" : "", 
                "KOH batch" : "Batch fabricated 04.11 Pre electrolyzed 100 h 30 wt %", 
                "Repeat experiment n cycles" : 1, # How many times you want to repeat the experiment 
                "Cleaning waiting time testing [s]" : 60, 
                "Cleaning waiting time deposition [s]" : 60, 
                "Cleaning cycles testing chamber" : 2, 
                "Cleaning cycles deposition chamber" : 2, 
                "Deposition batch" : "Electrolyte 1 NiSO4 0.4 M with 0.4 M NaCitrate + 0.3 M NaCl Fabricated 21.11.24", 
                "HCl concentration [mol / L]" : 3})
    


experiment_ML_set_4_nr_7 = Experiment(experimental_params={"Temperature_deposition [C]" : 28.4, 
              "Temperature_testing [C]" : 80,
              "Testing liquid KOH [w %]": 30, 
                "Deposition composition" : {"NiSO4": 0.32},
                "Roll while depositing" : True, 
                "Testing protocol" : {"testing protocol name" : testing_protocol_name, "protocol" : testing_experiment},
                "Deposition time [s]" : 40, 
                "Deposition current density [mA/cm2]" : 76.2, 
                "Wire type" : "Ni 99.8 %",
                "Filename testing data" : "",
                "Filename deposition data" : "", 
                "Filename temperature data" : "",
                "Filename folder" : "", 
                "General comments" : "No comment",
                "Clean after testing" : True, 
                "Maintain KOH after testing" : False, # This is to do retained electrolyte experiments 
                "Optimize using ML" : False, 
                "HCl dipping time [s]" : 900,
                "HCl cleaning concentration [mol / L]" : 3, 
                "KOH filling volume [ml]" : 10.9,
                "Deposition filling volume [ml]" : 15,
                "Experiment name" : "", 
                "KOH batch" : "Batch fabricated 04.11 Pre electrolyzed 100 h 30 wt %", 
                "Repeat experiment n cycles" : 1, # How many times you want to repeat the experiment 
                "Cleaning waiting time testing [s]" : 60, 
                "Cleaning waiting time deposition [s]" : 60, 
                "Cleaning cycles testing chamber" : 2, 
                "Cleaning cycles deposition chamber" : 2, 
                "Deposition batch" : "Electrolyte 1 NiSO4 0.4 M with 0.4 M NaCitrate + 0.3 M NaCl Fabricated 21.11.24", 
                "HCl concentration [mol / L]" : 3})


experiment_ML_set_4_nr_8 = Experiment(experimental_params={"Temperature_deposition [C]" : 55.9, 
              "Temperature_testing [C]" : 80,
              "Testing liquid KOH [w %]": 30, 
                "Deposition composition" : {"NiSO4": 0.0555},
                "Roll while depositing" : True, 
                "Testing protocol" : {"testing protocol name" : testing_protocol_name, "protocol" : testing_experiment},
                "Deposition time [s]" : 95.9, 
                "Deposition current density [mA/cm2]" : 51.5, 
                "Wire type" : "Ni 99.8 %",
                "Filename testing data" : "",
                "Filename deposition data" : "", 
                "Filename temperature data" : "",
                "Filename folder" : "", 
                "General comments" : "No comment",
                "Clean after testing" : True, 
                "Maintain KOH after testing" : False, # This is to do retained electrolyte experiments 
                "Optimize using ML" : False, 
                "HCl dipping time [s]" : 900,
                "HCl cleaning concentration [mol / L]" : 3, 
                "KOH filling volume [ml]" : 10.9,
                "Deposition filling volume [ml]" : 15,
                "Experiment name" : "", 
                "KOH batch" : "Batch fabricated 04.11 Pre electrolyzed 100 h 30 wt %", 
                "Repeat experiment n cycles" : 1, # How many times you want to repeat the experiment 
                "Cleaning waiting time testing [s]" : 60, 
                "Cleaning waiting time deposition [s]" : 60, 
                "Cleaning cycles testing chamber" : 2, 
                "Cleaning cycles deposition chamber" : 2, 
                "Deposition batch" : "Electrolyte 1 NiSO4 0.4 M with 0.4 M NaCitrate + 0.3 M NaCl Fabricated 21.11.24", 
                "HCl concentration [mol / L]" : 3})


experiment_ML_set_4_nr_9 = Experiment(experimental_params={"Temperature_deposition [C]" : 28.4, 
              "Temperature_testing [C]" : 80,
              "Testing liquid KOH [w %]": 30, 
                "Deposition composition" : {"NiSO4": 0.0823},
                "Roll while depositing" : True, 
                "Testing protocol" : {"testing protocol name" : testing_protocol_name, "protocol" : testing_experiment},
                "Deposition time [s]" : 156.6, 
                "Deposition current density [mA/cm2]" : 9.7, 
                "Wire type" : "Ni 99.8 %",
                "Filename testing data" : "",
                "Filename deposition data" : "", 
                "Filename temperature data" : "",
                "Filename folder" : "", 
                "General comments" : "No comment",
                "Clean after testing" : True, 
                "Maintain KOH after testing" : False, # This is to do retained electrolyte experiments 
                "Optimize using ML" : False, 
                "HCl dipping time [s]" : 900,
                "HCl cleaning concentration [mol / L]" : 3, 
                "KOH filling volume [ml]" : 10.9,
                "Deposition filling volume [ml]" : 15,
                "Experiment name" : "", 
                "KOH batch" : "Batch fabricated 04.11 Pre electrolyzed 100 h 30 wt %", 
                "Repeat experiment n cycles" : 1, # How many times you want to repeat the experiment 
                "Cleaning waiting time testing [s]" : 60, 
                "Cleaning waiting time deposition [s]" : 60, 
                "Cleaning cycles testing chamber" : 2, 
                "Cleaning cycles deposition chamber" : 2, 
                "Deposition batch" : "Electrolyte 1 NiSO4 0.4 M with 0.4 M NaCitrate + 0.3 M NaCl Fabricated 21.11.24", 
                "HCl concentration [mol / L]" : 3})


experiment_ML_set_4_nr_10 = Experiment(experimental_params={"Temperature_deposition [C]" : 39.6, 
              "Temperature_testing [C]" : 80,
              "Testing liquid KOH [w %]": 30, 
                "Deposition composition" : {"NiSO4": 0.0},
                "Roll while depositing" : True, 
                "Testing protocol" : {"testing protocol name" : testing_protocol_name, "protocol" : testing_experiment},
                "Deposition time [s]" : 312, 
                "Deposition current density [mA/cm2]" : 4, 
                "Wire type" : "Ni 99.8 %",
                "Filename testing data" : "",
                "Filename deposition data" : "", 
                "Filename temperature data" : "",
                "Filename folder" : "", 
                "General comments" : "No comment",
                "Clean after testing" : True, 
                "Maintain KOH after testing" : False, # This is to do retained electrolyte experiments 
                "Optimize using ML" : False, 
                "HCl dipping time [s]" : 900,
                "HCl cleaning concentration [mol / L]" : 3, 
                "KOH filling volume [ml]" : 10.9,
                "Deposition filling volume [ml]" : 15,
                "Experiment name" : "", 
                "KOH batch" : "Batch fabricated 04.11 Pre electrolyzed 100 h 30 wt %", 
                "Repeat experiment n cycles" : 1, # How many times you want to repeat the experiment 
                "Cleaning waiting time testing [s]" : 60, 
                "Cleaning waiting time deposition [s]" : 60, 
                "Cleaning cycles testing chamber" : 2, 
                "Cleaning cycles deposition chamber" : 2, 
                "Deposition batch" : "Electrolyte 1 NiSO4 0.4 M with 0.4 M NaCitrate + 0.3 M NaCl Fabricated 21.11.24", 
                "HCl concentration [mol / L]" : 3})

################################
experiment_ML_set_4_nr_11 = Experiment(experimental_params={"Temperature_deposition [C]" : 46, 
              "Temperature_testing [C]" : 80,
              "Testing liquid KOH [w %]": 30, 
                "Deposition composition" : {"NiSO4": 0.308},
                "Roll while depositing" : True, 
                "Testing protocol" : {"testing protocol name" : testing_protocol_name, "protocol" : testing_experiment},
                "Deposition time [s]" : 155, 
                "Deposition current density [mA/cm2]" : 95, 
                "Wire type" : "Ni 99.8 %",
                "Filename testing data" : "",
                "Filename deposition data" : "", 
                "Filename temperature data" : "",
                "Filename folder" : "", 
                "General comments" : "No comment",
                "Clean after testing" : True, 
                "Maintain KOH after testing" : False, # This is to do retained electrolyte experiments 
                "Optimize using ML" : False, 
                "HCl dipping time [s]" : 900,
                "HCl cleaning concentration [mol / L]" : 3, 
                "KOH filling volume [ml]" : 10.9,
                "Deposition filling volume [ml]" : 15,
                "Experiment name" : "", 
                "KOH batch" : "Batch fabricated 04.11 Pre electrolyzed 100 h 30 wt %", 
                "Repeat experiment n cycles" : 1, # How many times you want to repeat the experiment 
                "Cleaning waiting time testing [s]" : 60, 
                "Cleaning waiting time deposition [s]" : 60, 
                "Cleaning cycles testing chamber" : 2, 
                "Cleaning cycles deposition chamber" : 2, 
                "Deposition batch" : "Electrolyte 1 NiSO4 0.4 M with 0.4 M NaCitrate + 0.3 M NaCl Fabricated 21.11.24", 
                "HCl concentration [mol / L]" : 3})



experiment_ML_set_4_nr_12 = Experiment(experimental_params={"Temperature_deposition [C]" : 74, 
              "Temperature_testing [C]" : 80,
              "Testing liquid KOH [w %]": 30, 
                "Deposition composition" : {"NiSO4": 0.028},
                "Roll while depositing" : True, 
                "Testing protocol" : {"testing protocol name" : testing_protocol_name, "protocol" : testing_experiment},
                "Deposition time [s]" : 71, 
                "Deposition current density [mA/cm2]" : 93, 
                "Wire type" : "Ni 99.8 %",
                "Filename testing data" : "",
                "Filename deposition data" : "", 
                "Filename temperature data" : "",
                "Filename folder" : "", 
                "General comments" : "No comment",
                "Clean after testing" : True, 
                "Maintain KOH after testing" : False, # This is to do retained electrolyte experiments 
                "Optimize using ML" : False, 
                "HCl dipping time [s]" : 900,
                "HCl cleaning concentration [mol / L]" : 3, 
                "KOH filling volume [ml]" : 10.9,
                "Deposition filling volume [ml]" : 15,
                "Experiment name" : "", 
                "KOH batch" : "Batch fabricated 04.11 Pre electrolyzed 100 h 30 wt %", 
                "Repeat experiment n cycles" : 1, # How many times you want to repeat the experiment 
                "Cleaning waiting time testing [s]" : 60, 
                "Cleaning waiting time deposition [s]" : 60, 
                "Cleaning cycles testing chamber" : 2, 
                "Cleaning cycles deposition chamber" : 2, 
                "Deposition batch" : "Electrolyte 1 NiSO4 0.4 M with 0.4 M NaCitrate + 0.3 M NaCl Fabricated 21.11.24", 
                "HCl concentration [mol / L]" : 3})

#Robot_test.run_complete_experiment(experiment=experiment_uncertainty_3, 
#                                empty_after_deposition=True, 
#                                keep_wire_stationary=False, 
#                                evacuate_chambers_before_starting=True)


time.sleep(5)
Robot_test.run_complete_experiment(experiment=experiment_ML_set_4_nr_1, 
                                empty_after_deposition=True, 
                                keep_wire_stationary=False, 
                                evacuate_chambers_before_starting=True)
time.sleep(5)
Robot_test.run_complete_experiment(experiment=experiment_ML_set_4_nr_2, 
                                empty_after_deposition=True, 
                                keep_wire_stationary=False, 
                                evacuate_chambers_before_starting=True)
time.sleep(5)
Robot_test.run_complete_experiment(experiment=experiment_ML_set_4_nr_3, 
                                empty_after_deposition=True, 
                                keep_wire_stationary=False, 
                                evacuate_chambers_before_starting=True)


time.sleep(5)
Robot_test.run_complete_experiment(experiment=experiment_ML_set_4_nr_4, 
                                empty_after_deposition=True, 
                                keep_wire_stationary=False, 
                                evacuate_chambers_before_starting=True)



time.sleep(5)
Robot_test.run_complete_experiment(experiment=experiment_ML_set_4_nr_5, 
                                empty_after_deposition=True, 
                                keep_wire_stationary=False, 
                                evacuate_chambers_before_starting=True)


time.sleep(5)
Robot_test.run_complete_experiment(experiment=experiment_ML_set_4_nr_6, 
                                empty_after_deposition=True, 
                                keep_wire_stationary=False, 
                                evacuate_chambers_before_starting=True)

time.sleep(5)
Robot_test.run_complete_experiment(experiment=experiment_ML_set_4_nr_7, 
                                empty_after_deposition=True, 
                                keep_wire_stationary=False, 
                                evacuate_chambers_before_starting=True)


time.sleep(5)
Robot_test.run_complete_experiment(experiment=experiment_ML_set_4_nr_8, 
                                empty_after_deposition=True, 
                                keep_wire_stationary=False, 
                                evacuate_chambers_before_starting=True)


time.sleep(5)
Robot_test.run_complete_experiment(experiment=experiment_ML_set_4_nr_9, 
                                empty_after_deposition=True, 
                                keep_wire_stationary=False, 
                                evacuate_chambers_before_starting=True)


time.sleep(5)
Robot_test.run_complete_experiment(experiment=experiment_ML_set_4_nr_10, 
                                empty_after_deposition=True, 
                                keep_wire_stationary=False, 
                                evacuate_chambers_before_starting=True)


time.sleep(5)
Robot_test.run_complete_experiment(experiment=experiment_ML_set_4_nr_11, 
                                empty_after_deposition=True, 
                                keep_wire_stationary=False, 
                                evacuate_chambers_before_starting=True)


time.sleep(5)
Robot_test.run_complete_experiment(experiment=experiment_ML_set_4_nr_12, 
                                empty_after_deposition=True, 
                                keep_wire_stationary=False, 
                                evacuate_chambers_before_starting=True)




Robot_test.pump_KOH_into_testing_chamber(amount_ml=6)
time.sleep(5)
Robot_test.set_temperature_both_chambers(filename="bs.json",
                                         temperature_dep_electrolyte=30,
                                           temperature_KOH=30)
