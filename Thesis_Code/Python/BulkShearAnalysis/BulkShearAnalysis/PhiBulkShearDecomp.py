#This script takes in the frequencies, loss angles, modeled TE loss (eventually)
#and standard deviations in loss for a given temperature. It also takes in
#the coating bulk/shear dilution factors at each frequency. It then performs a fit of the following equation
#assuming shear is constant across frequency and bulk scales with f:
#Phi(imported) = D_shear*Phi_shear + D_bulk*(Phi_bulk + Phi_TE)
#python4mpia.github.io/fitting_data/least-squares-fitting.html for reference info. Comments will reference this page.
#For now this program runs one temperature at a time.
#TE has yet to be added, but once 12 K decomposition works, the modeled TE
#will be added to be run at warmer temperatures

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

#Ask the user what temperature we are fitting the loss at
print("What temperature is the loss data being fit at? Please enter an integer below:")
Temperature_str = raw_input()
Temperature_in = int(Temperature_str)

#Read in the frequencies and the associated dilution factors and total losses at those frequencies
print("Please enter the data file that holds the mode frequencies, loss, and standard deviation:")
loss_file = raw_input()
Freq = {}
Phi_tot = {}
Std_tot = {}
with open(loss_file) as f:
    lines = f.readlines()
    Freq = [line.split()[0] for line in lines]
    Phi_tot = [line.split()[1] for line in lines]
    Std_tot = [line.split()[2] for line in lines]
i = 0
while i < len(Freq) - 0.5:
    Freq[i] = float(Freq[i])
    Phi_tot[i] = float(Phi_tot[i])
    Std_tot[i] = float(Std_tot[i])
    i += 1

#Read in the dilution factors, and tell the user to make sure they line up with the frequency/loss file
print("Please enter the text file that holds the dilution factors. Bulk should be the first column, and shear the right. Make sure they line up row by row with the correct frequency from the previous file:")
dilution_file = raw_input()
D_bu = {}
D_sh = {}
with open(dilution_file) as f:
    lines = f.readlines()
    D_bu = [line.split()[0] for line in lines]
    D_sh = [line.split()[1] for line in lines]
i = 0
while i < len(D_bu) - 0.5:
    D_bu[i] = float(D_bu[i])
    D_sh[i] = float(D_sh[i])
    i += 1

#Define the model we will be fitting then perform the fit on that model. Stack overflow
#"Python curve_fit with multiple independent variables" for info on how this works.
def model(I, Phi_bu, Phi_sh):
    #The Dilution factors, and frequency are our data (I=independent variables)
    #and everything else is parameters to be fit.
    Freq, D_bu, D_sh = I
    #Phi_tot_fit = D_sh*Phi_sh + D_bu*Phi_bu*Freq
    #Above line assumes linear scaling of Phi_bu with frequency
    Phi_tot_fit = D_sh*Phi_sh + D_bu*Phi_bu
    #Above line assumes no scaling of Phi_bu with frequency
    return Phi_tot_fit

#Fit it. But jump around the initial parameter space and keep the fit that minimizes the residuals.
i = 0.
j = 0.
k = 0.
N_start = 50 #N_start**2 is the number of starting positions to be tested across the parameter space
Phi_sh_guess = 10.**-30
Phi_bu_guess = 10.**-30
perr = 10000000 #Initialize the error that we will compare at the end of each fit guess
popt = 'Start'
pcov = 'Start'
while i < N_start - 0.5:
    j = 0
    while j < N_start - 0.5:
        guess = np.array([Phi_bu_guess*(1.+10.**(i/2)), Phi_sh_guess*(1.+10.**(j/2))])
        #^Change starting position of our three guesses
        #popt_new, pcov_new = curve_fit(model, (Freq, D_bu, D_sh), Phi_tot, guess, sigma=Std_tot, bounds=(0, [10.**-1, 10.**-1]))
        popt_new, pcov_new = curve_fit(model, (Freq, D_bu, D_sh), Phi_tot, guess, sigma=Std_tot)
        perrdiag_new = np.sqrt(np.diag(pcov_new))
        perr_new = np.dot(perrdiag_new, perrdiag_new)
        if perr_new < perr:
            print(popt, perr)
            popt = popt_new
            pcov = pcov_new
            perr = perr_new
        j += 1
    print(i)
    i += 1

print(popt, perr)

#Note popt[0] = Phi_bu     popt[1] = Phi_sh
StdModel = np.zeros(len(Freq))
Phi_tot_fit = np.zeros(len(Freq))
i = 0
while i < len(Freq) - 0.5:
    #Phi_tot_fit[i] = D_sh[i]*popt[1] + D_bu[i]*popt[0]*Freq[i]
    #Above line assumes linear scaling between Phi_Bu and frequency
    Phi_tot_fit[i] = D_sh[i]*popt[1] + D_bu[i]*popt[0]
    #Above line assumes no scaling of Phi_bu with frequency
    i += 1
plt.errorbar(Freq, Phi_tot, Std_tot, linestyle='None', label='Total Loss Data', marker='o')
plt.errorbar(Freq, Phi_tot_fit, StdModel, label = 'Fitted Loss', marker='x')
i = 0
FreqModel = np.linspace(300, 10000, 100)
Phi_bu = np.zeros(len(FreqModel))
Phi_sh = np.zeros(len(FreqModel))
Phi_TE = np.zeros(len(FreqModel))
StdModel = np.zeros(len(FreqModel))
while i < len(FreqModel) - 0.5:
    #Phi_bu[i] = popt[0]*FreqModel[i]
    #Above line assumes linear scaling between Phi_Bu and frequency
    Phi_bu[i] = popt[0]
    #Above line assumes no scaling between Phi_Bu and frequency
    Phi_sh[i] = popt[1]
    i += 1
plt.errorbar(FreqModel, Phi_bu, StdModel, label = 'Bulk Loss', marker = 'None')
plt.errorbar(FreqModel, Phi_sh, StdModel, label = 'Shear Loss', marker = 'None')
ax = plt.gca()
ax.set_yscale('log')
plt.xlabel("Frequency (Hz)")
plt.ylabel("Loss Angle")
plt.title("AlGaAs " + Temperature_str + "K Loss vs Mode Frequency: Bulk Shear Decomposition")
plt.grid()
plt.legend()
plt.show()
