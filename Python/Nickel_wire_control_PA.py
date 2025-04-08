import numpy as np 
import matplotlib.pyplot as plt 
import time 
import threading 
import json 
from matplotlib.animation import FuncAnimation
import datetime
import serial

# We have now found some few constant 
# 3 * 23717 
# 9000 +- 50 out of HCl, into HCl test length
# We now introduce a datalogger into the mix 

def update_datalogger_wirepulling(steps, 
                                  reset_status = False,
                                  reset_steps = 0,
                                  data_logger_file = "datalogger_wire_roll.json"):
    '''
        Reset steps is the number of steps we should give to the Nickel wire roll after we reset it
    '''
    try:
        datalogger = open(data_logger_file)
        datalogger = json.load(datalogger)
    except Exception as e:
        print(e)
        print("Trying to create new datalogger file")
        datalogger = {"Wheel status": [steps]}

#Remove here
        data_logger_file = "datalogger_wire_roll.json"
        with open(data_logger_file, "w") as outfile: 
            json.dump(datalogger, outfile)
        return 

    if reset_status:
        datalogger["Wheel status"] = [reset_steps]
        with open(data_logger_file, "w") as outfile: 
            json.dump(datalogger, outfile)

    else:
        datalogger["Wheel status"].append(steps)
        with open(data_logger_file, "w") as outfile: 
            json.dump(datalogger, outfile)

def reset_wheel_to_start(serialcomm,
                          data_logger_file):
    try:
        datalogger = open(data_logger_file)
        datalogger = json.load(datalogger)
    except Exception as e:
        print(e)
        print("Failed to load a datalogger")

    # Sum over the steps to reset the wheel back to exact start position
    steps_to_reset = np.sum(datalogger["Wheel status"])

    # Reset the status of the wirepulling datalogger 
    update_datalogger_wirepulling(steps = 0, reset_status=True,reset_steps=0,
                                  data_logger_file=data_logger_file)
    

    max_step_size = 32767

    # First, handle the full 32767 step chunks
    full_chunks = steps_to_reset // max_step_size  # Number of full 32767 step chunks
    remaining_steps = steps_to_reset % max_step_size  # Steps left after full chunks
    print(full_chunks)
# Loop through each full chunk
    for _ in range(full_chunks):
        cmd_i = f"ReverRollWireNSteps {max_step_size}"  # Command for 32767 steps
        serialcomm.write(cmd_i.encode())  # Send command to Arduino
        confirmation = ""
        while confirmation != "Wire rolled reverse complete":
            confirmation = serialcomm.readline().decode().strip()

    # Finally, handle the remaining steps
    if remaining_steps > 0:
        cmd_i = f"ReverRollWireNSteps {remaining_steps}"  # Command for remaining steps
        serialcomm.write(cmd_i.encode())  # Send command to Arduino
        confirmation = ""
        while confirmation != "Wire rolled reverse complete":
            confirmation = serialcomm.readline().decode().strip()
    time.sleep(0.5)
    return True

def reset_actuator(serialcomm,
                          data_logger_file):
    try:
        datalogger = open(data_logger_file)
        datalogger = json.load(datalogger)
    except Exception as e:
        print(e)
        print("Failed to load a datalogger")

    # Sum over the steps to reset the wheel back to exact start position
    steps_to_reset = np.sum(datalogger["Wheel status"])

    # Reset the status of the wirepulling datalogger 
    update_datalogger_wirepulling(steps = 0, reset_status=True,reset_steps=0,
                                  data_logger_file=data_logger_file)
    

    n_steps_actuator = int(steps_to_reset / (200)) # Resets the actuator to the same starting position

    cmd_i = f"ReverseMoveActuatorNSteps {n_steps_actuator} "  # Command for 32767 steps
    serialcomm.write(cmd_i.encode())  # Send command to Arduino



def roll_wire_into_HCl(serialcomm):
    '''
        Rolls our wire into the HCl bath and then stops 
    '''

    if serialcomm == None:
        serialcomm = serial.Serial('/dev/cu.usbmodem1101', 9600)
        time.sleep(20)

    confirmation = ""
    cmd_i = "DipWireIntoHCl"
    serialcomm.write(cmd_i.encode())
    while confirmation != "Wire Rolled into HCl":
        confirmation = serialcomm.readline().decode().strip()

    time.sleep(0.5)
    update_datalogger_wirepulling(steps = 11650, reset_status=False, reset_steps=0,
                                data_logger_file="datalogger_wire_roll.json")
    return 11650

def roll_wire_HCl_to_water(serialcomm):
    '''
        Pump liquid from the syringe pump to the testing cell
        input params: command_dict, serialcomm, volume_df
    '''

    if serialcomm == None:
        serialcomm = serial.Serial('/dev/cu.usbmodem1101', 9600)
        time.sleep(20)

    confirmation = ""
    cmd_i = "RollWireHClToWater"
    serialcomm.write(cmd_i.encode())
    while confirmation != "Wire Rolled from HCl to water":
        confirmation = serialcomm.readline().decode().strip()
    time.sleep(0.5)
    update_datalogger_wirepulling(steps = 18875 * 2, reset_status=False, reset_steps=0,
                            data_logger_file="datalogger_wire_roll.json")
    return (18325 + 650) * 2

def roll_wire_while_depositing(serialcomm, deposition_time_total_s = 1):
    '''
        Persumed 10000 steps 
    '''

    steps = 2 * 5142
    steps_s = steps / (2 * deposition_time_total_s)
    steps_ms = steps_s * 10 ** (-3)
    delay_time = 1 / (steps_ms)
    print(delay_time)
    if serialcomm == None:
        serialcomm = serial.Serial('/dev/cu.usbmodem1101', 9600)
        time.sleep(20)

    confirmation = ""
    cmd_i = f"RollWireWhileExperimenting {steps} {delay_time} "
    serialcomm.write(cmd_i.encode())
    while confirmation != "Wire rolled X number of steps":
        confirmation = serialcomm.readline().decode().strip()
    time.sleep(0.5)
    update_datalogger_wirepulling(steps = 18875 * 2, reset_status=False, reset_steps=0,
                            data_logger_file="datalogger_wire_roll.json")
    return True

def roll_wire_water_testing(serialcomm):
    '''
        Rolls wire from water waiting station into the air waiting station
    '''


    confirmation = ""
    cmd_i = "RollWireWaterTesting" 
    serialcomm.write(cmd_i.encode())
    while confirmation != "Wire rolled water - testing":
        confirmation = serialcomm.readline().decode().strip()
    time.sleep(0.5)
    update_datalogger_wirepulling(steps = 51400, reset_status=False, reset_steps=0,
                        data_logger_file="datalogger_wire_roll.json")
    return True


def roll_wire_water_waiting(serialcomm):
    '''
        Rolls wire from water waiting station into the air waiting station
    '''


    confirmation = ""
    cmd_i = "RollWireWaterWaiting" 
    serialcomm.write(cmd_i.encode())
    while confirmation != "Wire rolled water - waiting":
        confirmation = serialcomm.readline().decode().strip()
    time.sleep(0.5)
    update_datalogger_wirepulling(steps = 18650, reset_status=False, reset_steps=0,
                        data_logger_file="datalogger_wire_roll.json")
    return True

def roll_wire_waiting_deposition(serialcomm):
    '''
        Rolls wire from water waiting station into the air waiting station
    '''


    confirmation = ""
    cmd_i = "RollWireWaitingDeposition" 
    serialcomm.write(cmd_i.encode())
    while confirmation != "Wire rolled waiting - deposition":
        confirmation = serialcomm.readline().decode().strip()
    time.sleep(0.5)
    update_datalogger_wirepulling(steps = 18650, reset_status=False, reset_steps=0,
                        data_logger_file="datalogger_wire_roll.json")
    return True


def roll_wire_water_deposition(serialcomm, through = True):
    '''
        Pump liquid from the syringe pump to the testing cell
        input params: command_dict, serialcomm, volume_df
    '''

    if serialcomm == None:
        serialcomm = serial.Serial('/dev/cu.usbmodem1101', 9600)
        time.sleep(20)

    confirmation = ""
    
    cmd_i = "RollWireWaterDeposition " 
    if through == True:
        cmd_i = "RollWireWaterDeposition_RollingWhileDepositing "
    
    print("This is the command we send to Arduino water deposition ", cmd_i)
    serialcomm.write(cmd_i.encode())
    while confirmation != "Wire rolled water - deposition":
        confirmation = serialcomm.readline().decode().strip()
    time.sleep(0.5)
    update_datalogger_wirepulling(steps = 19250 * 2, reset_status=False, reset_steps=0,
                        data_logger_file="datalogger_wire_roll.json")
    if through:
        return (19475 + 200) * 2 - 5142
    return (19475 + 200)  * 2

def roll_wire_deposition_testing(serialcomm, through = True, calibrate_ref = True):
    '''
        Pump liquid from the syringe pump to the testing cell
        input params: command_dict, serialcomm, volume_df
    '''

    if serialcomm == None:
        serialcomm = serial.Serial('/dev/cu.usbmodem1101', 9600)
        time.sleep(20)

    confirmation = ""
    cmd_i = "RollWireDepositionToTesting "
    
    if through == True:
        if calibrate_ref:
            cmd_i = "RollWireDepositionToTesting_RollingWhileDepositing_Ni_calib "
        else:
            cmd_i = "RollWireDepositionToTesting_RollingWhileDepositing "
    
    
    print("This is the command we send to Arduino water testing ", cmd_i)
    serialcomm.write(cmd_i.encode())
    while confirmation != "Wire rolled deposition - testing":
        confirmation = serialcomm.readline().decode().strip()
    time.sleep(0.5)
    update_datalogger_wirepulling(steps = 19775 * 2, reset_status=False, reset_steps=0,
                        data_logger_file="datalogger_wire_roll.json")
    if through:
        return (19775 + 250) * 2 - 5142
    return (19775 + 250) * 2

def roll_wire_N_steps(serialcomm = None, N_steps = 10000):
    '''
        Pump liquid from the syringe pump to the testing cell
        input params: command_dict, serialcomm, volume_df
    '''

    if serialcomm == None:
        serialcomm = serial.Serial('/dev/cu.usbmodem1101', 9600)
        time.sleep(20)

    confirmation = ""
    cmd_i = f"RollWireNSteps {N_steps} "

    
    print("This is the command we send to Arduino water testing ", cmd_i)
    serialcomm.write(cmd_i.encode())
    while confirmation != "Wire rolled X number of steps":
        confirmation = serialcomm.readline().decode().strip()
    time.sleep(0.5)