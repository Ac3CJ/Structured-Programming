# =========================================== TO DO LIST ===========================================
# Default output terms order (Vin (0), Vout (1), Iin (2), Iout (3), Pin (4), Pout (5), Zin (6), Zout (7), Av (8), Ai (9), Ap (10), T (11))
# outputTerms tuples are ordered as: (Output Index, Variable Name, Variable Unit, Decibel Boolean, Exponent)
# 3. Maybe consider what happens when there are two parallel components
#    connected in series between two nodes (not including common node)
# 12. Find a way to make the printing of output terms O(n) instead of O(n^2)
# 17. Make the maths more readable
# 18. Sort out logarithmic sweep
# 19. Figure out why the maths is wrong for Ext_a_Test_Circuit_1

# =========================================== ERROR HANDLING NOTES ===========================================
# 1. Check if the blocks exist, this should throw the right error
# 2. Check if the blocks are empty
# 3. Check if there are no source blocks
# 4. Check for illegal node connections n1=1 n2=5 etc.
# 5. Check for nonsense data in the .NET file, like non commented parts
# 6. Check for when there is no closing delimeter
# 7. Check for when there is no opening delimeter
# 8. Check for spaces between the equals and value
# 9. Check for spaces between dB and unit. For example: dB m V
# 10. Check for incorrect naming for variables in file

# =========================================== LIBRARIES ===========================================
import numpy as np
import math
import cmath

# =========================================== SUBROUTINES ===========================================

# ======================== READING AND ORGANISING DATA ========================

# ============== GENERAL ==============

def RemoveComments(file):
    """
    Removes the comments from the .NET file that is being read

    Args:
        file (_io.TextIOWrapper): This is the file that will be read

    Returns:
        text (str): String of file without the comments 
    """
    text = ""
    for line in file:
        if not (line.startswith('#')):     # Checks if the line doesn't start with a #
            text += line

    return text

def ExtractBlock(text, start, end):
    """
    Uses indexing to return the parts between start and end.
    Finds the instance of the start delimiter, then uses that as the beginning index, 
    then adds the length of the delimiter in case it is longer than a character. 
    Finds the final instance of the ending delimiter and uses that as the end of the index. 
    This can be used as each file has specific code blocks in the .NET files

    Args:
        text (str): Text to extract from
        start (str): The delimiter for the start of the block
        end (str): The delimiter for the end of the block

    Returns:
        text (str): Text between the start and end delimiters
    """
    return text[text.find(start)+len(start):text.rfind(end)]     

def RemoveEmptyElements(list0):
    """
    Removes empty elements from a list

    Args:
        list0 (list): The list to have empty elements removed

    Returns:
        list: New list without empty elements
    """    
    return list(filter(None, list0))

def ExtractExponent(prefix):
    """
    Extracts the exponent from the prefix of the units for each variable. This is a case statement to set the exponent for each variable.

    More information about this can be found in the table: https://basicelectronicscoed.files.wordpress.com/2015/07/metric-prefixes.png

    Args:
        prefix (str): String that contains the character for the prefix

    Returns:
        int: This is the exponent value
    """    
    if   "p" in prefix:  return -12
    elif "n" in prefix:  return -9
    elif "u" in prefix:  return -6
    elif "m" in prefix:  return -3
    elif "k" in prefix:  return 3
    elif "M" in prefix:  return 6
    elif "G" in prefix:  return 9
    else: return 0

# ============== CIRCUIT BLOCK ==============

def CheckComponentType(data):
    """
    Checks for the component type of the component

    Args:
        data (str): Holds the specific data for the component, either node data or component data

    Returns:
        Boolean: Will return True if the data includes the component type, False if it is node data
    """    
    if ('R' in data) or ('G' in data) or ('C' in data) or ('L' in data):
        return True
    return False

def ConvertCircuitData(component):
    """
    Converts the component data from str into a tuple that contains the relevant data.

    Tuple is in the form: (node 1, node 2, component type, component value)

    Nested Functions:
        AssignComponentData(arg1): Used to assign correct component data

    Args:
        component (str): String that contains the node data and component type and value

    Returns:
        componentData (tuple): Tuple containing the node component data
    """
    def AppendComponentData(data):
        """
        Appends the component data and ensures that all the relevant information is included.
        
        This is a nested function so the componentData can be directly manipulated as it is a
        variable from the outer function.

        Args:
            data (str): String of the split component data, can be connected nodes or component type.
        """        
        if not ("=" in data):
            componentData.append(ExtractExponent(data))
            return
        
        if (CheckComponentType(data)):
            componentData.append(data.split("=")[0])

        value = float(data.split("=")[1])
        componentData.append(value)
    
    component = component.split(" ")
    componentData = []

    for i in range(0, len(component)):
        try:
            AppendComponentData(component[i])
        except:
            raise TypeError("Invalid Data Type Entered: " + str(component[i]) + "\n Please Check Circuit")
        
    if len(componentData) >= 5: componentData[3] = componentData[3] * (10 ** componentData[4])  # Apply exponent to value

    return tuple(componentData)

def GetCircuitComponents(circuit):
    """
    Gets the components and relevant information of each component included in the circuit

    Args:
        circuit (str): String containing all of the information of the circuit components

    Returns:
        circuitComponents (list): List of tuples where each tuple contains the component information

    Additional Information:
        Format of circuitComponents: (Connection Type (str), Component Type(str), Component Value(float))
    """    
    circuitLines = circuit.split("\n")
    circuitComponents = []

    for line in circuitLines:
        if not (line == ""):
            circuitComponents.append(ConvertCircuitData(line))
        
    # Removes empty elements from list
    circuitComponents = RemoveEmptyElements(circuitComponents)

    # Sorts the list of tuples by values in nodes 1 and 2
    circuitComponents = sorted(circuitComponents, key=lambda x: (x[0], x[1]))

    # Checks if there is a connection to the common node, then inserts a 'P' or 'S' to the tuple depending on the connection type
    for i in range(0, len(circuitComponents)):
        if (circuitComponents[i].count(0) != 0): 
            circuitComponents[i] = ('P',) + circuitComponents[i]       
        else:
            circuitComponents[i] = ('S',) + circuitComponents[i]

    # Removes the node data from the circuitComponents tuples as they are no longer needed
    for i in range(0, len(circuitComponents)):
        circuitComponents[i] = circuitComponents[i][:1] + circuitComponents[i][3:]

    return circuitComponents

# ============== TERMS BLOCK ==============

def UpdateTermData(term, termsList):
    """
    Updates the term data depending on the type of data that is entered in.
    This can be seen as a case statement that ensures that all of the relevant data is inserted to the right index in termsList

    The order of the terms in the termsList is:
    [inputSource, sourceImpedance, loadImpedance, startFrequency, endFrequency, numberOfFrequencies]

    Args:
        term (str): The individual term to be read
        termsList (list): The list of all of the terms that are available to be read

    Returns:
        termsList (list): The updated list of all of the terms
    """    
    termValue = float(term.split("=")[1])
    if "VT" in term:        termsList[0] = ('V', termValue)
    elif "IN" in term:      termsList[0] = ('I', termValue)
    elif "RS" in term:      termsList[1] = termValue
    elif "GS" in term:      termsList[1] = 1/termValue
    elif "RL" in term:      termsList[2] = termValue
    elif "Fstart" in term:  termsList[3] = termValue
    elif "Fend" in term:    termsList[4] = termValue
    elif "Nfreqs" in term:  termsList[5] = termValue
    else: raise ValueError("Invalid Entry: " + str(term) + "\n Please Check Circuit")   # Throw an error if an undetected term is entered
    return termsList

def ConvertTerms(termLine, termsList):
    """
    Converts each line in the <TERMS> block into usable information. This separates all of the terms that are on the same line and ensures that the values are extracted.
    If the data entered is erroneous, then the program will raise an error and halt.

    The order of the terms in the termsList is:
    [inputSource, sourceImpedance, loadImpedance, startFrequency, endFrequency, numberOfFrequencies]

    Args:
        termLine (str): String containing the line of values to be read from
        termsList (list): The list of all of the terms that are available to be read

    Raises:
        TypeError: If an errorneous piece of data is found in the file, the program will halt

    Returns:
        termsList (list): The updated list of all of the terms
    """    
    terms = termLine.split(" ")

    for i in range(0, len(terms)):
        try:
            termsList = UpdateTermData(terms[i],termsList)
        except:
            raise TypeError("Invalid Data Type Entered: " + str(terms[i]) + "\n Please Check Circuit")  # Throw an error if an invalid entry is inputted
    return termsList

def GetTerms(terms):
    """
    Gets the value of the terms and unpacks them into a list. The terms text is split into it's separate lines, then each line is converted into a float or string
    
    The order of the terms in the termsList is:
        [inputSource, sourceImpedance, loadImpedance, startFrequency, endFrequency, numberOfFrequencies]

    inputSource is laid out as:
        (sourceType, sourceValue)

    Args:
        terms (str): String containing all of the information from the <TERMS> block of the .NET file

    Returns:
        termsList (List): List of each term and the value of them
    """    
    termsLines = terms.split("\n")
    termsList = [("", 0), 0, 0, 0, 0, 0]

    for i in range(0, len(termsLines)):
        if not (termsLines[i] == ""):
            termsList = ConvertTerms(termsLines[i], termsList)
    return termsList

# ============== OUTPUT BLOCK ==============

def ExtendDecibelAndExponent(outputUnit):
    """
    Extracts the decibel and exponent of the units, this is done by checking if dB is required, then extracting the prefix for the exponent if there is one.

    Note: Output will be [Decibel (bool), Exponent (int)]

    Args:
        outputUnit (str): String containing the units for the variable. This can contain a prefix and be a decibel measurement

    Returns:
        DecibelAndExponent (list): A list containing whether a decibel reading is required and also the desired prefix
    """    
    DecibelAndExponent = [False, 0]

    if "dB" in outputUnit:              # When dB is found, it sets the bool to True and removes it from the string
        DecibelAndExponent[0] = True
        outputUnit.replace("dB", "")
    try:
        DecibelAndExponent[1] = ExtractExponent(outputUnit[0])  # Checks the first character in the string which will be the prefix
    except:
        DecibelAndExponent[1] = 0       # This is run when there is no prefix for gain, added for robustness

    return DecibelAndExponent

def InsertOutputIndex(outputVariable):
    """
    Inserts the index for output variables, these indices correlate to the order of calculated outputs. A if else chain is used to check what index to return.

    Default output terms order and index [Vin (0), Vout (1), Iin (2), Iout (3), Pin (4), Pout (5), Zin (6), Zout (7), Av (8), Ai (9), Ap (10), T (11)]

    Args:
        outputVariable (str): String containing the variable that correlates to an index

    Raises:
        Exception: If an unknown Variable is present in the file an error is raised

    Returns:
        int: The index of the calculated output, which will be used when writing the data
    """    
    if   "Vin" in outputVariable:   return 0
    elif "Vout" in outputVariable:  return 1
    elif "Iin" in outputVariable:   return 2
    elif "Iout" in outputVariable:  return 3
    elif "Pin" in outputVariable:   return 4
    elif "Pout" in outputVariable:  return 5
    elif "Zin" in outputVariable:   return 6
    elif "Zout" in outputVariable:  return 7
    elif "Av" in outputVariable:    return 8
    elif "Ai" in outputVariable:    return 9
    elif "Ap" in outputVariable:    return 10
    elif "T" in outputVariable:     return 11
    

    raise Exception("Invalid Output Variable: " + str(outputVariable)) # Raise an error if an unknown output unit is entered

def ConvertOutputs(outputLine):
    """
    Converts the string of each line in the <OUTPUT> block into a tuple containing the relevant data for each output variable.

    The order for output is:
        (Output Index, Variable Name, Variable Unit, Decibel Boolean, Exponent)

    Args:
        outputLine (str): string for the <OUTPUT> block line

    Returns:
        output (tuple): Tuple containing the relevant data for each output variable
    """    
    output = outputLine.split(" ")
    if len(output) < 2: output.append("L")

    output.insert(0, InsertOutputIndex(output[0]))
    output.extend(ExtendDecibelAndExponent(output[2]))
    
    return tuple(output)

def GetOutputOrder(outputs):
    """
    Reads the text from the <OUTPUT> block and separates each line into a separate string. Each line is then read and the data is converted to a useful form.

    Each tuple is in the form of:
        (Output Index, Variable Name, Variable Unit, Decibel Boolean, Exponent)

    Args:
        outputs (str): String containing the text in the <OUTPUT> block

    Returns:
        outputTerms (list): List of tuples which contain all of the relevant data about each variable
    """    
    outputLines = outputs.split("\n")
    outputTerms = []

    for i in range(0, len(outputLines)):
        if not (outputLines[i] == ""):
            outputTerms.append(ConvertOutputs(outputLines[i].strip()))  # .strip() added to the end to remove trailing spaces
    
    # Removes empty elements from list
    outputTerms = RemoveEmptyElements(outputTerms)
    return outputTerms

# ============================== MATHEMATICS ==============================

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
        if   componentType == "R": impedance = componentValue
        elif componentType == "G": impedance = 1/componentValue
        elif componentType == "L": impedance = 1j*angularFrequency*componentValue
        elif componentType == "C": impedance = 1/(1j*angularFrequency*componentValue)
    
        if impedance != 0:      
            print("Getting Component Matrix")                                                
            componentMatrix = GetComponentMatrix(impedance, connectionType)
            ABCDMatrix = np.matmul(ABCDMatrix, componentMatrix)

    return ABCDMatrix

def ConvertToDecibel(value, outputVariable):
    if ("P" in outputVariable) or ("p" in outputVariable):
        return 10*cmath.log10(abs(value))
    return 20*cmath.log10(abs(value))

# ============================== FILE WRITING ==============================

def WriteDataToFile(file, outputTerms, outputs):
    """
    Writes the output data into the .csv file given that the file is open for editing. This function also converts the value into decibels and polar form when stated.
    outputTerm lists are laid out as: (Output Index, Variable Name, Variable Unit, Decibel Boolean, Exponent)

    Supporting Mathematics are linked below:
    
    Converting complex numbers to magnitude in dB and phase in rads: https://www.rohde-schwarz.com/uk/faq/converting-the-real-and-imaginary-numbers-to-magnitude-in-db-and-phase-in-degrees-faq_78704-30465.html
        
    Conversion to decibels: https://dspillustrations.com/pages/posts/misc/decibel-conversion-factor-10-or-factor-20.html#:~:text=The%20dB%20is%20calculated%20via,amplitude%2C%20the%20factor%20is%2020.

    Args:
        file (_io.TextIOWrapper): This is the file that will be read
        outputTerms (list): list of all of the output terms. This is a list of lists
        outputs (list): list of all of the output values
    """    
    decibelValue = 0
    for outputTerm in outputTerms:
        outputIndex = outputTerm[0]
        outputs[outputIndex] = outputs[outputIndex] / (10 ** outputTerm[4])
        # Checks if the value is read in decibels
        if outputTerms[3]:
            decibelValue = ConvertToDecibel(outputs[outputIndex], outputTerm[1])
            firstPart = str(np.real(decibelValue))
            secondPart = str(np.angle(outputs[outputIndex]))
        else:
            firstPart = str(np.real(outputs[outputIndex]))
            secondPart = str(np.imag(outputs[outputIndex]))

        file.write("," + firstPart + "," + secondPart)

# =========================================== MAIN CODE ===========================================
def main():
    # File Reading Section
    fileName = "Ext_a_Test_Circuit_1"
    fileDirectoryAndName = "TestFiles/" + fileName + ".net"
    with open(fileDirectoryAndName, 'r') as file:
        text = RemoveComments(file)

    print("READING FILE")
    circuitText = ExtractBlock(text, "<CIRCUIT>", "</CIRCUIT>")
    termsText = ExtractBlock(text, "<TERMS>", "</TERMS>")
    outputText = ExtractBlock(text, "<OUTPUT>", "</OUTPUT>")

    circuitComponents = GetCircuitComponents(circuitText)
    inputSource, sourceImpedance, loadImpedance, startFrequency, endFrequency, numberOfFrequencies = GetTerms(termsText)
    outputTerms = GetOutputOrder(outputText)

    outputValues = {
        "inputVoltage": 0,
        "outputVoltage": 0,
        "inputCurrent": 0,
        "outputCurrent": 0,
        "inputPower": 0,
        "outputPower": 0,
        "inputImpedance": 0,
        "outputImpedance": 0,
        "voltageGain": 0,
        "currentGain": 0,
        "powerGain": 0,
        "transmittance": 0,
    }

    # Write to the file
    with open(fileName + ".csv", 'w') as file:
        file.write("Freq")
        for outputTerm in outputTerms:
            if (outputTerm[3]): file.write(",|" + outputTerm[1] + "|,/_" + outputTerm[1])
            else:               file.write(",Re(" + outputTerm[1] + "),Im(" + outputTerm[1] + ")")
        file.write("\n Hz")
        for outputTerm in outputTerms:
            if (outputTerm[3]): file.write("," + outputTerm[2] + ",Rads")   
            else:               file.write("," + outputTerm[2] + "," + outputTerm[2])    
    
    print("PROCESSING DATA")

    # Data Processing Section
    #frequencies = np.linspace(int(startFrequency), int(endFrequency), int(numberOfFrequencies))
    frequencies = np.logspace(1, 7, 10)

    for frequency in frequencies:
        ABCDMatrix = CalculateMatrix(circuitComponents, 2*math.pi*frequency)

        print(ABCDMatrix)
        A_C = ABCDMatrix[0, 0]
        B_C = ABCDMatrix[0, 1]
        C_C = ABCDMatrix[1, 0]
        D_C = ABCDMatrix[1, 1]

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
        
        outputValues["inputPower"] = outputValues["inputVoltage"] * np.conj(outputValues["inputCurrent"])
        outputValues["outputVoltage"] = outputValues["inputVoltage"] * outputValues["voltageGain"]
        outputValues["outputCurrent"] = outputValues["inputCurrent"] * outputValues["currentGain"]
        outputValues["outputPower"] = outputValues["outputVoltage"] * np.conj(outputValues["outputCurrent"])

        # File Writing
        with open(fileName + ".csv", 'a') as file:
            file.write("\n"+str(frequency))
            WriteDataToFile(file, outputTerms, list(outputValues.values()))
        
    print("WRITING DATA")

if __name__ == "__main__":
    main()
