'''@file                TaskController.py
   @brief               
   @details              
                    
   @author              Philip Pang
   @author              Tim Jain
   @author              Jonathan Cederquist
   @date                February 17, 2022   
'''

import ClosedLoop
import utime

class TaskController:
    
    S0_INIT = 0
    S1_RUNNING = 1
    S2_STOPPED = 2
    
    stepResponseTimeLimit = 2000
    
    def __init__(self, share_setpoint, share_duty, share_pos, share_Stop, share_StartTime, queue_pos, queue_encTimes):
        self.share_setpoint = share_setpoint
        self.share_duty = share_duty
        self.share_pos = share_pos
        self.share_Stop = share_Stop
        self.share_StartTime = share_StartTime
        self.queue_pos = queue_pos
        self.queue_encTimes = queue_encTimes
        
        self.state = self.S0_INIT

        self.Control = ClosedLoop.ClosedLoop(50, self.share_setpoint.get())
        
    def task(self):
        
        while True:
            if self.state == self.S0_INIT:
                self.Control.change_setpoint(self.share_setpoint.get())
                print("StartTime is set")
                self.share_pos.put(0)
                self.share_StartTime.put(utime.ticks_ms())
                self.state = self.S1_RUNNING
                
            elif self.state == self.S1_RUNNING:
                
                if time >= self.stepResponseTimeLimit:
                    print(time)
                    self.share_Stop.put(1)
                    self.share_duty.put(0)
                    self.share_pos.put(0)
                    print("\nMotor Data:")
                    while not self.queue_pos.empty():
                        print(self.queue_encTimes.get(), self.queue_pos.get())
                    self.state = self.S2_STOPPED
                
                else:
                    # Update control signal and duty cycle
                    self.share_duty.put(int(self.Control.update(self.share_pos.get())))
                    time = utime.ticks_diff(utime.ticks_ms(), self.share_StartTime.get())
                    
                    # Save time and position data
                    if not self.queue_pos.full():
                        self.queue_encTimes.put(time)
                        self.queue_pos.put(self.share_pos.get())
                    

            elif self.state == self.S2_STOPPED:
                if not self.share_Stop.get():
                    self.state = self.S0_INIT
                    
            yield (self.state)
