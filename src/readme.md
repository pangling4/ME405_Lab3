# Multitasking: On Schedule
This exercise involved utilizing our motor driver, 
encoder driver, and closed loop controller. This involved
creating seperate tasks for these, and assigning
appropriate priorities and periods (sampling rates)
for each task. This involved utilizing the files
cotask.py, taskshare.py, and basic_tasks.py from
the ME405 support repository towards implementing
our multitasking regime. basic_tasks.py served
as a template towards creating our main.py in terms
of implementing the tasks and sending data over serial. 
It is necessary to perform multitasking in order to control 
the position of more than one motor. 




