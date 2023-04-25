# ====================================================================================================================================
#   Filename:     DataWriting.py
#   Summary:      The module that contains the code for writing the data to a .csv file or .png
#   Description:  This is a set of functions that are used to write the data into a .csv file. These include: Functions that write the
#                 information into the file, functions that format the numbers into the correct form, format the numbers and ensure
#                 that the data is written to the correct unit.
#
#   Author:       C.J. Gacay 
# ====================================================================================================================================

import matplotlib.pyplot as plt
import cmath
import numpy as np
import pandas as pd
import decimal

def ConvertToDecibel(value, outputVariable):
    """
    Converts the normal units into decibel units. This checks if the output variable is related to power and applies the relevant equation.

    Equation used: https://dspillustrations.com/pages/posts/misc/decibel-conversion-factor-10-or-factor-20.html#:~:text=The%20dB%20is%20calculated%20via,amplitude%2C%20the%20factor%20is%2020.

    Args:
        value (float): value to convert into decibels
        outputVariable (str): String of the output variable to check

    Returns:
        float: Converted decibel value
    """    
    if ("P" in outputVariable) or ("p" in outputVariable):  return 10*cmath.log10(abs(value))
    return 20*cmath.log10(abs(value))

def FormatNumber(value,n=11):
    """
    Formats the number for writing into the file. This rounds the number to 4 significant figures and converts them into scientific notation.
    This removes trailing zeros and also justifies the value to the right

    Args:
        value (float): The value to be formatted
        n (int, optional): This is how much to justify the text to the right by. Default is 11

    Returns:
        str: String format of the value, written in scientific notation to 4 significant figures
    """    
    return ('%.3e' % decimal.Decimal(value)).rjust(n)

def WriteDataToFile(outputTerms, outputs, fileName, frequency):
    """
    Writes the output data into the .csv file given that the file is open for editing. This function also converts the value into decibels and polar form when stated.
    outputTerm lists are laid out as: (Output Index, Variable Name, Variable Unit, Decibel Boolean, Exponent)

    Supporting Mathematics are linked below:
    
    Converting complex numbers to magnitude in dB and phase in rads: https://www.rohde-schwarz.com/uk/faq/converting-the-real-and-imaginary-numbers-to-magnitude-in-db-and-phase-in-degrees-faq_78704-30465.html
        
    Conversion to decibels: https://dspillustrations.com/pages/posts/misc/decibel-conversion-factor-10-or-factor-20.html#:~:text=The%20dB%20is%20calculated%20via,amplitude%2C%20the%20factor%20is%2020.

    Args:
        outputTerms (list): List of all of the output terms. This is a list of lists
        outputs (list): List of all of the output values
        fileName (str): Name of the file to write to
        frequency (float): Frequency that is being analysed
    """    
    decibelValue = 0
    with open(fileName, 'a') as file:
        file.write("\n"+FormatNumber(frequency,10))

    for outputTerm in outputTerms:
        outputIndex = outputTerm[0]
        #outputs[outputIndex] = outputs[outputIndex] / (10 ** outputTerm[4])     # Applies the exponent to the value

        # Checks if the value is read in decibels
        if (outputTerm[3]):
            decibelValue = ConvertToDecibel(outputs[outputIndex], outputTerm[1])
            firstPart = np.real(decibelValue)
            secondPart = np.angle(outputs[outputIndex])
        else:
            outputs[outputIndex] = outputs[outputIndex] / (10 ** outputTerm[4])     # Applies the exponent to the value
            firstPart = np.real(outputs[outputIndex])
            secondPart = np.imag(outputs[outputIndex])

        with open(fileName, 'a') as file:
            file.write("," + FormatNumber(firstPart) + "," + FormatNumber(secondPart))

    with open(fileName, 'a') as file:
            file.write(",")
    return

def InitialiseFile(fileName, outputTerms):
    """
    Initialises the file for writing by filling in the variables and units for each column

    Args:
        fileName (str): Name of the file to write to
        outputTerms (list): List of all of the output terms to consider
    """
    with open(fileName, 'a') as file:
        file.write("      Freq")
        for outputTerm in outputTerms:
            variable, variableUnit, decibleCheck = outputTerm[1:4]

            # Prints as in absolute and angle or real and imaginary depending on if it is a decibel value or not. Text is justified to the right
            if (decibleCheck): file.write("," + ("|" + str(variable) + "|").rjust(11) + ","+ ("/_" + str(variable)).rjust(11))
            else:               file.write(","+ ("Re(" + str(variable) + ")").rjust(11)+","+ ("Im(" + str(variable) + ")").rjust(11))      
        file.write("\n        Hz")
        for outputTerm in outputTerms:
            variable, variableUnit, decibleCheck = outputTerm[1:4]      # Unpacks the necessary data from the output terms from the list
            if (decibleCheck): file.write("," + (str(variableUnit)).rjust(11) + ",       Rads")                         # When in decibels, write in the unit and rads 
            else:               file.write("," + str(variableUnit).rjust(11) + "," + str(variableUnit).rjust(11))       # Displays the normal units otherwise
    return

def GenerateGraph(userColumns, inputFile, outputFile):
    """
    Generates the graphs for user-stated columns

    Args:
        userColumns (list): List of the user-stated columns for graph printing
        inputFile (str): File to read data from
        outputFile (str): File to print the graph image to
    """    
    graphColumns = [0,] + userColumns                                           # Joins the list of user inputs to a 0 to include the frequency
    outputData = pd.read_csv(inputFile, skiprows=[0, 1], usecols=graphColumns)  # Skip the first 2 rows as they contain the variable and units
    variables = pd.read_csv(inputFile, nrows=0, usecols=graphColumns)           # Creates a dictionary with the headers as keys
    unit = pd.read_csv(inputFile, nrows=1, usecols=graphColumns)                # Creates a table of values where the units are indexed at 0

    for i in range(1, len(graphColumns)):
        outputData.plot(0, i)                                                 # Plot with frequency on x axis and other data on y axis
        # Prints the axis labels with the units
        plt.xlabel("Frequency / Hz")
        plt.ylabel(list(variables.keys())[i] + " / " + unit.values[0][i])
        plt.legend("")
        plt.savefig(outputFile + "_" + str(graphColumns[i]) + ".png")
    return  

def CreateFile(fileName):
    """
    Creates an empty file with the inputted fileName. This MUST include the file extension

    Args:
        fileName (str): Name of the file
    """    
    with open(fileName, 'w') as file:
        file.write("")
    return
