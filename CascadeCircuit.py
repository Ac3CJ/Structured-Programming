# =========================================== NOTE TO SELF ===========================================
# outputTerms tuples are ordered as: (Output Index, Variable Name, Variable Unit, Decibel Boolean, Exponent)
# WHEN WRITING THE FILE, PUT COMMA BEFORE THE DATA POINT

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

# NOTE TO SELF: 

# =================================================================================================
# =========================================== LIBRARIES ===========================================
# =================================================================================================

import numpy as np
import math, sys, getopt, cmath, re, warnings
import pandas as pd
from matplotlib import pyplot as plt
#import FileReading as fr

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
        SyntaxError: _description_
    """    
    raise SyntaxError("Invalid entry: " + ' '.join(systemArguments) +
                                              "\n Example Entries:\n python CascadeCircuit.py -i a_Test_Circuit_1 -p [5,1,2]\n python CascadeCircuit.py input.net output.csv")

# ======================== READING AND ORGANISING DATA ========================

# ============== GENERAL ==============

def CleanTextLine(text):
    """
    Cleans the line of text from repeat spaces and commas as well as spaces before and after an equals sign.
    
    Examples shown below:
        text = "n1 =======    2   ,   n2 = 1, R   = === 17  "
        print(text)
        
        Output> n1=2 n2=1 R=17

    Args:
        text (str): String to be cleaned

    Returns:
        text (str): Cleaned string
    """    
    text = re.sub(r"[\s,]+", " ", text.strip())     # Checks for one or more occurences of a space or comma then replaces it with a space
    text = re.sub(r"[\s,]*=[\s,=]*", "=", text)     # Checks for zero or more occurences of a space or comma followed by an "=", then zero or more occurences of space, comma, "="
    return text

def CheckEmptyListError(myList, block="UNDEFINED"):
    """
    Checks if the list for a block is empty and throws an error 

    Args:
        myList (list): list that will be examined to throw an error
        block (str, optional): _description_. Defaults to "UNDEFINED".
    """    
    if (len(myList) <= 0): raise ValueError("Empty Block Detected! Check: " + block + " Block")
    return

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
        # Checks if the line doesn't start with a #
        if not (line.startswith('#')):
            text += line
            text = re.sub(r"#.*", "", text)
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
    if not ((start in text) or (end in text)): raise ValueError(start + " block is missing")
    return text[text.find(start)+len(start):text.rfind(end)]     

def RemoveEmptyElements(myList):
    """
    Removes empty elements from a list by filtering empty elements from the list

    Args:
        list0 (list): The list to have empty elements removed

    Returns:
        list: New list without empty elements
    """    
    return list(filter(None, myList))

def ExtractExponent(prefix=""):
    """
    Extracts the exponent from the prefix of the units for each variable. This is a case statement to set the exponent for each variable.

    More information about this can be found in the table: https://basicelectronicscoed.files.wordpress.com/2015/07/metric-prefixes.png

    Args:
        prefix (str, optional): String that contains the character for the prefix

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
    else: 
        warnings.warn("WARNING: No or unknown prefix: " + str(prefix) + " Defaulting to 0")
        return 0

# ============== CIRCUIT BLOCK ==============

def ValidateCircuit(componentData, componentText):
    """
    Validates the circuit line by checking if the data fits the predetermined list structure. The structure of the data is shown below:
        [int node1, int node, str componentType, float componentValue, int exponent]
    
    Args:
        componentData (list): list of all relevant data for the component
        componentText (str): original text that stores the text for the component

    Raises:
        ValueError: Invalid component for when the list is too long or short
        ValueError: Invalid component for when the list has incorrect data entries
    """    
    componentDataLength = len(componentData)

    # Checks if the component has less than 4 data entries or more than 5
    if componentDataLength < 4 or componentDataLength > 5: raise ValueError("Invalid Component: " + "".join(str(componentText)))
    
    # Boolean value to check
    componentCheck = (isinstance(componentData[0], (int, float))) and (isinstance(componentData[1], (int, float))) and (isinstance(componentData[2], str)) and (isinstance(componentData[3], (int, float)))
    
    # Returns if the component entries are valid and there are only 4 entries
    if ((componentDataLength < 5) and componentCheck): return
    
    # Returns if there are 5 component entries and also fits the structure of the componentData list
    if componentDataLength >= 5 and componentCheck and (isinstance(componentData[4], (int,float))): return
    
    raise ValueError("Invalid Component: " + "".join(str(componentText)))

def CheckComponentType(data=""):
    """
    Checks for the component type of the component

    Args:
        data (str, optional): Holds the specific data for the component, either node data or component data

    Returns:
        Boolean: Will return True if the data includes the component type, False if it is node data
    """    
    if ('R' in data) or ('G' in data) or ('C' in data) or ('L' in data): return True
    elif ('n1' in data) or ('n2' in data): return False
    else: raise ValueError("Unknown Variable Found: " + data)
    
def ConvertCircuitData(component):
    """
    Converts the component data from str into a tuple that contains the relevant data.

    Tuple is in the form: (node 1, node 2, component type, component value, exponent)

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
            componentData.append(ExtractExponent(data))     # Appends the exponent if there is no equals found  and returns
            return
        
        if (CheckComponentType(data)): componentData.append(data.split("=")[0]) # If the component type is legal, append the component type (before the equals sign)

        value = float(data.split("=")[1])   # Retrieves the value that is after the equals sign and appends it to the componentData list
        componentData.append(value)
    
    # Outer Function Code
    component = CleanTextLine(component)
    componentTermList = component.split(" ")
    componentData = []

    for term in componentTermList:
        try:
            AppendComponentData(term)
        except:
            raise ValueError("Invalid Data Entered: " + term + "\n Please Check Circuit")   # Called when the value is invalid and can't be converted to a float
    
    ValidateCircuit(componentData, component)
    try:
        if len(componentData) >= 5: componentData[3] = componentData[3] * (10 ** componentData[4])  # Apply exponent to value
    except:
        raise ValueError("Invalid Data Entered: " + component + "\n Please Check Circuit")

    return tuple(componentData)     # Returns the list as a tuple to avoid coupling issues

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
    circuitComponents = []
    seriesComponents = []
    circuitLines = circuit.split("\n")
    circuitLines = RemoveEmptyElements(circuitLines)

    for i in range(0, len(circuitLines)):
        if not (circuitLines[i] == ""): circuitComponents.append(ConvertCircuitData(circuitLines[i]))   # Appends all of the available components
        
    # Removes empty elements from list
    circuitComponents = RemoveEmptyElements(circuitComponents)

    # Checks if there is a connection to the common node, then inserts a 'P' or 'S' to the tuple depending on the connection type
    for i in range(0, len(circuitComponents)):
        if (circuitComponents[i].count(0) != 0): circuitComponents[i] = ('P',) + circuitComponents[i]       
        else: 
            # Checks if the nodes are 1 value apart, if they aren't raise an error (n1=1 n2=3)
            if (abs(circuitComponents[i][0] - circuitComponents[i][1]) > 1): raise ValueError("Invalid Circuit Connection: " + " ".join(circuitLines[i]))

            seriesComponents.append(sorted(circuitComponents[i][:2]))   # Appends series components to a separate list and only takes in the node values
            circuitComponents[i] = ('S',) + circuitComponents[i]

    # Sorts the list of tuples by values in nodes 1 and 2
    circuitComponents = sorted(circuitComponents, key=lambda x: (x[1], x[2]))

    # Gets the number of series components and makes a list of the first node values
    seriesLength = len(seriesComponents)
    seriesCheckList = [item[0] for item in seriesComponents]

    # Check if there are repeated series components (If they share two nodes).
    # Checks the length of the list against a set of itself, if they differ, there are duplicates. Sets cannot have duplicates, so it will change if there are repeats
    if seriesLength != len(set(seriesCheckList)): raise ValueError("Conflicting Circuit Connection:\n" + circuit)

    # Check if there are disconnected nodes, by creating a list from 1 to seriesLength and comparing it to the original seriesComponent list
    # If the circuit is connected the series components will increment by 1 from 1 to the seriesLength
    nodeCheckList = [i for i in range(1, int(seriesComponents[seriesLength-1][0])+1)]

    if seriesCheckList != nodeCheckList: raise ValueError("Missing Node Connection:\n" + circuit)

    # Removes the node data from the circuitComponents tuples as they are no longer needed
    for i in range(0, len(circuitComponents)):
        circuitComponents[i] = circuitComponents[i][:1] + circuitComponents[i][3:]

    return circuitComponents

# ============== TERMS BLOCK ==============
def CheckLogarithmicSweep(term):
    """
    Checks for an L in the term and returns a Boolean

    Args:
        term (str): String for the term to check

    Returns:
        boolean: Boolean value to state when to apply the sweep
    """    
    if "L" in term: return True
    return False

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
    elif "Fstart" in term:  
        termsList[3] = termValue
        termsList[6] = CheckLogarithmicSweep(term)      # Check if there is an L in the frequency 
    elif "Fend" in term:    
        termsList[4] = termValue
        termsList[6] = CheckLogarithmicSweep(term)
    elif "Nfreqs" in term:  termsList[5] = termValue
    else: raise ValueError("Invalid Entry: " + str(term) + "\n Please Check Circuit")   # Throw an error if an unexpected term is entered
    return termsList

def ConvertTerms(termLine, termsList, termsCounter):
    """
    Converts each line in the <TERMS> block into usable information. This separates all of the terms that are on the same line and ensures that the values are extracted.
    If the data entered is erroneous, then the program will raise an error and halt.

    The order of the terms in the termsList is:
    [inputSource, sourceImpedance, loadImpedance, startFrequency, endFrequency, numberOfFrequencies]

    Args:
        termLine (str): String containing the line of values to be read from
        termsList (list): The list of all of the terms that are available to be read
        termsCounter (int): Integer for the how many times the list has been updated

    Raises:
        TypeError: If an errorneous piece of data is found in the file, the program will halt

    Returns:
        termsList (list): The updated list of all of the terms
        termsCounter (int): Integer for the how many times the list has been updated
    """    
    termLine = CleanTextLine(termLine).strip()      # Clean out whitespace and delimiters
    terms = termLine.split(" ")
    for i in range(0, len(terms)):
        try:    
            termsList = UpdateTermData(terms[i],termsList) # Update the terms list and increment the counter by 1 for each successful update
            termsCounter += 1
        except:
            raise TypeError("Invalid Data Type Entered: " + terms[i] + "\n Please Check Circuit")  # Throw an error if an invalid entry is inputted
    return termsList, termsCounter

def GetTerms(terms):
    """
    Gets the value of the terms and unpacks them into a list. The terms text is split into it's separate lines, then each line is converted into a float or string
    
    The order of the terms in the termsList is:
        [inputSource, sourceImpedance, loadImpedance, startFrequency, endFrequency, numberOfFrequencies, Logarithmic Sweep Boolean]

    inputSource is laid out as:
        (sourceType, sourceValue)

    Args:
        terms (str): String containing all of the information from the <TERMS> block of the .NET file

    Returns:
        termsList (List): List of each term and the value of them
    """    
    termsLines = terms.split("\n")
    termsLines = RemoveEmptyElements(termsLines)
    termsList = ["", "", "", "", "", "", False]
    termsCounter = 0

    CheckEmptyListError(termsLines, "TERMS")

    for i in range(0, len(termsLines)):
        if not (termsLines[i] == ""):
            termsList, termsCounter = ConvertTerms(termsLines[i], termsList, termsCounter)
    if "" in termsList: raise ValueError("TERMS Block has a missing term! Check TERMS block.\n" + terms)
    # There are 6 terms, so if the counter is triggered too little or too many times, then the TERMS block is erroneous
    if termsCounter != 6: raise ValueError("TERMS Block has too many or too little terms! Check TERMS block.\n" + terms)
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
    outputUnitNew = CleanTextLine(outputUnit).strip()
    outputUnitNew = re.sub(r"V?A?W?(Ohms)?", "", outputUnitNew).strip()     # Checks for the known variable units and removes them from the decibels and exponent

    if "dB" in outputUnitNew:              # When dB is found, it sets the bool to True and removes it from the string
        DecibelAndExponent[0] = True
        outputUnitNew = outputUnitNew.replace("dB", "").strip()

    # If there is more information other than the prefix, raise an error
    if (len(outputUnitNew) > 1): raise ValueError("Error Detected: " + outputUnit + "\nCheck Circuit")   
    if (len(outputUnitNew) > 0): DecibelAndExponent[1] = ExtractExponent(outputUnitNew[0])  # Checks the first character in the string which will be the prefix

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
    output = re.split("\s", outputLine, 1)              # Split on first white space
    if len(output) < 2: output.append("L")              # If the gain has no units, then append an L 
    output.insert(0, InsertOutputIndex(output[0]))      # Insert the output index to the start of the list
    output.extend(ExtendDecibelAndExponent(output[2]))  # Extend the list with the 
    
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
        if not (outputLines[i] == ""): outputTerms.append(ConvertOutputs(outputLines[i].strip()))  # .strip() added to the end to remove trailing spaces
        
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
        try: 
            if   componentType == "R": impedance = componentValue
            elif componentType == "G": impedance = 1/componentValue
            elif componentType == "L": impedance = 1j*angularFrequency*componentValue
            elif componentType == "C": impedance = 1/(1j*angularFrequency*componentValue)
            else: raise ValueError("Unknown Component Found: " + " ".join(str(individualComponent)))
        except:
            raise ZeroDivisionError("Cannot divide by 0:\n(Connection Type, Component Type, Component Value, Exponent)\n" + "".join(str(individualComponent)))
    
        if impedance != 0:                                                     
            componentMatrix = GetComponentMatrix(impedance, connectionType)
            ABCDMatrix = np.matmul(ABCDMatrix, componentMatrix)

    return ABCDMatrix

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

# ============================== FILE WRITING ==============================

def FormatNumber(value):
    """
    Formats the number for writing into the file. This rounds the number to 4 significant figures and converts them into scientific notation

    Args:
        value (float): The value to be formatted

    Returns:
        str: String format of the value, written in scientific notation to 4 significant figures
    """    
    return  ('{:e}'.format(float('%.4g' % value)))

def WriteDataToFile(file, outputTerms, outputs, fileName, frequency):
    """Writes the output data into the .csv file given that the file is open for editing. This function also converts the value into decibels and polar form when stated.
    outputTerm lists are laid out as: (Output Index, Variable Name, Variable Unit, Decibel Boolean, Exponent)

    Supporting Mathematics are linked below:
    
    Converting complex numbers to magnitude in dB and phase in rads: https://www.rohde-schwarz.com/uk/faq/converting-the-real-and-imaginary-numbers-to-magnitude-in-db-and-phase-in-degrees-faq_78704-30465.html
        
    Conversion to decibels: https://dspillustrations.com/pages/posts/misc/decibel-conversion-factor-10-or-factor-20.html#:~:text=The%20dB%20is%20calculated%20via,amplitude%2C%20the%20factor%20is%2020.

    Args:
        file (_io.TextIOWrapper): This is the file that will be read
        outputTerms (list): List of all of the output terms. This is a list of lists
        outputs (list): List of all of the output values
        fileName (str): Name of the file to write to
        frequency (float): Frequency that is being analysed
    """    
    decibelValue = 0
    with open(fileName, 'a') as file:
        file.write("\n"+FormatNumber(frequency))
    for outputTerm in outputTerms:
        outputIndex = outputTerm[0]
        outputs[outputIndex] = outputs[outputIndex] / (10 ** outputTerm[4])

        # Checks if the value is read in decibels
        if (outputTerm[3]):
            decibelValue = ConvertToDecibel(outputs[outputIndex], outputTerm[1])
            firstPart = FormatNumber(np.real(decibelValue))
            secondPart = FormatNumber(np.angle(outputs[outputIndex]))
        else:
            firstPart = FormatNumber(np.real(outputs[outputIndex]))
            secondPart = FormatNumber(np.imag(outputs[outputIndex]))
        with open(fileName, 'a') as file:
            file.write("," + firstPart + "," + secondPart)
    return

def InitialiseFile(fileName, outputTerms):
    """
    Initialises the file for writing by filling in the variables and units for each column

    Args:
        fileName (str): Name of the file to write to
        outputTerms (list): List of all of the output terms to consider
    """
    with open(fileName, 'w') as file:
        file.write("Freq")
        for outputTerm in outputTerms:
            variable, variableUnit, decibleCheck = outputTerm[1:4]                                  # Unpacks the necessary data from the output terms from the list
            if (decibleCheck): file.write(",|" + str(variable) + "|,/_" + str(variable))            # When there are decibels, write it as modulus as phase
            else:               file.write(",Re(" + str(variable) + "),Im(" + str(variable) + ")")  # Write as real and imaginary components otherwise
        file.write("\n Hz")
        for outputTerm in outputTerms:
            variable, variableUnit, decibleCheck = outputTerm[1:4]                                  # Unpacks the necessary data from the output terms from the list
            if (decibleCheck): file.write("," + str(variableUnit) + ",Rads")                        # When in decibels, write in the unit and rads 
            else:               file.write("," + str(variableUnit) + "," + str(variableUnit))       # Displays the normal units otherwise
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
    variables = pd.read_csv(inputFile, nrows=0, usecols=graphColumns)
    unit = pd.read_csv(inputFile, nrows=1, usecols=graphColumns) 
    for i in range(1, len(graphColumns)):
        outputData.plot(0, i)                                                 # Plot with frequency on x axis and other data on y axis
        plt.xlabel("Frequency / Hz")
        plt.ylabel(list(variables.keys())[i] + " / " + unit.values[0][i])
        plt.savefig(outputFile + "_" + str(graphColumns[i]) + ".png")
    return

# =================================================================================================
# =========================================== MAIN CODE ===========================================
# =================================================================================================
# python CascadeCircuit.py -i a_Test_Circuit_1 -p [5,1,2]
# python CascadeCircuit.py a_Test_Circuit_1.net test.csv
def main():
    systemArguments = sys.argv[1:]
    #systemArguments = ["a_Test_Circuit_1EVIL.net", "test.csv"]

    graphParameters = "1"           # String of 1 to initialise the data
    graphBoolean = False
    fileBoolean = False
    options = [] 
    arguments = []

    # Sets the netFileName and csvFileName to the first and second entries of the systemArguments, this gets overwritten if the user enters the file for a graph
    netFileName = systemArguments[0]
    if len(systemArguments) > 1: csvFileName = systemArguments[1]
    else: ErrorRaiseCommandLineEntry(systemArguments)

    # Reading System Inputs
    try:
        options, arguments = getopt.getopt(systemArguments,"hi:p:")
    except getopt.GetoptError:
        print('Input invalid! Input line as: CascadeCircuit.py -i <inputfile> -p <parameter>')
        sys.exit(2)
    print(arguments)


    for optionAndArgument in options:
        if len(optionAndArgument) > 2: ErrorRaiseCommandLineEntry(systemArguments) 
        if optionAndArgument[0] == '-h':
            print ('test.py -i <inputfile> -p <parameter>')
            sys.exit()
        elif optionAndArgument[0] in ("-i", "--ifile"):
            netFileName = optionAndArgument[1] + ".net"
            csvFileName = optionAndArgument[1] + ".csv"
            pngFileName = optionAndArgument[1]
            fileBoolean = True
        elif optionAndArgument[0] in ("-p", "--param"):
            graphParameters = optionAndArgument[1].strip()
            graphBoolean = True

    if not (".net" in netFileName): raise OSError("File extension is invalid: " + netFileName)
    if not (".csv" in csvFileName): raise OSError("File extension is invalid: " + csvFileName)

    # Arguments should be empty in this case, when it is full, then the command line prompt is written incorrectly
    if fileBoolean and len(arguments) > 0: ErrorRaiseCommandLineEntry(systemArguments)
    if re.search(r".+[[]", graphParameters) or re.search(r"[]].+", graphParameters): ErrorRaiseCommandLineEntry(systemArguments)

    #if not (re.search(r"[[]([0-9]+\s*,*)+[]]", graphParameters)): ErrorRaiseCommandLineEntry(systemArguments)
    userColumns= re.findall(r'\d+', graphParameters)    # Use REGEX to extract all numbers
    userColumns = [int(i) for i in userColumns]         # Convert the strings into integers
    userColumns = RemoveEmptyElements(userColumns)       
    userColumns = sorted(userColumns)

    # File Reading and Error Handling
    print("READING FILE")
    try:
        with open(netFileName, 'r') as file:
            text = RemoveComments(file)
    except:
        raise FileNotFoundError("No file or directory: '" + netFileName + "'")

    circuitText = ExtractBlock(text, "<CIRCUIT>", "</CIRCUIT>")
    termsText = ExtractBlock(text, "<TERMS>", "</TERMS>")
    outputText = ExtractBlock(text, "<OUTPUT>", "</OUTPUT>")

    if (circuitText == "") or (termsText == "") or (outputText == ""): raise ValueError("Empty Block Detected!\n Check file: " + netFileName)

    print("READING CIRCUIT BLOCK")
    circuitComponents = GetCircuitComponents(circuitText)
    print("READING TERMS BLOCK")
    inputSource, sourceImpedance, loadImpedance, startFrequency, endFrequency, numberOfFrequencies, logarithmicSweepBoolean = GetTerms(termsText)
    print("READING OUTPUT BLOCK")
    outputTerms = GetOutputOrder(outputText)

    CheckEmptyListError(circuitComponents, "CIRCUIT")
    CheckEmptyListError(outputTerms, "OUTPUT")

    # Check if the entered maximum column, the user entered is greater than the output terms or less than equal to 0
    if (len(outputTerms) < max(userColumns)) or (min(userColumns) <= 0): raise IndexError("Column " + str(max(userColumns)) + 
                                                                                          " is out of range. Enter a value between 1-" + str(len(outputTerms)-1))

    outputValues = {"inputVoltage": 0, "outputVoltage": 0, "inputCurrent": 0, "outputCurrent": 0, "inputPower": 0, "outputPower": 0, "inputImpedance": 0, "outputImpedance": 0,
        "voltageGain": 0, "currentGain": 0, "powerGain": 0, "transmittance": 0,}

    # Write to the file to get the initial format
    InitialiseFile(csvFileName, outputTerms)   
    
    # Data Processing Section
    print("PROCESSING DATA")

    # For logspace, apply a log function to the frequencies so that the values are the base of the exponent
    if (logarithmicSweepBoolean == True): frequencies = np.logspace(math.log10(startFrequency), math.log10(endFrequency), int(numberOfFrequencies))
    else: frequencies = np.linspace(startFrequency, endFrequency, int(numberOfFrequencies))

    for frequency in frequencies:
        # Creating the Matrices
        ABCDMatrix = CalculateMatrix(circuitComponents, 2*math.pi*frequency)

        A_C = ABCDMatrix[0, 0]
        B_C = ABCDMatrix[0, 1]
        C_C = ABCDMatrix[1, 0]
        D_C = ABCDMatrix[1, 1]

        # Calculating all of the values
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
        #outputValues["outputPower"] = outputValues["inputPower"] * outputValues["powerGain"]
        outputValues["outputPower"] = outputValues["outputVoltage"] * np.conj(outputValues["outputCurrent"])
        
        # File Writing
        WriteDataToFile(file, outputTerms, list(outputValues.values()), csvFileName, frequency)
        
    print("WRITING DATA")

    # Output Graphs
    if graphBoolean == True: GenerateGraph(userColumns, csvFileName, pngFileName)

    print("ENDING PROGRAM")

if __name__ == "__main__":  # Allows code to be run as a script, but not when imported as a module. This is the top file
    main() 
