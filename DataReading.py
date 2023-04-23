# ====================================================================================================================================
#   Filename:     DataReading.py
#   Summary:      The module that contains the code for reading the data from the file
#   Description:  This is a set of functions that are used to read the .net file and output the relevant data back to the main code.
#                 The functions also handle the error handling for erroneous file entries and flags them before they can reach the
#                 main program as an error, or worse a mathematical error.
#
#   Author:       C.J. Gacay 
# ====================================================================================================================================

import re, warnings

# =============================================================================================================================
# ========================================================== GENERAL ==========================================================
# =============================================================================================================================

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

# ===================================================================================================================================
# ========================================================== CIRCUIT BLOCK ==========================================================
# ===================================================================================================================================

def CheckNodeConnections(seriesComponents):
    """
    Checks the node connections of the circuit by using the series components node data. If the node connections are invalid then an error is raised

    Erroneous inputs:
        "n1=1 n2=2 R=1"

        "n1=1 n2=2 G=0.5"
        
        OR

        "n1=1 n2=2 R=1"

        "n1=3 n2=4 R=2"

    Args:
        seriesComponents (list): list of tuples for each series component. This only contains the node data

    Raises:
        ValueError: Raised when there is a conflicting circuit connection in the series section
        ValueError: Raised when there is a missing node connection
    """    
    # Gets the number of series components and makes a list of the first node values
    seriesLength = len(seriesComponents)
    seriesCheckList = [item[0] for item in seriesComponents]

    # Check if there are repeated series components (If they share two nodes).
    # Checks the length of the list against a set of itself, if they differ, there are duplicates.
    if seriesLength != len(set(seriesCheckList)): raise ValueError("Conflicting Circuit Connection: Series components cannot share the same nodes.\n\nCheck CIRCUIT Block")

    # Check if there are disconnected nodes, by creating a list from 1 to seriesLength and comparing it to the original seriesComponent list
    if seriesLength != 0:
        nodeCheckList = [i for i in range(1, int(seriesCheckList[seriesLength-1])+1)]          
        if seriesCheckList != nodeCheckList: raise ValueError("Missing Node Connection: All nodes must be connected by a component\n\nCheck CIRCUIT Block")

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
        boolean: Will return True if the data includes the component type, False if it is node data
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

    Raises:
        ValueError: Invalid circuit connections: Series nodes must be adjacent
        ValueError: Conflicting circuit connections: Series components cannot share the same nodes
        ValueError: Missing node connection: All nodes must be connected by a component

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
            if (abs(circuitComponents[i][0] - circuitComponents[i][1]) != 1): raise ValueError("Invalid Circuit Connection: Series nodes must be adjacent\n" + "".join(circuitLines[i]))

            seriesComponents.append(sorted(circuitComponents[i][:2]))   # Appends series components to a separate list and only takes in the node values
            circuitComponents[i] = ('S',) + circuitComponents[i]

    # Sorts the list of tuples by values in nodes 1 and 2
    circuitComponents = sorted(circuitComponents, key=lambda x: (x[1], x[2]))
    seriesComponents = sorted(seriesComponents, key=lambda x: (x[0], x[1]))

    CheckNodeConnections(seriesComponents)

    # Removes the node data from the circuitComponents tuples as they are no longer needed
    for i in range(0, len(circuitComponents)):
        circuitComponents[i] = circuitComponents[i][:1] + circuitComponents[i][3:]

    return circuitComponents

# =================================================================================================================================
# ========================================================== TERMS BLOCK ==========================================================
# =================================================================================================================================

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

# ==================================================================================================================================
# ========================================================== OUTPUT BLOCK ==========================================================
# ==================================================================================================================================

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

# ==================================================================================================================================
# ========================================================== FILE READING ==========================================================
# ==================================================================================================================================

def ReadFile(fileName):
    """
    Reads the file and returns the text that is inside each of the blocks

    Args:
        fileName (str): string for the file name to analyse

    Raises:
        FileNotFoundError: Raised if the file entered does not exist
        ValueError: Raised when one of the blocks in the .net file is empty

    Returns:
        circuitText(str): String of the circuit block text
        termnsText(str): String of the circuit block text
        outputText(str): String of the circuit block text
    """    
    print("READING FILE")
    try:
        with open(fileName, 'r') as file:
            text = RemoveComments(file)
    except:
        raise FileNotFoundError("No file or directory: '" + fileName + "'")

    circuitText = ExtractBlock(text, "<CIRCUIT>", "</CIRCUIT>")
    termsText = ExtractBlock(text, "<TERMS>", "</TERMS>")
    outputText = ExtractBlock(text, "<OUTPUT>", "</OUTPUT>")

    if (circuitText == "") or (termsText == "") or (outputText == ""): raise ValueError("Empty Block Detected!\n Check file: " + fileName)

    return circuitText, termsText, outputText
