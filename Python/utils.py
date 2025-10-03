from datetime import datetime
import os 
import os
import json
from pathlib import Path
import numpy as np 
from scipy.spatial.distance import cdist
import torch
# eg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1 /f Handle longer paths in windows 
def handle_long_path(path):
    """
    Handle long Windows paths by adding the extended path prefix if needed.
    
    Args:
        path (str): The original path
        
    Returns:
        str: Path that can handle longer lengths
    """
    # Check path length
    path_length = len(path)
    print(f"Path length: {path_length} characters")
    
    if path_length >= 260:
        print("Path exceeds Windows 260 character limit!")
        
        if not path.startswith("\\\\?\\"):
            # Convert to absolute path if it isn't already
            abs_path = os.path.abspath(path)
            # Add extended-length path prefix
            extended_path = "\\\\?\\" + abs_path
            print("Converting to extended path format")
            print(f"New path: {extended_path}")
            return extended_path
    
    return path

def load_parameter_sets(input_parameter_set_path = "", 
                        goal_parameter_set_path = ""):
    '''
        Returns the loaded parameter sets as arrays
        Note that the parameters here are not normalized
    '''
    x_data = []
    y_data = []
    if os.path.exists(input_parameter_set_path):

        with open(input_parameter_set_path, 'r') as infile:
            input_params = json.load(infile)

        with open(goal_parameter_set_path, 'r') as infile:
            y_set = json.load(infile)
        
        
        for experiment_i in input_params.keys():
            dep_current_density_mA_cm2 = input_params[experiment_i]["Deposition current density [mA/cm2]"]
            dep_time_s = input_params[experiment_i]["Deposition time [s]"]
            temperature_dep_C_realized = input_params[experiment_i]["Temperature_deposition [C] realized"]
            NiSO4_conc = input_params[experiment_i]["Deposition composition mol / L"]["NiSO4"]
            x_data.append([dep_current_density_mA_cm2, dep_time_s, NiSO4_conc, temperature_dep_C_realized])
            print(experiment_i, "This is where it fails")

        for experiment_i in y_set.keys():
            y_goal_stability = y_set[experiment_i]["Stability slope [mV/scan]"] 
            y_goal_activity = y_set[experiment_i]["Overpotential LSV @ 100 mA_cm2 [mV]"] 
            y_data.append([y_goal_stability, y_goal_activity])

    return x_data, y_data

def save_parameter_sets(input_parameter_set_path, 
                        goal_parameter_set_path, 
                        input_params_x = [],
                        goal_params_y = [], 
                        experiment_names = [], 
                        IR_correction = 0):
    
    if os.path.exists(input_parameter_set_path):
        with open(input_parameter_set_path, 'r') as infile:
            input_params = json.load(infile)
    else:
        input_params = {}
    for input_param_x, experiment_name in zip(input_params_x, experiment_names):
        input_parameters_exp_i = {experiment_name: input_param_x}
        
        input_params.update(input_parameters_exp_i)
    with open(input_parameter_set_path, 'w') as outfile:
        json.dump(input_params, outfile, indent=4)
    

    if os.path.exists(goal_parameter_set_path):
        with open(goal_parameter_set_path, 'r') as infile:
            goal_params = json.load(infile)
    else:
        goal_params = {}
        
    for goal_param_y, experiment_name in zip(goal_params_y, experiment_names):
        goal_parameters_exp_i = {experiment_name : goal_param_y}

        goal_params.update(goal_parameters_exp_i)
    with open(goal_parameter_set_path, 'w') as outfile:
        json.dump(goal_params, outfile, indent=4)
    

def save_suggested_experiments_to_ML_log(
    suggested_experiments: torch.tensor, 
    ML_log_path,  method = "", 
    iteration=1, experiment=1,
    acquisition_value: float = None,
    predicted_y: torch.tensor = None,
    prediction_uncertainty: torch.tensor = None,
    model_params = None
    ):
    iteration_num = len([file for file in os.listdir(ML_log_path) if "ML_suggested_experiments_" in file]) + 1

    # only a single experiment is suggested
    if len(suggested_experiments.shape) == 1:
        suggested_experiments = suggested_experiments.reshape(1, -1)
    
    ML_path_dict = f"ML_suggested_experiments_{iteration_num}.json"
    current_time = datetime.now()
    timestamp = current_time.strftime("%d.%m.%Y_%H-%M")
    timestamp_dict = {"Experiment started timestamp" : timestamp}
    abs_path_ML_dict = os.path.join(ML_log_path, ML_path_dict)
    if model_params == None:
        params = "None"
    else:
        params = model_params
    complete_experiment_dict = {}
    for i, experiment_i in enumerate(suggested_experiments):
        experiment_i = [float(param) for param in experiment_i]
        ml_values = {"Acquisition value": acquisition_value, "Predicted y": predicted_y[i].item(), "Prediction uncertainty": prediction_uncertainty[i].item()}
        
        experiment_subdict = {f"Experiment = {experiment} Iteration : {iteration} Suggested Experiment {i + 1} params = [dep current density mA/cm2, deposition time, NiSO4 concentration, deposition temperature] optimizer method = {method}, params : {params}": experiment_i, 
                              "ML-outputs" : ml_values}
        
        complete_experiment_dict.update(experiment_subdict)

        # TODO: want this here?
        
        # complete_experiment_dict.update(ml_values)
        
    # if the file already exists, we load it and append the new data
    if os.path.exists(abs_path_ML_dict):
        with open(abs_path_ML_dict, 'r') as infile:
            ML_dict = json.load(infile)

        number_of_iterations = len(ML_path_dict.keys())
        ML_path_iteration_i = {f"Iteration {number_of_iterations + 1} {timestamp}": complete_experiment_dict}
        ML_dict.update(ML_path_iteration_i)
        ML_dict.update(timestamp_dict)
        with open(abs_path_ML_dict, 'w') as outfile:
            json.dump(ML_dict, outfile, indent=4)
   
    else:
        ML_dict = {}
        ML_path_iteration_i = {f"Iteration {1} {timestamp}": complete_experiment_dict}
        print(ML_path_iteration_i)
        
        ML_dict.update(ML_path_iteration_i)
        ML_dict.update(timestamp_dict)
        with open(abs_path_ML_dict, 'w') as outfile:
            json.dump(ML_dict, outfile, indent=4)



def calculate_volumes(stock_solutions, desired_concentrations, chamber_volume):
    '''
        Calculate the volumes needed from each syringe pump to achieve the desired 
        molar concentrations.
    '''
    total_volume = 0
    volumes = {}

    # Initialize all volumes to 0
    if chamber_volume == 0:
        # We do no deposition
        for solute in stock_solutions:
            volumes[solute] = {'amount ml': 0, 'Pump': stock_solutions[solute]["Pump"]}
        return volumes
    for solute in stock_solutions:
        volumes[solute] = {'amount ml': 0, 'Pump': stock_solutions[solute]["Pump"]}
    
    # Calculate required volumes for the desired concentrations
    for solute, desired_concentration in desired_concentrations.items():
        stock_concentration = stock_solutions[solute]["Concentration [mol/L]"]
        volume = (desired_concentration * chamber_volume) / stock_concentration
        volumes[solute]['amount ml'] = volume
        total_volume += volume
    
    # Calculate remaining volume for H2O
    volumes["H2O"]['amount ml'] = chamber_volume - total_volume
    print("Chamber volume", chamber_volume)
    print(desired_concentrations, "Desired conc")
    print(stock_solutions, "Stock")
    if volumes["H2O"]['amount ml'] < 0:
        print('That high of a concentration is not possible')
        return None

    return volumes




def check_constraints(C_des, C_stock):
    """Check if the conditions satisfy the constraints."""
    return sum(C_des[i] / C_stock[i] for i in range(len(C_des))) <= 1

def sample_point():
    # Discrete parameter ranges
    pH_liquid_molarity = [0.005 * i for i in range(21)]  # Discrete molarity points
    temperature = [(30 + i) for i in range(41)]         # Discrete temperatures
    I_mA_cm2 = [i for i in range(1, 201)]               # Discrete current densities
    dep_time = [60 + i for i in range(541)]             # Discrete deposition times
    molarity = 0.4
    molarity_NiSO4 = [0.002 + molarity / 200 * i for i in range(200)]  # Discrete Nickel molarities
    molarity_Na2Mo = [0.002 + molarity / 200 * i for i in range(200)]  # Discrete Molybdenum molarities

    """Randomly sample a single point from the discrete space."""
    molarity_Ni = np.random.choice(molarity_NiSO4)
    molarity_Mo = np.random.choice(molarity_Na2Mo)
    pH = np.random.choice(pH_liquid_molarity)
    temp = np.random.choice(temperature)
    current_density = np.random.choice(I_mA_cm2)
    time = np.random.choice(dep_time)
    return np.array([molarity_Ni, molarity_Mo, pH, temp, current_density, time])

def maximin_sampling_discrete(n_conditions=15, batch_size=100, molarity = 0.4):
    """Perform maximin sampling on a discrete space with constraints."""
    selected_points = []

    while len(selected_points) < n_conditions:
        # Generate a batch of random points
        batch = np.array([sample_point() for _ in range(batch_size)])
        
        # Filter the batch based on constraints
        feasible_points = []
        for point in batch:
            molarity_Ni, molarity_Mo, pH, _, _, _ = point
            C_des = [molarity_Ni, molarity_Mo, pH]
            C_stock = [molarity, molarity, 1]
            if check_constraints(C_des, C_stock):
                feasible_points.append(point)
        
        feasible_points = np.array(feasible_points)
        if len(feasible_points) == 0:
            continue  # Skip if no feasible points in this batch
        
        # Perform maximin selection within the batch
        for candidate in feasible_points:
            if len(selected_points) == 0:
                selected_points.append(candidate)
                continue
            
            distances = cdist(feasible_points, np.array(selected_points), metric='euclidean')
            min_distances = np.min(distances, axis=1)
            best_idx = np.argmax(min_distances)
            selected_points.append(feasible_points[best_idx])
            
            if len(selected_points) >= n_conditions:
                break

    return np.array(selected_points)


def make_folder_for_experiment(folder_dir = "",
                               experiment_name = ""):

    if experiment_name == "":
        time = datetime.now()

# Format the date and time to only include minutes
        experiment_name = 'Experiment_' + str(time.strftime("%Y-%m-%d %H:%M"))

    try:
        os.mkdir(os.path.join(folder_dir, experiment_name))
        return os.path.join(folder_dir, experiment_name)
    except Exception as e:
        print(e)

def check_if_exists_make_folder(temperature, Ni_sample):
    '''
        Function that checks if a folder exists and if it doesnt, it makes the folder name
    '''
    filename_folder_1 = f"C://Users//Catbot-adm//Desktop//CatBot//Python//Electrochemical_data//{temperature}"
    if os.path.exists(filename_folder_1):
        pass
    else:
        os.mkdir(filename_folder_1)
    filename_folder = f"C://Users//Catbot-adm//Desktop//CatBot//Python//Electrochemical_data//{temperature}//{Ni_sample}"
    if os.path.exists(filename_folder):
        return filename_folder
    os.mkdir(filename_folder)
    return filename_folder


def make_folder_deposition_experiment(current_density, 
                                      deposition_time,
                                      folder_dir = "C://Users//Catbot-adm//Desktop//CatBot//Python//Electrochemical_data//Coated_wires",
                                      temperature_dep = 30, 
                                      temperature_testing = 70, protocol = 2):
    
    new_folder_name = f"Dep_current_density_{current_density}_dep_time_{deposition_time}_temp_dep_{temperature_dep}_temp_test_{temperature_testing}_protocol_{protocol}"
    new_path = os.path.join(folder_dir, new_folder_name)
    if os.path.exists(new_path): # If the path exists
        num_experiments = len(os.listdir(new_path)) # Checking how many times we have reproduced this experiment
        try:
            new_experiment_folder_name = os.path.join(new_path, str(num_experiments + 1))
            os.mkdir(new_experiment_folder_name)
            
            return new_experiment_folder_name, new_folder_name
        except:
            print("Failed to make folder")
    else:
        num_experiments = 1
        os.mkdir(new_path)
        os.mkdir(os.path.join(new_path, num_experiments))

        return os.path.join(new_path, num_experiments), new_folder_name

    
def save_ML_log():
    '''
        Should save the points that the ML model suggests, such that we can backtrack it, and also the timestamps
    '''

    return 