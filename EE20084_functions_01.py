# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 13:12:08 2020

@author: eessrp
"""
import sys
import os

def My_open_file(filename, mode):
    """ Function that attempts to open a file in a specified mode
        On failing to open the file the current directory is printed to
        the screen showing the directory that the Python program can see
        :param filename - the name of the file ot be opened
        :type string
        :param mode - the file opening mode, r, w, t, b, a
        :type string
        :return file pointer
        :rtype pointer
    """
    try:
        fp=open( filename, mode)
    except FileNotFoundError:
        print('File <%s> not found'%(filename))
        current_location=os.getcwd() 
        # gets the directory where the program is executing 
        print("executing program in directory: "+current_location) 
        sys.exit(2)  # exits the program, returning 2 to the operating system 
    return(fp)

def find_int(string_to_search,name,noisy):
    """
    Function that looks for an occurence of name in the string_to_search. 
    If found the equals sign following name is sought and the string to the
    right of the equals sign is interpretted as an integer. Looks for a string
    like 'Npt=3" in string_to_search, looking for 'Npt' and to return 3.
    Success or failure is indicated by a boolean that is returns, and this 
    should be acted on in the calling program.
    :param string_to_search - the text string to be searched
    :type string
    :param name - text string of the item to be sought in string_to_search
    :type string
    :param noisy - boolean, if true produces more output to the screen
    :type boolean
    :return rtn - integer value found, or particular negative values when not found
    :rtype integer
    :return ok - boolean, true if name and integer found otherwise false
    :rtype bool
    """
    pp=string_to_search.find(name)    # looks for name in string_to_search
    if (pp>-1):     # name has been found, pp is the index where name is
        lname=len(name)
        idx=pp+lname   # points at character after name
        new_str=string_to_search[idx:]  # copy from idx to end
        qqe=new_str.find('=')  # search for equals sign
        if (qqe>-1):   # equals found
            idx=qqe+1  # point at character after equals sign
            valstring=new_str[idx:]
            substring=valstring.split(',') #variables need to be separated by commas
            teststring=substring[0].strip() # strip gets rid of spare spaces
            try:
                rtn=int(teststring)  #convert string to integer
                if noisy:
                    print("Found %s = %g from <%s>"%(name,rtn,teststring))
                ok=True
            except ValueError:
                if noisy:
                    print('ERROR:\nTried to find int <%s> in string <%s>, valstring is <%s>, teststring is <%s>'%(name,string_to_search,valstring,teststring))
                rtn=-987654321
                ok=False
        else:  # equals not found
            rtn=-113355
            ok=False
            if noisy:
                print('ERROR:\nTried to find int <%s> in string <%s>. Found <%s> but no equals symbol'%(name,new_str))
    else:  # name not found in string_to_search
        rtn=-123456789
        if noisy:
            print("Failed to find <%s> in <%s>"%(name, str))
        ok = False
    return(rtn, ok)
#