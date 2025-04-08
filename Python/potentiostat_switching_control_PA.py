import numpy as np 
import matplotlib.pyplot as plt 
import time 
import serial

def activate_potentiostat_deposition(serialcomm = None):
    '''
        Activates the deposition potentiostat, by switching the servo 
        and sending a signal to the relay box to change the counter to the deposition chamber
    '''
    if serialcomm == None:
        serialcomm = serial.Serial('/dev/cu.usbmodem1101', 9600)
        time.sleep(20)

    confirmation = ""
    cmd_i = "ActivatePotentiostatDeposition "
    serialcomm.write(cmd_i.encode())
    while confirmation != "Deposition Potentiostat Activated":
        confirmation = serialcomm.readline().decode().strip()

    time.sleep(2)
    return True


def deactivate_potentiostat_deposition(serialcomm = None):
    '''
        Deactivates the deposition potentiostat, by switching the servo 
        and sending a signal to the relay box to change the counter to the deposition chamber
    '''
    confirmation = ""
    cmd_i = "DeactivatePotentiostatDeposition "
    serialcomm.write(cmd_i.encode())
    timeout = 10
    time_start = time.time()
    time_0 = 0
    while (confirmation != "Deposition Potentiostat deactivated") or (time_0 < timeout):
        if time_0 > timeout: 
            print("Timeout error / reading serialcomm for deactivating potentiostat")
            return False
        print("Confirmation potentiostat:", confirmation)
        confirmation = serialcomm.readline().decode().strip()
        time_0 = int(time.time() - time_start)
    return True

def activate_potentiostat_testing(serialcomm = None):
    '''
        Activates the testing potentiostat, by switching the servo 
        and sending a signal to the relay box to change the counter to the testing chamber
    '''
    if serialcomm == None:
        serialcomm = serial.Serial('/dev/cu.usbmodem1101', 9600)
        time.sleep(20)

    confirmation = ""
    cmd_i = "ActivatePotentiostatTesting "
    serialcomm.write(cmd_i.encode())
    while confirmation != "Testing potentiostat activated":
        confirmation = serialcomm.readline().decode().strip()
    time.sleep(2)
    return True


def deactivate_potentiostat_testing(serialcomm = None):
    '''
        Deactivates the testing potentiostat, by switching the servo 
        and sending a signal to the relay box to change the counter to the testing chamber
    '''
    if serialcomm == None:
        serialcomm = serial.Serial('/dev/cu.usbmodem1101', 9600)
        time.sleep(20)

    confirmation = ""
    cmd_i = "DeactivatePotentiostatTesting "
    serialcomm.write(cmd_i.encode())
    timeout = 10
    time_start = time.time()
    time_0 = 0
    while confirmation != "Testing potentiostat dectivated" or time_0 > timeout:
        print("Confirmation potentiostat:", confirmation)
        confirmation = serialcomm.readline().decode().strip()
        time_0 = time.time() - time_start
        print(time_0)
    
    if time_0 > timeout:
        print("Timeout error / reading serialcomm for deactivating potentiostat")
    return True
