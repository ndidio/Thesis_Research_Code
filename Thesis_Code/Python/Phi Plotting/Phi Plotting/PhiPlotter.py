import matplotlib.pyplot as plt

#Ask the user how many text files they want to plot
print("Please enter the total number of modes you wish to plot:")
num_files = raw_input()
num_files = int(num_files)

#Ask the user for the names of each text file they want to plot
i = 0
files_list = {}
while i < num_files-0.5:
    print("Please enter the file name below, this message will repeat for each file:")
    files_list[i] = raw_input()
    i += 1
i = 0

#Import the data from each file into the lists of lists T and Q
#T[0] and Q[0] are each lists holding T and Q from the first file and so on
#We also need to convert the lists to floats, which is the additional loop
T = {}
Q = {}
Phi = {}
Std = {}
while i < num_files-0.5:
    with open(files_list[i]) as f:
        lines = f.readlines()
        T[i] = [line.split()[0] for line in lines]
        Q[i] = [line.split()[1] for line in lines]
        Phi[i] = [line.split()[1] for line in lines]
        Std[i] = [line.split()[2] for line in lines]
        j = 0
        while j < len(T[i])-0.5:
            T[i][j] = float(T[i][j])
            Q[i][j] = 1/float(Q[i][j])
            Phi[i][j] = float(Phi[i][j])
            Std[i][j] = float(Std[i][j])
            j += 1
    i += 1
i = 0

#Ask the user if they want Q or Phi for their y-axis, and plot accordingly
print("Do you want to have Q or Loss Angle on your y-axis? (Q/Phi):")
Ans = raw_input()

#Make the labels for the files pretty and plot the T and Q/Phi lists
while i < num_files-0.5:
    files_list[i] = files_list[i].replace('Coated', 'Coating')
    files_list[i] = files_list[i].replace('Averaged Phi.txt', '$\phi$')
    if Ans == 'Q':
        plt.errorbar(T[i], Q[i], Std[i], label = files_list[i], linestyle='None', marker='o')
        plt.title("4 Inch Diameter Si AlGaAs-coated: Q vs Temperature")
        plt.ylabel("Q (unitless)")
    if Ans == 'Phi':
        #i = 0
        #j = 0
        #while i < num_files-0.5:
        #    while j < len(T[i]) - 0.5:
        #        Phi[i][j] = 1.0/Phi[i][j]
        #        j += 1
        #    j = 0
        #    i += 1
        plt.errorbar(T[i], Phi[i], Std[i], label = files_list[i], linestyle='None', marker='o',)
        #plt.title("4 Inch Diameter Si AlGaAs-coated: Loss Angle $\phi$ vs Temperature")
        plt.ylabel("Loss Angle ($\phi$)", fontsize=14)
    i += 1
ax = plt.gca()
ax.set_yscale('log')
plt.xlabel("Temperature (K)", fontsize=14)
plt.grid()
plt.legend()
plt.show()
