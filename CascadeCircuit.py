# ============================== TO DO LIST ==============================
# 1. Sort the circuit by parallel components initially, then insert the
#    correct series components in
# 2. 
#
# ======================================================================
import numpy as np

def RemoveComments(file):
    text = ""
    for line in file:
        if not (line.find('#')==0):
            text += line
    return text

# Uses indexing to return the parts between start and end. Finds the instance of the start
# delimiter, then uses that as the beginning index, then adds the length of the delimiter in case
# it is longer than a character. Finds the final instance of the ending delimiter and uses that
# as the end of the index. This can be used as each file has specific code blocks in the .NET files
def ExtractBlock(text, start, end):
    return text[text.find(start)+len(start):text.rfind(end)]     

def main():
    with open('a_Test_Circuit_1.net', 'r') as file:
        text = RemoveComments(file)

        circuitText = ExtractBlock(text, "<CIRCUIT>", "</CIRCUIT>")
        termsText = ExtractBlock(text, "<TERMS>", "</TERMS>")
        outputText = ExtractBlock(text, "<OUTPUT>", "</OUTPUT>")

        print(circuitText)
        print(termsText)
        print(outputText)

if __name__ == "__main__":
    main()