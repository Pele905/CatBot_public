import sys
from PySide2.QtCore import QIODevice, QThread, QObject, Signal
from PySide2.QtSerialPort import QSerialPort
from PySide2.QtWidgets import QApplication
from SquidstatPyLibrary import (AisDeviceTracker, AisDCData, AisACData,
                                AisExperiment, AisInstrumentHandler,AisEISGalvanostaticElement, AisDCPotentialSweepElement,
                                AisConstantCurrentElement, AisOpenCircuitElement, AisCyclicVoltammetryElement, 
                                AisSteppedCurrentElement)

import time


def make_subexperiment_to_dictionary(subexperiment):

    if subexperiment.name == "Cyclic voltammetry ":
        print("a")
    # Or whatever
    return 

def nickel_calibration_KOH(shift):
    experiment = AisExperiment()
    # start frequency, end frequency, stepsPerDecade, currentBias, currentAmplitude
    # Seeing
    # Defined new testing protocol from Thu's input avoid Mo oxidiation at 0.7

    mA = 10**(-3)
    A = 0.975 # Area in cm2 
    time = 20 # How many minutes
    short_CP_time =2

    opencircuitElement = AisOpenCircuitElement(10, 2)

    CvElement_1000 = AisCyclicVoltammetryElement(0-shift,1-shift,0-shift, 0-shift ,1,0.000001)

    experiment.appendElement(opencircuitElement)
    experiment.appendElement(CvElement_1000, 10)

    return experiment

def second_protocol_with_steps():
    experiment = AisExperiment()
    # start frequency, end frequency, stepsPerDecade, currentBias, currentAmplitude
    # Seeing
    mA = 10**(-3)
    A = 0.975 # Area in cm2 
    time = 10 # How many minutes
    opencircuitElement = AisOpenCircuitElement(300, 2)
    smoothing_LSV = AisDCPotentialSweepElement(-0.3, 0.6, 0.02, 0.01)
    galvanostatiEISElement = AisEISGalvanostaticElement(100000, 1, 7, -10 * mA * A, -1 * mA * A)

    constantcurrentElement1mA_cm2 = AisConstantCurrentElement(-1 * mA * A, 1, 60 * time)
    constantcurrentElement2mA_cm2 = AisConstantCurrentElement(-2 * mA * A, 1, 60 * time)
    constantcurrentElement5mA_cm2 = AisConstantCurrentElement(-5 * mA * A, 1, 60 * time)
    constantcurrentElement10mA_cm2 = AisConstantCurrentElement(-10 * mA * A, 1, 60 * time)
    constantcurrentElement20mA_cm2 = AisConstantCurrentElement(-20 * mA * A, 1, 60 * time)
    constantcurrentElement50mA_cm2 = AisConstantCurrentElement(-50 * mA * A, 1, 60 * time)

    CvElement_stability = AisCyclicVoltammetryElement(0,-0.3,0.7,0 ,0.05,0.01)

    CvElement_20 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.02,0.1)
    CvElement_40 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.04,0.1)
    CvElement_80 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.08,0.01)
    CvElement_160 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.160,0.01)
    CvElement_320 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.320,0.01)

    LSV = AisDCPotentialSweepElement(0, -0.5, 0.02, 0.01)

    # Start off with open circuit element + GEIS
    experiment.appendElement(opencircuitElement, 1)
    experiment.appendElement(galvanostatiEISElement, 1)
    experiment.appendElement(smoothing_LSV, 1)
    # Then Do ECSA
    experiment.appendElement(CvElement_320, 5)
    experiment.appendElement(CvElement_160, 5)
    experiment.appendElement(CvElement_80, 5)
    experiment.appendElement(CvElement_40, 5)
    experiment.appendElement(CvElement_20, 5)

    # Then preconditioning at 50 mA/cm2 
    experiment.appendElement(constantcurrentElement50mA_cm2, 1)
    
    # Getting the ohmic resistance from EIS 
    experiment.appendElement(LSV, 1)

    # Then do CPs to gather activity 
    experiment.appendElement(constantcurrentElement20mA_cm2, 1)
    experiment.appendElement(constantcurrentElement10mA_cm2, 1)
    experiment.appendElement(constantcurrentElement5mA_cm2, 1)
    experiment.appendElement(constantcurrentElement2mA_cm2, 1)
    experiment.appendElement(constantcurrentElement1mA_cm2, 1)
    
    # Testing stability
    experiment.appendElement(CvElement_stability, 100)
    
    # Then testing the activity after cycling 
    experiment.appendElement(constantcurrentElement20mA_cm2, 1)
    experiment.appendElement(constantcurrentElement10mA_cm2, 1)
    experiment.appendElement(constantcurrentElement5mA_cm2, 1)
    experiment.appendElement(constantcurrentElement2mA_cm2, 1)
    experiment.appendElement(constantcurrentElement1mA_cm2, 1)

    # Then testing the ECSA after cycling 
    experiment.appendElement(CvElement_320, 5)
    experiment.appendElement(CvElement_160, 5)
    experiment.appendElement(CvElement_80, 5)
    experiment.appendElement(CvElement_40, 5)
    experiment.appendElement(CvElement_20, 5)
    time = 5
    constantcurrentElement1mA_cm2 = AisConstantCurrentElement(-1 * mA * A, 1, 60 * time)
    constantcurrentElement2mA_cm2 = AisConstantCurrentElement(-2 * mA * A, 1, 60 * time)
    constantcurrentElement5mA_cm2 = AisConstantCurrentElement(-5 * mA * A, 1, 60 * time)
    constantcurrentElement10mA_cm2 = AisConstantCurrentElement(-10 * mA * A, 1, 60 * time)
    constantcurrentElement20mA_cm2 = AisConstantCurrentElement(-20 * mA * A, 1, 60 * time)
    constantcurrentElement50mA_cm2 = AisConstantCurrentElement(-50 * mA * A, 1, 60 * time)

    experiment.appendElement(constantcurrentElement1mA_cm2, 1)
    experiment.appendElement(constantcurrentElement5mA_cm2, 1)
    experiment.appendElement(constantcurrentElement1mA_cm2, 1)
    experiment.appendElement(constantcurrentElement10mA_cm2, 1)
    experiment.appendElement(constantcurrentElement1mA_cm2, 1)
    experiment.appendElement(constantcurrentElement20mA_cm2, 1)
    experiment.appendElement(constantcurrentElement1mA_cm2, 1)
    experiment.appendElement(constantcurrentElement50mA_cm2, 1)
    experiment.appendElement(constantcurrentElement1mA_cm2, 1)
    experiment.appendElement(constantcurrentElement20mA_cm2, 1)
    experiment.appendElement(constantcurrentElement1mA_cm2, 1)
    experiment.appendElement(constantcurrentElement10mA_cm2, 1)
    experiment.appendElement(constantcurrentElement1mA_cm2, 1)
    experiment.appendElement(constantcurrentElement5mA_cm2, 1)
    experiment.appendElement(constantcurrentElement1mA_cm2, 1)

    return experiment, "second_protocol_with_steps"

def run_debugging_experiment():
    experiment = AisExperiment()
    mA = 10**(-3)
    A = 1.07 # Area in cm2 
    time = 10 # How many minutes
    opencircuitElement = AisOpenCircuitElement(10, 2)

    galvanostatiEISElement = AisEISGalvanostaticElement(100000, 1, 7, -10 * mA * A, -1 * mA * A)
    experiment.appendElement(opencircuitElement, 1)
    CvElement_640 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.640,0.01)
    # Getting the ohmic resistance from EIS 
    experiment.appendElement(CvElement_640, 1)
    return experiment, "debugging"

def pulsed_deposition_protocol(current_pulse_height_mA_cm2 = -10, 
                               step_duration = 5, 
                               total_amount_deposited = 100):
    '''
        We need to maintain the total amount of catalyst loaded onto the susbstrate the be the same every time 

        total amount of deposited material should be in C / cm2 assuming 100 % FE
    '''
    # total amount deposited per cm2 assuming 100 % FE is 
    mA = 10**(-3)
    amount_dep_step = step_duration * current_pulse_height_mA_cm2 * mA  # Amount of deposited material in once cycle  

    amount_pulses = int(total_amount_deposited / (amount_dep_step))
    experiment = AisExperiment()
    
    A = 0.975 # Area of the wire in solution 
    
    # Starting current, end_current, step_size, step_duration, sampling interval
    stepped_current_element = AisSteppedCurrentElement(0, 
                                                       current_pulse_height_mA_cm2 * A,
                                                       current_pulse_height_mA_cm2 * A,
                                                       step_duration, 
                                                       0.1)
    opencircuitElement = AisOpenCircuitElement(10, 2)
    experiment.appendElement(opencircuitElement, 1)
    for _ in range(amount_pulses):

        experiment.appendElement(stepped_current_element)
    return experiment

def Ni_Mo_optimization_testing_protocol(shift=1.125):
    experiment = AisExperiment()
    # start frequency, end frequency, stepsPerDecade, currentBias, currentAmplitude
    # Seeing
    # Defined new testing protocol from Thu's input avoid Mo oxidiation at 0.7

    mA = 10**(-3)
    A = 0.975 # Area in cm2 
    time = 20 # How many minutes
    short_CP_time =2

    opencircuitElement = AisOpenCircuitElement(10, 2)

    galvanostatiEISElement = AisEISGalvanostaticElement(100000, 1, 7, -10 * mA * A, -0.5 * mA * A)
    # Outer extreme area is now 0.4 V reducing our testing time to 1 hours and 30 minutes between samples
    CvElement_stability = AisCyclicVoltammetryElement(0.1 - shift,-0.3-shift,0.4-shift,0.1 - shift ,0.05,0.01)
    
    CvElement_20 = AisCyclicVoltammetryElement(0.5-shift,0.575-shift,0.5-shift,0.5-shift,0.02,0.01)
    CvElement_40 = AisCyclicVoltammetryElement(0.5-shift,0.575-shift,0.5-shift,0.5-shift,0.04,0.01)
    CvElement_80 = AisCyclicVoltammetryElement(0.5-shift,0.575-shift,0.5-shift,0.5-shift,0.08,0.001)
    CvElement_160 = AisCyclicVoltammetryElement(0.5-shift,0.575-shift,0.5-shift,0.5-shift,0.160,0.0001)
    CvElement_320 = AisCyclicVoltammetryElement(0.5-shift,0.575-shift,0.5-shift,0.5-shift,0.320,0.0001)

    LSV_smooth_scan_back = AisDCPotentialSweepElement(-0.3-shift, 0.5-shift, 0.05, 0.01)
    
    # Start off with open circuit element + GEIS
    experiment.appendElement(opencircuitElement, 1)
    experiment.appendElement(galvanostatiEISElement, 1)
    experiment.appendElement(LSV_smooth_scan_back, 1)
    # Then Do ECSA
    experiment.appendElement(CvElement_320, 5)
    experiment.appendElement(CvElement_160, 5)
    experiment.appendElement(CvElement_80, 5)
    experiment.appendElement(CvElement_40, 5)
    experiment.appendElement(CvElement_20, 5)

    experiment.appendElement(CvElement_stability, 100)
    # Getting the polarisation path after Stability CV
    
    experiment.appendElement(LSV_smooth_scan_back, 1)
    # Then testing the ECSA after cycling 
    experiment.appendElement(CvElement_320, 5)
    experiment.appendElement(CvElement_160, 5)
    experiment.appendElement(CvElement_80, 5)
    experiment.appendElement(CvElement_40, 5)
    experiment.appendElement(CvElement_20, 5)

    return experiment, "testing_protocol_Ni_Mo"

def coated_wire_testing_protocol_1():
    experiment = AisExperiment()
    # start frequency, end frequency, stepsPerDecade, currentBias, currentAmplitude
    # Seeing
    mA = 10**(-3)
    A = 0.975 # Area in cm2 
    time = 20 # How many minutes
    short_CP_time =2

    opencircuitElement = AisOpenCircuitElement(10, 2)

    galvanostatiEISElement = AisEISGalvanostaticElement(100000, 1, 7, -10 * mA * A, -1 * mA * A)
    galvanostatiEISElement_100mA_cm2 = AisEISGalvanostaticElement(100000, 1, 7, -100 * mA * A, -1 * mA * A)

    constantcurrentElement1mA_cm2 = AisConstantCurrentElement(-1 * mA * A, 1, 60 * short_CP_time)
    constantcurrentElement100mA_cm2 = AisConstantCurrentElement(-100 * mA * A, 1, 60 * time)

    CvElement_stability = AisCyclicVoltammetryElement(0,-0.3,0.7,0 ,0.05,0.01)

    CvElement_20 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.02,0.1)
    CvElement_40 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.04,0.1)
    CvElement_80 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.08,0.01)
    CvElement_160 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.160,0.01)
    CvElement_320 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.320,0.01)
    CvElement_640 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.640,0.01)

    LSV_smooth_scan_back = AisDCPotentialSweepElement(-0.3, 0.6, 0.05, 0.01)

    LSV = AisDCPotentialSweepElement(0, -0.5, 0.005, 0.01)

    LSV.setMaxAbsoluteCurrent(0.1 * A)
    # Start off with open circuit element + GEIS
    experiment.appendElement(opencircuitElement, 1)
    experiment.appendElement(galvanostatiEISElement, 1)
    experiment.appendElement(LSV_smooth_scan_back, 1)
    # Then Do ECSA
    
    experiment.appendElement(CvElement_320, 5)
    experiment.appendElement(CvElement_160, 5)
    experiment.appendElement(CvElement_80, 5)
    experiment.appendElement(CvElement_40, 5)
    experiment.appendElement(CvElement_20, 5)

    # Then preconditioning at 50 mA/cm2 
    # hydrogen atmosphere
    experiment.appendElement(constantcurrentElement1mA_cm2, 1)
       
    # Getting fresh reaction path 
    experiment.appendElement(LSV, 1)

    # Then preconditioning at 100 mA/cm2 
    experiment.appendElement(constantcurrentElement100mA_cm2, 1)

    #Then GEIS at 100 mA/cm2
    experiment.appendElement(galvanostatiEISElement_100mA_cm2, 1)

    # Getting polarization path after CP 
    experiment.appendElement(LSV, 1)

    # Testing stability
    experiment.appendElement(CvElement_stability, 100)
    

    # Getting the polarisation path after Stability CV
    experiment.appendElement(LSV, 1)
    
    experiment.appendElement(LSV_smooth_scan_back, 1)
    # Then testing the ECSA after cycling 
    experiment.appendElement(CvElement_320, 5)
    experiment.appendElement(CvElement_160, 5)
    experiment.appendElement(CvElement_80, 5)
    experiment.appendElement(CvElement_40, 5)
    experiment.appendElement(CvElement_20, 5)
    return experiment , "testing_protocol_coated_wires_1"

def ML_testing_script():
    experiment = AisExperiment()
    # start frequency, end frequency, stepsPerDecade, currentBias, currentAmplitude
    # Seeing
    mA = 10**(-3)
    A = 0.975 # Area in cm2 
    time = 20 # How many minutes
    short_CP_time = 0.1*5

    opencircuitElement = AisOpenCircuitElement(4, 2)
    CvElement_20 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.02,0.1)
    CvElement_40 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.04,0.1)
    CvElement_80 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.08,0.01)
    CvElement_160 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.160,0.01)
    CvElement_320 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.320,0.01)
    
    galvanostatiEISElement = AisEISGalvanostaticElement(100000, 100, 7, -10 * mA * A, -1 * mA * A)
    constantcurrentElement1mA_cm2 = AisConstantCurrentElement(-1 * mA * A, 1, 60 * short_CP_time)
    CvElement_stability = AisCyclicVoltammetryElement(0,-0.3,0.3,0 ,0.05,0.01)

    LSV_smooth_scan_back = AisDCPotentialSweepElement(-0.3, 0.6, 0.5, 0.01)

    LSV = AisDCPotentialSweepElement(0, -0.5, 0.25, 0.001)

    LSV.setMaxAbsoluteCurrent(0.1 * A)
    # Start off with open circuit element + GEIS
    experiment.appendElement(opencircuitElement, 1)
    experiment.appendElement(galvanostatiEISElement, 1)
    experiment.appendElement(LSV_smooth_scan_back, 1)
    experiment.appendElement(CvElement_320, 2)
    experiment.appendElement(CvElement_160, 2)
    experiment.appendElement(CvElement_80, 2)
    experiment.appendElement(CvElement_40, 1)
    experiment.appendElement(CvElement_20, 1)

    experiment.appendElement(constantcurrentElement1mA_cm2, 1)
    4
    # Getting fresh reaction path 
    experiment.appendElement(LSV, 1)
    
   
    experiment.appendElement(CvElement_stability, 20)
    experiment.appendElement(LSV_smooth_scan_back, 1)
    experiment.appendElement(CvElement_320, 2)
    experiment.appendElement(CvElement_160, 2)
    experiment.appendElement(CvElement_80, 2)
    experiment.appendElement(CvElement_40, 1)
    experiment.appendElement(CvElement_20, 1)
    return experiment , "ML_testing_script"

def OCV_experiment(time):
    experiment = AisExperiment()
    LSV = AisDCPotentialSweepElement(0, -0.5, 0.02, 0.01)
    LSV.setMaxAbsoluteCurrent(-0.2)
    opencircuitElement = AisOpenCircuitElement(time, 2)
    experiment.appendElement(opencircuitElement, 1)
    experiment.appendElement(LSV, 1)
    experiment.appendElement(opencircuitElement, 1)
    return experiment, "OCV"

def deposition_experiment(deposition_time_s, deposition_current_density_mA_cm2):
    A = 0.975 # The area of the electrode
    calc_deposition_current_density_mA_cm2 = -deposition_current_density_mA_cm2 / 1000 * A
    experiment = AisExperiment()
    opencircuitElement = AisOpenCircuitElement(10, 2)
    constantcurrentElement_mA_cm2 = AisConstantCurrentElement(calc_deposition_current_density_mA_cm2, 1, deposition_time_s)
    experiment.appendElement(opencircuitElement, 1)
    experiment.appendElement(constantcurrentElement_mA_cm2, 1)
    return experiment

def second_protocol():
    experiment = AisExperiment()
    # start frequency, end frequency, stepsPerDecade, currentBias, currentAmplitude
    # Seeing
    mA = 10**(-3)
    A = 0.975 # Area in cm2 
    time = 10 # How many minutes
    opencircuitElement = AisOpenCircuitElement(300, 2)

    galvanostatiEISElement = AisEISGalvanostaticElement(100000, 1, 7, -10 * mA * A, -1 * mA * A)

    constantcurrentElement1mA_cm2 = AisConstantCurrentElement(-1 * mA * A, 1, 60 * time)
    constantcurrentElement2mA_cm2 = AisConstantCurrentElement(-2 * mA * A, 1, 60 * time)
    constantcurrentElement5mA_cm2 = AisConstantCurrentElement(-5 * mA * A, 1, 60 * time)
    constantcurrentElement10mA_cm2 = AisConstantCurrentElement(-10 * mA * A, 1, 60 * time)
    constantcurrentElement20mA_cm2 = AisConstantCurrentElement(-20 * mA * A, 1, 60 * time)
    constantcurrentElement50mA_cm2 = AisConstantCurrentElement(-50 * mA * A, 1, 60 * time)

    CvElement_stability = AisCyclicVoltammetryElement(0,-0.3,0.7,0 ,0.05,0.01)

    CvElement_20 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.02,0.1).setApproxMaxCurrent(0.05)
    CvElement_40 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.04,0.1).setApproxMaxCurrent(0.05)
    CvElement_80 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.08,0.01).setApproxMaxCurrent(0.05)
    CvElement_160 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.160,0.01).setApproxMaxCurrent(0.05)
    CvElement_320 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.320,0.01).setApproxMaxCurrent(0.05)

    LSV = AisDCPotentialSweepElement(0, -0.5, 0.02, 0.01)

    # Start off with open circuit element + GEIS
    experiment.appendElement(opencircuitElement, 1)
    experiment.appendElement(galvanostatiEISElement, 1)

    # Then Do ECSA
    experiment.appendElement(CvElement_320, 5)
    experiment.appendElement(CvElement_160, 5)
    experiment.appendElement(CvElement_80, 5)
    experiment.appendElement(CvElement_40, 5)
    experiment.appendElement(CvElement_20, 5)

    # Then preconditioning at 50 mA/cm2 
    experiment.appendElement(constantcurrentElement50mA_cm2, 1)
    
    # Getting the ohmic resistance from EIS 
    experiment.appendElement(LSV, 1)

    # Then do CPs to gather activity 
    experiment.appendElement(constantcurrentElement20mA_cm2, 1)
    experiment.appendElement(constantcurrentElement10mA_cm2, 1)
    experiment.appendElement(constantcurrentElement5mA_cm2, 1)
    experiment.appendElement(constantcurrentElement2mA_cm2, 1)
    experiment.appendElement(constantcurrentElement1mA_cm2, 1)
    
    # Testing stability
    experiment.appendElement(CvElement_stability, 100)
    
    # Then testing the activity after cycling 
    experiment.appendElement(constantcurrentElement20mA_cm2, 1)
    experiment.appendElement(constantcurrentElement10mA_cm2, 1)
    experiment.appendElement(constantcurrentElement5mA_cm2, 1)
    experiment.appendElement(constantcurrentElement2mA_cm2, 1)
    experiment.appendElement(constantcurrentElement1mA_cm2, 1)

    # Then testing the ECSA after cycling 
    experiment.appendElement(CvElement_320, 5)
    experiment.appendElement(CvElement_160, 5)
    experiment.appendElement(CvElement_80, 5)
    experiment.appendElement(CvElement_40, 5)
    experiment.appendElement(CvElement_20, 5)
    return experiment, "second_protocol"

def third_protocol():
    experiment = AisExperiment()
    # start frequency, end frequency, stepsPerDecade, currentBias, currentAmplitude
    # Seeing
    mA = 10**(-3)
    A = 1.07 # Area in cm2 
    time = 20 # How many minutes
    opencircuitElement = AisOpenCircuitElement(10, 2)

    galvanostatiEISElement = AisEISGalvanostaticElement(1000000, 1, 10, -10 * mA * A, -1 * mA * A)

    constantcurrentElement50mA_cm2 = AisConstantCurrentElement(-50 * mA * A, 1, 60 * time)

    galvanostatiEISElement1mA_cm2  = AisEISGalvanostaticElement(1000000, 1, 10, -1 * mA * A, -1/10 * mA * A)
    galvanostatiEISElement2mA_cm2  = AisEISGalvanostaticElement(1000000, 1, 10, -2 * mA * A, -2/10 * mA * A)
    galvanostatiEISElement5mA_cm2  = AisEISGalvanostaticElement(1000000, 1, 10, -5 * mA * A, -5/10 * mA * A)
    galvanostatiEISElement10mA_cm2 = AisEISGalvanostaticElement(1000000, 1, 10, -10 * mA * A, -10/10 * mA * A)
    galvanostatiEISElement20mA_cm2 = AisEISGalvanostaticElement(1000000, 1, 10, -20 * mA * A, -20/10 * mA * A)

    CvElement_stability = AisCyclicVoltammetryElement(0,-0.3,0.7,0 ,0.05,0.01)

    CvElement_20 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.02,0.1).setApproxMaxCurrent(0.05)
    CvElement_40 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.04,0.1).setApproxMaxCurrent(0.05)
    CvElement_80 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.08,0.01).setApproxMaxCurrent(0.05)
    CvElement_160 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.160,0.01).setApproxMaxCurrent(0.05)
    CvElement_320 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.320,0.01) .setApproxMaxCurrent(0.05)

    LSV = AisDCPotentialSweepElement(0, -0.5, 0.005, 0.01)

    # Start off with open circuit element + GEIS
    experiment.appendElement(opencircuitElement, 1)
    experiment.appendElement(galvanostatiEISElement, 1)

    # Then Do ECSA
    experiment.appendElement(CvElement_320, 5)
    experiment.appendElement(CvElement_160, 5)
    experiment.appendElement(CvElement_80, 5)
    experiment.appendElement(CvElement_40, 5)
    experiment.appendElement(CvElement_20, 5)

    # Then preconditioning at 50 mA/cm2 
    experiment.appendElement(constantcurrentElement50mA_cm2, 1)
    
    # Getting the ohmic resistance from EIS 
    experiment.appendElement(LSV, 1)

    # Then do CPs to gather activity 
    experiment.appendElement(galvanostatiEISElement20mA_cm2, 1)
    experiment.appendElement(galvanostatiEISElement10mA_cm2, 1)
    experiment.appendElement(galvanostatiEISElement5mA_cm2, 1)
    experiment.appendElement(galvanostatiEISElement2mA_cm2, 1)
    experiment.appendElement(galvanostatiEISElement1mA_cm2, 1)
    
    # Testing stability
    experiment.appendElement(CvElement_stability, 100)
    
    # Then testing the activity after cycling 
    experiment.appendElement(galvanostatiEISElement20mA_cm2, 1)
    experiment.appendElement(galvanostatiEISElement10mA_cm2, 1)
    experiment.appendElement(galvanostatiEISElement5mA_cm2, 1)
    experiment.appendElement(galvanostatiEISElement2mA_cm2, 1)
    experiment.appendElement(galvanostatiEISElement1mA_cm2, 1)

    # Then testing the ECSA after cycling 
    experiment.appendElement(CvElement_320, 5)
    experiment.appendElement(CvElement_160, 5)
    experiment.appendElement(CvElement_80, 5)
    experiment.appendElement(CvElement_40, 5)
    experiment.appendElement(CvElement_20, 5)
    return experiment, "third protocol"





def third_protocol_rune():
    experiment = AisExperiment()
    # start frequency, end frequency, stepsPerDecade, currentBias, currentAmplitude
    # Seeing
    mA = 10**(-3)
    A = 1.07 # Area in cm2 
    time = 30 # How many minutes
    opencircuitElement = AisOpenCircuitElement(10, 2)
    #iR correction
    galvanostatiEISElement = AisEISGalvanostaticElement(1000000, 1, 10, -1 * mA * A, -1 * mA * A)
    #ECSA
    CvElement_20 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.02,0.1)
    CvElement_40 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.04,0.1)
    CvElement_80 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.08,0.01)
    CvElement_160 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.160,0.01)
    CvElement_320 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.320,0.01) 
    #stability of overpotential
    constantcurrentElement50mA_cm2 = AisConstantCurrentElement(-50 * mA * A, 1, 60 * time)
    #tafel slope and overpotential
    LSV = AisDCPotentialSweepElement(0, -0.5, 0.005, 0.01)
    #resistance measure 
    galvanostatiEISElement1mA_cm2  = AisEISGalvanostaticElement(1000000, 1, 10, -1 * mA * A, -1/10 * mA * A)
    galvanostatiEISElement10mA_cm2 = AisEISGalvanostaticElement(1000000, 1, 10, -10 * mA * A, -10/10 * mA * A)
    #cyclic stability test
    CvElement_stability = AisCyclicVoltammetryElement(0,-0.3,0.7,0 ,0.05,0.01)
    
 

    # Start off with open circuit element + GEIS
    experiment.appendElement(opencircuitElement, 1)
    experiment.appendElement(galvanostatiEISElement, 1)

    # Then Do ECSA
    experiment.appendElement(CvElement_320, 5)
    experiment.appendElement(CvElement_160, 5)
    experiment.appendElement(CvElement_80, 5)
    experiment.appendElement(CvElement_40, 5)
    experiment.appendElement(CvElement_20, 5)

    # Then preconditioning at 50 mA/cm2 
    experiment.appendElement(constantcurrentElement50mA_cm2, 1)
    
    # Getting the ohmic resistance from EIS 
    experiment.appendElement(LSV, 1)

    # Then do CPs to gather activity 
    
    experiment.appendElement(galvanostatiEISElement10mA_cm2, 1)
    experiment.appendElement(galvanostatiEISElement1mA_cm2, 1)
    
    # Testing stability
    experiment.appendElement(CvElement_stability, 100)

    # Getting the ohmic resistance from EIS 
    experiment.appendElement(LSV, 1)
    

    # Then testing the ECSA after cycling 
    experiment.appendElement(CvElement_320, 5)
    experiment.appendElement(CvElement_160, 5)
    experiment.appendElement(CvElement_80, 5)
    experiment.appendElement(CvElement_40, 5)
    experiment.appendElement(CvElement_20, 5)
    return experiment






def PureCV():
    experiment = AisExperiment()
    # start frequency, end frequency, stepsPerDecade, currentBias, currentAmplitude
    # Seeing
    mA = 10**(-3)
    A = 1.07 # Area in cm2 
    time = 10 # How many minutes
    opencircuitElement = AisOpenCircuitElement(10, 2)
    #iR correction
    #cyclic stability test
    CvElement_stability = AisCyclicVoltammetryElement(0,-0.3,0.7,0 ,0.05,0.01)
    #stability of overpotential
    constantcurrentElement10mA_cm2 = AisConstantCurrentElement(-10 * mA * A, 1, 60 * time)
    # Start off with open circuit element + GEIS
    experiment.appendElement(opencircuitElement, 1)
    # Testing stability
    experiment.appendElement(CvElement_stability, 100)
    # Then preconditioning at 10 mA/cm2 
    experiment.appendElement(constantcurrentElement10mA_cm2, 1)
    # Testing stability
    experiment.appendElement(CvElement_stability, 100)
    return experiment






def PureCV_long():
    experiment = AisExperiment()
    # start frequency, end frequency, stepsPerDecade, currentBias, currentAmplitude
    # Seeing
    mA = 10**(-3)
    A = 1.07 # Area in cm2 
    time = 60 # How many minutes
    opencircuitElement = AisOpenCircuitElement(10, 2)
    #iR correction
    #cyclic stability test
    CvElement_stability = AisCyclicVoltammetryElement(0,-0.3,0.7,0 ,0.05,0.01)
    #stability of overpotential
    constantcurrentElement10mA_cm2 = AisConstantCurrentElement(-10 * mA * A, 1, 60 * time)
    # Start off with open circuit element + GEIS
    experiment.appendElement(opencircuitElement, 1)
    # Testing stability
    experiment.appendElement(CvElement_stability, 100)
    # Then preconditioning at 10 mA/cm2 
    experiment.appendElement(constantcurrentElement10mA_cm2, 1)
    # Testing stability
    experiment.appendElement(CvElement_stability, 100)
    return experiment

def PureCV_strong():
    experiment = AisExperiment()
    # start frequency, end frequency, stepsPerDecade, currentBias, currentAmplitude
    # Seeing
    mA = 10**(-3)
    A = 1.07 # Area in cm2 
    time = 10 # How many minutes
    opencircuitElement = AisOpenCircuitElement(10, 2)
    #iR correction
    #cyclic stability test
    CvElement_stability = AisCyclicVoltammetryElement(0,-0.3,0.7,0 ,0.05,0.01)
    #stability of overpotential
    constantcurrentElement10mA_cm2 = AisConstantCurrentElement(-100 * mA * A, 1, 60 * time)
    # Start off with open circuit element + GEIS
    experiment.appendElement(opencircuitElement, 1)
    # Testing stability
    experiment.appendElement(CvElement_stability, 100)
    # Then preconditioning at 10 mA/cm2 
    experiment.appendElement(constantcurrentElement10mA_cm2, 1)
    # Testing stability
    experiment.appendElement(CvElement_stability, 100)
    return experiment


def PureCV_strong_long():
    experiment = AisExperiment()
    # start frequency, end frequency, stepsPerDecade, currentBias, currentAmplitude
    # Seeing
    mA = 10**(-3)
    A = 1.07 # Area in cm2 
    time = 60 # How many minutes
    opencircuitElement = AisOpenCircuitElement(10, 2)
    #iR correction
    #cyclic stability test
    CvElement_stability = AisCyclicVoltammetryElement(0,-0.3,0.7,0 ,0.05,0.01)
    #stability of overpotential
    constantcurrentElement10mA_cm2 = AisConstantCurrentElement(-100 * mA * A, 1, 60 * time)
    # Start off with open circuit element + GEIS
    experiment.appendElement(opencircuitElement, 1)
    # Testing stability
    experiment.appendElement(CvElement_stability, 100)
    # Then preconditioning at 10 mA/cm2 
    experiment.appendElement(constantcurrentElement10mA_cm2, 1)
    # Testing stability
    experiment.appendElement(CvElement_stability, 100)
    return experiment

