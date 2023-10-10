import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import matplotlib.ticker as mticker
from matplotlib.ticker import LinearLocator
#This code generates the loss angle or spectral density for the Thermoelastic loss of a coated substrate.
#It initially uses the Zhou model to calculate loss from the interface, then the Cagnoli model to
#calculate loss from the bulk substrate. Bulk coating loss is considered negligible due to its miniscule
#thickness as compared to the substrate, but this can also be calculated using Fejer's effective
#medium approach.

#The below comment block contains all the prior information you need to simulate the 
#thermoelastic loss:
#You will need to enter coefficient of thermal expansion, thermal conductivity, and specific heat
#at constant volume of your substrate and coating(s). This can be used for room temperature GeNS
#if you only enter values at room temp (300 K) and select "Temp" as the quantity you wish to hold
#constant. For Cryo GeNS applications, you will need to know the physical parameters over your temperature
#range. You will also need a txt file holding the substrate dilution factors for a given mode family (generally
#this will be mode family 1 since those are the easiest modes to measure) and the frequencies of those modes.
#This can be found using the Cagnoli paper and matching their dilution factors to your measured
#mode frequencies (if using crystalline silicon substrates).
#This file should have the frequency as the first column and the dilution factor as the second column.
#Additionally, if your coating is a multi-layer, you will need to enter material properties for
#both materials. The below is coded for GaAs and AlGaAs.

#The script can plot as the independent variable Frequency (2D), Temperature (2D), or both (3D).
#Expression for interface loss comes from Zhou, Molina-Ruiz, Hellman, "Strategies to Reduce the
#Thermoelastic Loss of Multimaterial Coated Finite Substrates" on ArXiV
#The substrate loss comes from Cagnoli et al 2017 "Mode-dependent losses
#in disc resonators." Our silicon substrate crystal orientation is <100> when I was using them,
#though if you have ordered new substrates you should check that this is still correct for yours.

#Right now the program is coded for the alternating GaAs-AlGaAs layer on my (Nick Didio) Si resonators.

#Following lines all declare constants for substrate. Coating constants come after.
sub_al_300 = 2.6*(10**-6) #Units of 1/K (coefficient of thermal expansion)
sub_al_200 = 1.4*(10**-6)
sub_al_122 = -5.*(10**-8)
#sub_al_122 = -6.*(10**-8)
sub_al_100 = -33.*(10**-8)
#sub_al_100 = -38.*(10**-8)
sub_al_50 = -45.*(10**-8)
sub_al_20 = -0.27*(10**-8)
sub_al_12 = 0.13*(10**-8)
sub_kap_300 = 156  #Units of W/(m-K) (thermal conductivity)
sub_kap_250 = 195 #Extra temperatures for better interpolation
sub_kap_200 = 266
sub_kap_175 = 325
sub_kap_150 = 420
sub_kap_122 = 620
sub_kap_100 = 950
sub_kap_50 = 2600
sub_kap_20 = 3000
sub_kap_12 = 1800
#Heat capacity at constant volume
sub_cv_300 = 20.24 #Units of J/(mole-K) (converted to J/(kg-K) below)
sub_cv_250 = 19
sub_cv_200 = 17
sub_cv_122 = 10
sub_cv_100 = 7.5
sub_cv_50 = 2.5
sub_cv_20 = 1.6
sub_cv_12 = 1.45
sub_K = 95*(10**9) #Units of Pa, Bulk Modulus
sub_E = 169*(10**9) #Units of Pa, Young's Modulus
sub_p = .00233*(10**6) #Units of kg/(m^3)
sub_L = .0005 #Units of m (substrate thickness)
sub_sig = 0.28 #Poisson ratio, unitless, from azom.com
#Initialize the different linear expansion coefficients
#and specific heat at constant volume
#and thermal conductivity at different temperatures
sub_al = np.zeros(7)
sub_cv = np.zeros(8)#Extras for 250 K data point
sub_kap = np.zeros(10)#Extras for 250, 175, 150 K data points
sub_al[6] = sub_al_300
sub_al[5] = sub_al_200
sub_al[3] = sub_al_100
sub_al[2] = sub_al_50
sub_al[1] = sub_al_20
sub_al[4] = sub_al_122
sub_al[0] = sub_al_12
sub_cv[7] = sub_cv_300
sub_cv[6] = sub_cv_250
sub_cv[5] = sub_cv_200
sub_cv[3] = sub_cv_100
sub_cv[2] = sub_cv_50
sub_cv[1] = sub_cv_20
sub_cv[4] = sub_cv_122
sub_cv[0] = sub_cv_12
sub_kap[9] = sub_kap_300
sub_kap[8] = sub_kap_250
sub_kap[7] = sub_kap_200
sub_kap[6] = sub_kap_175
sub_kap[5] = sub_kap_150
sub_kap[3] = sub_kap_100
sub_kap[2] = sub_kap_50
sub_kap[1] = sub_kap_20
sub_kap[4] = sub_kap_122
sub_kap[0] = sub_kap_12
#Adjustment based on Zhou value
#sub_kap = sub_kap*0.6
u = 0.028 #Molar mass of Si (units of kg/mol)
sub_cv = sub_cv/u #convert cv to units of J/(kg-K)
#For testing altering values of substrate physical parameters
#i = 0
#while i < len(sub_al)-0.5:
#    sub_al[i] = sub_al[i]/10000
    #sub_kap[i] = sub_kap[i]*100
#    i += 1

#Initialize coating constants. This first one is AlGaAs. Note that thermal conductivity
#of AlGaAs-GaAs stacks are much lower than effective medium would suggest,
#so the lower values are from literature and match the GaAs values.
coat_E = 8.36*(10**10) #Young's Modulus, units of Pa
coat_sig = 0.40 #Poisson Ratio
coat_al_300 = 5.0*(10**-6) #Units of 1/K (coefficient of thermal expansion)
coat_al_200 = 3.65*(10**-6)
coat_al_122 = 1.4*(10**-6)
coat_al_100 = 0.8*(10**-6)
coat_al_50 = -0.13*(10**-6)
coat_al_20 = -1.0*(10**-8)
coat_al_12 = -1.0*(10**-9)
coat_kap_300 = 10  #Units of W/(m-K) (thermal conductivity)
coat_kap_250 = 12.5
coat_kap_200 = 15
coat_kap_175 = 16.4
coat_kap_150 = 18.1
coat_kap_122 = 20
coat_kap_100 = 25
coat_kap_50 = 75
coat_kap_20 = 250
coat_kap_12 = 350
#Specific Heat at constant volume
coat_cv_300 = 0.57 #Units of J/(g-K) (converted to J/(kg-K) below)
coat_cv_200 = 0.39
coat_cv_122 = 0.25
coat_cv_100 = 0.21
coat_cv_50 = 0.12
coat_cv_40 = 0.097
coat_cv_30 = 0.074
coat_cv_20 = 0.051
coat_cv_12 = 0.027
coat_K = 7.79*(10**10) #Units of Pa, bulk modulus
coat_p = .00233*(10**6) #Units of kg/(m^3), density
coat_L = 6.28*(10**-6) #Units of m, total thickness of coating
#Initialize the different linear expansion coefficients
#and specific heat at constant volume
#and thermal conductivity and wpeak at different temperatures
coat_al = np.zeros(7)
coat_cv = np.zeros(9)#More data points for better interpolation
coat_kap = np.zeros(10)#More data points for better interpolation
coat_al[6] = coat_al_300
coat_al[5] = coat_al_200
coat_al[3] = coat_al_100
coat_al[2] = coat_al_50
coat_al[1] = coat_al_20
coat_al[4] = coat_al_122
coat_al[0] = coat_al_12
coat_cv[8] = coat_cv_300
coat_cv[7] = coat_cv_200
coat_cv[5] = coat_cv_100
coat_cv[4] = coat_cv_50
coat_cv[3] = coat_cv_40
coat_cv[2] = coat_cv_30
coat_cv[1] = coat_cv_20
coat_cv[6] = coat_cv_122
coat_cv[0] = coat_cv_12
coat_cv = 1000*coat_cv #Convert units to J/(kg-K)
coat_kap[9] = coat_kap_300
coat_kap[8] = coat_kap_250
coat_kap[7] = coat_kap_200
coat_kap[6] = coat_kap_175
coat_kap[5] = coat_kap_150
coat_kap[3] = coat_kap_100
coat_kap[2] = coat_kap_50
coat_kap[1] = coat_kap_20
coat_kap[4] = coat_kap_122
coat_kap[0] = coat_kap_12
T0 = np.array([12, 20, 50, 100, 122, 200, 300]) #Tells interpolating
#function what temperatures the input constants are at. This is the default
#temperatures but I have specific arrays for when I've needed more points for
#better interpolation below.
#Below temperature arrays for thermal conductivity and cv, extra points
T0_kap = np.array([12, 20, 50, 100, 122, 150, 175, 200, 250, 300])
T0_coat_cv = np.array([12, 20, 30, 40, 50, 100, 122, 200, 300])
T0_sub_cv = np.array([12, 20, 50, 100, 122, 200, 250, 300])

#Initialize second coating. Note that for GaAs-AlGaAs the thermal conductivity
#of the multi-layer is not well approximated by effective medium calculations
#and should be taken from literature. Those sources also had specific heat,
#cv, so I used that value for both as well.
coat2_E = 8.53*(10**10) #Young's Modulus, units of Pa
coat2_sig = 0.31 #Poisson Ratio
coat2_al_300 = 5.8*(10**-6) #Units of 1/K (coefficient of thermal expansion)
coat2_al_200 = 4.5*(10**-6)
coat2_al_122 = 2.3*(10**-6)
coat2_al_100 = 1.9*(10**-6)
coat2_al_50 = -0.5*(10**-6)
coat2_al_20 = -1.0*(10**-7)
coat2_al_12 = -1.0*(10**-8)
coat2_K = 7.55*(10**10) #Units of Pa, bulk modulus
coat2_p = .00532*(10**6) #Units of kg/(m^3), density
coat2_al = np.zeros(7)
coat2_al[6] = coat_al_300
coat2_al[5] = coat_al_200
coat2_al[3] = coat_al_100
coat2_al[2] = coat_al_50
coat2_al[1] = coat_al_20
coat2_al[4] = coat_al_122
coat2_al[0] = coat_al_12
coat2_kap = coat_kap #Thermal conductivity from literature for stack
coat2_cv = coat_cv #Specific heat from literature for stack


#For testing altering values of coating physical parameters.
#Be weary of altering parameter array sizes.
#i = 0
#coat_al = coat_al/1.7
#coat_kap = coat_kap*2
#while i < len(coat_al)-0.5:
#    coat_al[i] = coat_al[i]/10000
#    i += 1

#Create the frequency array and temperature arrays.
#It is not necessary to create a temperature array if
#only checking thermoelastic loss at room temperature.
ndata = 100000 #This is the number of points created
#Below is the frequency range you wish to simulate.
#There is a problem here with extrapolating mode family dilution
#factors out above and below data range, so when plotting
#total loss (interface plus substrate bulk) you will only see
#the result in the frequency range between the first and last
#modes.
#Also note ndata is resized for the 3d model and all the interpolations
#are shortened as well. This happens at the beginning of the 3d modeling
#section (where neither temp nor frequency are restricted).
freq = np.logspace(-3.0, 10.0, num=ndata)
#print(freq[0], freq[ndata-1])
T_low = 12 #Put the lowest temperature that you have data for
T_high = 300 #Put the highest temperature that you have data for
Temper = np.linspace(T_low, T_high, num=ndata)
i = 0
j = 0

#Find the interpolated values of thermal expansion coefficient,
#specific heat, and thermal conductivity. This section
#can be commented out if you are only checking at room temp.
sub_f_al = interp1d(T0, sub_al, kind='cubic')
sub_f_cv = interp1d(T0_sub_cv, sub_cv, kind='cubic')
sub_f_kap = interp1d(T0_kap, sub_kap, kind='cubic')
coat_f_al = interp1d(T0, coat_al, kind='cubic')
coat_f_cv = interp1d(T0_coat_cv, coat_cv, kind='cubic')
coat_f_kap = interp1d(T0_kap, coat_kap, kind='cubic')
coat2_f_al = interp1d(T0, coat2_al, kind='cubic')
#Next nine arrays hold the actual interpolated values
sub_al_interp = sub_f_al(Temper)
sub_cv_interp = sub_f_cv(Temper)
sub_kap_interp = sub_f_kap(Temper)
coat_al_interp = coat_f_al(Temper)
coat_cv_interp = coat_f_cv(Temper)
coat_kap_interp = coat_f_kap(Temper)
coat2_al_interp = coat2_f_al(Temper)
coat2_cv_interp = coat_cv_interp #From literature for bulk coating
coat2_kap_interp = coat_kap_interp #From literature for bulk coating

'''  
#For plotting the interpolated values to compare to your loss curve (I recommend commenting out
#everything below this plot if you want to use this)
#print('Interpolated k at 300 K: ' + str(coat_kap_interp[len(Temper)-1]))
#print('Actual k at 300 K: ' + str(coat_kap_300))
plt.plot(Temper, coat_al_interp)
ax = plt.gca()
#ax.set_yscale('log')
#ax.set_xscale('log')
plt.title('Interpolation Plot')
plt.xlabel('Temperature (K)')
plt.ylabel('Your parameter here!')
plt.grid()
plt.show()
'''

def coth(x): #Cuts down on some of the math, numpy doesn't seem to have coth
    result = 1/np.tanh(x)
    return result

#Ask the user if they want a single temperature slice (and vary frequency)
#or if they want a single frequency slice (and vary temperature)
#or if they want to vary both (plot a surface instead of a line)
print("What variable will you hold constant? (Temp, Freq, None):")
Type = raw_input()

if Type == 'Temp':
    print("What temperature do you want to model interface thermoelastic loss for? Enter an integer please:")
    const_temp = raw_input()
    const_temp = float(const_temp)

    #First we will calculate the interface loss, then the substrate, then coating bulk, then add them.
    
    #Pick out the values of the physical parameters at the requested temperature
    difference_array = np.absolute(Temper-const_temp)
    index = difference_array.argmin()
    sub_al_const = sub_al_interp[index]
    sub_cv_const = sub_cv_interp[index]
    sub_kap_const = sub_kap_interp[index]
    coat_al_const = coat_al_interp[index]
    coat_cv_const = coat_cv_interp[index]
    coat_kap_const = coat_kap_interp[index]
    coat2_al_const = coat2_al_interp[index]

    #Initialize shortcut quantities used to calculate loss
    #We use AlGaAs quantities where we know them since that is contacting
    #the substrate. Bulk quantities for cv and thermal conductivity
    #are valid for this model.
    sub_gamma = np.zeros(len(freq), dtype=complex)
    coat_gamma = np.zeros(len(freq), dtype=complex)
    q = np.zeros(len(freq), dtype=complex)
    Theta_s_para = np.zeros(len(freq), dtype=complex)
    Theta_f_para = np.zeros(len(freq), dtype=complex)
    Theta_s_perp = np.zeros(len(freq), dtype=complex)
    Theta_f_perp = np.zeros(len(freq), dtype=complex)
    A = np.zeros(len(freq), dtype=complex) #Placeholder constant to make math easier for parallel phi
    B = np.zeros(len(freq), dtype=complex) #Placeholder constant to make math easier for perpendicular phi
    phi_para = np.zeros(len(freq))
    phi_perp = np.zeros(len(freq))
    phi_int = np.zeros(len(freq)) #Loss from the interface
    phi_tot = np.zeros(len(freq))
    R = ((coat_kap_const*coat_cv_const)/(sub_kap_const*sub_cv_const))**0.5
    i = 0
    a = (2*coat_L*(1-coat_sig)/coat_E) + (2*sub_L*(1-sub_sig)/sub_E)
    b = ((1-2*coat_sig)*(1+coat_sig)*coat_L/(coat_E*(1-coat_sig))) + ((1-2*sub_sig)*(1+sub_sig)*sub_L/(sub_E*(1-sub_sig)))
    #a and b are the same as A and B, placeholders
    #Note that A,a are for parallel and B,b are for perpendicular
    
    #Below constants are used for particular solutions for theta (see equations
    #2 and 5 and Appendix A of the paper)
    del_beta_para = 2*((coat_al_const/coat_cv_const)-(sub_al_const/sub_cv_const))
    del_beta_perp = (coat_al_const*(1+coat_sig))/(coat_cv_const*(1-coat_sig)) - (sub_al_const*(1+sub_sig))/(sub_cv_const*(1-sub_sig))
    
    while i < len(freq)-0.5:
        sub_gamma[i] = ((1+1j)*((np.pi*freq[i]*sub_cv_const/sub_kap_const)**0.5))
        coat_gamma[i] = ((1+1j)*((np.pi*freq[i]*coat_cv_const/coat_kap_const)**0.5))
        q[i] = (sub_gamma[i]*(sub_L))
        
        #To test values of gamma and q
        #print(sub_gamma[i].imag, coat_gamma[i].imag, q[i].imag)
        #break
        
        #Below constants are from particular solutions for theta from the paper
        #such that theta_1_f_parallel = Theta_1_f_parallel*sigma_0*T
        #Theta_1_j_parallel = Theta_j_para to keep things a little shorter
        #Same for del_beta_para and del_beta_perp, note that the multiplication
        #by temperature (const_temp) is carried out in the calculation of phi
        
        #To test values of del_beta
        #print(del_beta_para, del_beta_perp)
        #break
        
        Theta_f_para[i] = ((1/(np.cosh(coat_gamma[i]*coat_L)+R*np.sinh(coat_gamma[i]*coat_L)*coth(q[i]))))*del_beta_para
        Theta_f_perp[i] = ((1/(np.cosh(coat_gamma[i]*coat_L)+R*np.sinh(coat_gamma[i]*coat_L)*coth(q[i]))))*del_beta_perp
        Theta_s_para[i] = -1*((R/(coth(coat_gamma[i]*coat_L)*np.sinh(q[i])+R*np.cosh(q[i]))))*del_beta_para
        Theta_s_perp[i] = -1*((R/(coth(coat_gamma[i]*coat_L)*np.sinh(q[i])+R*np.cosh(q[i]))))*del_beta_perp
        
        #Theta_f[i] = ((1/(np.cosh(coat_gamma[i]*coat_L)+R*np.sinh(coat_gamma[i]*coat_L)*coth(q[i]))))*del_beta
        #Theta_s[i] = ((R/(coth(coat_gamma[i]*coat_L)*np.sinh(q[i])+R*np.cosh(q[i]))))*del_beta
        
        #To test values of Theta
        #print(Theta_f_para[i].imag, Theta_f_perp[i].imag, Theta_s_para[i].imag, Theta_s_perp[i].imag)
        #break

        #A and B are also placeholders for longer expressions to make things a little simpler when typing out phi expressions
        A[i] = (((2*coat_sig-2)*Theta_f_para[i]*coat_al_const*(coat_gamma[i]**-1)*np.sinh(coat_gamma[i]*coat_L))+((4-2*coat_sig)*sub_al_const*Theta_s_para[i]*np.cosh(sub_gamma[i]*sub_L)*coat_L)-(2*sub_al_const*Theta_s_para[i]*(sub_gamma[i]**-1)*np.sinh(sub_gamma[i]*sub_L)))
        B[i] = ((coat_al_const*Theta_f_perp[i]*(coat_gamma[i]**-1)*np.sinh(coat_gamma[i]*coat_L))+(2*coat_sig*sub_al_const*((1-coat_sig)**-1)*Theta_s_perp[i]*np.cosh(sub_gamma[i]*sub_L)*coat_L)-((1+sub_sig)*((1-sub_sig)**-1)*sub_al_const*Theta_s_perp[i]*(sub_gamma[i]**-1)*np.sinh(sub_gamma[i]*sub_L)))
        
        #To test values of A and B
        #print(A[i].imag, B[i].imag)
        #break

        #Calculate phi_para and phi_perp, then add to get phi_total
        phi_para[i] = 2*const_temp*abs(A[i].imag)/a
        phi_perp[i] = 2*const_temp*abs(B[i].imag)/b
        
        #To test values of phi_para and phi_perp
        #print(phi_para[i], phi_perp[i])

        phi_int[i] = (phi_para[i] + phi_perp[i])
        #break

        i += 1
    
    print('Do you want to simulate substrate data as well? (Y/N) Note that this will prevent you from seeing interface loss at frequencies outside your recorded:')
    substrate_loss_ans = raw_input()

    print('Do you want to simulate bulk coating loss as well due to a multilayer? (Y/N):')
    coating_loss_ans = raw_input()

    #print(phi_tot[0], phi_tot[i-1])
    #IMPORTANT: If you want to simulate just loss from the interface
    #plot the above phi_tot_int. Below I will add the loss from the substrate
    #to the loss from the interface to get the total loss of the system.
    #The substrate loss comes from Cagnoli et al 2017 Mode-dependent losses
    #in disc resonators
    
    if substrate_loss_ans == 'Y' and coating_loss_ans != 'Y':
        #Save the old freq and phi_int arrays, we will change
        #them later on to match up with the frequency range of our
        #modes
        old_phi_int = phi_int
        old_freq = freq

        #Initialize the debye peak, wpeak (only one when
        #temperature is held constant)
        wpeak = (sub_kap_const/sub_cv_const)*((np.pi/sub_L)**2)

        #Interpolate between the dilution factors for the
        #given mode family. First read in the file with frequency
        #in the first column and dilution factor in the second.
        print('Please enter the data file containing the mode frequencies and dilution factors for a single mode family (1st column = frequency, 2nd column = dilution factor):')
        mode_file = raw_input()
        with open(mode_file) as f:
            lines = f.readlines()
            mode_freq = [line.split()[0] for line in lines]
            D_fact = [line.split()[1] for line in lines]
        i = 0
        while i < len(mode_freq)-0.5:
            mode_freq[i] = float(mode_freq[i])
            D_fact[i] = float(D_fact[i])
            i += 1
        #Below is where the interpolation happens for the dilution factors
        f_D_fact = interp1d(mode_freq, D_fact, kind='cubic')
        D_fact_freq = np.linspace(mode_freq[0], mode_freq[len(mode_freq)-1], num=ndata)
        D_fact_interp = f_D_fact(D_fact_freq)
        
        #Test the D_fact interpolation
        #plt.plot(D_fact_freq, D_fact_interp)
        #plt.scatter(mode_freq, D_fact)
        #ax = plt.gca()
        #ax.set_yscale('log')
        #ax.set_xscale('log')
        #plt.title('D Factor Interpolation')
        #plt.xlabel('Frequency (Hz)')
        #plt.ylabel('Dilution Factor (unitless)')
        #plt.grid()
        #plt.show()
        
        #Now we need to further interpolate to get the same number of points between
        #the frequencies of the first and last mode for phi_int. First we find the
        #indices of phi_int that correspond to the first and last mode frequencies
        #Note that the frequencies won't perfectly align since there is a small
        #discrepancy between the freq and mode_freq arrays, but we produce so many
        #data points this discrepancy will be very small.
        difference_array = np.absolute(freq - D_fact_freq[0])
        index0 = difference_array.argmin()
        difference_array = np.absolute(freq - D_fact_freq[ndata-1])
        indexN = difference_array.argmin
        #Now chop off all parts of phi_int that are outside these two indices
        i = 1
        index_del = np.zeros(1) #We know the first index will get chopped
        while i < len(phi_int)-0.5:
            if i < index0 or i > indexN:
                index_del = np.append(index_del, i)
            i += 1
        freq = np.delete(freq, index_del)
        phi_int = np.delete(phi_int, index_del)
        #We can finally build the interpolated points between the modes
        f_phi_int = interp1d(freq, phi_int, kind='cubic', fill_value='extrapolate')
        phi_int_interp = f_phi_int(D_fact_freq)

        #Test the phi_int interpolation
        #plt.plot(old_freq, old_phi_int)
        #plt.plot(D_fact_freq, phi_int_interp)
        #ax = plt.gca()
        #ax.set_yscale('log')
        #ax.set_xscale('log')
        #plt.title('Interface Loss Interpolation')
        #plt.xlabel('Frequency (Hz)')
        #plt.ylabel('Interface TED')
        #plt.grid()
        #plt.show()

        #Create the angular frequency array
        w = 2*np.pi*D_fact_freq

        #Now we can finally craft all the substrate loss points (N=ndata)
        phi_sub = np.zeros(len(D_fact_freq))
        i = 0
        while i < len(D_fact_freq)-0.5:
            phi_sub[i] = D_fact_interp[i]*((3*sub_al_const)**2)*sub_K*const_temp*w[i]*wpeak/(sub_cv_const*(w[i]**2+wpeak**2))
            i += 1

        #And add the substrate loss to the interface loss
        phi_tot = phi_int_interp + phi_sub

        #Plot it
        plt.plot(D_fact_freq, phi_tot)
        #12 K loss of coated sample mode 1 plotted below
        if const_temp == 12.0:
            plt.scatter(390, 6.78*(10**-8))
        #122 K loss of coated sample mode 1 plotted below
        if const_temp == 122.0:
            plt.scatter(390, 8.78*(10**-8))
        #300 K loss of coated sample mode 1 plotted below
        if const_temp == 300.0:
            plt.scatter(390, 2.44*(10**-5))
        ax = plt.gca()
        ax.set_yscale('log')
        ax.set_xscale('log')
        plt.title('Thermoelastic Loss of AlGaAs Coated Silicon Substrate from Interface and Substrate')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Loss Angle $\phi_{TED}$')
        plt.grid()
        plt.show()

    if substrate_loss_ans == 'Y' and coating_loss_ans == 'Y':
        
        #Save the old freq and phi_int arrays, we will change
        #them later on to match up with the frequency range of our
        #modes
        old_phi_int = phi_int
        old_freq = freq

        #Initialize the debye peak, wpeak (only one when
        #temperature is held constant)
        wpeak = (sub_kap_const/sub_cv_const)*((np.pi/sub_L)**2)

        #Interpolate between the dilution factors for the
        #given mode family. First read in the file with frequency
        #in the first column and dilution factor in the second.
        print('Please enter the data file containing the mode frequencies and dilution factors for a single mode family (1st column = frequency, 2nd column = dilution factor):')
        mode_file = raw_input()
        with open(mode_file) as f:
            lines = f.readlines()
            mode_freq = [line.split()[0] for line in lines]
            D_fact = [line.split()[1] for line in lines]
        i = 0
        while i < len(mode_freq)-0.5:
            mode_freq[i] = float(mode_freq[i])
            D_fact[i] = float(D_fact[i])
            i += 1
        #Below is where the interpolation happens for the dilution factors
        f_D_fact = interp1d(mode_freq, D_fact, kind='cubic')
        D_fact_freq = np.linspace(mode_freq[0], mode_freq[len(mode_freq)-1], num=ndata)
        D_fact_interp = f_D_fact(D_fact_freq)
        
        #Test the D_fact interpolation
        #plt.plot(D_fact_freq, D_fact_interp)
        #plt.scatter(mode_freq, D_fact)
        #ax = plt.gca()
        #ax.set_yscale('log')
        #ax.set_xscale('log')
        #plt.title('D Factor Interpolation')
        #plt.xlabel('Frequency (Hz)')
        #plt.ylabel('Dilution Factor (unitless)')
        #plt.grid()
        #plt.show()
        
        #Now we need to further interpolate to get the same number of points between
        #the frequencies of the first and last mode for phi_int. First we find the
        #indices of phi_int that correspond to the first and last mode frequencies
        #Note that the frequencies won't perfectly align since there is a small
        #discrepancy between the freq and mode_freq arrays, but we produce so many
        #data points this discrepancy will be very small.
        difference_array = np.absolute(freq - D_fact_freq[0])
        index0 = difference_array.argmin()
        difference_array = np.absolute(freq - D_fact_freq[ndata-1])
        indexN = difference_array.argmin
        #Now chop off all parts of phi_int that are outside these two indices
        i = 1
        index_del = np.zeros(1) #We know the first index will get chopped
        while i < len(phi_int)-0.5:
            if i < index0 or i > indexN:
                index_del = np.append(index_del, i)
            i += 1
        freq = np.delete(freq, index_del)
        phi_int = np.delete(phi_int, index_del)
        #We can finally build the interpolated points between the modes
        f_phi_int = interp1d(freq, phi_int, kind='cubic', fill_value='extrapolate')
        phi_int_interp = f_phi_int(D_fact_freq)

        #Test the phi_int interpolation
        #plt.plot(old_freq, old_phi_int)
        #plt.plot(D_fact_freq, phi_int_interp)
        #ax = plt.gca()
        #ax.set_yscale('log')
        #ax.set_xscale('log')
        #plt.title('Interface Loss Interpolation')
        #plt.xlabel('Frequency (Hz)')
        #plt.ylabel('Interface TED')
        #plt.grid()
        #plt.show()

        #Create the angular frequency array
        w = 2*np.pi*D_fact_freq

        #Do Fejer's effective medium averaging for the layers. This is only necessary
        #for Young's modulus, Poisson ratio, and coefficient of thermal expansion
        #Note that in my case (coded below) the GaAs layer is one extra layer thicker
        #due to outer GaAs layer being twice as thick, so GaAs is 12 layers and
        #AlGaAs is 11 where each layer is 266 nm.
        coat2_L = (266*(10**-9))*12 #Total thickness of coating 2 (GaAs)
        coat1_L = (266*(10**-9))*11 #Total thickness of coating 1 (AlGaAs)
        layer_l = 266*(10**-9) #Thickness of individual layers
        E_avg = (coat1_L/(coat1_L+coat2_L))*coat_E + (coat2_L/(coat1_L+coat2_L))*coat2_E
        sig_avg = (coat1_L/(coat1_L+coat2_L))*coat_sig + (coat2_L/(coat1_L+coat2_L))*coat2_sig
        al_avg = (coat1_L/(coat1_L+coat2_L))*coat_al_const + (coat2_L/(coat1_L+coat2_L))*coat2_al_const
        E_div_sig_avg = (coat1_L/(coat1_L+coat2_L))*(coat_E/(1-coat_sig)) + (coat2_L/(coat1_L+coat2_L))*(coat2_E/(1-coat2_sig))
        E_al_div_sig_avg = (coat1_L/(coat1_L+coat2_L))*(coat_E*coat_al_const/(1-coat_sig)) + (coat2_L/(coat1_L+coat2_L))*(coat2_E*coat2_al_const/(1-coat2_sig))
        

        #Now we can finally craft all the substrate and coating loss points (N=ndata)
        phi_sub = np.zeros(len(D_fact_freq))
        g = np.zeros(len(D_fact_freq), dtype=complex) #Fejer shorthand variable to hold math
        g_imag = np.zeros(len(D_fact_freq))
        phi_coat = np.zeros(len(D_fact_freq))
        im = 1j
        #Tau = (coat_L**2)*coat_cv_const/coat_kap_const #Fejer constant
        Tau = 10**-15
        print('Tau equals ' + str(Tau))
        R = (coat_cv_const*coat_kap_const/(sub_cv_const*sub_kap_const))**0.5 #Fejer constant
        phi_coat_term1 = 2*coat_cv_const*const_temp/E_div_sig_avg
        phi_coat_term2 = (coat_cv_const**-1)*E_al_div_sig_avg - (sub_cv_const**-1)*(sub_E*sub_al_const/(1-sub_sig))
        phi_coat_term2 = phi_coat_term2**2
        i = 0
        while i < len(D_fact_freq)-0.5:
            phi_sub[i] = D_fact_interp[i]*((3*sub_al_const)**2)*sub_K*const_temp*w[i]*wpeak/(sub_cv_const*(w[i]**2+wpeak**2))
            g[i] = -1*np.sinh((im*w[i]*Tau)**0.5)/(((im*w[i]*Tau)**0.5)*((np.cosh((im*w[i]*Tau)**0.5)+R*np.sinh((im*w[i]*Tau)**0.5))))
            g_imag[i] = g[i].imag #Did this cuz I kept getting a weird error that may have impacted result
            phi_coat[i] = phi_coat_term1*phi_coat_term2*g_imag[i]
            i += 1
        

        #And add the substrate loss and coating loss to the interface loss
        #phi_tot = phi_int_interp + phi_coat
        phi_tot = phi_int_interp + phi_sub + phi_coat

        #Plot it
        plt.plot(D_fact_freq, phi_tot, label='Total')
        plt.plot(D_fact_freq, phi_sub, label='Substrate')
        plt.plot(D_fact_freq, phi_coat, label='Coating')
        plt.plot(D_fact_freq, phi_int_interp, label='Interface')
        #12 K loss of coated sample mode 1 plotted below
        if const_temp == 12.0:
            plt.scatter(390, 6.78*(10**-8))
        #122 K loss of coated sample mode 1 plotted below
        if const_temp == 122.0:
            plt.scatter(390, 8.78*(10**-8))
        #300 K loss of coated sample mode 1 plotted below
        if const_temp == 300.0:
            plt.scatter(390, 2.44*(10**-5))
        ax = plt.gca()
        ax.set_yscale('log')
        ax.set_xscale('log')
        plt.title('Total Thermoelastic Loss of AlGaAs Coated Silicon Substrate')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Loss Angle $\phi_{TED}$')
        plt.grid()
        plt.legend()
        plt.show()

    if substrate_loss_ans != 'Y' and coating_loss_ans != 'Y':
        title_str = 'AlGaAs Coated Thin Disk Resonator Thermoelastic Loss from Interface at ' + str(const_temp) + ' K'
        plt.plot(freq, phi_int)
        #12 K loss of coated sample mode 1 plotted below
        if const_temp == 12.0:
            plt.scatter(390, 6.78*(10**-8))
        #122 K loss of coated sample mode 1 plotted below
        if const_temp == 122.0:
            plt.scatter(390, 8.78*(10**-8))
        #300 K loss of coated sample mode 1 plotted below
        if const_temp == 300.0:
            plt.scatter(390, 2.44*(10**-5))
        ax = plt.gca()
        ax.set_yscale('log')
        ax.set_xscale('log')
        plt.title(title_str)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Thermoelastic Loss $\phi_{TE}$')
        plt.grid()
        plt.legend()
        plt.show()




if Type == 'Freq':
    print("What frequency do you want to model Thermoelastic Loss for? Enter an integer please:")
    const_freq = raw_input()
    const_freq = float(const_freq)

    #Calculate shortcut quantities then calculate loss
    sub_gamma = np.zeros(len(Temper), dtype=complex)
    coat_gamma = np.zeros(len(Temper), dtype=complex)
    q = np.zeros(len(Temper), dtype=complex)
    Theta_s_para = np.zeros(len(Temper), dtype=complex)
    Theta_f_para = np.zeros(len(Temper), dtype=complex)
    Theta_s_perp = np.zeros(len(Temper), dtype=complex)
    Theta_f_perp = np.zeros(len(Temper), dtype=complex)
    A = np.zeros(len(Temper), dtype=complex) #Placeholder constant to make math easier for parallel phi
    B = np.zeros(len(Temper), dtype=complex) #Placeholder constant to make math easier for perpendicular phi
    phi_para = np.zeros(len(Temper))
    phi_perp = np.zeros(len(Temper))
    phi_int = np.zeros(len(Temper))
    phi_tot = np.zeros(len(Temper))
    R = np.zeros(len(Temper))
    del_beta_para = np.zeros(len(Temper))
    del_beta_perp = np.zeros(len(Temper))
    i = 0
    a = (2*coat_L*(1-coat_sig)/coat_E) + (2*sub_L*(1-sub_sig)/sub_E)
    b = ((1-2*coat_sig)*(1+coat_sig)*coat_L/(coat_E*(1-coat_sig))) + ((1-2*sub_sig)*(1+sub_sig)*sub_L/(sub_E*(1-sub_sig)))
    #a and b are the same as A and B, placeholders
    #Note that A,a are for parallel and B,b are for perpendicular
    while i < len(freq)-0.5:
        R[i] = ((coat_kap_interp[i]*coat_cv_interp[i])/(sub_kap_interp[i]*sub_cv_interp[i]))**0.5
        sub_gamma[i] = ((1+1j)*((np.pi*const_freq*sub_cv_interp[i]/sub_kap_interp[i])**0.5))
        coat_gamma[i] = ((1+1j)*((np.pi*const_freq*coat_cv_interp[i]/coat_kap_interp[i])**0.5))
        q[i] = (sub_gamma[i]*(sub_L))
        #To test values of gamma and q
        #print(sub_gamma[i].imag, coat_gamma[i].imag, q[i].imag)
        #break
        #Below constants are from particular solutions for theta from the paper
        #such that theta_1_f_parallel = Theta_1_f_parallel*sigma_0*T
        #Theta_1_j_parallel = Theta_j_para to keep things a little shorter
        #Same for del_beta_para and del_beta_perp, note that the multiplication
        #by temperature is carried out in the calculation of phi
        
        del_beta_para[i] = 2*((coat_al_interp[i]/coat_cv_interp[i])-(sub_al_interp[i]/sub_cv_interp[i]))
        del_beta_perp[i] = (coat_al_interp[i]*(1+coat_sig))/(coat_cv_interp[i]*(1-coat_sig)) - (sub_al_interp[i]*(1+sub_sig))/(sub_cv_interp[i]*(1-sub_sig))
        
        #To test values of del_beta
        #print(del_beta_para[i], del_beta_perp[i])
        #break

        Theta_f_para[i] = ((1/(np.cosh(coat_gamma[i]*coat_L)+R[i]*np.sinh(coat_gamma[i]*coat_L)*coth(q[i]))))*del_beta_para[i]
        Theta_f_perp[i] = ((1/(np.cosh(coat_gamma[i]*coat_L)+R[i]*np.sinh(coat_gamma[i]*coat_L)*coth(q[i]))))*del_beta_perp[i]
        Theta_s_para[i] = -1*((R[i]/(coth(coat_gamma[i]*coat_L)*np.sinh(q[i])+R[i]*np.cosh(q[i]))))*del_beta_para[i]
        Theta_s_perp[i] = -1*((R[i]/(coth(coat_gamma[i]*coat_L)*np.sinh(q[i])+R[i]*np.cosh(q[i]))))*del_beta_perp[i]

        #To test values of Theta
        #print(Theta_f_para[i].imag, Theta_f_perp[i].imag, Theta_s_para[i].imag, Theta_s_perp[i].imag)
        #break
        
        #A and B are also placeholders for longer expressions to make things a little simpler when typing out phi expressions
        A[i] = (((2*coat_sig-2)*Theta_f_para[i]*coat_al_interp[i]*(coat_gamma[i]**-1)*np.sinh(coat_gamma[i]*coat_L))+((4-2*coat_sig)*sub_al_interp[i]*Theta_s_para[i]*np.cosh(sub_gamma[i]*sub_L)*coat_L)-(2*sub_al_interp[i]*Theta_s_para[i]*(sub_gamma[i]**-1)*np.sinh(sub_gamma[i]*sub_L)))
        B[i] = ((coat_al_interp[i]*Theta_f_perp[i]*(coat_gamma[i]**-1)*np.sinh(coat_gamma[i]*coat_L))+(2*coat_sig*sub_al_interp[i]*((1-coat_sig)**-1)*Theta_s_perp[i]*np.cosh(sub_gamma[i]*sub_L)*coat_L)-((1+sub_sig)*((1-sub_sig)**-1)*sub_al_interp[i]*Theta_s_perp[i]*(sub_gamma[i]**-1)*np.sinh(sub_gamma[i]*sub_L)))
        
        #To test values of A and B
        #print(A[i].imag, B[i].imag)
        #break

        #Calculate phi_para and phi_perp, then add to get phi_total
        phi_para[i] = (2*Temper[i]*abs(A[i].imag)/a)
        phi_perp[i] = (2*Temper[i]*abs(B[i].imag)/b)
        #To test values of phi_para and phi_perp
        #print(phi_para[i], phi_perp[i])

        phi_int[i] = (phi_para[i] + phi_perp[i])
        #break

        i += 1
    
    #print(phi_tot[0], phi_tot[i-1])
   
    #Now let's do the substrate loss
    print('Do you want to simulate substrate data as well? (Y/N) This will only work if the frequency you entered above falls between that of your first and last mode of the dilution factor family:')
    substrate_loss_ans = raw_input()
   
    print('Do you want to simulate coating thermoelastic loss as well? (Y/N):')
    coating_loss_ans = raw_input()

    if substrate_loss_ans == 'Y' and coating_loss_ans != 'Y':
        #Initialize the debye peaks, wpeak
        wpeak = np.zeros(len(Temper))
        i = 0
        while i < len(Temper)-0.5:
            wpeak[i] = (sub_kap_interp[i]/sub_cv_interp[i])*((np.pi/sub_L)**2)
            i += 1

        #We need to interpolate between the dilution factors, then
        #pick out the dilution factor that corresponds to the
        #frequency closest to the one entered by the user, const_freq.
        #Start by importing the dilution factor data.
        print('Please enter the data file containing the mode frequencies and dilution factors for a single mode family (1st column = frequency, 2nd column = dilution factor):')
        mode_file = raw_input()
        with open(mode_file) as f:
            lines = f.readlines()
            mode_freq = [line.split()[0] for line in lines]
            D_fact = [line.split()[1] for line in lines]
        i = 0
        while i < len(mode_freq)-0.5:
            mode_freq[i] = float(mode_freq[i])
            D_fact[i] = float(D_fact[i])
            i += 1
        #Below is where the interpolation happens for the dilution factors
        f_D_fact = interp1d(mode_freq, D_fact, kind='cubic')
        D_fact_freq = np.linspace(mode_freq[0], mode_freq[len(mode_freq)-1], num=ndata)
        #^This is a lot of data points, but it does make D_fact_interp the same
        #size as the temperature array, which is useful.
        D_fact_interp = f_D_fact(D_fact_freq)
        
        #Now that we have a bunch of dilution factors between the
        #first and last frequency, let's pick out the one the user wants.
        difference_array = np.absolute(D_fact_freq - const_freq)
        index = difference_array.argmin()
        #"index" is the element of D_fact_interp we want.
        D_fact_const = D_fact_interp[index]

        #Now that we have the dilution factor for our frequency,
        #we can calculate the loss
        i = 0
        w = const_freq*2*np.pi
        phi_sub = np.zeros(len(Temper))
        while i < len(Temper)-0.5:
            phi_sub[i] = D_fact_const*((3*sub_al_interp[i])**2)*sub_K*Temper[i]*w*wpeak[i]/(sub_cv_interp[i]*(w**2+wpeak[i]**2))
            i += 1
        
        #Add the substrate and interface losses
        phi_tot = phi_int + phi_sub

        #Import data and overlay if the user wants
        print('Do you want to import data to overlay as well? (Y/N):')
        Ans = raw_input()
        if Ans == 'Y':
            print('Please enter the text file that holds your data (Column 1 = Temperature, Column 2 = Loss, Column 3 = Error):')
            data_file = raw_input()
            T_Meas = {}
            Phi_Meas = {}
            StD_Meas = {}
            with open(data_file) as f:
                lines = f.readlines()
                T_Meas = [line.split()[0] for line in lines]
                Phi_Meas = [line.split()[1] for line in lines]
                StD_Meas = [line.split()[2] for line in lines]
            #Convert them to floats
            i = 0
            while i < len(T_Meas)-0.5:
                T_Meas[i] = float(T_Meas[i])
                Phi_Meas[i] = float(Phi_Meas[i])
                StD_Meas[i] = float(StD_Meas[i])
                i += 1
            plt.errorbar(T_Meas, Phi_Meas, StD_Meas, label='Measured Total Loss', linestyle='None', marker='o', color='red')

        #Plot the total loss
        plt.plot(Temper, phi_int, label='Modeled loss of interface', color='orange')
        plt.plot(Temper, phi_sub, label='Modeled loss of substrate', color='green')
        plt.plot(Temper, phi_tot, label='Modeled loss of substrate plus interface', color = 'blue')
        ax = plt.gca()
        ax.set_yscale('log')
        #ax.set_xscale('log')
        plt.title('Thermoelastic Loss of AlGaAs Coated Silicon Substrate and Coating Interface')
        plt.xlabel('Temperature (K)')
        plt.ylabel('Loss Angle $\phi_{TED}$')
        plt.legend()
        plt.grid()
        plt.show()

    if substrate_loss_ans == 'Y' and coating_loss_ans == 'Y':
        #Initialize the debye peaks, wpeak
        wpeak = np.zeros(len(Temper))
        i = 0
        while i < len(Temper)-0.5:
            wpeak[i] = (sub_kap_interp[i]/sub_cv_interp[i])*((np.pi/sub_L)**2)
            i += 1

        #We need to interpolate between the dilution factors, then
        #pick out the dilution factor that corresponds to the
        #frequency closest to the one entered by the user, const_freq.
        #Start by importing the dilution factor data.
        print('Do you have mode family data? (Y/N):')
        mode_fam_ans = raw_input()
        
        if mode_fam_ans == 'Y':
            print('Please enter the data file containing the mode frequencies and dilution factors for a single mode family (1st column = frequency, 2nd column = dilution factor):')
            mode_file = raw_input()
            with open(mode_file) as f:
                lines = f.readlines()
                mode_freq = [line.split()[0] for line in lines]
                D_fact = [line.split()[1] for line in lines]
            i = 0
            while i < len(mode_freq)-0.5:
                mode_freq[i] = float(mode_freq[i])
                D_fact[i] = float(D_fact[i])
                i += 1
            #Below is where the interpolation happens for the dilution factors
            f_D_fact = interp1d(mode_freq, D_fact, kind='cubic')
            D_fact_freq = np.linspace(mode_freq[0], mode_freq[len(mode_freq)-1], num=ndata)
            #^This is a lot of data points, but it does make D_fact_interp the same
            #size as the temperature array, which is useful.
            D_fact_interp = f_D_fact(D_fact_freq)
        
            #Now that we have a bunch of dilution factors between the
            #first and last frequency, let's pick out the one the user wants.
            difference_array = np.absolute(D_fact_freq - const_freq)
            index = difference_array.argmin()
            #"index" is the element of D_fact_interp we want.
            D_fact_const = D_fact_interp[index]
        
        if mode_fam_ans != 'Y':
            print('Please enter your substrate dilution factor for your chosen mode:')
            D_fact_const = raw_input()
            D_fact_const = float(D_fact_const)
        
        #First calculate effective medium quantities (Fejer)
        coat2_L = (266*(10**-9))*12 #Total thickness of coating 2
        coat1_L = (266*(10**-9))*11 #Total thickness of coating 1
        layer_l = 266*(10**-9) #Thickness of individual layers
        E_avg = (coat1_L/(coat1_L+coat2_L))*coat_E + (coat2_L/(coat1_L+coat2_L))*coat2_E
        sig_avg = (coat1_L/(coat1_L+coat2_L))*coat_sig + (coat2_L/(coat1_L+coat2_L))*coat2_sig
        E_div_sig_avg = (coat1_L/(coat1_L+coat2_L))*(coat_E/(1-coat_sig)) + (coat2_L/(coat1_L+coat2_L))*(coat2_E/(1-coat2_sig))
        i = 0
        E_al_div_sig_avg = np.zeros(len(Temper))
        while i < len(Temper)-0.5:
            E_al_div_sig_avg[i] = (coat1_L/(coat1_L+coat2_L))*(coat_E*coat_al_interp[i]/(1-coat_sig)) + (coat2_L/(coat1_L+coat2_L))*(coat2_E*coat2_al_interp[i]/(1-coat2_sig))
            i += 1

        #Now that we have the dilution factor for our frequency,
        #we can calculate the loss.
        i = 0
        w = const_freq*2*np.pi
        phi_sub = np.zeros(len(Temper))
        g = np.zeros(len(Temper), dtype=complex) #Fejer shorthand variable
        g_imag = np.zeros(len(Temper))
        phi_coat = np.zeros(len(Temper))
        phi_coat_term1 = np.zeros(len(Temper))
        phi_coat_term2 = np.zeros(len(Temper))
        im = 1j
        Tau = np.zeros(len(Temper))
        R = np.zeros(len(Temper))
        while i < len(Temper)-0.5:
            phi_sub[i] = D_fact_const*((3*sub_al_interp[i])**2)*sub_K*Temper[i]*w*wpeak[i]/(sub_cv_interp[i]*(w**2+wpeak[i]**2)) #Cagnoli substrate loss
            Tau[i] = (coat_L**2)*coat_cv_interp[i]/coat_kap_interp[i]
            #Below line to tune Tau, unphysical results otherwise
            Tau[i] = Tau[i]/400000
            R[i] = (coat_cv_interp[i]*coat_kap_interp[i]/(sub_cv_interp[i]*sub_kap_interp[i]))**0.5
            phi_coat_term1[i] = 2*coat_cv_interp[i]*Temper[i]/E_div_sig_avg
            phi_coat_term2[i] = (coat_cv_interp[i]**-1)*E_al_div_sig_avg[i] - (sub_cv_interp[i]**-1)*(sub_E*sub_al_interp[i]/(1-sub_sig))
            phi_coat_term2[i] = phi_coat_term2[i]**2
            g[i] = -1*np.sinh((im*w*Tau[i])**0.5)/(((im*w*Tau[i])**0.5)*((np.cosh((im*w*Tau[i])**0.5)+R[i]*np.sinh((im*w*Tau[i])**0.5))))
            g_imag[i] = g[i].imag #Did this cuz I kept getting a weird error that may have impacted result
            phi_coat[i] = phi_coat_term1[i]*phi_coat_term2[i]*g_imag[i]
            
            i += 1
        
        #Add the substrate and interface losses and coating losses
        phi_tot = phi_sub + phi_int + phi_coat 

        #Import data and overlay if the user wants
        print('Do you want to import data to overlay as well? (Y/N):')
        Ans = raw_input()
        if Ans == 'Y':
            print('Please enter the text file that holds your data (Column 1 = Temperature, Column 2 = Loss, Column 3 = Error):')
            data_file = raw_input()
            T_Meas = {}
            Phi_Meas = {}
            StD_Meas = {}
            with open(data_file) as f:
                lines = f.readlines()
                T_Meas = [line.split()[0] for line in lines]
                Phi_Meas = [line.split()[1] for line in lines]
                StD_Meas = [line.split()[2] for line in lines]
            #Convert them to floats
            i = 0
            while i < len(T_Meas)-0.5:
                T_Meas[i] = float(T_Meas[i])
                Phi_Meas[i] = float(Phi_Meas[i])
                StD_Meas[i] = float(StD_Meas[i])
                i += 1
            plt.errorbar(T_Meas, Phi_Meas, StD_Meas, label='Measured Total Loss', linestyle='None', marker='o', color='red')

        #Plot the total loss
        plt.plot(Temper, phi_int, label='Modeled thermoelastic loss of interface', color='orange')
        plt.plot(Temper, phi_sub, label='Modeled thermoelastic loss of substrate', color='green')
        plt.plot(Temper, phi_coat, label='Modeled thermoelastic loss of coating', color = 'purple')
        plt.plot(Temper, phi_tot, label='Total modeled thermoelastic loss', color = 'blue')
        ax = plt.gca()
        ax.set_yscale('log')
        #ax.set_xscale('log')
        plt.title('Total Thermoelastic Loss of AlGaAs Coated Silicon Substrate')
        plt.xlabel('Temperature (K)')
        plt.ylabel('Loss Angle $\phi_{TED}$')
        plt.legend()
        plt.grid()
        plt.show()


    if substrate_loss_ans != 'Y' and coating_loss_ans != 'Y':
        #Let's import data and overlay it as well (if the user wants)
        print('Do you want to import data to overlay as well? (Y/N):')
        Ans = raw_input()
        if Ans == 'Y':
            print('Please enter the text file that holds your data (Column 1 = Temperature, Column 2 = Loss, Column 3 = Error):')
            data_file = raw_input()
            T_Meas = {}
            Phi_Meas = {}
            StD_Meas = {}
            with open(data_file) as f:
                lines = f.readlines()
                T_Meas = [line.split()[0] for line in lines]
                Phi_Meas = [line.split()[1] for line in lines]
                StD_Meas = [line.split()[2] for line in lines]
            #Convert them to floats
            i = 0
            while i < len(T_Meas)-0.5:
                T_Meas[i] = float(T_Meas[i])
                Phi_Meas[i] = float(Phi_Meas[i])
                StD_Meas[i] = float(StD_Meas[i])
                i += 1
            plt.errorbar(T_Meas, Phi_Meas, StD_Meas, label='Measured Total Loss', linestyle='None', marker='o', color='red')

        title_str = 'AlGaAs Coated Thin Disk Resonator Thermoelastic Loss from Interface at ' + str(const_freq) + ' Hz'
        plt.plot(Temper, phi_int, label='Modeled Loss Due to Interface')
        ax = plt.gca()
        ax.set_yscale('log')
        #ax.set_xscale('log')
        plt.title(title_str)
        plt.xlabel('Temperature (K)')
        plt.ylabel('Thermoelastic Loss $\phi$')
        plt.grid()
        plt.legend()
        plt.show()




if Type == 'None':
    #We first resize everything so this doesn't take
    #a lifetime to compute. We resize ndata and
    #the frequencies simulated to lie between the first
    #and last mode. If no substrate data is wanted,
    #we simply plot between 1e1 and 1e6 Hz. These
    #can be changed if you want to change them.
    ndata = 1000
    print('Do you want to simulate substrate data as well? (Y/N) This will only plot frequencies between your first and last mode of the dilution factor mode family:')
    substrate_loss_ans = raw_input()
    
    if substrate_loss_ans == 'Y': 
        #Interpolate between the dilution factors for the
        #given mode family. First read in the file with frequency
        #in the first column and dilution factor in the second.
        print('Please enter the data file containing the mode frequencies and dilution factors for a single mode family (1st column = frequency, 2nd column = dilution factor):')
        mode_file = raw_input()
        with open(mode_file) as f:
            lines = f.readlines()
            mode_freq = [line.split()[0] for line in lines]
            D_fact = [line.split()[1] for line in lines]
        i = 0
        while i < len(mode_freq)-0.5:
            mode_freq[i] = float(mode_freq[i])
            D_fact[i] = float(D_fact[i])
            i += 1
        #Below is where the interpolation happens for the dilution factors
        f_D_fact = interp1d(mode_freq, D_fact, kind='cubic')
        D_fact_freq = np.linspace(mode_freq[0], mode_freq[len(mode_freq)-1], num=ndata)
        D_fact_interp = f_D_fact(D_fact_freq)
        
        #Test the D_fact interpolation
        #plt.plot(D_fact_freq, D_fact_interp)
        #plt.scatter(mode_freq, D_fact)
        #ax = plt.gca()
        #ax.set_yscale('log')
        #ax.set_xscale('log')
        #plt.title('D Factor Interpolation')
        #plt.xlabel('Frequency (Hz)')
        #plt.ylabel('Dilution Factor (unitless)')
        #plt.grid()
        #plt.show()
        
        #Now we create the frequency space which we will calculate
        #the losses over.
        D_fact_freq0_log = np.log10(D_fact_freq[0])
        D_fact_freqN_log = np.log10(D_fact_freq[len(D_fact_freq)-1])
        freq = np.logspace(D_fact_freq0_log, D_fact_freqN_log, num=ndata)
    
    if substrate_loss_ans != 'Y':
        freq = np.logspace(1.0, 6.0, num=ndata)

    #Create the temperature array.
    #It is not necessary to create a temperature array if
    #only checking thermoelastic loss at room temperature.
    #print(freq[0], freq[ndata-1])
    T_low = 12 #Put the lowest temperature that you have data for
    T_high = 300 #Put the highest temperature that you have data for
    Temper = np.linspace(T_low, T_high, num=ndata)
    i = 0
    j = 0

    #Find the interpolated values of thermal expansion coefficient,
    #specific heat, and thermal conductivity. This section
    #can be commented out if you are only checking at room temp.
    sub_f_al = interp1d(T0, sub_al, kind='cubic')
    sub_f_cv = interp1d(T0_sub_cv, sub_cv, kind='cubic')
    sub_f_kap = interp1d(T0_kap, sub_kap, kind='cubic')
    coat_f_al = interp1d(T0, coat_al, kind='cubic')
    coat_f_cv = interp1d(T0_coat_cv, coat_cv, kind='cubic')
    coat_f_kap = interp1d(T0_kap, coat_kap, kind='cubic')
    #Next six arrays hold the actual interpolated values
    sub_al_interp = sub_f_al(Temper)
    sub_cv_interp = sub_f_cv(Temper)
    sub_kap_interp = sub_f_kap(Temper)
    coat_al_interp = coat_f_al(Temper)
    coat_cv_interp = coat_f_cv(Temper)
    coat_kap_interp = coat_f_kap(Temper)

    '''  
    #For plotting the interpolated values to compare to your loss curve (I recommend commenting out
    #everything below this plot if you want to use this)
    #print('Interpolated k at 300 K: ' + str(coat_kap_interp[len(Temper)-1]))
    #print('Actual k at 300 K: ' + str(coat_kap_300))
    plt.plot(Temper, coat_al_interp)
    ax = plt.gca()
    #ax.set_yscale('log')
    #ax.set_xscale('log')
    plt.title('Interpolation Plot')
    plt.xlabel('Temperature (K)')
    plt.ylabel('Your parameter here!')
    plt.grid()
    plt.show()
    '''

    #Calculate shortcut quantities then calculate loss
    sub_gamma = np.zeros(len(Temper), dtype=complex)
    coat_gamma = np.zeros(len(Temper), dtype=complex)
    q = np.zeros(len(Temper), dtype=complex)
    Theta_s_para = np.zeros(len(Temper), dtype=complex)
    Theta_f_para = np.zeros(len(Temper), dtype=complex)
    Theta_s_perp = np.zeros(len(Temper), dtype=complex)
    Theta_f_perp = np.zeros(len(Temper), dtype=complex)
    A = np.zeros(len(Temper), dtype=complex) #Placeholder constant to make math easier for parallel phi
    B = np.zeros(len(Temper), dtype=complex) #Placeholder constant to make math easier for perpendicular phi
    phi_para = np.zeros(len(Temper))
    phi_perp = np.zeros(len(Temper))
    phi_int = np.zeros((len(Temper), len(freq)))
    phi_sub = np.zeros((len(Temper), len(freq)))
    phi_tot = np.zeros((len(Temper), len(freq)))
    #Temper and freq are the same size but I create the arrays
    #this way to remind me which axis holds which values.
    R = np.zeros(len(Temper))
    del_beta_para = np.zeros(len(Temper))
    del_beta_perp = np.zeros(len(Temper))
    i = 0
    j = 0
    a = (2*coat_L*(1-coat_sig)/coat_E) + (2*sub_L*(1-sub_sig)/sub_E)
    b = ((1-2*coat_sig)*(1+coat_sig)*coat_L/(coat_E*(1-coat_sig))) + ((1-2*sub_sig)*(1+sub_sig)*sub_L/(sub_E*(1-sub_sig)))
    #a and b are the same as A and B, placeholders
    #Note that A,a are for parallel and B,b are for perpendicular
    while j < len(Temper)-0.5:
        i = 0
        #The following quantity doesn't change with frequency,
        #and neither do any of the interpolated quantities. All
        #variables that don't will have j denote their index.
        R[j] = ((coat_kap_interp[j]*coat_cv_interp[j])/(sub_kap_interp[j]*sub_cv_interp[j]))**0.5
        del_beta_para[j] = 2*((coat_al_interp[j]/coat_cv_interp[j])-(sub_al_interp[j]/sub_cv_interp[j]))
        del_beta_perp[j] = (coat_al_interp[j]*(1+coat_sig))/(coat_cv_interp[j]*(1-coat_sig)) - (sub_al_interp[j]*(1+sub_sig))/(sub_cv_interp[j]*(1-sub_sig))
        #Note that multiplication by temperature is done in
        #calculation of phi_int
        while i < len(freq)-0.5:#Note that freq and Temper are same size to keep things simple
            sub_gamma[i] = ((1+1j)*((np.pi*freq[i]*sub_cv_interp[j]/sub_kap_interp[j])**0.5))
            coat_gamma[i] = ((1+1j)*((np.pi*freq[i]*coat_cv_interp[j]/coat_kap_interp[j])**0.5))
            q[i] = (sub_gamma[i]*(sub_L))
            #To test values of gamma and q
            #print(sub_gamma[j].imag, coat_gamma[j].imag, q[i].imag)
            #break
    
            Theta_f_para[i] = ((1/(np.cosh(coat_gamma[i]*coat_L)+R[j]*np.sinh(coat_gamma[i]*coat_L)*coth(q[i]))))*del_beta_para[j]
            Theta_f_perp[i] = ((1/(np.cosh(coat_gamma[i]*coat_L)+R[j]*np.sinh(coat_gamma[i]*coat_L)*coth(q[i]))))*del_beta_perp[j]
            Theta_s_para[i] = -1*((R[j]/(coth(coat_gamma[i]*coat_L)*np.sinh(q[i])+R[j]*np.cosh(q[i]))))*del_beta_para[j]
            Theta_s_perp[i] = -1*((R[j]/(coth(coat_gamma[i]*coat_L)*np.sinh(q[i])+R[j]*np.cosh(q[i]))))*del_beta_perp[j]

            #To test values of Theta
            #print(Theta_f_para[i].imag, Theta_f_perp[i].imag, Theta_s_para[i].imag, Theta_s_perp[i].imag)
            #break
        
            #A and B are also placeholders for longer expressions to make things a little simpler when typing out phi expressions
            A[i] = (((2*coat_sig-2)*Theta_f_para[i]*coat_al_interp[j]*(coat_gamma[i]**-1)*np.sinh(coat_gamma[i]*coat_L))+((4-2*coat_sig)*sub_al_interp[j]*Theta_s_para[i]*np.cosh(sub_gamma[i]*sub_L)*coat_L)-(2*sub_al_interp[j]*Theta_s_para[i]*(sub_gamma[i]**-1)*np.sinh(sub_gamma[i]*sub_L)))
            B[i] = ((coat_al_interp[j]*Theta_f_perp[i]*(coat_gamma[i]**-1)*np.sinh(coat_gamma[i]*coat_L))+(2*coat_sig*sub_al_interp[j]*((1-coat_sig)**-1)*Theta_s_perp[i]*np.cosh(sub_gamma[i]*sub_L)*coat_L)-((1+sub_sig)*((1-sub_sig)**-1)*sub_al_interp[j]*Theta_s_perp[i]*(sub_gamma[i]**-1)*np.sinh(sub_gamma[i]*sub_L)))
        
            #To test values of A and B
            #print(A[i].imag, B[i].imag)
            #break

            #Calculate phi_para and phi_perp, then add to get phi_total
            phi_para[i] = (2*Temper[i]*abs(A[i].imag)/a)
            phi_perp[i] = (2*Temper[i]*abs(B[i].imag)/b)
            #To test values of phi_para and phi_perp
            #print(phi_para[i], phi_perp[i])

            phi_int[j][i] = (phi_para[i] + phi_perp[i])
            #break

            i += 1
    
            #print(phi_int[0], phi_int[i-1])

        j += 1
    
    #Do the whole song and dance for substrate from above but
    #with temperature and frequency varying.
    
    if substrate_loss_ans == 'Y':
        #Initialize all the debye peaks, wpeak.
        #These only change over temperature.
        wpeak = np.zeros(len(Temper))
        i = 0
        while i < len(Temper)-0.5:
            wpeak[i] = (sub_kap_interp[i]/sub_cv_interp[i])*((np.pi/sub_L)**2)
            i += 1
        
        #We also need to initialize the angular frequency array
        w = np.zeros(len(freq))
        i = 0
        while i < len(freq)-0.5:
            w[i] = 2*np.pi*freq[i]
            i += 1
        
        i = 0
        j = 0
        while j < len(Temper)-0.5:
            i = 0
            while i < len(freq)-0.5:
                phi_sub[j][i] = D_fact_interp[i]*((3*sub_al_interp[j])**2)*sub_K*Temper[j]*w[i]*wpeak[j]/(sub_cv_interp[j]*(w[i]**2 + wpeak[j]**2))
                phi_tot[j][i] = phi_sub[j][i] + phi_int[j][i]
                i += 1
            j += 1

        #Ok, now let's plot our 3D surfaces generated.
        #These are phi_int_interp, phi_sub, and phi_tot.
        #I'm going to comment out the two smaller surfaces
        #since I don't have any experience plotting multiple
        #surfaces. A fun exercise for the reader!
        fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
        X, Y = np.meshgrid(freq, Temper)
        surf = ax.plot_surface(X, Y, np.log10(phi_tot), cmap=cm.coolwarm, edgecolor='none', linewidth=0, antialiased=False)
        #surf = ax.plot_surface(X, Y, np.log10(phi_sub), cmap=cm.coolwarm, edgecolor='none', linewidth=0, antialiased=False)
        #surf = ax.plot_surface(X, Y, np.log10(phi_int_interp), cmap=cm.coolwarm, edgecolor='none', linewidth=0, antialiased=False)
        fig.colorbar(surf)
        title_str = 'Modeled Thermoelastic Loss for AlGaAs Coated Silicon Substrate'
        ax.set_ylabel("Temperature (K)")
        ax.set_xlabel('Frequency (Hz)')
        ax.set_zlabel('Loss Angle log($\phi$)')
        ax.set_title(title_str)
        plt.show()

    #And if the user does not want to model substrate loss...
    if substrate_loss_ans != 'Y':
        fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
        X, Y = np.meshgrid(freq, Temper)
        surf = ax.plot_surface(X, Y, np.log10(phi_int), cmap=cm.coolwarm, edgecolor='none', linewidth=0, antialiased=False)
        fig.colorbar(surf)
        title_str = 'Modeled Thermoelastic Loss from Interface for AlGaAs Coated Silicon Substrate'
        ax.set_ylabel("Temperature (K)")
        ax.set_xlabel('Frequency (Hz)')
        ax.set_zlabel('Loss Angle log($\phi$)')
        ax.set_title(title_str)
        plt.show()


#'''




