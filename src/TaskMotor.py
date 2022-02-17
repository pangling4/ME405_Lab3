'''@file                TaskMotor.py
   @brief               
   @details              
                    
   @author              Philip Pang
   @author              Tim Jain
   @author              Jonathan Cederquist
   @date                February 17, 2022   
'''

import MotorDriver
import pyb

class TaskMotor:
    def __init__ (self, motor_ID, share_duty):
        self.share_duty = share_duty
        if motor_ID == 1:
            # Slo_Moe
            self.Moe = MotorDriver.MotorDriver(pyb.Pin.board.PA10, pyb.Pin.board.PB4, pyb.Pin.board.PB5, 3)
        
        elif motor_ID == 2:
            # Bro_Moe
            self.Moe = MotorDriver.MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1, 5)
        
    def task(self):
        self.Moe.enable()
        while True:
            self.Moe.set_duty_cycle(self.share_duty.get())   
            yield (0)
        
