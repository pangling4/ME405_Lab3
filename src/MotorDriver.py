"""!
@file MotorDriver.py
This motor driver is designed to control the motors provided in the ME405 Lab by Dr Ridgely
using a Nucleo L476RG microcontroller. PWM is used to control speed with higher resolution
and efficiency. 

@author Jonathan Cederquist
@author Tim Jain
@author Philip Pang

@date   26-Jan-2022
"""
import pyb
import utime

class MotorDriver:
    '''! 
    @brief This class allows instances of motors to be made and controlled individually
    '''

    def __init__ (self, en_pin, in1pin, in2pin, timer):
        '''! 
        @brief Instantiates motor driver by initializing GPIO pins and turning the motor off for safety. 
        @details A timer object is also made. This will be used to send PWM'd power to the motors
        
        @param en_pin Pin object for enabling motor (AKA sleep pin): high() for enable, low() for disable
        @param in1pin Pin object for motor input
        @param in2pin Pin object for motor input
        @param timer An integer designating which timer to use for the pin objects specified
        '''
        print ('Creating a motor driver')
        
        # output pins that supply power to motors
        pin1 = pyb.Pin (in1pin, pyb.Pin.OUT_PP)
        pin2 = pyb.Pin (in2pin, pyb.Pin.OUT_PP)
        
        # enable pin to stop or start motors
        self.en_pin = pyb.Pin (en_pin, pyb.Pin.OUT_PP)
        self.en_pin.low()
        
        # a timer object is created with pins configured to create PWM signals
        tim = pyb.Timer (timer, freq=20000)
        self.ch1 = tim.channel (1, pyb.Timer.PWM, pin=pin1)
        self.ch2 = tim.channel (2, pyb.Timer.PWM, pin=pin2)
        

    def set_duty_cycle (self, duty):
        '''!
        @brief This method sets the duty cycle to be sent to the motor to the given level. Positive values
        cause torque in one direction, negative values in the opposite direction.
        @param duty A signed integer representing desired duty cycle for the power sent to the motor 
        '''
        
        # CASE 1 & 2: positive duty cycle
        if duty > 0:
            # CASE 1: duty cycle needs to be at MAX = 100%
            if duty > 100:
                self.ch1.pulse_width_percent(100)
            # CASE 2: duty cycle is below MAX = 100%
            else:
                self.ch1.pulse_width_percent(duty)  
            self.ch2.pulse_width_percent(0)
        
        # CASE 3 & 4: negative duty cycle
        elif duty < 0:
            # CASE 3: duty cycle needs to be at MAX = 100%
            if duty < -100:
                self.ch2.pulse_width_percent(100)
            # CASE 4: duty cycle is below MAX = 100%
            else:
                self.ch2.pulse_width_percent(-duty)
            self.ch1.pulse_width_percent(0)
        
        # CASE 5: duty cycle is zero
        else:
            self.ch1.pulse_width_percent(0)
            self.ch2.pulse_width_percent(0)

        
    def enable(self):
        '''!
        @brief This method enables the motor by setting the sleep pin to high
        '''
        self.en_pin.high()
        
    def disable(self):
        '''!
        @brief This method disables the motor by setting the sleep pin to low
        '''
        self.en_pin.low()
        
if __name__ == "__main__":
    '''!
    @brief Tests MotorDriver.py by creating two MotorDriver objects and sets them to different speeds
    '''
    # Instantiates two motor driver objects with appropriate pins and timer number
    motor1 = MotorDriver(pyb.Pin.board.PA10, pyb.Pin.board.PB4, pyb.Pin.board.PB5, 3)
    motor2 = MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1, 5)
    
    # Enable motor 1 and 2
    motor1.enable()
    motor1.set_duty_cycle(50)
    motor2.enable()
    motor2.set_duty_cycle(50)
    # Stay at current state for 3 seconds
    utime.sleep(3)
    
    # Flip motor direction
    motor1.set_duty_cycle(-50)
    motor2.set_duty_cycle(-50)
    # Stay at current state for 3 seconds
    utime.sleep(3)
    
    # Test invalid duty cycle
    motor1.set_duty_cycle(-150)
    motor2.set_duty_cycle(-150)
    # Stay at current state for 3 seconds
    utime.sleep(3)
    
    # Stop motors
    motor1.set_duty_cycle(0)
    motor1.disable()
    motor2.set_duty_cycle(0)
    motor2.disable()
    