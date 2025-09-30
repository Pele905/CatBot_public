import numpy as np 
import matplotlib.pyplot as plt 
import time 
import threading 
import json 
from matplotlib.animation import FuncAnimation
import datetime
import serial


def update_datalogger_test(data_logger_file = "datalogger.json", cmd_dict = {}, save_file = False, iteration = 0):
 
    liquid_data = open(data_logger_file)

    liquid_data_dict = json.load(liquid_data)
        
    print(liquid_data_dict)
    solutions = cmd_dict.keys()
    for pump, solution in zip(liquid_data_dict, solutions):
        print(solution)
        liquid_data_dict[pump].append(liquid_data_dict[pump][-1] - cmd_dict[solution]["amount ml"])
    
    if save_file:
        with open(data_logger_file, 'w') as file:
            json.dump(liquid_data_dict, file)  # Save DataFrame to CSV file
     

def convert_ml_to_steps(amount_ml, pump):

    '''
        Calibration curves from the pumps. That is how many steps to achieve one ml of liquid
    '''

    pump_data_calibration = {'Pump 1' : 302, "Pump 2" : 303, 
                         "Pump 3" : 301, "Pump 4" : 302, 
                         "Pump 5": 302, "Pump 6": 303,
                         "Pump 7": 302 
    }

    return int(pump_data_calibration[pump] * amount_ml)


def set_liquids_syringe(command_dict, 
                         serialcomm = None, 
                         ):
    '''
        Pump liquid from the syringe pump to the testing cell
        input params: command_dict, serialcomm, volume_df
    '''

    if serialcomm == None:
        serialcomm = serial.Serial('/dev/cu.usbmodem1101', 9600)
        time.sleep(20)

    for pumping_liquid in command_dict.keys():
        amount = command_dict[pumping_liquid]["amount ml"] 
        pump = command_dict[pumping_liquid]["Pump"] 
        pump_str = "Pump " + str(pump)
        amount_step = str(convert_ml_to_steps(float(amount), pump_str))
        cmd_i = f"SyringePumps {pump} {amount_step} backward refill "

        if amount == 0:
              # Since no reload is necessary, we do not do anything
              
              continue
        else:
            serialcomm.write(cmd_i.encode())
            confirmation = ""
            while confirmation != "SyringePump movement comp":
                confirmation = serialcomm.readline().decode().strip()
                
                time.sleep(2)
    return True

def pump_HCl_into_cleaning_station(serialcomm = None):

    if serialcomm == None:
        return False
    CMD = "FILL_HCL"
    serialcomm.write(CMD.encode())
    time.sleep(16)
    return 


def pump_HCl_from_cleaning_station_to_holder(serialcomm = None):

    if serialcomm == None:
        return False
    CMD = "EVAC_HCL"
    serialcomm.write(CMD.encode())
    time.sleep(16)
    return 


def recharge_liquids_syringe(command_dict, 
                         serialcomm = None, 
                         data_logger_file = None, 
                         save_history = True,
                         ):
    '''
        Pump liquid from the syringe pump to the testing cell
        input params: command_dict, serialcomm, volume_df
    '''
    try:
        liquid_data = open(data_logger_file)
        liquid_data_hist = json.load(liquid_data)
    except:
        volume_df_initial = {"Pump 1": [10],
                    "Pump 2": [10], 
                    "Pump 3": [10], 
                    "Pump 4": [10], 
                    "Pump 5": [10], 
                    "Pump 6": [10], 
                    "Pump 7": [10]}
#Remove here
        data_logger_file = "datalogger.json"
        with open(data_logger_file, "w") as outfile: 
            json.dump(volume_df_initial, outfile)
        time.sleep(1)
        liquid_data = open(data_logger_file)
        liquid_data_hist = json.load(liquid_data)


    if serialcomm == None:
        serialcomm = serial.Serial('/dev/cu.usbmodem1101', 9600)
        time.sleep(20)

    for pumping_liquid in command_dict.keys():
        amount = command_dict[pumping_liquid]["amount ml"] # Find the amount we need to recharge
        pump = command_dict[pumping_liquid]["Pump"] # Find the corresponding pump
        pump_str = "Pump " + str(pump)
        amount_step = str(convert_ml_to_steps(float(amount), pump_str))
        cmd_i = f"SyringePumps {pump} {amount_step} backward refill "

        if amount == 0:
              # Since no reload is necessary, we do not do anything
              liquid_data_hist[pump_str].append(liquid_data_hist[pump_str][-1]) 
              continue
        else:
            serialcomm.write(cmd_i.encode())
            confirmation = ""
            while confirmation != "SyringePump movement comp":
                confirmation = serialcomm.readline().decode().strip()
                liquid_data_hist[pump_str].append(liquid_data_hist[pump_str][-1] + command_dict[pumping_liquid]["amount ml"])
                time.sleep(2)
            #liquid_data_hist[pump_str].append(liquid_data_hist[pump_str][-1] + command_dict[pumping_liquid]["amount ml"])
    
    if save_history:
        with open(data_logger_file, 'w') as file:
            json.dump(liquid_data_hist, file)  # Save DataFrame to CSV file
    return True




def pump_liquids_syringe(command_dict, 
                         serialcomm = None, 
                         data_logger_file = None, 
                         save_history = True,
                         flush_volume = 4, 
                         chamber = "testing"):
    '''
        Pump liquid from the syringe pump to the testing cell
        input params: command_dict, serialcomm, volume_df
    '''
    try:
        liquid_data = open(data_logger_file)
        liquid_data_hist = json.load(liquid_data)
    except Exception as e:
        print(e)
        volume_df_initial = {"Pump 1": [19],
                    "Pump 2": [10], 
                    "Pump 3": [10], 
                    "Pump 4": [10], 
                    "Pump 5": [31], 
                    "Pump 6": [32], 
                    "Pump 7": [10]}
        #Remove here
        data_logger_file = "datalogger.json"
        with open(data_logger_file, "w") as outfile: 
            json.dump(volume_df_initial, outfile)
        time.sleep(1)
        liquid_data = open(data_logger_file)
        liquid_data_hist = json.load(liquid_data)

    if serialcomm == None:
        serialcomm = serial.Serial('/dev/cu.usbmodem1101', 9600)
        time.sleep(20)

    evacuate_set = False
    print(command_dict)
    for pumping_liquid in command_dict.keys():
        amount = command_dict[pumping_liquid]["amount ml"]

        pump = command_dict[pumping_liquid]["Pump"]
        pump_str = "Pump " + str(pump)

        amount_step = str(convert_ml_to_steps(float(amount), pump_str))
            # If amount larger that certain value reload before experiment
        extra_amount = 45
            # We may also need to flush the electrolyte
        if amount > liquid_data_hist[pump_str][-1]:
            evacuate_set = True
            print("We suck liquid")

            liquid_added = convert_ml_to_steps(int(extra_amount),pump_str) # We add liquid till we reach 50 
            cmd_i = f"SyringePumps {pump} {liquid_added} backward refill "

            serialcomm.write(cmd_i.encode())
            confirmation = ""
            while confirmation != "SyringePump movement comp":
                confirmation = serialcomm.readline().decode().strip()
                 # We simply fill liquid until it reaches 50 ml 

                time.sleep(2)
            liquid_data_hist[pump_str].append(extra_amount + liquid_data_hist[pump_str][-1] - flush_volume)

            flush_volume_steps = str(convert_ml_to_steps(float(flush_volume), pump_str))
            # Next we need to flush the syringe pumps as well 
            cmd_flush_tubes = f"SyringePumps {pump} {flush_volume_steps} forward "

            serialcomm.write(cmd_flush_tubes.encode())
            confirmation = ""
            while confirmation != "SyringePump movement comp":
                confirmation = serialcomm.readline().decode().strip()
                 # We simply fill liquid until it reaches 50 ml 

                
            # Now we have flushed the tubes, and we need to remove the excess liquids

            #cmd_empty_chamber = "EVAC_SOL_TEST " if chamber == "testing" else "EVAC_SOL "
            #serialcomm.write(cmd_empty_chamber.encode())
            #confirmation = ""
            #while confirmation != "complete evacuation":
            #    confirmation = serialcomm.readline().decode().strip()
    
    
    print("Testing evacuation going now", time.time())
    if chamber == "testing" and evacuate_set == True:
        serialcomm.write("EVAC_SOL_TEST ".encode())
        confirmation = ""
        while confirmation != "complete evacuation":
            confirmation = serialcomm.readline().decode().strip()
    
        print("Evacuated testing chamber", time.time())
    else:
        if evacuate_set == True:
            serialcomm.write("EVAC_SOL ".encode())
            confirmation = ""
            while confirmation != "complete evacuation":
                confirmation = serialcomm.readline().decode().strip()

    for pumping_liquid in command_dict.keys():
        amount = command_dict[pumping_liquid]["amount ml"]

        pump = command_dict[pumping_liquid]["Pump"]
        pump_str = "Pump " + str(pump)

        amount_step = str(convert_ml_to_steps(float(amount), pump_str))
        confirmation = ""
        cmd_i = "SyringePumps " + str(pump) + " " + amount_step + " forward "
        
        print(cmd_i, "This is the command for pushing out liquid")
        
        if amount == 0:
            liquid_data_hist[pump_str].append(liquid_data_hist[pump_str][-1] - command_dict[pumping_liquid]["amount ml"])
            continue
        serialcomm.write(cmd_i.encode())
        while confirmation != "SyringePump movement comp":
            confirmation = serialcomm.readline().decode().strip()
            
            print(confirmation)
        liquid_data_hist[pump_str].append(liquid_data_hist[pump_str][-1] - command_dict[pumping_liquid]["amount ml"])
    
    for pump_str in liquid_data_hist.keys():
        liquid_data_hist[pump_str] = liquid_data_hist[pump_str][-3:] # Save only last three entries 
        
    if save_history:
        with open(data_logger_file, 'w') as file:
            json.dump(liquid_data_hist, file)  # Save DataFrame to CSV file
    return True




def pump_liqiud_mixing_deposition(serialcomm = None):
    '''
        Function for peristaltic pump from mixing chamber into synthesi 
    '''
    if serialcomm == None:
        return False
    CMD = "FILL_SOL"
    serialcomm.write(CMD.encode())
    time.sleep(60)
    return 


def pump_liquid_deposition_waste(serialcomm=None):
    #command for evacuation the solution
    if serialcomm == None:
        return False
    CMD = "EVAC_SOL"
    serialcomm.write(CMD.encode())
    time.sleep(15)
    return 


def pump_liquid_mixing_test(serialcomm=None):
        #command for pumping liquid from testing to waste
    if serialcomm == None:
        return False
    CMD = "FILL_SOL_TEST"
    serialcomm.write(CMD.encode())
    time.sleep(60)
    return 

def pump_liquid_testing_waste(serialcomm=None):
        #command for pumping liquid from testing to waste
    if serialcomm == None:
        return False
    CMD = "EVAC_SOL_TEST"
    serialcomm.write(CMD.encode())
    time.sleep(15)
    return 

def pump_cleaning_mixing_deposition(serialcomm = None):
    if serialcomm == None:
        return False
    

    CMD = "FILL_SOL"
    serialcomm.write(CMD.encode())
    return 

def clean_testing_chamber():
    '''
        Function for cleaning the testing chamber 
        this function should call on function for sending cleaning liquid into the testing chamber
    '''
    return 



