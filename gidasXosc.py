import pandas as pd
import numpy as np
from lxml import etree
import lxml.etree as ET     #xml processing
import copy 
import csv 
import os
from pandas.io import excel

#loading the excel file
data_time = pd.read_excel(r'C:\Users\user\Desktop\CHALMERS\AEP project\GIDAS\Excel Files GIDAS\dynamics2021.xlsx')
dfT = pd.DataFrame(data_time)
#print(df)

def caseIDcount(GIDASfile):   #finding the number of crash cases
    with open(GIDASfile,'r') as csvfile:
        reader = csv.DictReader(csvfile)
        column = [row['CASEID'] for row in reader]
        #print(column)
    Cid = int(max(column))
    
    return Cid

cid = caseIDcount('dynamics2021.csv')

#case id startification of dataframes
list_of_CaseDfs = [

    group_df 

    for j, group_df in dfT.groupby('CASEID')

]

# saving each case in seperate csv files
for j, group_df in dfT.groupby('CASEID'):
    group_df.to_csv('{}.csv'.format(j), header=False, index_label=False)


#dataframe of case 1
Case = pd.read_csv(r'2.csv', header=None)   #file change needed for new case xosc file creation
Case.rename(columns={0: 'remove', 1: 'CASEID',2: 'PARTID',3: 'VARIATION',4: 'TIME',5: 'POSX',6: 'POSY',7: 'POSZ',8: 'POSPHI',9: 'POSTHETA',10: 'POSPSI',11: 'VX',12: 'VY',13: 'VZ',14: 'AX',15: 'AY',16: 'AZ',17: 'MUE',18: 'REC'}, inplace=True)
del Case['remove']
Case.to_csv('case2.csv', index=False) # save to new csv file
df_case = pd.DataFrame(Case)

def buildentities(GIDASfile):   #finding and returning the number of participants with assigning names
    # find the CASE ID
    with open(GIDASfile,'r') as csvfile:
        reader = csv.DictReader(csvfile)
        column = [row['PARTID'] for row in reader]

    a = int(max(column))

    #build the nameEntities in Xosc
    nameofentities = []

    for i in range(a):
        num = str(i+1)       
        nameofentities.extend(['object_' + num])

    return nameofentities, a

cases = buildentities('case2.csv')  # file change needed


def buildMangroups(GIDASfile):   #finding and returning the number of participants with assigning names
    # find the CASE ID
    with open(GIDASfile,'r') as csvfile:
        reader = csv.DictReader(csvfile)
        column = [row['PARTID'] for row in reader]

    b = int(max(column))
    #print(a)

    #build the nameEntities in Xosc
    mangroups = []

    for i in range(b):
        num = str(i+1)       
        mangroups.extend(['mangroup_' + num])

    return mangroups, b 

maneuver_groups = buildMangroups('case2.csv')  #file change needed

#####################################################################################


# Load the xosc-template-file
parser = ET.XMLParser(remove_blank_text=True) #removes whitespace nodes between elements
treeXosc = ET.parse('ESmini_Template.xosc', parser) 
rootXosc = treeXosc.getroot() #root element is the html element. This function returns root element of the tree root.

def addEntitiesToXoscTemplate(rootXoscTempl, numEntities):

    actObjParent = rootXoscTempl.find(".//Entities")
    privateObjParent = rootXoscTempl.find(".//Actions")
    seqObjParent = rootXoscTempl.find(".//Act")
    VertexObjParent = rootXoscTempl.find(".//Polyline")
                    
    # We will just duplicate these to use when we add to the template (deepcopy creates new list of elements and does not make changes to the original)       
    dupl_Object = copy.deepcopy(actObjParent.find(".//ScenarioObject"))
    dupl_Private = copy.deepcopy(privateObjParent.find(".//Private"))
    dupl_Sequence = copy.deepcopy(seqObjParent.find(".//ManeuverGroup"))
    dupl_vertex = copy.deepcopy(seqObjParent.find(".//Vertex"))
    #print(dupl_vertex)
    # Append as many Object as entities in the VTD
    for i in range(0, numEntities-1):
        actObjParent.append(copy.deepcopy(dupl_Object))

    # Append as many Init as entities in the VTD
    for i in range(0, numEntities-1):
        privateObjParent.append(copy.deepcopy(dupl_Private))

    # Append as many Init as entities in the VTD
    for i in range(0, numEntities-1):
        seqObjParent.append(copy.deepcopy(dupl_Sequence))

gidasent = addEntitiesToXoscTemplate(rootXosc, cases[1])


# def getVhlTypeByEntityName(xoscIn, entityName):    
#     # A utility function that just adds some basic information to the xosc template

#     try:
#         # Fix story owner 
#         vhlType = xoscIn.find(".//Entities/ScenarioObject[@name='" + entityName + "']/Vehicle").get('vehicleCategory')
#     except:
#         vhlType = 'Error'
#         #print('Cannot parse ' + xoscIn)

#     return vhlType

# gidasve = getVhlTypeByEntityName(rootXosc, 'Car')
    
def setEntityNameByOrder(rootXosc, nameentities): #to name the entities, actions and entity references in ascending order to be distinct

    # Get all nodes for objects, inits and sequences - the now complete file (all nodes for entities just duplicated) 
    allObjects = rootXosc.findall(".//Entities/ScenarioObject")
    allInits = rootXosc.findall(".//Storyboard/Init/Actions/Private")
    allSequences = rootXosc.findall(".//Story/Act/ManeuverGroup")

    for i in range(0,len(nameentities)):
        allObjects[i].set("name", nameentities[i])
        allInits[i].set("entityRef", nameentities[i])
        allSequences[i].find(".//Actors/EntityRef").set("entityRef", nameentities[i])

    return rootXosc

def setManeuverNameByOrder(rootXosc, mangroup_n): #to name the maneuvers groups in ascending order to be distinct

    # Get all nodes for objects, inits and sequences - the now complete file (all nodes for entities just duplicated) 
    allact = rootXosc.findall(".//Storyboard/Story/Act/ManeuverGroup")

    for i in range(0,len(mangroup_n)):
        allact[i].set("name",mangroup_n[i])

    return rootXosc

gidaspd = setEntityNameByOrder(rootXosc, cases[0])
mangroup_n = setManeuverNameByOrder(rootXosc, maneuver_groups[0])

#participant data read
data_part = pd.read_excel(r'C:\Users\user\Desktop\CHALMERS\AEP project\GIDAS\Excel Files GIDAS\participant_data.xlsx')
df = pd.DataFrame(data_part)

vehtype = []
#editing the type for all entities
def getVhlTypeByEntityName( rootXosc,typefile):
    with open(typefile,'r') as csvfile:
        reader = csv.DictReader(csvfile)
        caseid = [row['CASEID'] for row in reader]

    with open(typefile,'r') as csvfile:
        reader = csv.DictReader(csvfile)
        VehType = [row['PARTTYPE'] for row in reader]
        
        #print(caseid)
        #print(VehType)
        for vehicles in VehType:
            if vehicles == '0':            
                vehtype.append('car')
            if vehicles == '1':            
                vehtype.append('pedestrian')
            if vehicles == '2':            
                vehtype.append('motorbike')
            if vehicles == '3':            
                vehtype.append('bicycle')
            if vehicles == '4':            
                vehtype.append('truck')
            if vehicles == '5':            
                vehtype.append('bus')
            if vehicles == '6':            
                vehtype.append('tram')
            if vehicles == '7':            
                vehtype.append('trailer')
        # for ind, cases in enumerate(caseid):
        # #print(ind)
        #     if cases == '2':                 # to extract for the 1st case
        #         vehtype.append(VehType[ind])  
        for cases in caseid:
            if cases != '2':            #AS WE DO NOT WANT THE VEHICLE TYPE FOR CASEID1
               vehtype.remove('car')
    print(vehtype)      
    # A utility function that just adds some basic information to the xosc template
    vhlType = rootXosc.findall(".//Entities/ScenarioObject/Vehicle")
    for i in range(0,len(vehtype)):
        vhlType[i].set("vehicleCategory", vehtype[i])
        
    return rootXosc

completetemplate = getVhlTypeByEntityName(rootXosc,'participant_data.csv')

width_values = []
length_values = []
height_values = []
CogX = []
CogY = []
CogZ = []

#editing the type for all entities
def getVhlParamsByEntityName( rootXosc,typefile):
    with open(typefile,'r') as csvfile:
        reader = csv.DictReader(csvfile)
        caseid = [row['CASEID'] for row in reader]
    with open(typefile,'r') as csvfile:
        reader = csv.DictReader(csvfile)
        VehWidth = [row['WIDTH'] for row in reader]
    with open(typefile,'r') as csvfile:
        reader = csv.DictReader(csvfile)
        VehLength = [row['LENGTH'] for row in reader]
    with open(typefile,'r') as csvfile:
        reader = csv.DictReader(csvfile)
        VehHeight = [row['HEIGHT'] for row in reader]
    with open(typefile,'r') as csvfile:
        reader = csv.DictReader(csvfile)
        cogx = [row['COGX'] for row in reader]
    with open(typefile,'r') as csvfile:
        reader = csv.DictReader(csvfile)
        cogy = [row['COGY'] for row in reader]
    with open(typefile,'r') as csvfile:
        reader = csv.DictReader(csvfile)
        cogz = [row['COGZ'] for row in reader]
    #print(VehWidth)
    for ind, cases in enumerate(caseid):
        #print(ind)
        if cases == '1':                 # to extract for the 1st case
            width_values.append(VehWidth[ind])             
            length_values.append(VehLength[ind])            
            height_values.append(VehHeight[ind]) 
            CogX.append(cogx[ind])             
            CogY.append(cogy[ind])            
            CogZ.append(cogz[ind]) 
    #print(width_values)


    # A utility function that just adds some basic information to the xosc template
    vhldimension = rootXosc.findall(".//Entities/ScenarioObject/Vehicle/BoundingBox/Dimensions")
    vehCenter = rootXosc.findall(".//Entities/ScenarioObject/Vehicle/BoundingBox/Center")
    for i in range(0,len(width_values)):
        vhldimension[i].set("width",width_values[i])
        vhldimension[i].set("length",length_values[i])
        vhldimension[i].set("height",height_values[i])
        vehCenter[i].set("x",CogX[i])
        vehCenter[i].set("y",CogY[i])
        vehCenter[i].set("z",CogZ[i])
    return rootXosc

completetemplate = getVhlParamsByEntityName(rootXosc,'participant_data.csv')

def saveFilledXoscTemplateToDisc(xoscOutFileName, treeXoscTempl):
    # Utility function to save the completed xosc to disc
    # We use pretty_print to make it look nice...
    treeXoscTempl.write(xoscOutFileName, xml_declaration=True, pretty_print=True)

    # We have to replace the top row (VTD does not like it otherwise) 
    #addXMLheaderToXoxx(xoscOutFileName)

    return True


def VertexandWorldposExtract(xoscIn, nameentities, num, GIDASfile):
    xlocation = {}
    ylocation = {}
    zlocation = {}
    vertex = {}
    heading = {}
    
    data = pd.read_csv(GIDASfile)
    df = pd.DataFrame(data)
    #print(data)
    for i in range(num):
        #extract the period to test
        i=i+1
        numberofvehicle = df[(df['PARTID'] == i )]
        i=i-1
        #print(numberofvehicle)
        xlocation[i] = list(numberofvehicle.loc[:,'POSX'])
        ylocation[i] = list(numberofvehicle.loc[:,'POSY'])
        zlocation[i] = list(numberofvehicle.loc[:,'POSZ'])
        heading[i] = list(numberofvehicle.loc[:,'POSPSI'])
        vertex[i] = list(numberofvehicle.loc[:,'TIME'])

        #heading[i] = list(numberofvehicle.loc[:,'heading'])
    #print(xlocation[0][0])
    # print(ylocation[0])
    # print(heading[0])

    for v in range(num):   
   
        #print(v)
        name = nameentities[v]
        #print(xlocation[v][0])
        #print(name)
        
        # set the initial location
        initial = xoscIn.find(".//Actions/Private[@entityRef='" + name + "']")
        initWorldVTD = initial.find(".//WorldPosition")
        initWorldVTD.set('x', str(xlocation[v][0]))
        initWorldVTD.set('y', str(ylocation[v][0]))
        initWorldVTD.set('h', str(heading[v][0]))
        initWorldVTD.set('z', str(zlocation[v][0]))
        
        sequencesElem = xoscIn.find(".//Actors/EntityRef[@entityRef='" + name + "']")
        #print(sequencesElem)
        sqepp = sequencesElem.getparent().getparent() # add sqepp

        vertexElem_deepCopy = copy.deepcopy(sqepp.find(".//Vertex[@time='0.0']"))
        #print(vertexElem_deepCopy)

    
        # Remove all the vertices for this polyline
        rootPolyline= sqepp.find(".//Polyline")
        d_root = rootPolyline.getparent().remove(rootPolyline)
      
        # Add it again so that we can fill it with new data
        tmpRoot = sqepp.find(".//Shape")
        ET.SubElement(tmpRoot, 'Polyline') 
        d_root= sqepp.find(".//Polyline")
        AddVert = len(xlocation[v])
        # print(AddVert)
            
        for t in range(AddVert):

            vertexElem_copy = copy.deepcopy(vertexElem_deepCopy)
            
            vertexElem_copy.set("time",str(vertex[v][t]))
            worldElem = vertexElem_copy.find(".//WorldPosition")
            worldElem.set("x",str(xlocation[v][t]))
            worldElem.set("y",str(ylocation[v][t]))
            worldElem.set("h",str(heading[v][t]))
            worldElem.set("z",str(zlocation[v][t]))
            d_root.append(vertexElem_copy)

VertexandWorldposExtract(rootXosc, cases[0], cases[1], 'case2.csv')
saveFilledXoscTemplateToDisc('CASE2.xosc', treeXosc)


