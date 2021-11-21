from types import FrameType, MappingProxyType
import pandas as pd
import numpy as np
from lxml import etree
import lxml.etree as ET
import copy 
import csv
from os import remove, times
 
# Load the xosc-template-file
parser = ET.XMLParser(remove_blank_text=True)
treeXosc = ET.parse('ESmini_Template.xosc', parser)
rootXosc = treeXosc.getroot()

#make sure how many vehicle appear
def buildentities(inDfile):

    # find the number of the tracks 
    with open(inDfile,'r') as csvfile:
        reader = csv.DictReader(csvfile)
        column = [row['trackId'] for row in reader]
    #print(column)

    column = list(map(int,column))
    a = max(column)
    #print(a)

    #build the nameEntities in Xosc
    nameofentities = []

    for i in range(a+1):
        num = str(i+1)
        nameofentities.extend(['object_' + num])

    return nameofentities 

alloffentities = buildentities('00_tracks.csv')
num = len(alloffentities)
print(num)
# print(alloffentities)

#add all entities_1 into the template
def addEntitiestToXoscTemplate(rootXoscTempl, numEntities):

    actObjParent = rootXoscTempl.find(".//Entities")
    privateObjParent = rootXoscTempl.find(".//Actions")
    seqObjParent = rootXoscTempl.find(".//Act")
                
    # We will just duplicate these to use when we add to the template        
    dupl_Object = copy.deepcopy(actObjParent.find(".//ScenarioObject"))
    dupl_Private = copy.deepcopy(privateObjParent.find(".//Private"))
    dupl_Sequence = copy.deepcopy(seqObjParent.find(".//ManeuverGroup"))

    # Append as many Object as entities in the VTD
    for i in range(0, numEntities-1):
        actObjParent.append(copy.deepcopy(dupl_Object))

    # Append as many Init as entities in the VTD
    for i in range(0, numEntities-1):
        privateObjParent.append(copy.deepcopy(dupl_Private))

    # Append as many Init as entities in the VTD
    for i in range(0, numEntities-1):
        seqObjParent.append(copy.deepcopy(dupl_Sequence))

    return rootXoscTempl

completetemplate = addEntitiestToXoscTemplate(rootXosc, num)

#edit the name of all entities
def setEntityNameByOrder( rootXosc, namesEntities):

    # Get all nodes for objects, inits and sequences - the now complete file (all nodes for entities just duplicated) 
    allObjects = rootXosc.findall(".//Entities/ScenarioObject")
    allInits = rootXosc.findall(".//Storyboard/Init/Actions/Private")
    allSequences = rootXosc.findall(".//Story/Act/ManeuverGroup")

    for i in range(0,len(namesEntities)):
        allObjects[i].set("name", namesEntities[i])
        allInits[i].set("entityRef", namesEntities[i])
        allSequences[i].find(".//Actors/EntityRef").set("entityRef", namesEntities[i])

    return rootXosc

completetemplate = setEntityNameByOrder(rootXosc, alloffentities)

#edit the typr for all entities
def getVhlTypeByEntityName( rootXosc,typefile):

    with open(typefile,'r') as csvfile:
        reader = csv.DictReader(csvfile)
        typeofeach_v = [row['class'] for row in reader]
    with open(typefile,'r') as csvfile:
        reader = csv.DictReader(csvfile)
        widthofeach_v = [row['width'] for row in reader]
    with open(typefile,'r') as csvfile:
        reader = csv.DictReader(csvfile)
        lengthofeach_v = [row['length'] for row in reader]

    # print(typeofeach_v)
    print(len(typeofeach_v))
    #print(len(widthofeach_v))
    #print(len(lengthofeach_v))
           
    # A utility function that just adds some basic information to the xosc template
    vhlType = rootXosc.findall(".//Entities/ScenarioObject/Vehicle")
    vhldimension = rootXosc.findall(".//Entities/ScenarioObject/Vehicle/BoundingBox/Dimensions")
    print(len(vhlType))
    for i in range(0,len(vhlType)):
        vhlType[i].set("vehicleCategory", typeofeach_v[i])
        vhldimension[i].set("width",widthofeach_v[i])
        vhldimension[i].set("length",lengthofeach_v[i])
        vhldimension[i].set("height",'1.6')


    return rootXosc

completetemplate = getVhlTypeByEntityName(rootXosc,'00_tracksMeta.csv')



#save the complete template
def saveFilledXoscTemplateToDisc( xoscOutFileName, treeXoscTempl):
    # Utility function to save the completed xosc to disc

    # We use pretty_print to make it look nice...
    treeXoscTempl.write(xoscOutFileName, xml_declaration=True, pretty_print=True)

    # We have to replace the top row (VTD does not like it otherwise) 
    #addXMLheaderToXoxx(xoscOutFileName)

    return True

saveFilledXoscTemplateToDisc('test12.xosc',treeXosc )

#get the trajectory and time information
def numberoftrack_inform(inDfile, number):

    xlocation = []
    ylocation = []
    frame = []
    heading = []
    
    data = pd.read_csv(inDfile)
    df = pd.DataFrame(data)
   
    for i in range(num):
        #extract the period to test
        numberofvehicle = df[(df['trackId'] == i )]
        xlocation[i] = [numberofvehicle.loc[:,'xCenter']]
        ylocation[i] = [numberofvehicle.loc[:,'yCenter']]
        frame[i] = [numberofvehicle.loc[:,'frame']]
        heading[i] = [numberofvehicle.loc[:,'heading']]
    #print(xlocation)
    #print(type(xlocation))
    b = len(xlocation.keys())
    print(xlocation)

    return xlocation, ylocation, frame, heading,b


#put the trajectory information into the template
def replaceXYHInXoscByEntityName(xoscIn, xoscOut, entityName, num, inDfile):

    xlocation = {}
    ylocation = {}
    frame = {}
    heading = {}
    
    data = pd.read_csv(inDfile)
    df = pd.DataFrame(data)
    print(df)
    for i in range(num):
        #extract the period to test
        numberofvehicle = df[(df['trackId'] == i )]
        xlocation[i] = list(numberofvehicle.loc[:,'xCenter'])
        ylocation[i] = list(numberofvehicle.loc[:,'yCenter'])
        frame[i] = list(numberofvehicle.loc[:,'frame'])
        

        # for ii in range(len(frame[i])):
        #     time[i][ii] = 0.04*float(frame[i][ii])
        #     return time[i]

        heading[i] = list(numberofvehicle.loc[:,'heading'])
    # print(frame[0])
    # print(xlocation[0])
    # print(ylocation[0])
    # print(heading[0])
    

    for v in range(num):



        name = entityName[v]

        # set the initial location
        initial = xoscIn.find(".//Actions/Private[@entityRef='" + name + "']")
        initWorldVTD = initial.find(".//WorldPosition")
        initWorldVTD.set('x', str(xlocation[v][0]))
        initWorldVTD.set('y', str(ylocation[v][0]))
        initWorldVTD.set('h', str(heading[v][0]))              
        
        #print(name)
        sequencesElem = xoscIn.find(".//Actors/EntityRef[@entityRef='" + name + "']")
        #print(sequencesElem)
        sqepp = sequencesElem.getparent().getparent() # add sqepp

        vertexElem_deepCopy = copy.deepcopy(sqepp.find(".//Vertex[@time='0.0']"))
        #print(vertexElem_deepCopy)

        
        # saveFilledXoscTemplateToDisc('test13.xosc',treeXosc)

        # Remove all the vertices for this polyline
        rootPolyline= sqepp.find(".//Polyline")
        d_root = rootPolyline.getparent().remove(rootPolyline)
      
        # Add it again so that we can fill it with new data
        tmpRoot = sqepp.find(".//Shape")
        ET.SubElement(tmpRoot, 'Polyline') 
        d_root= sqepp.find(".//Polyline")
        numVertToAdd = len(xlocation[v])
        # print(numVertToAdd)
            
        for t in range(numVertToAdd):

            vertexElem_copy = copy.deepcopy(vertexElem_deepCopy)
            
            time = 0.04*(float((frame[v][t])))
            vertexElem_copy.set("time",str(time))
            worldElem = vertexElem_copy.find(".//WorldPosition")
            worldElem.set("x",str(xlocation[v][t]))
            worldElem.set("y",str(ylocation[v][t]))
            worldElem.set("h",str(heading[v][t]))
            d_root.append(vertexElem_copy)

    saveFilledXoscTemplateToDisc(xoscOut, treeXosc)

replaceXYHInXoscByEntityName(rootXosc,'test14.xosc',alloffentities,num,'00_tracks.csv')








