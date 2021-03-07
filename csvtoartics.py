#!/usr/bin/python

"""
CSV to Logic Articulation plist converter
Version 2: handles multiple outputs per articulation (Logic allows for three)
Adrian Sutton 2019

This takes a CSV file with rows containing articulation data and converts it into a .plist XML file (Articulation Set) that Logic Pro X uses.

Usage (with the input CSV file in the same directory as this python script): ./csvtoartics.py <csvFile.csv>
You can also omit the csvFile name on the commandline IF that csv file is specifically `named "artics.csv", i.e. just run ./csvtoartics.py

The expected CSV columns are as follows:
========================================
Articulation name
Channel (1-16) (N.B. this is 1-based, not 0-based)
Articulation Symbol name, e.g. 'staccato', corresponding to the name of Logic's symbols for these things in its own articulation editor

Input (type, e.g. Note On, Program etc.)
Selector (the first MIDI data byte.. e.g. the note number if a note)
Value Start (the lowest value of the second MIDI data byte, e.g. velocity if a note)
Value End (the highest value of the second MIDI data byte, e.g. velocity if a note)
Mode (Permanent, Momentary etc.)

Output 1 (type e.g. Note On, Program etc.)
Channel (1-16)
Selector (the first MIDI data byte.. e.g. the note number if a note)
Value (the second MIDI data byte, e.g. velocity if a note)

Output 2 (type e.g. Note On, Program etc.)
Channel (1-16)
Selector (the first MIDI data byte.. e.g. the note number if a note)
Value (the second MIDI data byte, e.g. velocity if a note)

Output 3 (type e.g. Note On, Program etc.)
Channel (1-16)
Selector (the first MIDI data byte.. e.g. the note number if a note)
Value (the second MIDI data byte, e.g. velocity if a note)

"""
import os
import sys
import xml.etree.ElementTree as ET

# This function is needed to get your generated XML to include line breaks and indentations! Doesn't do it on its own! Grrrr..
def indent(elem, level=0):
    i = "\n" + level*"  "
    j = "\n" + (level-1)*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            indent(subelem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = j
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = j
    return elem


multipleOutputs = False #This is changed to true if we detect articulations using multiple output messages

#Get the details from the supplied CSV file
try:
    csvFilePath = sys.argv[1]
except:
    csvFilePath = "artics.csv"

try:
    csvFile = open(csvFilePath,"r")
    textArticLines = csvFile.readlines()
    csvFile.close
except:
    print "No CSV file specified, or cannot find artics.csv"
    sys.exit()

#Get the file stub for use later
plistName = os.path.splitext(os.path.split(csvFilePath)[1])[0]

#Load in the CSV file and create a dictionary of its members
articIDCount = 1 #IDs will start at 1
articsList = []

#Useful data starts on the second row (first row is headers)
#Get each line and store its data in a dictionary object
#Increment the ID number after each line
for line in textArticLines[1:]:
    artic = {}
    lineElems = line.split(',')
    artic["articName"] = lineElems[0].rstrip()
    if artic["articName"] == '':
        artic["articName"] = "--"
    print "Articulation: " + artic["articName"]
    try:
        artic["articChannel"] = int(lineElems[1].rstrip()) - 1
    except:
        artic["articChannel"] = 0
    artic["articSymbol"] = lineElems[2].rstrip()

    #Input
    artic["inType"] = lineElems[3].rstrip()
    if not (artic["inType"] == ''):
        #artic["inType"] = "Note On"
        try:
            artic["inSelector"] = int(lineElems[4].rstrip())
        except:
            artic["inSelector"] = 0
        try:
            artic["inValStart"] = int(lineElems[5].rstrip())
        except:
            artic["inValStart"] = 1
        try:
            artic["inValEnd"] = int(lineElems[6].rstrip())
        except:
            artic["inValEnd"] = 127
        artic["inMode"] = lineElems[7].rstrip()

    #Output 1
    artic["out1Type"] = lineElems[8].rstrip()
    if artic["out1Type"] == '':
        artic["out1Type"] = "Note On"
    try:
        artic["out1Channel"] = int(lineElems[9].rstrip()) - 1
    except:
        artic["out1Channel"] = 0
    try:
        artic["out1Selector"] = int(lineElems[10].rstrip())
    except:
        artic["out1Selector"] = 0
    try:
        artic["out1Val"] = int(lineElems[11].rstrip())
    except:
        artic["out1Val"] = 0

    #Output 2
    artic["out2Type"] = lineElems[12].rstrip()
    if not (artic["out2Type"] == ''): #Only if we're using the 2nd/3rd outputs
        try:
            artic["out2Channel"] = int(lineElems[13].rstrip()) - 1
        except:
            artic["out2Channel"] = 0
        try:
            artic["out2Selector"] = int(lineElems[14].rstrip())
        except:
            artic["out2Selector"] = 0
    	try:
            artic["out2Val"] = int(lineElems[15].rstrip())
        except:
            artic["out2Val"] = 0

    #Output 3
    artic["out3Type"] = lineElems[16].rstrip()
    if not (artic["out3Type"] == ''): #Only if we're using the 3rd output
        try:
            artic["out3Channel"] = int(lineElems[17].rstrip()) - 1
        except:
            artic["out3Channel"] = 0
        try:
            artic["out3Selector"] = int(lineElems[18].rstrip())
        except:
            artic["out3Selector"] = 0
        try:
            artic["out3Val"] = int(lineElems[19].rstrip())
        except:
            artic["out3Val"] = 0

    artic["ID"] = articIDCount
    articsList.append(artic)
    articIDCount += 1


#Create the root XML (plist) tree
root = ET.Element("plist", attrib={'version':'1.0'})
dict = ET.SubElement(root, "dict")
tKey = ET.SubElement(dict, "key")
tKey.text = "Articulations"
arrayArtics = ET.SubElement(dict, "array")

for artic in articsList:
    articDict = ET.SubElement(arrayArtics, "dict")
    tKey = ET.SubElement(articDict, "key")
    tKey.text = "ArticulationID"
    tInteger = ET.SubElement(articDict, "integer")
    tInteger.text = str(artic["ID"])
    tKey = ET.SubElement(articDict, "key")
    tKey.text = "ID"
    tInteger = ET.SubElement(articDict, "integer")
    tInteger.text = str(1000 + artic["ID"])
    tKey = ET.SubElement(articDict, "key")
    tKey.text = "MidiChannel"
    tInteger = ET.SubElement(articDict, "integer")
    tInteger.text = str(artic["articChannel"])
    tKey = ET.SubElement(articDict, "key")
    tKey.text = "Name"
    tString = ET.SubElement(articDict, "string")
    tString.text = artic["articName"]
    tKey = ET.SubElement(articDict, "key")
    tKey.text = "Output"
    outArray = ET.SubElement(articDict, "array")

    #Do output 1
    output = ET.SubElement(outArray, "dict")
    tKey = ET.SubElement(output, "key")
    tKey.text = "MB1"
    tInteger = ET.SubElement(output, "integer")
    tInteger.text = str(artic["out1Selector"])
    tKey = ET.SubElement(output, "key")
    tKey.text = "MidiChannel"
    tInteger = ET.SubElement(output, "integer")
    tInteger.text = str(artic["out1Channel"])
    tKey = ET.SubElement(output, "key")
    tKey.text = "Status"
    tString = ET.SubElement(output, "string")
    tString.text = artic["out1Type"]
    tKey = ET.SubElement(output, "key")
    tKey.text = "ValueLow"
    tInteger = ET.SubElement(output, "integer")
    tInteger.text = str(artic["out1Val"])
    tKey = ET.SubElement(articDict, "key")
    tKey.text = "OutputChannel"
    tInteger = ET.SubElement(articDict, "integer")
    tInteger.text = str(artic["out1Channel"])

    #Do output 2 if not empty
    if not (artic["out2Type"]==''):
        multipleOutputs = True
        output = ET.SubElement(outArray, "dict")
        tKey = ET.SubElement(output, "key")
        tKey.text = "MB1"
        tInteger = ET.SubElement(output, "integer")
        tInteger.text = str(artic["out2Selector"])
        tKey = ET.SubElement(output, "key")
        tKey.text = "MidiChannel"
        tInteger = ET.SubElement(output, "integer")
        tInteger.text = str(artic["out2Channel"])
        tKey = ET.SubElement(output, "key")
        tKey.text = "Status"
        tString = ET.SubElement(output, "string")
        tString.text = artic["out2Type"]
        tKey = ET.SubElement(output, "key")
        tKey.text = "ValueLow"
        tInteger = ET.SubElement(output, "integer")
        tInteger.text = str(artic["out2Val"])
        tKey = ET.SubElement(articDict, "key")
        tKey.text = "OutputChannel"
        tInteger = ET.SubElement(articDict, "integer")
        tInteger.text = str(artic["out2Channel"])

    #Do output 3 if not empty
    if not (artic["out3Type"]==''):
        output = ET.SubElement(outArray, "dict")
        tKey = ET.SubElement(output, "key")
        tKey.text = "MB1"
        tInteger = ET.SubElement(output, "integer")
        tInteger.text = str(artic["out3Selector"])
        tKey = ET.SubElement(output, "key")
        tKey.text = "MidiChannel"
        tInteger = ET.SubElement(output, "integer")
        tInteger.text = str(artic["out3Channel"])
        tKey = ET.SubElement(output, "key")
        tKey.text = "Status"
        tString = ET.SubElement(output, "string")
        tString.text = artic["out3Type"]
        tKey = ET.SubElement(output, "key")
        tKey.text = "ValueLow"
        tInteger = ET.SubElement(output, "integer")
        tInteger.text = str(artic["out3Val"])
        tKey = ET.SubElement(articDict, "key")
        tKey.text = "OutputChannel"
        tInteger = ET.SubElement(articDict, "integer")
        tInteger.text = str(artic["out3Channel"])

    if artic["articSymbol"] != '':
        tKey = ET.SubElement(articDict, "key")
        tKey.text = "Symbol"
        tString = ET.SubElement(articDict, "string")
        tString.text = artic["articSymbol"]


#Add the multiple outputs tag if we need it
if multipleOutputs==True:
    keyName = ET.SubElement(dict, "key")
    keyName.text = "MultipleOutputsActive"
    dict.append(ET.fromstring("<true/>"))

keyName = ET.SubElement(dict, "key")
keyName.text = "Name"
nameString = ET.SubElement(dict, "string")
nameString.text = plistName + ".plist"
keySwitches = ET.SubElement(dict, "key")
keySwitches.text = "Switches"
arraySwitches = ET.SubElement(dict, "array")

#Run through each artic again, this time detailing the switches
for artic in articsList:
    if not (artic["inType"]==''):
        switchDict = ET.SubElement(arraySwitches, "dict")
        tKey = ET.SubElement(switchDict, "key")
        tKey.text = "ID"
        tInteger = ET.SubElement(switchDict, "integer")
        tInteger.text = str(1000 + artic["ID"])
        tKey = ET.SubElement(switchDict, "key")
        tKey.text = "MB1"
        tInteger = ET.SubElement(switchDict, "integer")
        tInteger.text = str(artic["inSelector"])
        if artic["inMode"] != "Permanent":
            tKey = ET.SubElement(switchDict, "key")
            tKey.text = "Mode"
            tString = ET.SubElement(switchDict, "string")
            tString.text = artic["inMode"]
        tKey = ET.SubElement(switchDict, "key")
        tKey.text = "Status"
        tString = ET.SubElement(switchDict, "string")
        tString.text = str(artic["inType"])
        tKey = ET.SubElement(switchDict, "key")
        tKey.text = "ValueHigh"
        tInteger = ET.SubElement(switchDict, "integer")
        tInteger.text = str(artic["inValEnd"])
        tKey = ET.SubElement(switchDict, "key")
        tKey.text = "ValueLow"
        tInteger = ET.SubElement(switchDict, "integer")
        tInteger.text = str(artic["inValStart"])

indent(root)

tree = ET.ElementTree(root)

with open(plistName + '.plist', 'wb') as f:
    f.write('<?xml version="1.0" encoding="UTF-8" ?>\n<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'.encode('utf8'))  #Header stuff for Logic Articulation .plist file
    tree.write(f, 'utf-8')

f.close()

print "Converted to " + plistName + ".plist"
