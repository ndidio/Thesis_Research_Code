#This code takes as input the .csv or .txt files that the temperature controller spits out.
#It converts that file to however many .txt files the user wants. The maximum is five.
#Three for the three temperature probes, and two for the two heater powers.
#Each file has the time on the first column and the user's desired quantity on the second column.

import numpy as np

#Ask the user what file they want to convert
print("Please enter the .csv or .txt file you wish to convert:")
primary_file = raw_input()

#First chop off the top line that is just info about what each column is
primary = open(primary_file, "r")
lines = primary.readlines()
primary.close()
del lines[0]
chopped = open('Chopped_Data.txt', "w+")
for line in lines:
    chopped.write(line)
chopped.close()

#Now the data itself (delimited by commas) is held in the file called 'Chopped_Data.txt'
#Next we ask the user which quantity or quantities they want to extract
print("How many quantities do you wish to extract? (Maximum of 5)")
num_params = raw_input()
num_params = int(num_params)

#Now we ask which parameters they want to extract
print("Which parameters do you want to extract? Type them one at a time.")
print("SampleFloor, Stage, PulseTube, SampleHeat, and CH Heat are the five options")
i = 0
params = [0]
while i < num_params-0.5:
    params.append(raw_input())
    i += 1

'''#Test Printing
print('Here is what params looks like after it is taken in:')
print(params)
'''

#Now 'params' is a list holding the names of the parameters we want.
#Let's convert each parameter in that list to a column number.
text_params = []
for i in range(len(params)):
    text_params.append(params[i])#Save the old params to text_params
for i in range(len(params)):
    if params[i] == 'SampleFloor':
        params[i] = int(1)
    if params[i] == 'Stage':
        params[i] = int(2)
    if params[i] == 'PulseTube':
        params[i] = int(4)
    if params[i] == 'SampleHeat':
        params[i] = int(7)
    if params[i] == 'CH Heat':
        params[i] = int(12)

#Test Printing
#print('Here is what params looks like after it is converted to column number:')
#print(params)

#'params' now holds the column numbers of the desired quantities. Let's use those and chopped to make the .txt files.
chopped = open('Chopped_Data.txt', "r")
lines = chopped.readlines()
i = 1
j = 0
while i < len(params)-0.5:
    result = []
    j = 0
    while j < len(lines)-0.5:
        result.append(lines[j].split(',')[0])
        #print(i, params[i], j, lines[j])
        result.append(lines[j].split(',')[params[i]] + '\n')
        j += 1
    txtfile = open("TimeVsTemp" + text_params[i] + ".txt","w")
    for element in result:
        txtfile.write(element + ' ')
    txtfile.close
    i += 1
