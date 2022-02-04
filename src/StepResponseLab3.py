"""!
@file StepResponseLab3.py
 Test program to communicate with nucleo board through
 serial USB connection. Asks user to input proportional
 gain to be used and plots motor position vs time data.

@author Jonathan Cederquist
@author Tim Jain
@author Philip Pang

@date   2-Feb-2022
"""

import serial
from matplotlib import pyplot as pp

# initialize data arrays to plot
timeList = []
positionList = []

# open serial communication
with serial.Serial ('COM3', 115200, timeout = 1) as s_port:
    
    # prompts user for Kp, and codes string into a byte
    period = bytes(input("Input integer controller period [ms]: "), 'utf-8')
    # writes user specified Kp to serial communication and "enters"
    s_port.write(period + b'\r')

    # motor choice functionality does not exist yet
    # motor = bytes(input("Specify which motor to run [1,2]: "), 'utf-8')
    # s_port.write(motor, b'\r')
    
    # need to read first line in advance because that's where the kp input is
    s_port.readline()
    
    # Wait for step response to complete
    while s_port.inWaiting() == 0:
        pass
        
    # infinite loop 
    while s_port.inWaiting() > 0:
        try:
            line = s_port.readline().strip(b'\r\n').split(b' ')
            timeList.append(float(line[0].decode()))
            positionList.append(float(line[1].decode()))
            
            # print to track progress and trace errors
            print(line)
            
        # skips values that will not cast to a float
        except ValueError:
            pass

print("Data Collection Complete")

# PLOTTING
fig, plt = pp.subplots()
plt.plot(timeList, positionList)
plt.set(xlabel = "Time [ms]", ylabel = "Position [rad]")
plt.set(title = "Flywheel Position, Controller Period="+ str(period.decode()))

# set y limits of plot in radians
plt.set_ylim(0,7)

# display plot
pp.show()