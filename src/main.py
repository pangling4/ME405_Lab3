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
    Slo_Moe = MotorDriver.MotorDriver(pyb.Pin.board.PA10, pyb.Pin.board.PB4, pyb.Pin.board.PB5, 3)
    
    Slo_Moe.enable()
    
    while True:
        
        Slo_Moe.set_duty_cycle(share_duty.get())
        #print('Duty cycle: ', share_duty.get())

        yield (0)

def task2_Encoder ():
    """!
    Task which runs the encoder.
    """
    Slo_Enco = EncoderDriver.EncoderDriver(pyb.Pin(pyb.Pin.cpu.B6), pyb.Pin(pyb.Pin.cpu.B7), 4)
    
    Slo_Enco.zero()
    
    counter = 0
    
    while True:
        
        Slo_Enco.update()
        share_pos.put(Slo_Enco.read())
        
        if not(queue_pos.full()):
            queue_pos.put(Slo_Enco.read())
        #print('Encoder Position: ', share_pos.get())

        #yield (share_pos.get())
        yield (counter)
        counter += 1

def task3_Controller ():
    """!
    Task which runs the closed loop controller.
    """
    
    Slo_Control = ClosedLoop.ClosedLoop(100, math.pi*2)
    
    while True:
        
        Slo_Control.change_setpoint(share_setpoint.get())
        
        #print('Control Setpoint: ', share_setpoint.get())
        
        share_duty.put(int(Slo_Control.update(share_pos.get())))
        
        yield (0)


# This code creates a share, a queue, and two tasks, then starts the tasks. The
# tasks run until somebody presses ENTER, at which time the scheduler stops and
# printouts show diagnostic information about the tasks, share, and queue.
if __name__ == "__main__":
    #print ('Multitasking')

    # Create a shares for motor duty cycle, controller setpoint, and encoder position
    share_duty = task_share.Share ('i', thread_protect = False, name = "Share_Duty")
    share_setpoint = task_share.Share ('f', thread_protect = False, name = "Share_Setpoint")
    share_pos = task_share.Share ('f', thread_protect = False, name = "Share_Pos")
    queue_pos = task_share.Queue('f', 200, thread_protect = False, name = "Queue_Pos")
    
    Contperiod = int(input("Set Controller Period: "))
    
    
    # Initialize shared variables
    share_duty.put(0)
    share_setpoint.put(math.pi*2)
    share_pos.put(0)
    

    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed
    task1_Mot = cotask.Task (task1_Motor, name = 'Task1_Motor', priority = 1, 
                         period = 10, profile = True, trace = False)
    task2_Enco = cotask.Task (task2_Encoder, name = 'Task2_Encoder', priority = 3, 
                         period = 10, profile = True, trace = True)
    task3_Cont = cotask.Task (task3_Controller, name = 'Task3_Controller', priority = 2, 
                         period = Contperiod, profile = True, trace = False)
    cotask.task_list.append (task1_Mot)
    cotask.task_list.append (task2_Enco)
    cotask.task_list.append (task3_Cont)
    

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect ()

    # Start a timer to time step response
    start = utime.ticks_ms()
    
    # Run the scheduler with the chosen scheduling algorithm. Quit if any 
    # character is received through the serial port
    while True:
        if utime.ticks_diff(utime.ticks_ms(), start) >= 2000:
            break
        cotask.task_list.pri_sched ()

    # Empty the comm port buffer of the character(s) just pressed
#     if vcp.any():
#         vcp.read ()
    
    share_duty.put(0)
    task1_Mot.schedule()
    
# 
#     # Print a table of task data and a table of shared information data
#     print ('\n' + str (cotask.task_list))
#     print ('\r\n')
    
    trace = task2_Enco.get_trace()
    timeList = trace.split("\n")
    times = []
    
    for item in timeList:
        times.append(item.strip().split(":")[0])
    
    # Get that boi outta here
    times.pop(0)
    queue_pos.get()
    
    timeCounter = 0
    
    while not queue_pos.empty():
        print(times[timeCounter], queue_pos.get())
        timeCounter += 1