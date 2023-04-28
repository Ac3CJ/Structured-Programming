# ====================================================================================================================================
#   Filename:     CascadeCircuit.py
#   Summary:      This is the main module of the program
#   Description:  This is the main code of the program, which handles the command line inputs, data processing and mathematics of the
#                 circuit. This calls the other modules to read and write to the designated files
#
#   Author:       C.J. Gacay 
# ====================================================================================================================================

# =========================================== NOTE TO SELF ===========================================
# outputTerms tuples are ordered as: (Output Index, Variable Name, Variable Unit, Decibel Boolean, Exponent)
# python CascadeCircuit.py -i a_Test_Circuit_1 -p [5,1,2]
# python CascadeCircuit.py a_Test_Circuit_1.net test.csv
# python AutoTest_08.py CascadeCircuit.py 1.0e-14 1.0e-14
# https://moodle.bath.ac.uk/pluginfile.php/2016444/mod_resource/content/6/Coursework_definition_2022_23_v01_pngfigs.pdf-correctedByPAVE%20%281%29.pdf

# =========================================== ERROR HANDLING NOTES ===========================================
# 1. Check if the blocks exist, this should throw the right error DONE
# 2. Check if the blocks are empty DONE
# 3. Check if there are no source components    DONE
# 4. Check for illegal node connections n1=1 n2=5 etc. DONE
# 5. Check for nonsense data in the .NET file, like non commented parts DONE
# 6. Check for when there is no closing delimeter DONE
# 7. Check for when there is no opening delimeter DONE
# 8. Check for spaces between the equals and value  DONE
# 9. Check for spaces between dB and unit. For example: dB mV   DONE
# 10. Check for incorrect naming for variables in file    DONE
# 11. Check if the graph input is within range for file.    DONE
# 12. Check if the same graph is being outputted    DONE
# 13. Check if there are uncommented comments, decide if the program should stop or ignore it DONE
# 14. Check for missing variable in circuit block   DONE
# 15. Check if both Fstart and Fend have an L or not    DONE
# 16. When resistance or inductance is 0 when parallel, and conductance or capacitance 0    DONE
# 17. Check for other component type letters, "A", "E", "P", etc. DONE
# 18. When there are multiple input sources DONE
# 19. Check when there are multiple values with the same nodes if they are in series DONE
# 20. Check for discontinued circuits: n1=1 n2=2 R=10       n1=3 n2=4 C=1e-6    DONE 
# 21. Check for divide by 0 in the maths        DONE
# 22. Zero load impedance and source impedance  DONE
# 23. Swap the end frequency and start frequency DONE

# =================================================================================================
# =========================================== LIBRARIES ===========================================
# =================================================================================================

import numpy as np
import math, sys, getopt, re, warnings
import DataReading as dataRead
import DataWriting as dataWrite

# ===================================================================================================
# =========================================== SUBROUTINES ===========================================
# ===================================================================================================

# ============================== ERROR HANDLING ==============================

def ErrorRaiseCommandLineEntry(systemArguments=[]):
    """
    This raises an error with pre-determined text for when there is an error in the command line

    Args:
        systemArguments (list, optional): _description_. Defaults to [].

    Raises:
        SyntaxError: Raises a syntax error that has occurred in the command line inputs
    """    
    raise SyntaxError("Invalid entry: " + ' '.join(systemArguments) +
                                              "\n Example Entries:\n python CascadeCircuit.py -i a_Test_Circuit_1 -p [5,1,2]\n python CascadeCircuit.py input.net output.csv")

# ============================== COMMAND LINE ==============================

def FormatCommandLine(systemArguments):
    """
    Formats the command line inputs so that it is in the standard form to work with the other subroutines. This ensures that edgecase inputs are formatted properly
    so that the program can read different styles user input.
    
    This takes in the command line input, creates a string of them separated by commas, extracts the graph parameters and removes it from the rest of the string, the 
    program then replaces the commas with spaces in the string (without graph parameters) and concatenates both strings together before splitting it by the white space.

    This is so that the graph parameters can be written as [5, 1, 2], [5,1,2], or [5,     1   ,   2] 

    Args:
        systemArguments (list): list of the arguments inputted by the user

    Returns:
        list: list of the arguments in the standard form
    """    
    graphParameterString = ""
    commandLineString = ",".join(systemArguments)

    commandLineString = re.sub(r"[[][.|/';:{}+,\s]*", "[", commandLineString)
    commandLineString = re.sub(r"[.|/';:{}+,\s]*[]]", "]", commandLineString)

    graphParameterPosition = re.search(r"[[]\d", commandLineString)

    if not (graphParameterPosition == None):
        graphParameterString = "".join(commandLineString[graphParameterPosition.start():])
        commandLineString = "".join(commandLineString[:graphParameterPosition.start()])

    commandLineString = re.sub(r",+[.|/';:{}+,\s]*", " ", commandLineString)
    commandLineString +=  graphParameterString
    return commandLineString.split()

def ReadCommandLine(systemArguments):
    """
    Reads the command line input from the user and extracts the relevant data from it

    Args:
        systemArguments (list): list of arguments inputted by the user

    Raises:
        OSError: file extension is invalid for .net
        OSError: file extension is invalid for .csv

    Returns:
        netFileName (str): string for the .net input file
        csvFileName (str): string for the .csv output file
        pngFileName (str): string for the .png output file
        userColumns (list): list of integers for user inputted graph columns
        graphBoolean (bool): boolean to detect that a graph has been requested
    """    
    graphParameters = "1"           # String of 1 to initialise the data
    graphBoolean = False
    fileBoolean = False
    options = [] 
    arguments = []
    pngFileName = ""

    systemArguments = FormatCommandLine(systemArguments)

    # Sets the netFileName and csvFileName to the first and second entries of the systemArguments, this gets overwritten if the user enters the file for a graph
    netFileName = systemArguments[0]
    if len(systemArguments) > 1: csvFileName = systemArguments[1]
    else: ErrorRaiseCommandLineEntry(systemArguments)

    # Reading System Inputs
    try:
        options, arguments = getopt.getopt(systemArguments,"i:p:")
    except getopt.GetoptError:
        print('Input invalid! Input line as: CascadeCircuit.py -i <inputfile> -p <parameter>')
        sys.exit(2)

    # Read the options that were written into the command line
    for optionAndArgument in options:
        if optionAndArgument[0] in ("-i", "--ifile"):
            netFileName = optionAndArgument[1] + ".net"
            csvFileName = optionAndArgument[1] + ".csv"
            pngFileName = optionAndArgument[1]
            fileBoolean = True
        elif optionAndArgument[0] in ("-p", "--param"):
            graphParameters = optionAndArgument[1].strip()
            graphBoolean = True

    # Check that the file extensions are correct and raise an error if they are not correct
    if not (".net" in netFileName): raise OSError("File extension is invalid: " + netFileName)
    if not (".csv" in csvFileName): raise OSError("File extension is invalid: " + csvFileName)

    # Arguments should be empty in this case, when it is full, then the command line prompt is written incorrectly
    if fileBoolean and len(arguments) > 0: ErrorRaiseCommandLineEntry(systemArguments)
    if fileBoolean == False and len(systemArguments) > 2: ErrorRaiseCommandLineEntry(systemArguments)

    if graphBoolean == True:
        if re.search(r".+[[]", graphParameters) or re.search(r"[]].+", graphParameters): ErrorRaiseCommandLineEntry(systemArguments)
        if re.search(r"[[]\d", graphParameters) == None or re.search(r"\d[]]", graphParameters) == None: ErrorRaiseCommandLineEntry(systemArguments) 

    # Convert the user inputted columns into a list of numbers 
    userColumns= re.findall(r'\d+', graphParameters)        # Use REGEX to extract all numbers
    userColumns = [int(i) for i in userColumns]             # Convert the strings into integers
    userColumns = dataRead.RemoveEmptyElements(userColumns)       
    userColumns = sorted(userColumns)

    return netFileName, csvFileName, pngFileName, userColumns, graphBoolean

# ============================== MATHEMATICS ==============================

def GetFrequencies(startFrequency, endFrequency, numberOfFrequencies, logBoolean):
    """
    Gets a list of frequencies to analyse the circuit over. If a logarithmic sweep is detected, then the frequencies will be calculated in log scale

    Args:
        startFrequency (float): The starting frequency
        endFrequency (float): The ending frequency
        numberOfFrequencies (float): _description_
        logBoolean (boolean): _description_

    Returns:
        list: list of frequencies for the system to analyse the circuit over
    """    
    if logBoolean: return np.logspace(math.log10(startFrequency), math.log10(endFrequency), int(numberOfFrequencies))
    return np.linspace(startFrequency, endFrequency, int(numberOfFrequencies))

def GetComponentMatrix(impedance, connectionType):
    """
    Gets the ABCD Matrix of each individual component

    Supporting Mathematics (Page 15): https://moodle.bath.ac.uk/pluginfile.php/2016444/mod_resource/content/6/Coursework_definition_2022_23_v01_pngfigs.pdf-correctedByPAVE%20%281%29.pdf

    Args:
        impedance (complex): The impedance of the component
        connectionType (_type_): The type of connection, 'S' for Series and 'P' for Parallel

    Returns:
        matrix (ndarray): ABCD Matrix of the component
    """    
    matrix = np.array([[1, 0],
                       [0, 1]])
    if connectionType == "S":
        matrix = np.array([[1, impedance],
                           [0, 1]])
    elif connectionType == "P":
        matrix = np.array([[1, 0],
                           [1/impedance, 1]])
    return matrix

def CalculateMatrix(circuitComponents, angularFrequency):
    """
    Calculates the ABCD Matrix for the circuit for a given frequency.
    Supporting Mathematics (Page 14): https://moodle.bath.ac.uk/pluginfile.php/2016444/mod_resource/content/6/Coursework_definition_2022_23_v01_pngfigs.pdf-correctedByPAVE%20%281%29.pdf

    Component types will be denoted by a single letter:
        'R': Resistor
        'G': Conductor
        'L': Inductor
        'C': Capacitor

    Args:
        circuitComponents (list): List of the circuit component data (Each element should be laid out as a tuple in the form (Connection Type, Component Type, Component Value))
        angularFrequency (float): Frequency (IN RADS) that circuit will be analysed on

    Returns:
        ABCDMatrix (ndarray): Overall ABCD Matrix of the circuit
    """    
    ABCDMatrix = np.identity(2)

    for individualComponent in circuitComponents:
        impedance = 0 + 0j
        connectionType = individualComponent[0]
        componentType = individualComponent[1]
        componentValue = individualComponent[2]
        try: 
            if   componentType == "R": impedance = componentValue
            elif componentType == "G": impedance = 1/componentValue
            elif componentType == "L": impedance = 1j*angularFrequency*componentValue
            elif componentType == "C": impedance = 1/(1j*angularFrequency*componentValue)
            else: raise ValueError("Unknown Component Found: " + " ".join(str(individualComponent)))
        except:
            raise ZeroDivisionError("Cannot divide by 0:\n(Connection Type, Component Type, Component Value, Exponent)\n" + " ".join(str(individualComponent)))
            
    
        if impedance != 0:                                                     
            componentMatrix = GetComponentMatrix(impedance, connectionType)
            ABCDMatrix = np.matmul(ABCDMatrix, componentMatrix)

    return ABCDMatrix

# =================================================================================================
# =========================================== MAIN CODE ===========================================
# =================================================================================================
def main():

    # ========================================================
    # ===================== COMMAND LINE =====================
    # ========================================================

    netFileName, csvFileName, pngFileName, userColumns, graphBoolean = ReadCommandLine(sys.argv[1:])

    # ========================================================
    # ===================== FILE READING =====================
    # ========================================================

    dataWrite.CreateFile(csvFileName)
    circuitText, termsText, outputText = dataRead.ReadFile(netFileName)

    print("READING CIRCUIT BLOCK")
    circuitComponents = dataRead.GetCircuitComponents(circuitText)

    print("READING TERMS BLOCK")
    inputSource, sourceImpedance, loadImpedance, startFrequency, endFrequency, numberOfFrequencies, logarithmicSweepBoolean = dataRead.GetTerms(termsText)
    
    print("READING OUTPUT BLOCK")
    outputTerms = dataRead.GetOutputOrder(outputText)

    dataRead.CheckEmptyListError(circuitComponents, "CIRCUIT")
    dataRead.CheckEmptyListError(outputTerms, "OUTPUT")

    # Check if the entered maximum column, the user entered is greater than the output terms or less than equal to 0
    if (((len(outputTerms)*2)) < max(userColumns)) or (min(userColumns) <= 0): raise IndexError("Column " + str(max(userColumns)) + 
                                                                                          " is out of range. Enter a value between 1-" + str(((len(outputTerms)*2))))

    # Write to the file to get the initial format
    dataWrite.InitialiseFile(csvFileName, outputTerms)   
    
    # ===============================================================================
    # =============================== DATA PROCESSING ===============================
    # ===============================================================================

    print("PROCESSING DATA")

    outputValues = {"inputVoltage": 0, "outputVoltage": 0, "inputCurrent": 0, "outputCurrent": 0, "inputPower": 0, "outputPower": 0, "inputImpedance": 0, "outputImpedance": 0,
        "voltageGain": 0, "currentGain": 0, "powerGain": 0, "transmittance": 0,}

    # For logspace, apply a log function to the frequencies so that the values are the base of the exponent
    frequencies = GetFrequencies(startFrequency, endFrequency, numberOfFrequencies, logarithmicSweepBoolean)

    # SUPPORTING MATHEMATICS IS LINKED AT THE TOP OF THE FILE
    for frequency in frequencies:
        ABCDMatrix = CalculateMatrix(circuitComponents, 2*math.pi*frequency)

        A_C = ABCDMatrix[0, 0]
        B_C = ABCDMatrix[0, 1]
        C_C = ABCDMatrix[1, 0]
        D_C = ABCDMatrix[1, 1]

        # Check for zero values and perform maths
        try:
            outputValues["inputImpedance"] = (A_C * loadImpedance + B_C) / (C_C * loadImpedance + D_C)
            outputValues["outputImpedance"] = (D_C * sourceImpedance + B_C) / (C_C * sourceImpedance + A_C)
            outputValues["voltageGain"] = loadImpedance / (A_C * loadImpedance + B_C)
            outputValues["currentGain"] = 1 / (C_C * loadImpedance + D_C)
            outputValues["powerGain"] = outputValues["voltageGain"] * np.conj(outputValues["currentGain"])
            outputValues["transmittance"] = 2 / (A_C * loadImpedance+B_C + C_C * loadImpedance * sourceImpedance + D_C * sourceImpedance)

            if "V" in inputSource[0]:
                outputValues["inputVoltage"] = inputSource[1] * (outputValues["inputImpedance"] / (sourceImpedance + outputValues["inputImpedance"]))
                outputValues["inputCurrent"] = outputValues["inputVoltage"] / outputValues["inputImpedance"]
            else:
                outputValues["inputCurrent"] = inputSource[1] * (sourceImpedance / (sourceImpedance + outputValues["inputImpedance"]))
                outputValues["inputVoltage"] = outputValues["inputCurrent"] * outputValues["inputImpedance"]
        except:
            raise ZeroDivisionError("Division by Zero has occurred in Output Calculations! Please check the CIRCUIT and TERMS Blocks in: " + netFileName)    
        
        outputValues["inputPower"] = outputValues["inputVoltage"] * np.conj(outputValues["inputCurrent"])
        outputValues["outputVoltage"] = outputValues["inputVoltage"] * outputValues["voltageGain"]
        outputValues["outputCurrent"] = outputValues["inputCurrent"] * outputValues["currentGain"]
        outputValues["outputPower"] = outputValues["outputVoltage"] * np.conj(outputValues["outputCurrent"])
        
        dataWrite.WriteDataToFile(outputTerms, list(outputValues.values()), csvFileName, frequency)

    print("WRITING DATA")

    # Output Graphs
    if graphBoolean == True: dataWrite.GenerateGraph(userColumns, csvFileName, pngFileName)

    print("ENDING PROGRAM")

# ===================================================================================================
# =========================================== END OF CODE ===========================================
# ===================================================================================================

if __name__ == "__main__":  # Allows code to be run as a script, but not when imported as a module. This is the top file
    main()
    #print(FormatCommandLine(sys.argv[1:]))
