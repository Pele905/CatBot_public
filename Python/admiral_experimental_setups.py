import sys
from PySide2.QtCore import QIODevice, QThread, QObject, Signal
from PySide2.QtSerialPort import QSerialPort
from PySide2.QtWidgets import QApplication
from SquidstatPyLibrary import (AisDeviceTracker, AisDCData, AisACData,
                                AisExperiment, AisInstrumentHandler,AisEISGalvanostaticElement, AisDCPotentialSweepElement,
                                AisConstantCurrentElement, AisOpenCircuitElement, AisCyclicVoltammetryElement)

import time
from datetime import datetime
# This is the code we will use to control the admiral instruments potentiostats
# The script includes running a deposition script and running a testing script 

# initialize the application
def convert_to_csv_line(data_list):
    return ','.join(str(item) for item in data_list) 

def set_step_name(name):
    global stepName
    stepName = name
    print(stepName)

class WriteCSV:
    # init filename and file
    def __init__(self, filename):
        self.filename = filename
        self.file = None

        # open file and write headers
    def write_header(self, header):
        if self.file is None:
            self.file = open(self.filename, 'w')
        self.file.write(convert_to_csv_line(header) + '\n')

    # write data to file
    def write_data(self, data):
        if self.file is not None:
            self.file.write(convert_to_csv_line(data) + '\n')

    # close file when we are done  
    def close(self):
        if self.file is not None:
            self.file.close()

class ExperimentManager:
    def __init__(self, total_channels):
        self.total_channels = total_channels
        self.running_channels = set()

    def start_experiment(self, channel):
        if channel not in self.running_channels and 0 <= channel < self.total_channels:
            self.running_channels.add(channel)
            return True
        return False  # Experiment already running or invalid channel

    def complete_experiment(self, channel):
        if channel in self.running_channels:
            self.running_channels.remove(channel)

    def is_experiment_running(self, channel):
        return channel in self.running_channels

    def get_running_channels(self):
        return list(self.running_channels)
    # class to handle the plot and write functionality

class PlottingThread(QThread):
    # define the signal.
    plotData = Signal(float, float, float, float)
    plotImpedance = Signal(float, float, float, float, float, float, float)
    stopToPlot = Signal(int)
    
# init self with values to be written
    def __init__(self, csv_writer, experiment_manager, app):
        super().__init__()
        self.timestamps = []
        self.voltages = []
        self.frequencies = []
        self.Re_Z = []
        self.Im_Z = []
        self.current = []
        self.scan_rates = []
        self.step_number = 0 # Refers to which step number in the experimental sequence
        self.csv_writer = csv_writer
        self.app = app
        self.experiment_manager = experiment_manager
        
    # setup data file with headers and connect the call back function on emitting of Qt signal.
    def run(self):
        self.csv_writer.write_header(['Step name', 'Step number','Timestamp', 'Working Electrode Voltage [V]','Current [A]', 'Frequency [Hz]',
                                    'Re_Z', 'Im_Z', "Absolute timestamp", "Scan rate"])
        self.plotData.connect(self.add_data)
        self.plotImpedance.connect(self.add_impedance_data)
        self.stopToPlot.connect(self.close)
        self.exec_()
    # add data into list as well as call back handler you can use to plot the data on graph. ( Currently we are not using any plot.)
    def add_data(self,timestamp, voltage, current, scan_rates = 0):
        current_time = datetime.now()
        current_time = current_time.strftime("%d_%m_%Y %H:%M:%S")
        self.timestamps.append(timestamp)
        self.voltages.append(voltage)
        self.current.append(current)
        self.scan_rates.append(scan_rates)
        self.csv_writer.write_data([self.step_name,self.step_number, timestamp, voltage, current, 0, 0, 0, current_time, scan_rates])
    
    def add_impedance_data(self, timestamp, frequency, voltage=0, current=0, Re_Z=0, Im_Z=0):
        current_time = datetime.now()
        current_time = current_time.strftime("%d_%m_%Y %H:%M:%S")
        self.Re_Z.append(Re_Z)
        self.Im_Z.append(Im_Z)
        self.voltages.append(voltage)
        self.csv_writer.write_data([self.step_name,self.step_number, timestamp, voltage, current, frequency, Re_Z, Im_Z, current_time, 0])
    def update_step_name(self, name):
        self.step_name = name
        self.step_number += 1
    # close writer for a channel
    def close(self, channel):
        self.csv_writer.close()
        self.experiment_manager.complete_experiment(channel)
        self.quit()
        self.wait()
        # Check if there are no running channels left
        if len(self.experiment_manager.get_running_channels()) == 0:
            self.app.quit() 
    def stop(self):
        self.quit()
        self.wait()

def run_CV_stability_wait_tests(filename = "",
                                COM_port = "COM9",
                                app = None, 
                                CV_wait_time = 30,
                                wait_at_cutoff = 65):
    '''
        Runs CV stability wait tests. Waits for CV_wait_time (in minutes), at a specific cutoff for the stability testing cycles
    '''
    if app == None:
        app = QApplication.instance() or QApplication([])
    # instantiate a device tracker
    tracker = AisDeviceTracker.Instance()
    print("This gets called now")
    csv_writer = WriteCSV(filename)

    # start thread
    experiment_manager = ExperimentManager(total_channels = 1)
    plottingThread = PlottingThread(csv_writer, app=app, experiment_manager=experiment_manager)
    # define thread to write with number of active channels

    plottingThread.start()
    # interact with data and send experiments to device
    def onNewDeviceConnected(deviceName):
        # print which device has been connected
        print(f"Connected to: {deviceName}")
        # get handler using device name.
        handler = tracker.getInstrumentHandler(deviceName)
        # if handler is present for the particular device then we can interact with the data and upload/start/stop/puase/resume experiments
        if handler:
            # setup file name
            handler.activeDCDataReady.connect(lambda channel, data: (
                print("timestamp:", "{:.9f}".format(data.timestamp), "workingElectrodeVoltage: ",
                    "{:.9f}".format(data.workingElectrodeVoltage), "Current: ",
                    "{:.9f}".format(data.current)), 
                plottingThread.plotData.emit(data.timestamp, data.workingElectrodeVoltage, data.current)
            ))

            handler.activeACDataReady.connect(lambda channel, data: (
                print("frequency:", "{:.9f}".format(data.frequency),
                    "absoluteImpedance: ", "{:.9f}".format(data.absoluteImpedance), 
                    "phaseAngle: ", "{:.9f}".format(data.phaseAngle)),
                
                plottingThread.plotImpedance.emit(data.timestamp, data.frequency, 0, 0, data.realImpedance, data.imagImpedance) # this is what we were missing 
                
            ))
            stepName = ""
            # Updates the step names for every single step in the channel 
            handler.experimentNewElementStarting.connect(lambda channel, data: plottingThread.update_step_name(data.stepName))
                                                                                                           
            handler.experimentStopped.connect(lambda channel: (
                print(f"Experiment completed on channel {channel}"),
                plottingThread.stopToPlot.emit(channel),
                
                cleanup()
            ))


            experiment = AisExperiment()
            # start frequency, end frequency, stepsPerDecade, currentBias, currentAmplitude
            # Seeing
            mA = 10**(-3)
            A = 1.07 # Area in cm2 
            time = 10 # How many minutes
            opencircuitElement = AisOpenCircuitElement(10, 2)
            waiting_open_circuit = AisOpenCircuitElement(CV_wait_time * 60, 30)

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
            experiment.appendElement(CvElement_stability, wait_at_cutoff)
            
            # Waits during experiment where we run an open circuit
            experiment.appendElement(waiting_open_circuit, 1)

            experiment.appendElement(CvElement_stability, int(100 - wait_at_cutoff))

            # upload experiment to channel 1
            error = handler.uploadExperimentToChannel(0, experiment)
            print("There is an error", error)
            if error != 0:
                print(error.message())

            # start experiment on channel 1
            error = handler.startUploadedExperiment(0)
            if error != 0:
                print(error.message())
        def cleanup():
            ''' Clean up connections and stop the plotting thread '''
            
            for device in tracker.getConnectedDevices():
                handler = tracker.getInstrumentHandler(device)
                if handler:
                    handler.activeDCDataReady.disconnect()
                    handler.activeACDataReady.disconnect()
                    handler.experimentNewElementStarting.disconnect()
                    handler.experimentStopped.disconnect()
    # connect to device associated with the tracker
    
    connected_devices = tracker.getConnectedDevices()
    if connected_devices:
        
        for device in connected_devices:
            handler = tracker.getInstrumentHandler(device)
            if handler:
                # Attempt to disconnect signal and slot
                tracker.disconnect(handler)
                #tracker.disconnect(handler.activeACDataReady)
    tracker.newDeviceConnected.connect(onNewDeviceConnected)
    
    # Request the device to connect using com port 4
    
    error = tracker.connectToDeviceOnComPort(COM_port)

    if error:
        print(error.message())

        if error.message() == "Squidstat is already connected.":
            onNewDeviceConnected("Plus2254")
            print("we are sure")
            print(error.message())
            print("Here we get the error")


    #print(dir(tracker.deviceDisconnected.disconnect(COM_port)))
    # exit program
    #sys.exit(app.exec_())
    app.exec_()
    return 
def run_deposition_experiment(current_density_mA = 10, 
                      deposition_time = 30, 
                      filename = "data123.csv",
                      COM_port = "COM9", 
                      app = None, 
                      ):
    '''
        Script for running a constant current experiment for electrodeposition. 
        The data is subsequently stored inside a file called filename
    '''
    #app = QApplication([])
    if app == None:
        app = QApplication.instance() or QApplication([])
    # instantiate a device tracker
    tracker = AisDeviceTracker.Instance()
    print("This gets called now")
    csv_writer = WriteCSV(filename)
# add csv file to plotting thread

    # start thread
    experiment_manager = ExperimentManager(total_channels = 1)
    plottingThread = PlottingThread(csv_writer, app=app, experiment_manager=experiment_manager)
    # define thread to write with number of active channels

    plottingThread.start()
    # interact with data and send experiments to device
    def onNewDeviceConnected(deviceName):
        # print which device has been connected
        print(f"Connected to: {deviceName}")
        # get handler using device name.
        handler = tracker.getInstrumentHandler(deviceName)
        # if handler is present for the particular device then we can interact with the data and upload/start/stop/puase/resume experiments
        if handler:
            # setup file name


            # manages DC data input and output
            # add more variables if you want to print more data to the console
            handler.activeDCDataReady.connect(lambda channel, data: (
                print("timestamp:", "{:.9f}".format(data.timestamp), "workingElectrodeVoltage: ",
                    "{:.9f}".format(data.workingElectrodeVoltage), "Current: ",
                    "{:.9f}".format(data.current)), 
                plottingThread.plotData.emit(data.timestamp, data.workingElectrodeVoltage, data.current)
            ))

            handler.activeACDataReady.connect(lambda channel, data: (
                print("frequency:", "{:.9f}".format(data.frequency),
                    "absoluteImpedance: ", "{:.9f}".format(data.absoluteImpedance), 
                    "phaseAngle: ", "{:.9f}".format(data.phaseAngle)),
                
            ))
            stepName = ""
            # Updates the step names for every single step in the channel 
            handler.experimentNewElementStarting.connect(lambda channel, data: plottingThread.update_step_name(data.stepName))
                                                                                                           
            handler.experimentStopped.connect(lambda channel: (
                print(f"Experiment completed on channel {channel}"),
                plottingThread.stopToPlot.emit(channel),
                cleanup()
            ))

            current = current_density_mA * 1.07 * 10 ** (-3)
            # initialize an experiment
            experiment = AisExperiment()

            # define a constant current, with 1 s sampling time, and a duration of deposition time
            constantcurrentElement = AisConstantCurrentElement(current, 1, deposition_time * 60)
            
            # define an open circuit experiment with a duration of 10 s and a sampling time of 2 s
            opencircuitElement = AisOpenCircuitElement(10, 2)
            
            # add constant current as the first element in the list
            #experiment.appendElement(constantcurrentElement, 1)
            # add open circuit as the second element in the list
            experiment.appendElement(opencircuitElement, 1)
            experiment.appendElement(constantcurrentElement, 1)
            # upload experiment to channel 1
            error = handler.uploadExperimentToChannel(0, experiment)
            print("There is an error", error)
            if error != 0:
                print(error.message())

            # start experiment on channel 1
            error = handler.startUploadedExperiment(0)
            if error != 0:
                print(error.message())
        def cleanup():
            ''' Clean up connections and stop the plotting thread '''
            
            for device in tracker.getConnectedDevices():
                handler = tracker.getInstrumentHandler(device)
                if handler:
                    handler.activeDCDataReady.disconnect()
                    handler.activeACDataReady.disconnect()
                    handler.experimentNewElementStarting.disconnect()
                    handler.experimentStopped.disconnect()
    # connect to device associated with the tracker
    
    connected_devices = tracker.getConnectedDevices()
    if connected_devices:
        
        for device in connected_devices:
            handler = tracker.getInstrumentHandler(device)
            if handler:
                # Attempt to disconnect signal and slot
                tracker.disconnect(handler)
                #tracker.disconnect(handler.activeACDataReady)
    tracker.newDeviceConnected.connect(onNewDeviceConnected)
    
    # Request the device to connect using com port 4
    
    error = tracker.connectToDeviceOnComPort(COM_port)

    if error:
        print(error.message())

        if error.message() == "Squidstat is already connected.":
            onNewDeviceConnected("Plus2254")
            print("we are sure")
            print(error.message())
            print("Here we get the error")


    #print(dir(tracker.deviceDisconnected.disconnect(COM_port)))
    # exit program
    #sys.exit(app.exec_())
    app.exec_()
   
    #tracker.disconnectFromDeviceOnComPort(COM_port)

def run_specified_experiment(filename = "data123.csv",
                        COM_port = "COM9", 
                        app = None, 
                        experiment = None, 
                        squidstat_name = "Plus2254", 
                        channel = 0):
    if app == None:
        app = QApplication.instance() or QApplication([])

    # instantiate a device tracker
    tracker = AisDeviceTracker.Instance()
    print("This gets called now")
    csv_writer = WriteCSV(filename)
# add csv file to plotting thread

    # start thread
    experiment_manager = ExperimentManager(total_channels = 1)
    plottingThread = PlottingThread(csv_writer, app=app, experiment_manager=experiment_manager)
    # define thread to write with number of active channels

    plottingThread.start()
    # interact with data and send experiments to device
    def onNewDeviceConnected(deviceName):
        # print which device has been connected
        print(f"Connected to: {deviceName}")
        # get handler using device name.
        handler = tracker.getInstrumentHandler(deviceName)
        # if handler is present for the particular device then we can interact with the data and upload/start/stop/puase/resume experiments
        if handler:
            # setup file name

            # manages DC data input and output
            # add more variables if you want to print more data to the console
            handler.activeDCDataReady.connect(lambda channel, data: (
                #print("timestamp:", "{:.9f}".format(data.timestamp), "workingElectrodeVoltage: ",
                #    "{:.9f}".format(data.workingElectrodeVoltage), "Current: ",
                #    "{:.9f}".format(data.current)), 
                plottingThread.plotData.emit(data.timestamp, data.workingElectrodeVoltage, data.current, 0)
            ))

            handler.activeACDataReady.connect(lambda channel, data: (
                print("frequency:", "{:.9f}".format(data.frequency),
                    "absoluteImpedance: ", "{:.9f}".format(data.absoluteImpedance), 
                    "phaseAngle: ", "{:.9f}".format(data.phaseAngle), 
                    "working electrode voltage: ", "{:.9f}".format(data.workingElectrodeDCVoltage)),
                    
                
                plottingThread.plotImpedance.emit(data.timestamp, data.frequency, 0, 0, data.realImpedance, data.imagImpedance, data.workingElectrodeDCVoltage) # this is what we were missing 
                
            ))
            stepName = ""
            # Updates the step names for every single step in the channel 
            handler.experimentNewElementStarting.connect(lambda channel, data: plottingThread.update_step_name(data.stepName))
                                                                                                           
            handler.experimentStopped.connect(lambda channel: (
                print(f"Experiment completed on channel {channel}"),
                plottingThread.stopToPlot.emit(channel),
                
                cleanup()
            ))

            # upload experiment to channel 1
            error = handler.uploadExperimentToChannel(channel, experiment)
            print("There is an error", error)
            if error != 0:
                print(error.message())

            # start experiment on channel 1
            error = handler.startUploadedExperiment(channel)
            if error != 0:
                print(error.message())
        def cleanup():
            ''' Clean up connections and stop the plotting thread '''
            
            for device in tracker.getConnectedDevices():
                handler = tracker.getInstrumentHandler(device)
                if handler:
                    handler.activeDCDataReady.disconnect()
                    handler.activeACDataReady.disconnect()
                    handler.experimentNewElementStarting.disconnect()
                    handler.experimentStopped.disconnect()
    # connect to device associated with the tracker
    
    connected_devices = tracker.getConnectedDevices()
    if connected_devices:
        
        for device in connected_devices:
            handler = tracker.getInstrumentHandler(device)
            if handler:
                # Attempt to disconnect signal and slot
                tracker.disconnect(handler)
                #tracker.disconnect(handler.activeACDataReady)
    tracker.newDeviceConnected.connect(onNewDeviceConnected)
    
    # Request the device to connect using com port 4
    
    error = tracker.connectToDeviceOnComPort(COM_port)

    if error:
        print(error.message())

        if error.message() == "Squidstat is already connected.":
            onNewDeviceConnected(squidstat_name)
            print("we are sure")
            print(error.message())
            print("Here we get the error")


    #print(dir(tracker.deviceDisconnected.disconnect(COM_port)))
    # exit program
    #sys.exit(app.exec_())
    app.exec_()
   
    #tracker.disconnectFromDeviceOnComPort(COM_port)
    return 
def run_testing_protocol_coated_wires(filename = "data123.csv",
                      COM_port = "COM9", 
                      app = None):
    '''
        Script for running a constant current experiment for electrodeposition. 
        The data is subsequently stored inside a file called filename

        This is the old protocol run from prior to 6th September. What we learned is that higher current densities leads
        to unstable equillibriums in our dataset
    '''
    #app = QApplication([])
    if app == None:
        app = QApplication.instance() or QApplication([])
    # instantiate a device tracker
    tracker = AisDeviceTracker.Instance()
    print("This gets called now")
    csv_writer = WriteCSV(filename)
# add csv file to plotting thread

    # start thread
    experiment_manager = ExperimentManager(total_channels = 1)
    plottingThread = PlottingThread(csv_writer, app=app, experiment_manager=experiment_manager)
    # define thread to write with number of active channels

    plottingThread.start()
    # interact with data and send experiments to device
    def onNewDeviceConnected(deviceName):
        # print which device has been connected
        print(f"Connected to: {deviceName}")
        # get handler using device name.
        handler = tracker.getInstrumentHandler(deviceName)
        # if handler is present for the particular device then we can interact with the data and upload/start/stop/puase/resume experiments
        if handler:
            # setup file name


            # manages DC data input and output
            # add more variables if you want to print more data to the console
            handler.activeDCDataReady.connect(lambda channel, data: (
                print("timestamp:", "{:.9f}".format(data.timestamp), "workingElectrodeVoltage: ",
                    "{:.9f}".format(data.workingElectrodeVoltage), "Current: ",
                    "{:.9f}".format(data.current)), 
                plottingThread.plotData.emit(data.timestamp, data.workingElectrodeVoltage, data.current)
            ))

            handler.activeACDataReady.connect(lambda channel, data: (
                print("frequency:", "{:.9f}".format(data.frequency),
                    "absoluteImpedance: ", "{:.9f}".format(data.absoluteImpedance), 
                    "phaseAngle: ", "{:.9f}".format(data.phaseAngle)),
                
                plottingThread.plotImpedance.emit(data.timestamp, data.frequency, 0, 0, data.realImpedance, data.imagImpedance) # this is what we were missing 
                
            ))
            stepName = ""
            # Updates the step names for every single step in the channel 
            handler.experimentNewElementStarting.connect(lambda channel, data: plottingThread.update_step_name(data.stepName))
                                                                                                           
            handler.experimentStopped.connect(lambda channel: (
                print(f"Experiment completed on channel {channel}"),
                plottingThread.stopToPlot.emit(channel),
                
                cleanup()
            ))


            experiment = AisExperiment()
            # start frequency, end frequency, stepsPerDecade, currentBias, currentAmplitude
            # Seeing
            mA = 10**(-3)
            A = 1.07 # Area in cm2 
            time = 5 # How many minutes
            opencircuitElement = AisOpenCircuitElement(10, 2)


            galvanostatiEISElement = AisEISGalvanostaticElement(100000, 1, 7, -10 * mA * A, -1 * mA * A)
            constantcurrentElement10mA_cm2 = AisConstantCurrentElement(-10 * mA * A, 1, 60 * time)
            constantcurrentElement20mA_cm2 = AisConstantCurrentElement(-20 * mA * A, 1, 60 * time)
            constantcurrentElement50mA_cm2 = AisConstantCurrentElement(-50 * mA * A, 1, 60 * time)
            constantcurrentElement100mA_cm2 = AisConstantCurrentElement(-100 * mA * A, 1, 60 * time)
            LSV = AisDCPotentialSweepElement(0, -0.3, 0.02, 0.01)


            experiment.appendElement(opencircuitElement, 1)
            experiment.appendElement(galvanostatiEISElement, 1)


            
            #experiment.appendElement(galvanostatiEISElement, 1)
            # Testing the ECSA
            # startPotential, firstVoltageLimit, secondVoltageLimit, endVoltage, scanRate, samplingInterval
            CvElement_20 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.02,0.1)
            CvElement_40 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.04,0.1)
            CvElement_80 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.08,0.01)
            CvElement_160 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.160,0.01)
            CvElement_320 = AisCyclicVoltammetryElement(0.6,0.9,0.6,0.6,0.320,0.01) 

            CV_element_1000 = AisCyclicVoltammetryElement(0,-0.3,0.7,0 ,1,0.01)
            CV_element_500 = AisCyclicVoltammetryElement(0,-0.3,0.7,0 ,0.5,0.01)
            CV_element_250 = AisCyclicVoltammetryElement(0,-0.3,0.7,0 ,0.25,0.01)
            CV_element_125 = AisCyclicVoltammetryElement(0,-0.3,0.7,0 ,0.125,0.01)
            CV_element_50 = AisCyclicVoltammetryElement(0,-0.3,0.7,0 ,0.05,0.01)
            # Testing the stability with scanning at 0.05 mV/s
            CvElement_stability = AisCyclicVoltammetryElement(0,-0.3,0.7,0 ,0.05,0.01)

            # Getting the ohmic resistance from EIS 


            # Testing the performance for HER at different current densities
            #experiment.appendElement(constantcurrentElement10mA_cm2, 1)
            #experiment.appendElement(constantcurrentElement50mA_cm2, 1)
            experiment.appendElement(constantcurrentElement100mA_cm2, 1)

            experiment.appendElement(LSV, 1)
            experiment.appendElement(constantcurrentElement100mA_cm2, 1)
            experiment.appendElement(constantcurrentElement50mA_cm2, 1)
            experiment.appendElement(constantcurrentElement20mA_cm2, 1)
            experiment.appendElement(constantcurrentElement10mA_cm2, 1)

            # ECSA before experiment
            experiment.appendElement(CvElement_320, 5)
            experiment.appendElement(CvElement_160, 5)
            experiment.appendElement(CvElement_80, 5)
            experiment.appendElement(CvElement_40, 5)
            experiment.appendElement(CvElement_20, 5)
            
            # Testing stability
            experiment.appendElement(CvElement_stability, 100)
            
            experiment.appendElement(CvElement_320, 5)
            experiment.appendElement(CvElement_160, 5)
            experiment.appendElement(CvElement_80, 5)
            experiment.appendElement(CvElement_40, 5)
            experiment.appendElement(CvElement_20, 5)
            
            experiment.appendElement(constantcurrentElement100mA_cm2, 1)

            experiment.appendElement(LSV, 1)
            experiment.appendElement(constantcurrentElement100mA_cm2, 1)
            experiment.appendElement(constantcurrentElement50mA_cm2, 1)
            experiment.appendElement(constantcurrentElement20mA_cm2, 1)
            experiment.appendElement(constantcurrentElement10mA_cm2, 1)

            # These ones we add to see if there is any drift in the Nicke electrode after cycling
            experiment.appendElement(CV_element_1000, 3)
            experiment.appendElement(CV_element_500, 3)
            experiment.appendElement(CV_element_250, 3)
            experiment.appendElement(CV_element_125, 3)
            experiment.appendElement(CV_element_50, 3)

            # upload experiment to channel 1
            error = handler.uploadExperimentToChannel(0, experiment)
            print("There is an error", error)
            if error != 0:
                print(error.message())

            # start experiment on channel 1
            error = handler.startUploadedExperiment(0)
            if error != 0:
                print(error.message())
        def cleanup():
            ''' Clean up connections and stop the plotting thread '''
            
            for device in tracker.getConnectedDevices():
                handler = tracker.getInstrumentHandler(device)
                if handler:
                    handler.activeDCDataReady.disconnect()
                    handler.activeACDataReady.disconnect()
                    handler.experimentNewElementStarting.disconnect()
                    handler.experimentStopped.disconnect()
    # connect to device associated with the tracker
    
    connected_devices = tracker.getConnectedDevices()
    if connected_devices:
        
        for device in connected_devices:
            handler = tracker.getInstrumentHandler(device)
            if handler:
                # Attempt to disconnect signal and slot
                tracker.disconnect(handler)
                #tracker.disconnect(handler.activeACDataReady)
    tracker.newDeviceConnected.connect(onNewDeviceConnected)
    
    # Request the device to connect using com port 4
    
    error = tracker.connectToDeviceOnComPort(COM_port)

    if error:
        print(error.message())

        if error.message() == "Squidstat is already connected.":
            onNewDeviceConnected("Plus2254")
            print("we are sure")
            print(error.message())
            print("Here we get the error")


    #print(dir(tracker.deviceDisconnected.disconnect(COM_port)))
    # exit program
    #sys.exit(app.exec_())
    app.exec_()
   
    #tracker.disconnectFromDeviceOnComPort(COM_port)

def run_new_testing_protocol(filename = "data123.csv",
                      COM_port = "COM9", 
                      app = None):
    '''
        Script for running a constant current experiment for electrodeposition. 
        The data is subsequently stored inside a file called filename
    '''
    #app = QApplication([])
    if app == None:
        app = QApplication.instance() or QApplication([])
    # instantiate a device tracker
    tracker = AisDeviceTracker.Instance()
    print("This gets called now")
    csv_writer = WriteCSV(filename)
# add csv file to plotting thread

    # start thread
    experiment_manager = ExperimentManager(total_channels = 1)
    plottingThread = PlottingThread(csv_writer, app=app, experiment_manager=experiment_manager)
    # define thread to write with number of active channels

    plottingThread.start()
    # interact with data and send experiments to device
    def onNewDeviceConnected(deviceName):
        # print which device has been connected
        print(f"Connected to: {deviceName}")
        # get handler using device name.
        handler = tracker.getInstrumentHandler(deviceName)
        # if handler is present for the particular device then we can interact with the data and upload/start/stop/puase/resume experiments
        if handler:
            # setup file name


            # manages DC data input and output
            # add more variables if you want to print more data to the console
            handler.activeDCDataReady.connect(lambda channel, data: (
                print("timestamp:", "{:.9f}".format(data.timestamp), "workingElectrodeVoltage: ",
                    "{:.9f}".format(data.workingElectrodeVoltage), "Current: ",
                    "{:.9f}".format(data.current)), 
                plottingThread.plotData.emit(data.timestamp, data.workingElectrodeVoltage, data.current)
            ))

            handler.activeACDataReady.connect(lambda channel, data: (
                print("frequency:", "{:.9f}".format(data.frequency),
                    "absoluteImpedance: ", "{:.9f}".format(data.absoluteImpedance), 
                    "phaseAngle: ", "{:.9f}".format(data.phaseAngle)),
                
                plottingThread.plotImpedance.emit(data.timestamp, data.frequency, 0, 0, data.realImpedance, data.imagImpedance) # this is what we were missing 
                
            ))
            stepName = ""
            # Updates the step names for every single step in the channel 
            handler.experimentNewElementStarting.connect(lambda channel, data: plottingThread.update_step_name(data.stepName))
                                                                                                           
            handler.experimentStopped.connect(lambda channel: (
                print(f"Experiment completed on channel {channel}"),
                plottingThread.stopToPlot.emit(channel),
                
                cleanup()
            ))


            experiment = AisExperiment()
            # start frequency, end frequency, stepsPerDecade, currentBias, currentAmplitude
            # Seeing
            mA = 10**(-3)
            A = 1.07 # Area in cm2 
            time = 10 # How many minutes
            opencircuitElement = AisOpenCircuitElement(10, 2)

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
        

            # upload experiment to channel 1
            error = handler.uploadExperimentToChannel(0, experiment)
            print("There is an error", error)
            if error != 0:
                print(error.message())

            # start experiment on channel 1
            error = handler.startUploadedExperiment(0)
            if error != 0:
                print(error.message())
        def cleanup():
            ''' Clean up connections and stop the plotting thread '''
            
            for device in tracker.getConnectedDevices():
                handler = tracker.getInstrumentHandler(device)
                if handler:
                    handler.activeDCDataReady.disconnect()
                    handler.activeACDataReady.disconnect()
                    handler.experimentNewElementStarting.disconnect()
                    handler.experimentStopped.disconnect()
    # connect to device associated with the tracker
    
    connected_devices = tracker.getConnectedDevices()
    if connected_devices:
        
        for device in connected_devices:
            handler = tracker.getInstrumentHandler(device)
            if handler:
                # Attempt to disconnect signal and slot
                tracker.disconnect(handler)
                #tracker.disconnect(handler.activeACDataReady)
    tracker.newDeviceConnected.connect(onNewDeviceConnected)
    
    # Request the device to connect using com port 4
    
    error = tracker.connectToDeviceOnComPort(COM_port)

    if error:
        print(error.message())

        if error.message() == "Squidstat is already connected.":
            onNewDeviceConnected("Plus2254")
            print("we are sure")
            print(error.message())
            print("Here we get the error")


    #print(dir(tracker.deviceDisconnected.disconnect(COM_port)))
    # exit program
    #sys.exit(app.exec_())
    app.exec_()
   
    #tracker.disconnectFromDeviceOnComPort(COM_port)

def run_testing_XPS_wire_stability(filename = "data123.csv",
                      COM_port = "COM9", 
                      app = None, 
                      stop_at_cycle=1):
    '''
        Script for running a constant current experiment for electrodeposition. 
        The data is subsequently stored inside a file called filename
    '''
    #app = QApplication([])
    if app == None:
        app = QApplication.instance() or QApplication([])
    # instantiate a device tracker
    tracker = AisDeviceTracker.Instance()
    print("This gets called now")
    csv_writer = WriteCSV(filename)
# add csv file to plotting thread

    # start thread
    experiment_manager = ExperimentManager(total_channels = 1)
    plottingThread = PlottingThread(csv_writer, app=app, experiment_manager=experiment_manager)
    # define thread to write with number of active channels

    plottingThread.start()
    # interact with data and send experiments to device
    def onNewDeviceConnected(deviceName):
        # print which device has been connected
        print(f"Connected to: {deviceName}")
        # get handler using device name.
        handler = tracker.getInstrumentHandler(deviceName)
        # if handler is present for the particular device then we can interact with the data and upload/start/stop/puase/resume experiments
        if handler:
            # setup file name


            # manages DC data input and output
            # add more variables if you want to print more data to the console
            handler.activeDCDataReady.connect(lambda channel, data: (
                print("timestamp:", "{:.9f}".format(data.timestamp), "workingElectrodeVoltage: ",
                    "{:.9f}".format(data.workingElectrodeVoltage), "Current: ",
                    "{:.9f}".format(data.current)), 
                plottingThread.plotData.emit(data.timestamp, data.workingElectrodeVoltage, data.current)
            ))

            handler.activeACDataReady.connect(lambda channel, data: (
                print("frequency:", "{:.9f}".format(data.frequency),
                    "absoluteImpedance: ", "{:.9f}".format(data.absoluteImpedance), 
                    "phaseAngle: ", "{:.9f}".format(data.phaseAngle)),
                
                plottingThread.plotImpedance.emit(data.timestamp, data.frequency, 0, 0, data.realImpedance, data.imagImpedance) # this is what we were missing 
                
            ))
            stepName = ""
            # Updates the step names for every single step in the channel 
            handler.experimentNewElementStarting.connect(lambda channel, data: plottingThread.update_step_name(data.stepName))
                                                                                                           
            handler.experimentStopped.connect(lambda channel: (
                print(f"Experiment completed on channel {channel}"),
                plottingThread.stopToPlot.emit(channel),
                
                cleanup()
            ))

            experiment = AisExperiment()
            # start frequency, end frequency, stepsPerDecade, currentBias, currentAmplitude
            # Seeing
            mA = 10**(-3)
            A = 1.07 # Area in cm2 
            time = 10 # How many minutes
            opencircuitElement = AisOpenCircuitElement(10, 2)

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

            # Then Do ECSA
            experiment.appendElement(CvElement_320, 5)
            experiment.appendElement(CvElement_160, 5)
            experiment.appendElement(CvElement_80, 5)
            experiment.appendElement(CvElement_40, 5)
            experiment.appendElement(CvElement_20, 5)

            # Then preconditioning at 50 mA/cm2 
            experiment.appendElement(constantcurrentElement50mA_cm2, 1)
            

            experiment.appendElement(LSV, 1)

            # Then do CPs to gather activity 
            experiment.appendElement(constantcurrentElement20mA_cm2, 1)
            experiment.appendElement(constantcurrentElement10mA_cm2, 1)
            experiment.appendElement(constantcurrentElement5mA_cm2, 1)
            experiment.appendElement(constantcurrentElement2mA_cm2, 1)
            experiment.appendElement(constantcurrentElement1mA_cm2, 1)
            
            # Testing stability
            experiment.appendElement(CvElement_stability, stop_at_cycle)
            
            # upload experiment to channel 1
            error = handler.uploadExperimentToChannel(0, experiment)
            print("There is an error", error)
            if error != 0:
                print(error.message())

            # start experiment on channel 1
            error = handler.startUploadedExperiment(0)
            if error != 0:
                print(error.message())
        def cleanup():
            ''' Clean up connections and stop the plotting thread '''
            
            for device in tracker.getConnectedDevices():
                handler = tracker.getInstrumentHandler(device)
                if handler:
                    handler.activeDCDataReady.disconnect()
                    handler.activeACDataReady.disconnect()
                    handler.experimentNewElementStarting.disconnect()
                    handler.experimentStopped.disconnect()
    # connect to device associated with the tracker
    
    connected_devices = tracker.getConnectedDevices()
    if connected_devices:
        
        for device in connected_devices:
            handler = tracker.getInstrumentHandler(device)
            if handler:
                # Attempt to disconnect signal and slot
                tracker.disconnect(handler)
                #tracker.disconnect(handler.activeACDataReady)
    tracker.newDeviceConnected.connect(onNewDeviceConnected)
    
    # Request the device to connect using com port 4
    
    error = tracker.connectToDeviceOnComPort(COM_port)

    if error:
        print(error.message())

        if error.message() == "Squidstat is already connected.":
            onNewDeviceConnected("Plus2254")
            print("we are sure")
            print(error.message())
            print("Here we get the error")


    #print(dir(tracker.deviceDisconnected.disconnect(COM_port)))
    # exit program
    #sys.exit(app.exec_())
    app.exec_()
   
    #tracker.disconnectFromDeviceOnComPort(COM_port)

def run_GEIS(filename = "data123.csv",
                      COM_port = "COM9", 
                      app = None,
                      current = 10,
                      ):
    '''
        Script for performing EIS using 
    '''
    #app = QApplication([])
    if app == None:
        app = QApplication.instance() or QApplication([])
    # instantiate a device tracker
    tracker = AisDeviceTracker.Instance()
    print("This gets called now")
    csv_writer = WriteCSV(filename)
# add csv file to plotting thread

    # start thread
    experiment_manager = ExperimentManager(total_channels = 1)
    plottingThread = PlottingThread(csv_writer, app=app, experiment_manager=experiment_manager)
    # define thread to write with number of active channels

    plottingThread.start()
    # interact with data and send experiments to device
    def onNewDeviceConnected(deviceName):
        # print which device has been connected
        print(f"Connected to: {deviceName}")
        # get handler using device name.
        handler = tracker.getInstrumentHandler(deviceName)
        # if handler is present for the particular device then we can interact with the data and upload/start/stop/puase/resume experiments
        if handler:
            # setup file name


            # manages DC data input and output
            # add more variables if you want to print more data to the console
            handler.activeDCDataReady.connect(lambda channel, data: (
                print("timestamp:", "{:.9f}".format(data.timestamp), "workingElectrodeVoltage: ",
                    "{:.9f}".format(data.workingElectrodeVoltage), "Current: ",
                    "{:.9f}".format(data.current)), 
                plottingThread.plotData.emit(data.timestamp, data.workingElectrodeVoltage, data.current)
            ))

            handler.activeACDataReady.connect(lambda channel, data: (
                print("frequency:", "{:.9f}".format(data.frequency),
                    "absoluteImpedance: ", "{:.9f}".format(data.absoluteImpedance), 
                    "phaseAngle: ", "{:.9f}".format(data.phaseAngle)),
                
                plottingThread.plotImpedance.emit(data.timestamp, data.frequency, 0, 0, data.realImpedance, data.imagImpedance) # this is what we were missing 
                
            ))
            stepName = ""
            # Updates the step names for every single step in the channel 
            handler.experimentNewElementStarting.connect(lambda channel, data: plottingThread.update_step_name(data.stepName))
                                                                                                           
            handler.experimentStopped.connect(lambda channel: (
                print(f"Experiment completed on channel {channel}"),
                plottingThread.stopToPlot.emit(channel),
                
                cleanup()
            ))


            experiment = AisExperiment()
            # start frequency, end frequency, stepsPerDecade, currentBias, currentAmplitude
            # Seeing
            mA = 10**(-3)
            A = 1.07 # Area in cm2 
            opencircuitElement = AisOpenCircuitElement(10, 2)

            galvanostatiEISElement = AisEISGalvanostaticElement(100000, 1, 7, -current * mA * A, 1 * current * mA * A)
            experiment.appendElement(opencircuitElement, 1)
            experiment.appendElement(galvanostatiEISElement, 1)
            # upload experiment to channel 1
            error = handler.uploadExperimentToChannel(0, experiment)
            print("There is an error", error)
            if error != 0:
                print(error.message())

            # start experiment on channel 1
            error = handler.startUploadedExperiment(0)
            if error != 0:
                print(error.message())
        def cleanup():
            ''' Clean up connections and stop the plotting thread '''
            
            for device in tracker.getConnectedDevices():
                handler = tracker.getInstrumentHandler(device)
                if handler:
                    handler.activeDCDataReady.disconnect()
                    handler.activeACDataReady.disconnect()
                    handler.experimentNewElementStarting.disconnect()
                    handler.experimentStopped.disconnect()
    # connect to device associated with the tracker
    
    connected_devices = tracker.getConnectedDevices()
    if connected_devices:
        
        for device in connected_devices:
            handler = tracker.getInstrumentHandler(device)
            if handler:
                # Attempt to disconnect signal and slot
                tracker.disconnect(handler)
                #tracker.disconnect(handler.activeACDataReady)
    tracker.newDeviceConnected.connect(onNewDeviceConnected)
    
    # Request the device to connect using com port 4
    
    error = tracker.connectToDeviceOnComPort(COM_port)

    if error:
        print(error.message())

        if error.message() == "Squidstat is already connected.":
            onNewDeviceConnected("Plus2254")
            print("we are sure")
            print(error.message())
            print("Here we get the error")


    #print(dir(tracker.deviceDisconnected.disconnect(COM_port)))
    # exit program
    #sys.exit(app.exec_())
    app.exec_()
   
    #tracker.disconnectFromDeviceOnComPort(COM_port)

def run_OCP(filename = "data123.csv",
            COM_port = "COM9", 
            app = None, time = 10):
    '''
        Script for running a constant current experiment for electrodeposition. 
        The data is subsequently stored inside a file called filename
    '''
    #app = QApplication([])
    if app == None:
        app = QApplication.instance() or QApplication([])
    # instantiate a device tracker
    tracker = AisDeviceTracker.Instance()
    print("This gets called now")
    csv_writer = WriteCSV(filename)
# add csv file to plotting thread

    # start thread
    experiment_manager = ExperimentManager(total_channels = 1)
    plottingThread = PlottingThread(csv_writer, app=app, experiment_manager=experiment_manager)
    # define thread to write with number of active channels

    plottingThread.start()
    # interact with data and send experiments to device
    def onNewDeviceConnected(deviceName):
        # print which device has been connected
        print(f"Connected to: {deviceName}")
        # get handler using device name.
        handler = tracker.getInstrumentHandler(deviceName)
        # if handler is present for the particular device then we can interact with the data and upload/start/stop/puase/resume experiments
        if handler:
            # setup file name


            # manages DC data input and output
            # add more variables if you want to print more data to the console
            handler.activeDCDataReady.connect(lambda channel, data: (
                print("timestamp:", "{:.9f}".format(data.timestamp), "workingElectrodeVoltage: ",
                    "{:.9f}".format(data.workingElectrodeVoltage), "Current: ",
                    "{:.9f}".format(data.current)), 
                plottingThread.plotData.emit(data.timestamp, data.workingElectrodeVoltage, data.current)
            ))

            handler.activeACDataReady.connect(lambda channel, data: (
                print("frequency:", "{:.9f}".format(data.frequency),
                    "absoluteImpedance: ", "{:.9f}".format(data.absoluteImpedance), 
                    "phaseAngle: ", "{:.9f}".format(data.phaseAngle)),
                print(dir(data))
            ))
            stepName = ""
            # Updates the step names for every single step in the channel 
            handler.experimentNewElementStarting.connect(lambda channel, data: plottingThread.update_step_name(data.stepName))
                                                                                                           
            handler.experimentStopped.connect(lambda channel: (
                print(f"Experiment completed on channel {channel}"),
                plottingThread.stopToPlot.emit(channel),
                cleanup()
            ))

            # initialize an experiment
            experiment = AisExperiment()

            opencircuitElement = AisOpenCircuitElement(time, 2)
            

            experiment.appendElement(opencircuitElement, 1)

            error = handler.uploadExperimentToChannel(0, experiment)
            print("There is an error", error)
            if error != 0:
                print(error.message())

            # start experiment on channel 1
            error = handler.startUploadedExperiment(0)
            if error != 0:
                print(error.message())
        def cleanup():
            ''' Clean up connections and stop the plotting thread '''
            
            for device in tracker.getConnectedDevices():
                handler = tracker.getInstrumentHandler(device)
                if handler:
                    handler.activeDCDataReady.disconnect()
                    handler.activeACDataReady.disconnect()
                    handler.experimentNewElementStarting.disconnect()
                    handler.experimentStopped.disconnect()
    # connect to device associated with the tracker
    
    connected_devices = tracker.getConnectedDevices()
    if connected_devices:
        
        for device in connected_devices:
            handler = tracker.getInstrumentHandler(device)
            if handler:
                # Attempt to disconnect signal and slot
                tracker.disconnect(handler)
                #tracker.disconnect(handler.activeACDataReady)
    tracker.newDeviceConnected.connect(onNewDeviceConnected)
    
    # Request the device to connect using com port 4
    
    error = tracker.connectToDeviceOnComPort(COM_port)

    if error:
        print(error.message())

        if error.message() == "Squidstat is already connected.":
            onNewDeviceConnected("Plus2254")
            print("we are sure")
            print(error.message())
            print("Here we get the error")


    #print(dir(tracker.deviceDisconnected.disconnect(COM_port)))
    # exit program
    #sys.exit(app.exec_())
    app.exec_()
   
    #tracker.disconnectFromDeviceOnComPort(COM_port)



#run_deposition_experiment(current=0.001, deposition_time=5, filename="test_complete.csv")

