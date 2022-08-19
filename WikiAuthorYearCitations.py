#!/usr/bin/python 

"""
  This script reads the citations in Wikimedia format, and 
  produces a handy citation key for each of the references
  in order to have easy named citations from Wiki text.
  
  The script puts some effor for creating familiar author_year 
  style keys, which are unique.
  
  The script also tries to remove duplicates. Duplicate is defined
  so that if author's last name, year and title are equal. The 
  duplicates are not added in the list.
  
  The list of references can be copied in the Mediawiki page, and 
  cited using this syntax:
  
  <ref name=Author_year />
  
  Version 1.0, 18.1.2022, Petri Välisuo <petri.valisuo@uwasa.fi>
"""

import sys
import os 

Index=0
subkeys="abcdefgh"
subindex=0
UsedKeys=dict([])

def getLastname(ref):
    """ Parse the first author's last name from the record
        or return "Unknown<idx>" if none is found.
    """ 
    global Index
    if ref.count('last1'):
        start = ref.index('last1')
    elif ref.count('last'):
        start = ref.index('last')
    else:
        Index +=1
        return("Unknown%d" % Index)
    return(ref[start:].split('|')[0].split('=')[1].strip())

def getYear(ref):
    """ Parse the year from the date field, or return empty year
        if none is found.
    """
    if ref.count('| date'):
        start = ref.index('| date')
        date = ref[start:].split('|')[1].split('=')[1].strip()
        return(date.split('-')[0])
    else:
        return ("")
        
def getTitle(ref):
    """ Parse the title or return empty string.
    """
    if ref.count('| title'):
        start = ref.index('| title')
        title = ref[start:].split('|')[1].split('=')[1].strip()
        return(title)
    else:
        return ("")
        
def makeUniqueKey(lastname, year, title):
    """ Make unique citation key. If an author has several 
        publications in the same year, a subkeys "b", "c", ...
        are used. If in addition to author and year, even the
        titles are the same, the article is deemed as duplicate
        and an empty string is returned. 
    """
    global UsedKeys
    key="%s_%s" % (lastname, year)
    subindex=0
    while key in UsedKeys:
        if UsedKeys[key] == title:
            return("")
        else:
            key="%s_%s%s" % (lastname, year, "bcdefghijklm"[subindex])
            subindex+=1
    UsedKeys[key]=title
    return(key)
    

### Main program

# Check that the inputfilename is given, if not pring usage and exit
if len(sys.argv)<2:
    print("Usage: \n\t %s <bibfile> [<outputfile>]\n" % sys.argv[0])
    sys.exit(1)
inputfile = sys.argv[1]

# Check if the output file is given, if not use stdout
if len(sys.argv)<3:
    outputfile = sys.stdout
    outputfilename=""
else:
    outputfilename = sys.argv[2]

    # Check that the output file is not accidentally overwritten
    if os.path.exists(outputfilename):
        print("Output file %s already exists!" % outputfilename)
        answer = input("Is it ok to overwrite [y/N]?").lower()
        if answer!='y':
            print("Exit")
            sys.exit(-1)
    outputfile = open(outputfilename, 'w')

# Read the wikimedia formatted refereces which are for example
# Exported from Zotero
with open(inputfile, 'r') as fid:
        wikirefs=fid.readlines()


outputfile.write("<references>\n")
# Process each one of them, and produce a nice citaion key
for refraw in wikirefs:
    # Remove braces and trailing and leading spaces
    ref = refraw.replace('{', '').replace('}','').strip()
    try:
        # Parse citation information
        lastname = getLastname(ref)
        year = getYear(ref)
        title = getTitle(ref)
        key= makeUniqueKey(lastname, year, title)
    except Exception as e:
        # if something goes wrong, break
        print (e)
        print (lastname, year)
        print(ref)
        break
    else:
        # It worked, we have a key, unless the entry was a duplicate
        if len(key):
            # No dupliate, print it
            outputfile.write("<ref name=%s>%s</ref>\n" % (key, refraw))
        else:
            # It was a duplicate, skip it
            pass
            #print("Duplicate %s, %s, %s" % (lastname, year, title))

    #print(UsedKeys.keys())
outputfile.write("</references>\n")
if len(outputfilename)>0:
    outputfile.close()
