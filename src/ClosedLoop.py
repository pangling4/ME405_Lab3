''' @file       ClosedLoop.py
    @brief      Implements closed loop proportional controller for position
    @details    Class of closed loop controller that can be used to control PITTMAN motors given in ME 405 lab
                with NUCLEO L476RG microcontroller
                
    @author     Jonathan Cederquist
    @author     Tim Jain
    @author     Philip Pang
    @date       Last Modified 2/2/22
'''

import pyb
import utime

class ClosedLoop:
    '''!
    @brief This class implements a closed loop proportional controller
    '''
    
    def __init__ (self, kp, setpoint):
        '''! 
        @brief          Creates a ClosedLoop Controller object
        @details        Creates a ClosedLoop Controller object with the given
                        proportional control gain and reference value
        @param kp       Controller proportional gain in [% duty cycle/rad] 
        @param setpoint Reference value in rad for the system
        '''
        # Set controller proportional gain and setpoint
        self.kp = kp
        self.setpoint = setpoint
        
    def update(self, measured):
        '''!
        @brief              Updates the control signal based on the current error
        @details            Implements proportional control and returns the proportional
                            gain times the error (setpoint - actual position)
        @param measured     The current position of the system [rad] to compare to the setpoint
        '''
        
        # Calculate error and return proportional control signal
        error = self.setpoint - measured
        return self.kp*error
        
    def change_setpoint(self, setpoint):
        '''!
        @brief              Updates the setpoint of the controller
        @param setpoint     The new setpoint for the controller [rad]
        '''
        
        self.setpoint = setpoint
        
    def change_kp(self, kp):
        '''!
        @brief       Updates the proportional gain value of the controller
        @param kp    The new proportional gain for the controller [% duty cycle/rad]
        '''
        
        self.kp = kp