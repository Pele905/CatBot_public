import serial
import pandas as pd 
import numpy as np 

import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import time 
import threading 
import json 
from matplotlib.animation import FuncAnimation
from datetime import datetime
# Functions for ensuring that temperature in the alkaline and testing chambers 
# are well converged 
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

def filter_temp_data(data_dict, chamber):
    if chamber == "testing":
        temp_liquid = data_dict['Temp KOH']
        temp_copper = data_dict['Temp Copper holder']
    elif chamber == "deposition":
        temp_liquid = data_dict['Temp Electrolyte']
        temp_copper = data_dict['Temp Copper holder']
    heating_power = data_dict["Heating power"]
    time_s = data_dict['Time (s)']
    # Filter data where both temp_liquid and temp_copper are greater than 0
    filtered_temp_liquid = [temp for temp, copper in zip(temp_liquid, temp_copper) if temp > 0 and copper > 0]
    filtered_temp_copper = [copper for temp, copper in zip(temp_liquid, temp_copper) if temp > 0 and copper > 0]
    filtered_heating_power = [power for temp, copper, power in zip(temp_liquid, temp_copper, heating_power) if temp > 0 and copper > 0]
    filtered_time = [round(time_i) for temp, copper, time_i in zip(temp_liquid, temp_copper, time_s) if temp > 0 and copper > 0]
    return filtered_temp_liquid, filtered_temp_copper, filtered_heating_power, filtered_time

def save_png_from_data(filename = "", chamber = "testing"):
    
    fig, ax1 = plt.subplots(figsize=(10, 8))
    exp_name = filename.split(".")[0] # Get the name by removing the .json 

        
    with open(filename, 'r') as file:
        data_dict = json.load(file)

    if chamber == "testing":
        #temp_liquid = data_dict['Temp KOH']
        #temp_copper = data_dict['Temp Copper holder']
        temp_liquid, temp_copper, heating_power, time_s = filter_temp_data(data_dict=data_dict,
                                                                   chamber=chamber)
    if chamber == "deposition":
        temp_liquid, temp_copper, heating_power, time_s = filter_temp_data(data_dict=data_dict,
                                                                   chamber=chamber)

        #temp_liquid = data_dict['Temp Electrolyte']
        #temp_copper = data_dict['Temp Copper holder']
    #heating_power = data_dict["Heating power"]

    # Read data from the JSON file
    # Clear previous plot
    ax1.clear()
    ax2 = ax1.twinx()
    
    # Plot temperature data on primary axis with coolwarm colormap
    ax1.plot(time_s, temp_liquid, label='Temp electrolyte', color='red', linestyle='-')
    ax1.plot(time_s, temp_copper, label='Temp copper', color='red', linestyle='--')  # Dotted line
    ax1.set_xlabel('Time [s]', fontsize=20)
    ax1.set_ylabel('Temperature [C]', fontsize = 20)
    ax1.legend(loc='upper left', fontsize = 20)
    ax1.tick_params(axis='both', which='major', labelsize=18)
    # Create secondary axis for heating power
    
    ax2.clear()
    # Plot heating power data on secondary axis
    ax2.plot(time_s, heating_power, label='Heating power', color='blue')
    
    ax2.tick_params(axis='both', which='major', labelsize=18)
    ax2.set_ylabel('Heating Power', fontsize = 20)
    ax2.set_ylim(-1, 256)   
    ax2.yaxis.set_label_position('right')
    ax2.legend(loc='lower right',fontsize = 20)

    plt.tight_layout()
    plt.savefig(f'{exp_name}.png')

    plt.close()

    #plt.show()

def save_png_both_chambers(filename = ""):

        
    with open(filename, 'r') as file:
        data_dict = json.load(file)

 # Get the name by removing the .json 

    time_s = data_dict['Time (s)']
    temp_KOH = data_dict['Temp KOH']
    temp_copper_test = data_dict['Temp Copper holder test']
    temp_copper_dep = data_dict['Temp Copper holder dep']
    temp_electrolyte = data_dict['Temp Electrolyte']
    heating_power_test = data_dict["Heating power test"]
    heating_power_dep = data_dict["Heating power dep"] 

    plt.figure(figsize=(12, 9))
    exp_name = filename.split(".")[0]

    
    # Plot temperature data on primary axis with coolwarm colormap
    plt.plot(time_s, temp_KOH, label='Temp KOH', color='red', linestyle='-')
    plt.plot(time_s, temp_copper_test, label='Temp copper testing', color='red', linestyle='--')  # Dotted line
    plt.xlabel('Time [s]', fontsize=20)
    plt.ylabel('Temperature [C]', fontsize = 20)
    plt.legend(loc='upper left', fontsize = 20)
    plt.xticks(fontsize = 18)
    plt.yticks(fontsize = 18)
    # Create secondary axis for heating power
    
    plt.savefig(f'{exp_name}_test.png')
    plt.close()
    
    fig, ax1 = plt.subplots(figsize=(12, 9))
    exp_name = filename.split(".")[0]
    # Plot temperature data on primary axis with coolwarm colormap
    ax1.plot(time_s, temp_electrolyte, label='Temp electrolyte', color='red', linestyle='-')
    ax1.plot(time_s, temp_copper_dep, label='Temp copper deposition', color='red', linestyle='--')  # Dotted line
    ax1.set_xlabel('Time [s]', fontsize=20)
    ax1.set_ylabel('Temperature [C]', fontsize = 20)
    ax1.legend(loc='upper left', fontsize = 20)
    ax1.tick_params(axis='both', which='major', labelsize=18)
    # Create secondary axis for heating power
    
    plt.savefig(f'{exp_name}_dep.png')
    plt.close()
    



def plot_values_from_file(data_dict = None, filename = "", chamber = "testing"):
    counter = 0
    fig, ax1 = plt.subplots()
    exp_name = filename.split(".")[0] # Get the name by removing the .json 
    def animate(i):
        counter += 1
        with open(filename, 'r') as file:
            data_dict = json.load(file)

        if chamber == "testing":
            temp_liquid = data_dict['Temp KOH']
            temp_copper = data_dict['Temp Copper holder']

        if chamber == "deposition":
            temp_liquid = data_dict['Temp Electrolyte']
            temp_copper = data_dict['Temp Copper holder']
            heating_power = data_dict["Heating power"]
        # Read data from the JSON file
        
        # Clear previous plot
        ax1.clear()
        ax2 = ax1.twinx()
        
        # Plot temperature data on primary axis with coolwarm colormap
        ax1.plot(temp_liquid, label='Temp electrolyte', color='red', linestyle='-')
        ax1.plot(temp_copper, label='Temp copper', color='red', linestyle='--')  # Dotted line
        ax1.set_xlabel('Time [s]', fontsize=20)
        ax1.set_ylabel('Temperature [C]', fontsize = 20)
        ax1.legend(loc='upper left', fontsize = 20)
        ax1.tick_params(axis='both', which='major', labelsize=18)
        # Create secondary axis for heating power
        
        ax2.clear()
        # Plot heating power data on secondary axis
        ax2.plot(heating_power, label='Heating power', color='blue')
        
        ax2.tick_params(axis='both', which='major', labelsize=18)
        ax2.set_ylabel('Heating Power', fontsize = 20)
        ax2.set_ylim(-1, 256)   
        ax2.yaxis.set_label_position('right')
        ax2.legend(loc='lower right',fontsize = 20)

        
        plt.savefig(f'{exp_name}.png')
        print("We try saving")
    # Create animation
    ani = FuncAnimation(plt.gcf(), animate, interval=1000)  # Update plot every 5 seconds
    #plt.show()

def generate_temp_df(temp_df = None, serialcomm = None,save_file = True,  filename = "data.json", chamber = "testing",
                     starting_time = 0):
    temperature_reading = serialcomm.readline().decode().strip()
    time_read = time.time() - starting_time
    current_time = datetime.now()
    current_time = current_time.strftime("%d_%m_%Y %H:%M:%S")
    try:
        T_test = float(temperature_reading.split(":")[1].strip()[0:5])
        T_test_copper = float(temperature_reading.split(":")[2].strip()[0:5])
        T_dep = float(temperature_reading.split(":")[3].strip()[0:5])
        T_dep_copper = float(temperature_reading.split(":")[4].strip()[0:5])
        heating_power_num_dep = float(temperature_reading.split(":")[4].split("Heating power dep ")[1].split("H")[0])
        heating_power_num_test = float(temperature_reading.split(":")[4].split("Heating power test ")[1])
    except Exception as e:
        print('Error, temperature reading looks like this:', temperature_reading)
        T_dep = 0
        T_dep_copper = 0    
        T_test = 0  
        T_test_copper = 0
        heating_power_num_test = 0
        heating_power_num_dep = 0

    if temp_df == None:
        if chamber == "testing":
            data_df = {
            "Temp KOH" : [T_test],
            "Temp Copper holder" : [T_test_copper],
            "Heating power" : [heating_power_num_test],
            'Time (s)' : [time_read],
            'Exact time' : [current_time]
            }
        elif chamber == "deposition":
            data_df = {
                "Temp Electrolyte" : [T_dep],
                "Temp Copper holder" : [T_dep_copper],
                "Heating power" : [heating_power_num_dep],
                'Time (s)' : [time_read], 
                'Exact time' : [current_time]
            }
        elif chamber == "both":
            data_df = {
                "Temp KOH" : [T_test],
                "Temp Copper holder test" : [T_test_copper],
                "Temp Electrolyte" : [T_dep],
                "Temp Copper holder dep" : [T_dep_copper],
                "Heating power dep" : [heating_power_num_dep],
                "Heating power test" : [heating_power_num_test],
                'Time (s)' : [time_read],
                'Exact time' : [current_time]
            }
        #print(data_df)
        if save_file:
            with open(filename, 'w') as file:
                json.dump(temp_df, file)
        return data_df
    
    if chamber == "testing":
        temp_df["Temp KOH"].append(T_test)
        temp_df["Temp Copper holder"].append(T_test_copper)
        temp_df["Heating power"].append(heating_power_num)
        temp_df['Time (s)'].append(time_read)

    elif chamber == "deposition":
        temp_df["Temp Electrolyte"].append(T_dep)
        temp_df["Temp Copper holder"].append(T_dep_copper)
        temp_df["Heating power"].append(heating_power_num)
        temp_df['Time (s)'].append(time_read)
    elif chamber == "both":
        temp_df["Temp KOH"].append(T_test)
        temp_df["Temp Electrolyte"].append(T_dep)

        temp_df["Temp Copper holder test"].append(T_test_copper)
        temp_df["Temp Copper holder dep"].append(T_dep_copper)

        temp_df["Heating power test"].append(heating_power_num_test)
        temp_df["Heating power dep"].append(heating_power_num_dep)
        temp_df['Time (s)'].append(time_read)
        temp_df['Exact time'].append(current_time)

    #temp_df = temp_df.append(pd.DataFrame(temp_data_i), ignore_index=True)
    if save_file:
        with open(filename, 'w') as file:
            json.dump(temp_df, file)  # Save DataFrame to CSV file

    return temp_df

def save_png_continuously(filename = "", chamber = "testing", stop_event = None):
    while stop_event.is_set() == False:
        if chamber == "testing" or chamber == "deposition":
            try:
                save_png_from_data(filename=filename, chamber = chamber)
            except:
                pass
        elif chamber == "both":
            try:
                save_png_both_chambers(filename=filename)
            except:
                pass
        time.sleep(10)



def send_command_with_confirmation(serialcomm, temp_cmd):
    max_retries = 5
    for i in range(max_retries):
        try:
            if not serialcomm.is_open:
                serialcomm.open()
            serialcomm.flushInput()
            serialcomm.write(temp_cmd.encode())  # Send the command
            time.sleep(2)  # Give Arduino some time to process
            
            if serialcomm.in_waiting > 0:
                ack = serialcomm.read(serialcomm.in_waiting).decode().strip()
                if ack == "Temp Set":
                    print("Acknowledgment received. Command processed successfully.")
                    return True
        except serial.SerialException as e:
            print(f"Serial port error: {e}")
            try:
                serialcomm.close()
                time.sleep(1)
                serialcomm.open()  # Attempt to reopen the port
            except Exception as e:
                print(f"Failed to reopen serial port: {e}")
                return False  # Fail fast if the port cannot be reopened
        except serial.serialutil.PortNotOpenError:
            print("Port is not open. Attempting to reopen...")
            try:
                serialcomm.open()
            except Exception as e:
                print(f"Failed to open serial port: {e}")
                return False

        print("No acknowledgment received. Retrying...")
        time.sleep(1)  # Wait before retrying
    
    print("Failed to receive acknowledgment after multiple retries.")
    return False

def set_temperature_both_chambers(temperature_dep = 30, temperature_test = 30, 
                                  filename = "data.json", serialcomm = None, 
                               temp_df = None, stop_event = None):
    if serialcomm == None:
        serialcomm = serial.Serial('/dev/cu.usbmodem1101', 9600, timeout=2) # Communication to arduino occurs through modem
    
    time.sleep(5)
    # Write the desired temperature to the arduino controller 
    # Since we regulate temperature by using the copper chamber, the temperature of the electrolyte is 
    # less. Therefore we add a constant offset to this to ensure the liquid temperature is 
    # consistent

    temperature_correction_dep = get_temperature_correction_dep(temperature_dep)
    temp_cmd = "Deposition " + str((temperature_dep + temperature_correction_dep) * 1.035) # Correction found from Runes temp tests
    
    temperature_correction_test = get_temperature_correction_test(temperature_test)
    
    temp_cmd += " Testing " + str(temperature_test + temperature_correction_test)
    #serialcomm.write(temp_cmd.encode())
    confirmation = send_command_with_confirmation(serialcomm=serialcomm,
                                   temp_cmd=temp_cmd)
    
    if confirmation == True:
        print("Confirmation of temperature confirmed")
        print(temp_cmd)
        pass
    else:
        print("Failed to communicate with Arduino, retrying")
        serialcomm.close()
        serialcomm = serial.Serial('COM4', 115200, timeout=5) #UPDATE WHEN USING NEW COMPUTER#####################################################################################
        print("We manage to connect to temperature serial")
        time.sleep(20)
        confirmation = send_command_with_confirmation(serialcomm=serialcomm,
                                   temp_cmd=temp_cmd)
        #return False
    
    starting_time = time.time()
    while stop_event.is_set() == False:
        time.sleep(1)
        try:
            temp_df = generate_temp_df(temp_df, serialcomm, filename = filename, chamber = "both",
                                       starting_time=starting_time)
            
        except Exception as e:
            print(e)
            
    serialcomm.write("Deposition 0".encode())
    print("We sent command")
    return 

def set_temperature_deposition(temperature=30, filename = "data.json", serialcomm = None, 
                               temp_df = None, stop_event = None):
    '''
        Set temperature of the deposition chamber by Serial communication with Arduino
        input params: temperature, conv_crit amplitude of oscillation before temperature
        is considered to converge

        Returns the temperature data up until convergence of the temperature series 
    '''
    
    if serialcomm == None:
        serialcomm = serial.Serial('/dev/cu.usbmodem1101', 9600, timeout=2) # Communication to arduino occurs through modem
    
    time.sleep(5)
    # Write the desired temperature to the arduino controller 
    # Since we regulate temperature by using the copper chamber, the temperature of the electrolyte is 
    # less. Therefore we add a constant offset to this to ensure the liquid temperature is 
    # consistent

    temperature_correction = get_temperature_correction_dep(temperature)
    temp_cmd = "Deposition " + str((temperature + temperature_correction) * 1.035) # Correction found from Runes temp tests
    #serialcomm.write(temp_cmd.encode())
    confirmation = send_command_with_confirmation(serialcomm=serialcomm,
                                   temp_cmd=temp_cmd)
    
    if confirmation == True:
        print("Confirmation of temperature confirmed")
        print(temp_cmd)
        pass
    else:
        print("Failed to communicate with Arduino, retrying")
        serialcomm.close()
        serialcomm = serial.Serial('COM4', 115200, timeout=5) #UPDATE WHEN USING NEW COMPUTER#####################################################################################
        print("We manage to connect to temperature serial")
        time.sleep(20)
        confirmation = send_command_with_confirmation(serialcomm=serialcomm,
                                   temp_cmd=temp_cmd)
        #return False
    
    starting_time = time.time()
    while stop_event.is_set() == False:
        time.sleep(1)
        try:
            temp_df = generate_temp_df(temp_df, serialcomm, filename = filename, chamber = "deposition",
                                       starting_time=starting_time)
            
        except Exception as e:
            print(e)
            
    serialcomm.write("Deposition 0".encode())
    print("We sent command")
        

def set_temperature_testing(temperature=30, filename = "data.json", serialcomm = None, 
                               temp_df = None, stop_event = None):
    '''
        Set temperature of the deposition chamber by Serial communication with Arduino
        input params: temperature, conv_crit amplitude of oscillation before temperature
        is considered to converge
    '''
    if serialcomm == None:
        serialcomm = serial.Serial('/dev/cu.usbmodem1101', 9600, timeout=2) # Communication to arduino occurs through modem
    
    time.sleep(5)
    # Write the desired temperature to the arduino controller 
    # Since we regulate temperature by using the copper chamber, the temperature of the electrolyte is 
    # less. Therefore we add a constant offset to this to ensure the liquid temperature is 
    # consistent

    temperature_correction = get_temperature_correction_test(temperature)
    temp_cmd = "Testing " + str(temperature + temperature_correction)
    #serialcomm.write(temp_cmd.encode())
    confirmation = send_command_with_confirmation(serialcomm=serialcomm,
                                   temp_cmd=temp_cmd)
    
    if confirmation == True:
        print("Confirmation of temperature confirmed")
        print(temp_cmd)
        pass
    else:
        print("Failed to communicate with Arduino, retrying")
        serialcomm.close()
        serialcomm = serial.Serial('COM4', 115200, timeout=5) #UPDATE WHEN USING NEW COMPUTER#####################################################################################
        print("We manage to connect to temperature serial")
        time.sleep(20)
        confirmation = send_command_with_confirmation(serialcomm=serialcomm,
                                   temp_cmd=temp_cmd)
        #return False
    
    starting_time = time.time()
    while stop_event.is_set() == False:
        time.sleep(1)
        try:
            temp_df = generate_temp_df(temp_df, serialcomm, filename = filename, chamber = "testing",
                                       starting_time=starting_time)
            
        except Exception as e:
            print(e)
            
    serialcomm.write("Testing 0".encode())
    print("We sent command")


def check_convergence(window_size, datafile, desired_temperature = 40, event = None, 
                      convergence_setter = "Temp Copper holder", chamber = "Deposition"):
    with open(datafile, 'r') as file:
        data_dict = json.load(file)
        temp_array = data_dict[convergence_setter]
    try:
        temperature_window = temp_array[len(temp_array) - window_size : len(temp_array)]
        mean_temp_window = np.mean(temperature_window)

    except:
        temperature_window = temp_array[0: len(temp_array)]
        mean_temp_window = np.mean(temperature_window)

    if desired_temperature >= 50:
        temp_diff = 3 # I am afraid that we take forever to converge and start an experiment
        # Therefore convergence criteria have been loosened slightly 
    else:
        temp_diff = 2
    if abs(mean_temp_window - desired_temperature) < temp_diff:
        if np.std(temperature_window) < 0.5:
            print("Temperature converged: in chamber", chamber)
            event.set()
            return True

        #return False



def check_convergence_periodically(interval,window_size, filename, temperature, event,
                                   convergence_setter = "Temp Copper holder", chamber = "Deposition"):
    while not event.is_set():
        try:
            check_convergence(window_size, 
                              filename, 
                              temperature, 
                              event,
                              convergence_setter=convergence_setter, chamber=chamber)
            time.sleep(interval)
        except Exception as e:
            print(e)
            time.sleep(interval)
    
    time.sleep(1)

#