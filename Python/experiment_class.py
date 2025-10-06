from experimental_protocols import * 
import os
from datetime import datetime
from utils import *


experiment = {"Temperature_deposition [C]" : 30, 
              "Temperature_testing [C]" : 80,
              "Testing liquid KOH [w %]": 30, 
                "Deposition composition" : {"NiSO4": 0.3, "MnSO4": 0},
                "Roll while depositing" : True, 
                "Testing protocol" : {"testing protocol name" : "second_protocol", "protocol" : None},
                "Deposition time [s]" : 300, 
                "Deposition current density [mA/cm2]" : 30, 
                "Wire type" : "Ni 99.8 %",
                "Filename testing data" : "",
                "Filename deposition data" : "", 
                "Filename temperature data" : "",
                "Filename folder" : "", 
                "General comments" : "No comment",
                "Clean after testing" : True, 
                "Maintain KOH after testing" : True, # This is to do retained electrolyte experiments 
                "Optimize using ML" : False, 
                "HCl dipping time [s]" : 15,
                "HCl cleaning concentration [mol / L]" : 3, 
                "KOH filling volume [ml]" : 10.9,
                "Deposition filling volume [ml]" : 15,
                "Experiment name" : "", 
                "KOH batch" : "Batch fabricated 04.11 Pre electrolyzed 100 h 30 wt %", 
                "Repeat experiment n cycles" : 4, # How many times you want to repeat the experiment 
                "Cleaning waiting time testing [s]" : 60, 
                "Cleaning waiting time deposition [s]" : 60, 
                "Cleaning cycles testing chamber" : 2, 
                "Cleaning cycles deposition chamber" : 2, 
                "Deposition batch" : "Electrolyte 1 NiSO4 0.4 M with 0.3 M NaCitrate + 0.4 M NaCl", 
                "HCl concentration [mol / L]" : 3
              }
# How to set up datetime 

def try_to_make_folder(path):
    if os.path.exists(path) == False:
        try:
            os.makedirs(path)
            print("Folder made", path)
        except Exception as e:
            print(e, path)
    else:
        print("Folder already exists")


class Experiment:
    """
        Represents a single experimental run, capturing all parameters, metadata, and comments 
        to ensure reproducibility and facilitate error tracking.

        Attributes:
            experimental_params (dict): A dictionary containing all relevant experimental parameters, 
                such as testing temperature, solution concentrations, wire types, and any associated notes or comments.

        This class is used to define and organize an experiment, and can be integrated with CatBot 
        to execute the experiment automatically.
        
    """
    def __init__(self, 
                 experimental_params = None):
        if experimental_params is None:
            experimental_params = {}
        self.experimental_params = experimental_params
        if experimental_params != {}:
            self.dep_current_density_mA_cm2 = experimental_params["Deposition current density [mA/cm2]"]
            self.deposition_time_s = experimental_params["Deposition time [s]"]
            self.dep_temperature = experimental_params["Temperature_deposition [C]"]
            self.testing_temperature = experimental_params["Temperature_testing [C]"]
            self.KOH_concentration_wp = experimental_params["Testing liquid KOH [w %]"]
            self.deposiotion_composition_mol_l = experimental_params["Deposition composition"]
            self.roll_while_depositing = experimental_params["Roll while depositing"]
            self.testing_protocol = experimental_params["Testing protocol"]
            self.wire_type = experimental_params["Wire type"]
            self.filename_testing_data = experimental_params["Filename testing data"]
            self.filename_depositon_data = experimental_params["Filename deposition data"]
            self.filename_temperature_data = experimental_params["Filename temperature data"]
            self.filename_folder = experimental_params["Filename folder"]
            self.comments = experimental_params["General comments"]
            self.maintain_KOH_after_testing = experimental_params["Maintain KOH after testing"]
            self.HCl_dipping_time_s = experimental_params["HCl dipping time [s]"]
            self.KOH_filling_volume_ml = experimental_params["KOH filling volume [ml]"]
            self.deposition_filling_volume_ml = experimental_params["Deposition filling volume [ml]"]
            self.experiment_name = experimental_params["Experiment name"]
            self.KOH_batch = experimental_params["KOH batch"]
            self.HCl_cleaning_conc = experimental_params["HCl concentration [mol / L]"]
            self.repeat_experiment_n_times = experimental_params["Repeat experiment n cycles"]
            self.cleaning_waiting_time_testing_s = experimental_params["Cleaning waiting time testing [s]"]
            self.cleaning_waiting_time_deposition_s = experimental_params["Cleaning waiting time deposition [s]"]
            self.testing_chamber_cleaning_cycles = experimental_params["Cleaning cycles testing chamber"]
            self.deposition_chamber_cleaning_cycles = experimental_params["Cleaning cycles deposition chamber"]
            self.deposition_batch = experimental_params["Deposition batch"]
            self.experiment_count = 1

    def get_experimental_params(self):
        return self.experimental_params
    
    def get_testing_experiment(self):
        if type(self.experimental_params["Testing protocol"]) == str:
            if self.experimental_params["Testing protocol"] == "second protocol":
                
                return second_protocol()
            elif self.experimental_params["Testing protocol"] == "third protocol":
                return third_protocol
        else:
            return self.experimental_params["Testing protocol"]
    
    def get_deposition_experiment(self):

        if self.experimental_params["Deposition current density mA"] > 1000:
            print("Current density too high, max current is 1 A")
            return ValueError

        deposition_exp = deposition_experiment(deposition_time_ = self.deposition_time_s, 
                                               deposition_current_density_mA_cm2=self.dep_current_density_mA_cm2)
        return deposition_exp

    def get_filenames(self):
        temperature_testing = self.testing_temperature
        if self.experimental_params["Filename testing data"] == "":
            filename_testing_data = ""

    def get_experiment_name(self):
        if self.experimental_params["Experiment name"]:
            return self.experimental_params["Experiment name"]

    def set_experiment_name_based_on_experiment(self):
        protocol_name = self.testing_protocol["testing protocol name"]
        if self.maintain_KOH_after_testing:
            retained_electrolyte = "True"
        else:
            retained_electrolyte = "False"
        
        if self.roll_while_depositing:
            roll_while_depositing = "True"
        else:
            roll_while_depositing = "False"
        current_time = datetime.now()
        timestamp = current_time.strftime("%d.%m.%Y at %H:%M")
        self.experiment_name = "T_test_" + str(self.testing_temperature) + "C_" + "T_dep_" + str(self.dep_temperature) + "C_" + "dep_density_mA_cm2_" + str(self.dep_current_density_mA_cm2) + "_dep_time_s_" + str(self.deposition_time_s) + "_roll_while_depositing_" + roll_while_depositing + "_HCl_dipping_time_s_" + str(self.HCl_dipping_time_s) + "_HCl_molarity_" + str(self.HCl_cleaning_conc) + "_Retained_electrolyte_" + (retained_electrolyte) + "_Protocol_" + protocol_name + "_exp_cycle_" + str(self.experiment_count) + "_KOH_batch_" + self.KOH_batch + "_start_time_" + timestamp +".csv"                                                                                                                           
    
    def set_testing_filename_from_parameters(self):
        protocol_name = self.testing_protocol["testing protocol name"]
        if self.maintain_KOH_after_testing:
            retained_electrolyte = "True"
        else:
            retained_electrolyte = "False"
        
        if self.roll_while_depositing:
            roll_while_depositing = "True"
        else:
            roll_while_depositing = "False"
        current_time = datetime.now()
        timestamp = current_time.strftime("%d.%m.%Y_%H-%M")
        self.filename_testing_data = "Testing_T_test_" + str(self.testing_temperature) + "C_" + "T_dep_" + str(self.dep_temperature) + "C_" + "dep_I_mA_cm2_" + str(self.dep_current_density_mA_cm2) + "_dep_t_s_" + str(self.deposition_time_s) + "_roll_while_dep_" + roll_while_depositing + "_HCl_dip_t_s_" + str(self.HCl_dipping_time_s) + "_HCl_conc_" + str(self.HCl_cleaning_conc) + "_Retain_elyte_" + (retained_electrolyte) + "_protocol_" + protocol_name + "_exp_cyc_" + str(self.experiment_count) + "_KOH_conc_" + str(self.KOH_concentration_wp) + "_start_t_" + timestamp +".csv"              

    def set_deposition_filename_from_parameters(self):
        protocol_name = self.testing_protocol["testing protocol name"]
        if self.maintain_KOH_after_testing:
            retained_electrolyte = "True"
        else:
            retained_electrolyte = "False"
        
        if self.roll_while_depositing:
            roll_while_depositing = "True"
        else:
            roll_while_depositing = "False"
        current_time = datetime.now()
        timestamp = current_time.strftime("%d.%m.%Y_%H-%M")

        self.filename_depositon_data = "Dep_T_test_" + str(self.testing_temperature) + "C_" + "T_dep_" + str(self.dep_temperature) + "C_" + "dep_I_mA_cm2_" + str(self.dep_current_density_mA_cm2) + "_dep_t_s_" + str(self.deposition_time_s) + "_roll_while_dep_" + roll_while_depositing + "_HCl_dip_t_s_" + str(self.HCl_dipping_time_s) + "_HCl_conc_" + str(self.HCl_cleaning_conc) + "_Retain_elyte_" + (retained_electrolyte) + "_protocol_" + protocol_name + "_exp_cyc_" + str(self.experiment_count) + "_KOH_conc_" + str(self.KOH_concentration_wp) + "_start_t_" + timestamp +".csv"                                                                                                                           

    def update_experiment_count(self):
        '''
            Updates the experiment count cycles so that if you repeat an experiment, you simply start it over again 
        '''
        self.experiment_count += 1

    def make_folder_based_on_parameters(self):
        
        # We are dealing with clean nickel wires 
        main_folder = r"C:\Users\Catbot-adm\Desktop\CatBot\Python\Electrochemical_data\Electrochemical_data_second_phase"
        current_time = datetime.now()
        timestamp = current_time.strftime("%d_%m_%Y_%H_%M")
        if self.deposition_time_s == 0 or self.dep_current_density_mA_cm2 == 0:
            main_folder = os.path.join(main_folder, "Clean_nickel_wires")
            try_to_make_folder(main_folder)
        else:
            main_folder = os.path.join(main_folder, "Coated_wires")
            try_to_make_folder(main_folder)
        
        if self.HCl_dipping_time_s != 900:
            main_folder = os.path.join(main_folder, f"HCl_cleaning_time_s_{self.HCl_dipping_time_s}_conc_{self.HCl_cleaning_conc}M")
            try_to_make_folder(main_folder)
        if self.maintain_KOH_after_testing:
            main_folder = os.path.join(main_folder, "Retained_electrolyte_data")
            try_to_make_folder(main_folder)
        
        elif self.KOH_filling_volume_ml != 10.9:
            main_folder = os.path.join(main_folder, "Volume_tests")
            try_to_make_folder(main_folder)
        else:
            main_folder = os.path.join(main_folder, "Run_testing_protocol_only")
            try_to_make_folder(main_folder)

        protocol_name = self.testing_protocol["testing protocol name"]
        
        main_folder = os.path.join(main_folder, protocol_name)
        try_to_make_folder(main_folder)
        
        main_folder = os.path.join(main_folder, f"Testing_temp_{self.testing_temperature}_KOH_conc_{self.KOH_concentration_wp}w")
        try_to_make_folder(main_folder)

        # If we are using clean nickel wires 
        if "Clean_nickel_wires" in main_folder:
            if os.path.exists(main_folder) == False: 
                try_to_make_folder(main_folder)
                main_folder = os.path.join(main_folder, f"Series_1_start_time_{timestamp}") # Now we are in the series 
                print("We try to make this god darn folder but fail", main_folder)
                try_to_make_folder(main_folder)
            else:
                num_exps_in_folder = len(os.listdir(main_folder))
                main_folder = os.path.join(main_folder, f"Series_{num_exps_in_folder + 1}_start_time_{timestamp}")
                print("We try to make this god darn folder but fail and follder exists", main_folder)
                try_to_make_folder(main_folder)
            
            self.filename_folder = main_folder
        else:
            name = ""
            for salt in self.deposiotion_composition_mol_l:
                name += salt + "_" + str(self.deposiotion_composition_mol_l[salt]) + "_"
            main_folder = os.path.join(main_folder, f"I_mA_cm2_{self.dep_current_density_mA_cm2}_dep_time_{self.deposition_time_s}_{name}")
            if os.path.exists(main_folder) == False:
                try_to_make_folder(main_folder)
            
                main_folder = os.path.join(main_folder, f"Series_1_start_time_{timestamp}")
                try_to_make_folder(main_folder)
                self.filename_folder = main_folder
            else:
                num_experiments = len(os.listdir(main_folder))
                main_folder = os.path.join(main_folder, f"Series_{num_experiments + 1}_start_time{timestamp}")
                try_to_make_folder(main_folder)
                self.filename_folder = main_folder

    def make_folder_for_subexperiment(self, 
                                      return_folder = False):
        current_time = datetime.now()
        timestamp = current_time.strftime("%d_%m_%Y_%H_%M_")

        folder = os.path.join(self.filename_folder, f"{self.experiment_count}")
        self.subfolder_path = folder
        try_to_make_folder(folder)
        if return_folder:
            return folder

    def get_parameter_dict_name(self):
        current_time = datetime.now()
        timestamp = current_time.strftime("%d_%m_%Y_%H_%M")

        parameter_dict_name = f"Exp_{self.experiment_count}_{timestamp}_parameter_dict.json"
        return parameter_dict_name
    def get_all_parameters(self):
        return 
    
