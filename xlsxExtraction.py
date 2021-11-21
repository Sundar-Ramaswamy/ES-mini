import os
import pandas as pd
from pandas.io import excel
import csv

#loading the excel file
data_time = pd.read_excel(r'C:\Users\user\Desktop\CHALMERS\AEP project\GIDAS\Excel Files GIDAS\dynamics2021.xlsx')
df = pd.DataFrame(data_time)
#print(df)

def caseIDcount(GIDASfile):   #finding the number of crash cases
    with open(GIDASfile,'r') as csvfile:
        reader = csv.DictReader(csvfile)
        column = [row['CASEID'] for row in reader]

    Cid = int(max(column))
    #print(Cid)
caseIDcount('dynamics2021.csv')

#extract data for caseid 1       #here FOR loop can be used to create seperate excel files for each case
partsinCaseID1 = df[(df['CASEID'] < 2 )]
partsinCaseID1.to_csv('CaseID1.csv', index=False)

Case1 = pd.read_csv(r'C:\Users\user\Desktop\CHALMERS\AEP project\GIDAS\CaseID1.csv')
df_case1 = pd.DataFrame(Case1)
#print(df_case1)

def buildentities(GIDASfile):   #finding and returning the number of participants with assigning names
    # find the CASE ID
    with open(GIDASfile,'r') as csvfile:
        reader = csv.DictReader(csvfile)
        column = [row['PARTID'] for row in reader]

    a = int(max(column))
    #print(a)

    #build the nameEntities in Xosc
    nameofentities = []

    for i in range(a):
        num = str(i+1)       
        nameofentities.extend(['object_' + num])

    return nameofentities 

cases = buildentities('CaseID1.csv')

def VertexandWorldposExtract(GIDASfile):
    vertex = []
    xlocation = []
    ylocation = []
    frame = []
    heading = []
    with open(GIDASfile,'r') as csvfile:
        reader = csv.DictReader(csvfile)
        xlocation = [row['TIME'] for row in reader]
    with open(GIDASfile,'r') as csvfile:
        reader = csv.DictReader(csvfile)
        xlocation = [row['POSX'] for row in reader]
    with open(GIDASfile,'r') as csvfile:
        reader = csv.DictReader(csvfile)
        ylocation = [row['POSY'] for row in reader]
    with open(GIDASfile,'r') as csvfile:
        reader = csv.DictReader(csvfile)
        zlocation = [row['POSZ'] for row in reader]
    with open(GIDASfile,'r') as csvfile:
        reader = csv.DictReader(csvfile)
        heading = [row['POSPSI'] for row in reader]
    return vertex, xlocation, ylocation, frame, heading

inputs = VertexandWorldposExtract('CaseID1.csv')

