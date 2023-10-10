#This script is built to convert the Unix time the CTC outputs to time since turning on the data recording.
#The user selects how they want the time displayed (milliseconds, seconds, minutes, or hours)

import numpy as np

#Ask the user which time file to convert
print("Please enter the temperature time file you wish to convert:")
filename = raw_input()
time, T = np.loadtxt(filename, usecols=[0,1], unpack=True)
print("Enter unit of time you want to convert to (milliseconds, seconds, minutes, or hours):")
time_unit = raw_input()
filenamefix = filename.replace('.txt', '')
output_string = filenamefix + time_unit + '.txt'

#Do the converting (depending on how the user wants it converted)
i = 0
j = 0
confirm = 0
time_start = time[0]

if time_unit == 'milliseconds':
    confirm = 1
    while i < len(time)-0.5:
        time[i] = time[i] - time_start
        i += 1
    with open(output_string, 'w') as f:
        for j in range(len(time)):
            f.write(str(time[j]) + " " + str(T[j]) + "\n")
        f.close()

if time_unit == 'seconds':
    confirm = 1
    while i < len(time)-0.5:
        time[i] = time[i] - time_start
        time[i] = time[i]/1000#ms to s conversion
        i += 1
    with open(output_string, 'w') as f:
        for j in range(len(time)):
            f.write(str(time[j]) + " " + str(T[j]) + "\n")
        f.close()

if time_unit == 'minutes':
    confirm = 1
    while i < len(time)-0.5:
        time[i] = time[i] - time_start
        time[i] = time[i]/60000#ms to minutes conversion
        i += 1
    with open(output_string, 'w') as f:
        for j in range(len(time)):
            f.write(str(time[j]) + " " + str(T[j]) + "\n")
        f.close()

if time_unit == 'hours':
    confirm = 1
    while i < len(time)-0.5:
        time[i] = time[i] - time_start
        time[i] = time[i]/3600000#ms to hours conversion
        i += 1
    with open(output_string, 'w') as f:
        for j in range(len(time)):
            f.write(str(time[j]) + " " + str(T[j]) + "\n")
        f.close()

if confirm == 0:
    print("Please rerun the code and enter a valid unit of time, case matters.")


