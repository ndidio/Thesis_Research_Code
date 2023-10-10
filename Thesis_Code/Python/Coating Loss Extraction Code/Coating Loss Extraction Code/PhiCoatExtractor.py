#This script takes in text files with 3 columns, temperature, Q, and Standard Deviation in that order.
#It will also ask the user for a dilution factor and substrate loss. Using these numbers, it spits out a
#coating loss along with the new standard deviation for plotting purposes. This will create another text file with 3 columns.

import numpy as np
import matplotlib.pyplot as plt

#Ask the user for the name of the file that holds the data
print("Please enter the file name of the total loss you wish to analyze, please feed me Phi and not Q:")
file_name = raw_input()

T_tot = {}
Phi_tot = {}
Std_tot = {}
#Read the data in from the given file name
with open(file_name) as f:
    lines = f.readlines()
    T_tot = [line.split()[0] for line in lines]
    Phi_tot = [line.split()[1] for line in lines]
    Std_tot = [line.split()[2] for line in lines]
i = 0
while i < len(T_tot) - 0.5:
    T_tot[i] = float(T_tot[i])
    Phi_tot[i] = float(Phi_tot[i])
    Std_tot[i] = float(Std_tot[i])
    i += 1

#Ask the user what the substrate loss data file is
print("Please enter the substrate loss data file:")
file_name_sub = raw_input()

T_sub = {}
Phi_sub = {}
Std_sub = {}
#Read the substrate data in from the given file name
with open(file_name_sub) as f:
    lines = f.readlines()
    T_sub = [line.split()[0] for line in lines]
    Phi_sub = [line.split()[1] for line in lines]
    Std_sub = [line.split()[2] for line in lines]
i = 0
while i <len(T_sub) - 0.5:
    T_sub[i] = float(T_sub[i])
    Phi_sub[i] = float(Phi_sub[i])
    Std_sub[i] = float(Std_sub[i])
    i += 1

#Ask the user for the dilution factor
print("Please enter the dilution factor:")
D = raw_input()
D = float(D)

#Calculate the coating loss at each temperature
#To make sure we only read data where we have temperatures for both substrate and total, I'm going to step through and write the
#shared temperatures along with their data to new arrays. If we don't have a common temperature, we interpolate between the
#nearest two substrate temperatures.
i = 0
j = 0 #This steps through temperatures
i_hold = 0 #Placeholder to record the index of T_tot that we are currently on, used in indexing values of Phi and Std Coating
T_tot_temp = 0 #Holds value at which we have a match to the outermost while loop
T_sub_temp = 0 #Same as above for substrate
Phi_tot_temp = 0 #Holds value of Phi at a found temperature
Phi_sub_temp = 0 #Same as above for substrate
Std_tot_temp = 0 #Holds value of standard deviation at a found temperature
Std_sub_temp = 0 #Same as above for substrate
Coated_check = 0 #Placeholder to check if there is coated temperature data at the given step
T_coat = T_tot #Initialize array to hold the temperatures of the coating loss data, it's the same temps as the total so v easy
Phi_coat = np.zeros(len(T_coat)) #Same as above but for Phi, we put zeros cuz we need to calculate coating loss below
Std_coat = np.zeros(len(T_coat)) #Same as above but for Standard Deviation.
while j < 301:
    TempFound_count = 0
    T_tot_temp = 0
    Coated_check = 0
    while i < len(T_tot) - 0.5:
        if T_tot[i] == j:
            TempFound_count += 1
            Coated_check += 1
            i_hold = i
            T_tot_temp = T_tot[i]
            Phi_tot_temp = Phi_tot[i]
            Std_tot_temp = Std_tot[i]
        i += 1
    i = 0
    while i < len(T_sub) - 0.5:
        if T_sub[i] == j:
            TempFound_count += 1
            T_sub_temp = T_sub[i]
            Phi_sub_temp = Phi_sub[i]
            Std_sub_temp = Std_sub[i]
        i += 1
    i = 0
    if TempFound_count == 2 and Coated_check == 1: #We have matching temperature data and don't need to interpolate
        Phi_coat[i_hold] = (1/D)*Phi_tot_temp + (1-(1/D))*Phi_sub_temp
        Std_coat[i_hold] = ((1/D)*(Std_tot_temp**2) + abs((1 - (1/D)))*(Std_sub_temp**2))**0.5
    if TempFound_count == 1 and Coated_check == 1: #We have non matching data, and need to interpolate substrate data
        Phi_sub_interp = np.interp(T_tot_temp, T_sub, Phi_sub)
        Std_sub_interp = np.interp(T_tot_temp, T_sub, Std_sub)
        #Now use the interpolated data to find the coating loss
        Phi_coat[i_hold] = (1/D)*Phi_tot_temp + (1-(1/D))*Phi_sub_interp
        Std_coat[i_hold] = ((1/D)*(Std_tot_temp**2) + abs((1 - (1/D)))*(Std_sub_interp**2))**0.5
    j += 1

#Now that we have loss, we can easily convert to Q if the user wants us to. Also ask them which mode they are analyzing.
print("Do you want to receive your data in Q or Phi?")
Ans = raw_input()
print("Which mode are you analyzing?")
Mode_num = raw_input()

if Ans == 'Phi':
    #Now T_coat, Phi_coat, and Std_coat hold all the relevant loss data for the coating. Let's save it as a text file and
    #plot it.
    i = 0
    output_string = "Coating " + file_name
    with open(output_string, 'w') as f:
        while i < len(T_coat) - 0.5:
            f.write(str(T_coat[i]) + " " + str(Phi_coat[i]) + " " + str(Std_coat[i]) + "\n")
            i += 1

    plt.errorbar(T_coat, Phi_coat, Std_coat, linestyle='None', marker='o')
    ax = plt.gca()
    ax.set_yscale('log')
    plt.xlabel("Temperature (K)")
    plt.ylabel("Loss Angle")
    plt.title("AlGaAs Mode " + Mode_num + " Loss Angle vs Temperature")
    plt.grid()
    plt.show()
        
if Ans == 'Q':
    #First we have to convert the Phi and Std arrays to the proper values
    i = 0
    Q_coat = np.zeros(len(Phi_coat))
    StdQ_coat = np.zeros(len(Phi_coat))
    while i < len(Phi_coat) - 0.5:
        Q_coat[i] = 1/Phi_coat[i]
        StdQUpper = 1/(Phi_coat[i] - Std_coat[i])
        StdQLower = 1/(Phi_coat[i] + Std_coat[i])
        StdQ_coat[i] = StdQUpper - StdQLower
        i += 1
    #Now T_coat, Q_coat, and StdQ_coat hold all the relevant quality data for the coating. Let's save it as a text file and
    #plot it.
    i = 0
    output_string = "Coating Mode " + Mode_num + " Averaged Q.txt"
    with open(output_string, 'w') as f:
        while i < len(T_coat) - 0.5:
            f.write(str(T_coat[i]) + " " + str(Q_coat[i]) + " " + str(StdQ_coat[i]) + "\n")
            i += 1

    plt.errorbar(T_coat, Q_coat, StdQ_coat, linestyle='None', marker='o')
    ax = plt.gca()
    ax.set_yscale('log')
    plt.xlabel("Temperature (K)")
    plt.ylabel("Quality Factor")
    plt.title("AlGaAs Mode " + Mode_num + " Quality Factor vs Temperature")
    plt.grid()
    plt.show()





















