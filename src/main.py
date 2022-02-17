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
# import pyb
import math
import utime
import cotask
import task_share

import TaskMotor
import TaskEncoder
import TaskController
        
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
    share_StartTime_1 = task_share.Share('i', thread_protect = False, name = "share_StartTime")
    share_Stop_1 = task_share.Share('i', thread_protect = False, name = "share_Stop")
    share_StartTime_2 = task_share.Share('i', thread_protect = False, name = "share_StartTime_2")
    share_Stop_2 = task_share.Share('i', thread_protect = False, name = "share_Stop_2")
    
    # Initialize shared variables
    share_duty_1.put(0)
    share_setpoint_1.put(math.pi*2)
    share_pos_1.put(0)
    share_duty_2.put(0)
    share_setpoint_2.put(math.pi*4)
    share_pos_2.put(0)
    share_Stop_1.put(0)
    share_Stop_2.put(0)
    
    # Create task objects
    motor1 = TaskMotor.TaskMotor(1, share_duty_1)
    enco1 = TaskEncoder.TaskEncoder(1, share_pos_1, share_Stop_1)
    control1 = TaskController.TaskController(share_setpoint_1, share_duty_1, share_pos_1, share_Stop_1, share_StartTime_1, queue_pos_1, queue_enc1Times)
    
    motor2 = TaskMotor.TaskMotor(2, share_duty_2)
    enco2 = TaskEncoder.TaskEncoder(2, share_pos_2, share_Stop_2)
    control2 = TaskController.TaskController(share_setpoint_2, share_duty_2, share_pos_2, share_Stop_2, share_StartTime_2, queue_pos_2, queue_enc2Times)

    
    # Putting task objects in cotask run list
    task1_Mot = cotask.Task (motor1.task, name = 'Task1_Motor', priority = 1,
                             period = 20, profile = True, trace = False)
    
    task2_Enco = cotask.Task (enco1.task, name = 'Task2_Encoder', priority = 3, 
                              period = 10, profile = True, trace = False)
    
    task3_Cont = cotask.Task (control1.task, name = 'Task3_Controller', priority = 5, 
                              period = 20, profile = True, trace = False)
            
    task4_Mot2 = cotask.Task (motor2.task, name = 'Task4_Motor2', priority = 2,
                              period = 20, profile = True, trace = False)
    
    task5_Enco2 = cotask.Task (enco2.task, name = 'Task5_Encoder2', priority = 4, 
                               period = 10, profile = True, trace = False)
    
    task6_Cont2 = cotask.Task (control2.task, name = 'Task6_Controller2', priority = 6, 
                               period = 20, profile = True, trace = False)
    
    cotask.task_list.append (task1_Mot)
    cotask.task_list.append (task2_Enco)
    cotask.task_list.append (task3_Cont)
    cotask.task_list.append (task4_Mot2)
    cotask.task_list.append (task5_Enco2)
    cotask.task_list.append (task6_Cont2)    
    
    Contperiod = int(input("Set Controller Period: "))
    Contperiod2 = int(input("Set Second Controller Period: "))
    
    # Set period of controller based on user input
    task3_Cont.set_period(Contperiod)
    task6_Cont2.set_period(Contperiod2)
    
    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect ()
    
    while True:
        try:
            cotask.task_list.pri_sched ()
                
        except KeyboardInterrupt:
            print("End Program")
            share_duty_1.put(0)
            share_duty_2.put(0)
            task1_Mot.schedule()
            task4_Mot2.schedule()
            break
        
    