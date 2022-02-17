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
import math
import utime
import cotask
import task_share
import MotorDriver
import EncoderDriver
import ClosedLoop
import TaskMotor
import TaskEncoder
import TaskController


def task1_Motor ():
    """!
    Task which drivers the motor.
    """
    #Initialize and Enable Motor 1
    Slo_Moe = MotorDriver.MotorDriver(pyb.Pin.board.PA10, pyb.Pin.board.PB4, pyb.Pin.board.PB5, 3)
    Slo_Moe.enable()
    while True:
        Slo_Moe.set_duty_cycle(share_duty_1.get())   
        yield (0)

def task4_Motor2 ():
    """!
    Task which drivers the motor.
    """
    #Initialize and Enable Motor 2        
    Bro_Moe = MotorDriver.MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1, 5)
    Bro_Moe.enable()
    while True:
        Bro_Moe.set_duty_cycle(share_duty_2.get())
        yield (0)

def task2_Encoder ():
    """!
    Task which runs the encoder.
    """
    # Initialize and zero Encoder 1
    Slo_Enco = EncoderDriver.EncoderDriver(pyb.Pin(pyb.Pin.cpu.B6), pyb.Pin(pyb.Pin.cpu.B7), 4)
    Slo_Enco.zero()
    while True:
        if share_Stop.get():
            print("zeroing Slo encoder")
            Slo_Enco.zero()
        Slo_Enco.update()
        share_pos_1.put(Slo_Enco.read())
        share_Stop.put(0)
        yield (0)
        
def task5_Encoder2 ():
    """!
    Task which runs the encoder.
    """
    # Initialize and zero Encoder 2
    Bro_Enco = EncoderDriver.EncoderDriver(pyb.Pin(pyb.Pin.cpu.C6), pyb.Pin(pyb.Pin.cpu.C7), 8)
    Bro_Enco.zero()
    while True:
        if share_Stop_2.get():
            print("zeroing Bro encoder")
            Bro_Enco.zero()
        Bro_Enco.update()
        share_pos_2.put(Bro_Enco.read())
        share_Stop_2.put(0)
        yield (0)
        
def task3_Controller ():
    """!
    Task which runs the closed loop controller.
    """
    S0_INIT = 0
    S1_RUNNING = 1
    S2_STOPPED = 2
    
    state = S0_INIT
    
    Slo_Control = ClosedLoop.ClosedLoop(50, share_setpoint_1.get())
    
    while True:
        
        if state == S0_INIT:
            Slo_Control.change_setpoint(share_setpoint_1.get())
            print("StartTime is set")
            share_pos_1.put(0)
            share_StartTime.put(utime.ticks_ms())
            state = S1_RUNNING
            
        elif state == S1_RUNNING:
            
            # Update control signal and duty cycle
            share_duty_1.put(int(Slo_Control.update(share_pos_1.get())))
            
            # Save time and position data
            if not queue_enc1Times.full():
                queue_enc1Times.put(utime.ticks_diff(utime.ticks_ms(), share_StartTime.get()))
            
            if not queue_pos_1.full():
                queue_pos_1.put(share_pos_1.get())
                
            if (utime.ticks_diff(utime.ticks_ms(), share_StartTime.get()) >= stepResponseTimeLimit):
                print(utime.ticks_diff(utime.ticks_ms(), share_StartTime.get()))
                share_Stop.put(1)
                share_duty_1.put(0)
                state = S2_STOPPED
                
        elif state == S2_STOPPED:
            if not share_Stop.get():
                state = S0_INIT
                
        yield (state)
        
def task6_Controller2 ():
    """!
    Task which runs the closed loop controller.
    """
    S0_INIT = 0
    S1_RUNNING = 1
    S2_STOPPED = 2
    
    state = S0_INIT
    
    Bro_Control = ClosedLoop.ClosedLoop(50, share_setpoint_2.get())
    
    while True:
        
        if state == S0_INIT:
            Bro_Control.change_setpoint(share_setpoint_2.get())
            
            print("StartTime_2 is set")
            share_pos_2.put(0)
            share_StartTime_2.put(utime.ticks_ms())
            state = S1_RUNNING
            
        elif state == S1_RUNNING:
            
            # Update control signal and duty cycle
            share_duty_2.put(int(Bro_Control.update(share_pos_2.get())))
            
            # Save time and position data
            if not queue_enc2Times.full():
                queue_enc2Times.put(utime.ticks_diff(utime.ticks_ms(), share_StartTime_2.get()))
            
            if not queue_pos_2.full():
                queue_pos_2.put(share_pos_2.get())
                
            if (utime.ticks_diff(utime.ticks_ms(), share_StartTime_2.get()) >= stepResponseTimeLimit):
                print(utime.ticks_diff(utime.ticks_ms(), share_StartTime_2.get()))
                share_Stop_2.put(1)
                share_duty_2.put(0)
                state = S2_STOPPED
                
        elif state == S2_STOPPED:
            if not share_Stop_2.get():
                state = S0_INIT
                
        yield (state)
        
# def task7_User ():
#     """!
#     Task which interacts with the user.
#     """

def printData():
    """!
    Print function for Motor1 data.
    """
    while not queue_pos_1.empty():
        print(queue_enc1Times.get(), queue_pos_1.get())
    #print("End of Motor 1 data.\n")    
  
    
def printData_2():
    """!
    Print function for Motor2 data.
    """
    while not queue_pos_2.empty():
        print(queue_enc2Times.get(), queue_pos_2.get()) 
    #print("End of Motor 2 data.\n")    

        
# This code creates a share, a queue, and two tasks, then starts the tasks. The
# tasks run until somebody presses ENTER, at which time the scheduler stops and
# printouts show diagnostic information about the tasks, share, and queue.
if __name__ == "__main__":    
    
    # Create a shares for motor duty cycle, controller setpoint, and encoder position
    share_duty_1 = task_share.Share ('i', thread_protect = False, name = "share_duty_1")
    share_setpoint_1 = task_share.Share ('f', thread_protect = False, name = "share_setpoint_1")
    share_pos_1 = task_share.Share ('f', thread_protect = False, name = "share_pos_1")
    queue_pos_1 = task_share.Queue('f', 100, thread_protect = False, name = "queue_pos_1")
    queue_enc1Times = task_share.Queue('f', 100, thread_protect = False, name = "queue_enc1Times")
    
    # Create a shares for second motor duty cycle, controller setpoint, and encoder position
    share_duty_2 = task_share.Share ('i', thread_protect = False, name = "share_duty_2")
    share_setpoint_2 = task_share.Share ('f', thread_protect = False, name = "share_setpoint_2")
    share_pos_2 = task_share.Share ('f', thread_protect = False, name = "share_pos_2")
    queue_pos_2 = task_share.Queue('f', 100, thread_protect = False, name = "queue_pos_2")
    queue_enc2Times = task_share.Queue('f', 100, thread_protect = False, name = "queue_enc2Times")
    
    # Create share flags to control states in tasks
    share_StartTime = task_share.Share('i', thread_protect = False, name = "share_StartTime")
    share_Stop = task_share.Share('i', thread_protect = False, name = "share_Stop")
    share_StartTime_2 = task_share.Share('i', thread_protect = False, name = "share_StartTime_2")
    share_Stop_2 = task_share.Share('i', thread_protect = False, name = "share_Stop_2")
    
    # Initialize shared variables
    share_duty_1.put(0)
    share_setpoint_1.put(math.pi*2)
    share_pos_1.put(0)
    share_duty_2.put(0)
    share_setpoint_2.put(math.pi*4)
    share_pos_2.put(0)
    share_Stop.put(0)
    share_Stop_2.put(0)
    
    # First set of tasks
    task1_Mot = cotask.Task (task1_Motor, name = 'Task1_Motor', priority = 1, 
                         period = 20, profile = True, trace = False)
    task2_Enco = cotask.Task (task2_Encoder, name = 'Task2_Encoder', priority = 2, 
                         period = 10, profile = True, trace = False)
    task3_Cont = cotask.Task (task3_Controller, name = 'Task3_Controller', priority = 3, 
                         period = 20, profile = True, trace = False)
            
    # Second set of tasks
    task4_Mot2 = cotask.Task (task4_Motor2, name = 'Task4_Motor2', priority = 1, 
                         period = 20, profile = True, trace = False)
    task5_Enco2 = cotask.Task (task5_Encoder2, name = 'Task5_Encoder2', priority = 2, 
                         period = 10, profile = True, trace = False)
    task6_Cont2 = cotask.Task (task6_Controller2, name = 'Task6_Controller2', priority = 3, 
                         period = 20, profile = True, trace = False)
    
    cotask.task_list.append (task1_Mot)
    cotask.task_list.append (task2_Enco)
    cotask.task_list.append (task3_Cont)
    cotask.task_list.append (task4_Mot2)
    cotask.task_list.append (task5_Enco2)
    cotask.task_list.append (task6_Cont2)
    
    # Set step response time limit in milliseconds
    stepResponseTimeLimit = 2000
    
    Contperiod = int(input("Set Controller Period: "))
    Contperiod2 = int(input("Set Second Controller Period: "))
    
    # Set period of controller based on user input
    task3_Cont.set_period(Contperiod)
    task6_Cont2.set_period(Contperiod2)
    
    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect ()
    
    # Run first instances of both controller tasks
    cotask.task_list.pri_sched ()
    
    while True:
        try:
            cotask.task_list.pri_sched ()
                    
            # Print (send) data for motor 1
            if share_Stop.get():
                printData()
                
            if share_Stop_2.get():
                printData_2()
                
        except KeyboardInterrupt:
            print("End Program")
            share_duty_1.put(0)
            share_duty_2.put(0)
            task1_Mot.schedule()
            task4_Mot2.schedule()
            break
        
    