"""!
@file main.py
    This file contains tasks to simultaneously perform closed loop control
    on two Pittman motors in ME 405 Lab
    
@author Jonathan Cederquist
@author Tim Jain
@author Philip Pang
@date   Last Modified 2/3/22
"""

import gc
import pyb
import cotask
import task_share
import MotorDriver
import EncoderDriver
import ClosedLoop
import math
import utime


def task1_Motor ():
    """!
    Task which drivers the motor.
    """
    
    S0_INIT = 0
    S1_RUNNING = 1
    S2_STOPPED = 2
    
    state = S0_INIT
    while True:
        
        if state == S0_INIT:
            Slo_Moe = MotorDriver.MotorDriver(pyb.Pin.board.PA10, pyb.Pin.board.PB4, pyb.Pin.board.PB5, 3)
    
            Slo_Moe.enable()
            
            state = S1_RUNNING
            
        elif state == S1_RUNNING:
            Slo_Moe.set_duty_cycle(share_duty_1.get())
            
            if share_Stop.get() == 1:
                state = S2_STOPPED
                
        elif state == S2_STOPPED:
            Slo_Moe.set_duty_cycle(0)
            Slo_Moe.disable()
            print("IN STOP STATE")
        
            if not share_Stop.get():
                state = S0_INIT
                
        yield (state)

def task2_Encoder ():
    """!
    Task which runs the encoder.
    """
    S0_INIT = 0
    S1_RUNNING = 1
    S2_STOPPED = 2
    
    state = S0_INIT
    while True:
        
        if state == S0_INIT:
            Slo_Enco = EncoderDriver.EncoderDriver(pyb.Pin(pyb.Pin.cpu.B6), pyb.Pin(pyb.Pin.cpu.B7), 4)
    
            Slo_Enco.zero()
            
            state = S1_RUNNING
            
        elif state == S1_RUNNING:
            Slo_Enco.update()
            share_pos_1.put(Slo_Enco.read())
            
            if not(queue_enc1Times.full()):
                queue_enc1Times.put(utime.ticks_diff(utime.ticks_ms(), share_StartTime.get()))
            
            if not(queue_pos_1.full()):
                queue_pos_1.put(Slo_Enco.read())
            
            if share_Stop.get():
                state = S2_STOPPED
                
        elif state == S2_STOPPED:
            Slo_Enco.zero()
        
            if not(share_Stop.get()):
                state = S0_INIT
                
        yield (state)
    
def task3_Controller ():
    """!
    Task which runs the closed loop controller.
    """
    S0_INIT = 0
    S1_RUNNING = 1
    S2_STOPPED = 2
    
    state = S0_INIT
    while True:
        
        if state == S0_INIT:
            Slo_Control = ClosedLoop.ClosedLoop(50, share_setpoint_1.get())
            
            state = S1_RUNNING
            
        elif state == S1_RUNNING:
            share_duty_1.put(int(Slo_Control.update(share_pos_1.get())))
            
            if share_Stop.get():
                state = S2_STOPPED
                
        elif state == S2_STOPPED:
            Slo_Control.change_kp(0)
        
            if not share_Stop.get():
                state = S0_INIT
                
        yield (state)

def task4_Motor2 ():
    """!
    Task which drivers the motor.
    """
    Bro_Moe = MotorDriver.MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1, 5)
    
    Bro_Moe.enable()
    
    while True:
        
        Bro_Moe.set_duty_cycle(share_duty_2.get())
        #print('Duty cycle: ', share_duty_2.get())

        yield (0)

def task5_Encoder2 ():
    """!
    Task which runs the encoder.
    """
    Bro_Enco = EncoderDriver.EncoderDriver(pyb.Pin(pyb.Pin.cpu.C6), pyb.Pin(pyb.Pin.cpu.C7), 8)
    
    Bro_Enco.zero()
    
    counter = 0
    
    while True:
        
        Bro_Enco.update()
        share_pos_2.put(Bro_Enco.read())
        
        if not(queue_pos_2.full()):
            queue_pos_2.put(Bro_Enco.read())
        #print('Encoder Position: ', share_pos_2.get())

        yield (counter)
        counter += 1

def task6_Controller2 ():
    """!
    Task which runs the closed loop controller.
    """
    
    Bro_Control = ClosedLoop.ClosedLoop(100, math.pi*2)
    
    while True:
        
        Bro_Control.change_setpoint(share_setpoint_2.get())
        
        #print('Control Setpoint: ', share_setpoint_2.get())
        
        share_duty_2.put(int(Bro_Control.update(share_pos_2.get())))
        
        yield (0)
        
# This code creates a share, a queue, and two tasks, then starts the tasks. The
# tasks run until somebody presses ENTER, at which time the scheduler stops and
# printouts show diagnostic information about the tasks, share, and queue.
if __name__ == "__main__":    
    
    # Create a shares for motor duty cycle, controller setpoint, and encoder position
    share_duty_1 = task_share.Share ('i', thread_protect = False, name = "share_duty_1")
    share_setpoint_1 = task_share.Share ('f', thread_protect = False, name = "share_setpoint_1")
    share_pos_1 = task_share.Share ('f', thread_protect = False, name = "share_pos_1")
    queue_pos_1 = task_share.Queue('f', 500, thread_protect = False, name = "queue_pos_1")
    queue_enc1Times = task_share.Queue('f', 500, thread_protect = False, name = "queue_enc1Times")
    share_StartTime = task_share.Share('i', thread_protect = False, name = "share_StartTime")
    share_Stop = task_share.Share('i', thread_protect = False, name = "share_Stop")
    
    # Create a shares for second motor duty cycle, controller setpoint, and encoder position
    share_duty_2 = task_share.Share ('i', thread_protect = False, name = "share_duty_2")
    share_setpoint_2 = task_share.Share ('f', thread_protect = False, name = "share_setpoint_2")
    share_pos_2 = task_share.Share ('f', thread_protect = False, name = "share_pos_2")
    queue_pos_2 = task_share.Queue('f', 200, thread_protect = False, name = "queue_pos_2")
    
    # Initialize shared variables
    share_duty_1.put(0)
    share_setpoint_1.put(math.pi*2)
    share_pos_1.put(0)
    share_duty_2.put(0)
    share_setpoint_2.put(math.pi*2)
    share_pos_2.put(0)
    
    # First set of tasks
    task1_Mot = cotask.Task (task1_Motor, name = 'Task1_Motor', priority = 1, 
                         period = 10, profile = True, trace = False)
    task2_Enco = cotask.Task (task2_Encoder, name = 'Task2_Encoder', priority = 3, 
                         period = 10, profile = True, trace = False)
    task3_Cont = cotask.Task (task3_Controller, name = 'Task3_Controller', priority = 2, 
                         period = 10, profile = True, trace = False)
            
    # Second set of tasks
    task4_Mot2 = cotask.Task (task4_Motor2, name = 'Task4_Motor2', priority = 1, 
                         period = 10, profile = True, trace = False)
    task5_Enco2 = cotask.Task (task5_Encoder2, name = 'Task5_Encoder2', priority = 3, 
                         period = 10, profile = True, trace = False)
    task6_Cont2 = cotask.Task (task6_Controller2, name = 'Task6_Controller2', priority = 2, 
                         period = 10, profile = True, trace = False)
    
    cotask.task_list.append (task1_Mot)
    cotask.task_list.append (task2_Enco)
    cotask.task_list.append (task3_Cont)
    #cotask.task_list.append (task4_Mot2)
    #cotask.task_list.append (task5_Enco2)
    #cotask.task_list.append (task6_Cont2)
    
    # Set step response time limit in milliseconds
    stepResponseTimeLimit = 2000
    
    while True:
        try:
            
            Contperiod = int(input("Set Controller Period: "))
            
            # Set period of controller based on user input
            task3_Cont.set_period(Contperiod)
            
            # Reset stop flag
            share_Stop.put(0)
            
            # Reset shared variables
            share_duty_1.put(0)
            share_setpoint_1.put(math.pi*2)
            share_pos_1.put(0)
            share_duty_2.put(0)
            share_setpoint_2.put(math.pi*2)
            share_pos_2.put(0)
            
            # Run the memory garbage collector to ensure memory is as defragmented as
            # possible before the real-time scheduler is started
            gc.collect ()

            # Start a timer to time step response
            share_StartTime.put(utime.ticks_ms())
            
            # Run the scheduler with priority scheduling algorithm
            while True:
                cotask.task_list.pri_sched ()
                
                if utime.ticks_diff(utime.ticks_ms(), share_StartTime.get()) >= stepResponseTimeLimit:
                    share_Stop.put(1)
                    break
            
            utime.sleep_ms(15)
            
            task1_Mot.schedule()
            task2_Enco.schedule()
            task3_Cont.schedule()
       
            while not queue_pos_1.empty():
                print(queue_enc1Times.get(), queue_pos_1.get())
            
        except KeyboardInterrupt:
            break
        
    