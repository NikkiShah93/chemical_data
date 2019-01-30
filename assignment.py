
# # Assignment

# In this assignment I have four data sets that each includes different properties of chemical compound.
# The goal is to have a database that contains name, CAS number, the source/s and some properties that are optional.
# The four data sets are:
# 1.	ChemIDPlus.  This is stored in XML format.  
# 2.	MeSH Supplemental Records.  This is stored in XML format.
# 3.	Pesticide Product Information System (PPIS).  This is in text table format across multiple files. 
# 4.	IARC List of Classifications.  This is in Excel format.
# 

# First step is to import libraries that is going to be needed for this exercise. 


import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')


# # Data cleaning
# In this part, I will read each data set in here and then work on cleaning them one by one and eventually have
# the parts that I will be using in my final database clean and ready.
# 
# I have more experince working with Excel files in Python so I start with that. 
# First read it here, so I could have a better understanding of what I am working with.
# 
# Then I will work on text files, that apears to be fixed width files.
# 
# I will work on the XML files at the end of this part, since I think they are the challenging ones for me.


#First reading it using Pandas (personal perefrence)
#After taking look at it noticed the header are on the second row (indexing starts at 0 in Python)

iarc = pd.read_excel('input\List_of_Classifications.xls', header = 1)

#The only two columns that I will be using from this table are CAS # and Agent

classification_list = iarc[["CAS No.", "Agent"]]

#There are lots of NaNs in the file and since we want to have the CAS # for 
#all the chemicals that we are using in the final database, we could just drop them

classification_list.dropna(subset = ['CAS No.'], inplace = True, axis = 0)

#The index has to be reset when you drop certain rows
#Indexing is not that important in the end since I want to save these data sets without their indexing

classification_list.reset_index(drop = True, inplace = True)

#Checking the new data set there are strange characters in the CAS # and agent names
#Since there are html tags in some rows, we could use BeautifulSoup to get rid of them

classification_list['Agent'] = [BeautifulSoup(text, 'lxml').get_text() for text in classification_list['Agent']]
classification_list['CAS No.'] = [BeautifulSoup(text, 'lxml').get_text() for text in classification_list['CAS No.']]

#There are some unwanted characters as well, so we try to clean them up too

classification_list['CAS No.'] = classification_list['CAS No.'].str.split("\n").str[0]
classification_list['CAS No.'] = classification_list['CAS No.'].str.split("[").str[0]

#Adding a column for source

classification_list['Source_IARC'] = 'IARC'

#Taking a look at this, looks clean and ready to use

classification_list.to_excel('IARC_clean.xls', index= False)


# For the next step, I want to read in the text file.
# In this data set we have several text files that are fixed width data sets so we read them using that.
# After carful consideration of each file and reading the pdf file I tried to go about doing this in the following way:


#First file to read in is the Chemcas.txt
#Taking a look at it I figured that by specifying the colspecs we could get the columns
#Using the pdf file, we used the correct naming for each column

chemCas = pd.read_fwf('input/CHEMCAS.TXT', colspecs=[(0, 6), (7, None)], header = None)
chemCas.columns = ['PC_Code', 'CAS_NR']

#The scond file is Chemname.txt
#This one was the tricky one since the pdf did not mention the naming for each column specifically
#but I came up with something that I could understand
#I skiped the first 4 rows because it was difficult to understand them

chemName = pd.read_fwf('input/CHEMNAME.TXT', header = None, colspecs=[(0,6),(6,7),(7,10),(10, 12), (12, None)], skiprows = 4)

#Getting rid of the whitespaces in the following columns
chemName[3].map(str)
chemName[4].map(str)

chemName[3].str.strip(' ')
chemName[4].str.strip(' ')

#Replacing the NaN values with an empty character for the concatenation purposes

chemName[3].replace(np.nan, '', inplace = True)

#Having both of the columns in column 4

chemName[4] = chemName[3] + chemName[4]

#I noticed the rows with R in the first column of text file
#have the CAS number, so I used the second column that include that part to make a new dataframe for CAS #
#I get the ID part as well in order to connect the names to the right CAS #

CAS_no = chemName[chemName[1] == 'R'][[0, 4]]

#Cleaning parts because it has some strings as well as the CAS # itself

CAS_no[4] = CAS_no[4].str.split('No.').str[1]
CAS_no[4] = CAS_no[4].str.split('(').str[0]


#Getting rid of the whitespace

CAS_no[4] = CAS_no[4].str.strip(' ')

#Adding header

CAS_header = ['ID', 'CAS_NR']
CAS_no.columns = CAS_header

#I noticed that there are T, C, S values in the second column as well so I just
#made a dataframe to record each of them there
#The ID is needed as well for the last part

t_name = chemName[chemName[1] == 'T'][[0, 4]]
t_name.columns = ['ID', 'T_name']
c_name = chemName[chemName[1] == 'C'][[0, 4]]
c_name.columns = ['ID', 'C_name']

#Based on what was mentioned in the pdf file, the rows with S are Systematic names

s_name = chemName[chemName[1] == 'S'][[0, 4]]
s_name.columns = ['ID', 'systematic_name']

#In order to make it easire for myself, I replaced nan values in second columns with string 'Na'
#and then record them in another dataframe
#It was mentionded in the pdf file that this part is common name 
#so that's what I called this column

chemName[1].replace(np.nan, 'Na', inplace = True)
names = chemName[chemName[1] == 'Na'][[0, 4]]
names_header = ['ID', 'Common_name']
names.columns = names_header

#Other text files such as Company.txt, Formula.txt, Prodtype.txt and Product.txt were read into here as well
#I used pdf file as reference for the columns name

comName = pd.read_fwf('input/COMPANY.TXT', header = None, colspecs=[(0,6),(7,66),(66, 126), (126, 176), (176, 226), (226, 228), (228, 233), (233, 273), (273, 283)])
comName.columns = ['CO_NR', 'CO_Name', 'CO_Name2', 'CO_Street', 'CO_City', 'CO_State', 'CO_Zip', 'CO_Contact', 'CO_Phone']

formula = pd.read_fwf('input/FORMULA.TXT', header = None, colspecs=[(0,11),(11,17),(17, None)])
formula.columns = ['REG_NR', 'PC_Code', 'PC_PCT']

prodtype = pd.read_fwf('input/PRODTYPE.TXT', header = None, colspecs=[(0,11),(11, None)])
prodtype.columns = ['REG_NR', 'Type_Code']

product = pd.read_fwf('input/PRODUCT.TXT', header = None, colspecs=[(0,11),(11,13),(13, 14), (14, 22), (22, 30), (30, 32), (32, 102), (102, 103), (103, 105), (105, None)])
product.columns = ['REG_NR', 'Form_Code', 'TOX_Code', 'APPR_Date', 'CAN_Date', 'CT_Date', 'Prod_Name', 'RUP_Flag', 'PM_Code', 'COND_Flag']

#Going through the dataframes, I think common and systematic names as well as CAS # are the most important columns
#so I only use them in the final datafram from this source
#I used ID for joining since that was the only common part between them

ppis = names.join(CAS_no.set_index('ID'), on = 'ID')
ppis.dropna(subset = ['CAS_NR'], inplace = True)
ppis.reset_index(drop=True, inplace=True)
ppis = ppis.join(t_name.set_index('ID'), on = 'ID')
ppis = ppis.join(c_name.set_index('ID'), on = 'ID')
ppis = ppis.join(s_name.set_index('ID'), on = 'ID')

#There were couple of cases that had / in instead of - in the CAS #
#I was trying to target those but I could not
#Then I figure it out that they are not actually in the dataset here
#so something was happening to them when I was saving them as CSV file
#so I decided on saving them as excel file and see what happens
#fortunately, the problem was fixed by doing that

#My attepts to replace the non existing forward slash

#ppis['CAS_NR'] = ppis['CAS_NR'].map(str)
#ppis[~ppis['CAS_NR'].str.contains('/')]
#ppis['CAS_NR'].replace('/', np.nan, inplace = True)
#ppis.dropna(subset=['CAS_NR'], inplace = True)


#Correcting for the spaces in the middle of the names

ppis['Common_name'].replace('-\s+', '-', regex=True, inplace = True)
ppis['systematic_name'].replace('-\s+', '-', regex=True, inplace = True)


#Adding source column 

ppis['Source_PPIS'] = 'PPIS'

#Final dataframe from PPIS source

ppis.to_excel('PPIS_clean.xls', index = False)


# For me the tricky part was working with XML files.
# I have never actually worked with this type especially when it has many attributes.
# After doing research and try some different methods I came up with the following code.
# It might not be most efficient way to do this but it is the way I found that could actually give me what I am looking for.
# 
# The first data set that I am working with in XML format is ChemId.xml
# I looked for attributes that I thought could be useful for the final result.


#Opening the file and saving it into chemId using BeatifulSoup

with open("input/chemid.xml") as chemid:
    chemId = BeautifulSoup(chemid, 'xml')
    
#Creating a list that could be used to append the values to

chemID_data = []

#Looping through the chemId and finding the chamical tags that are used for each chemical compound (Used dtd file as reference)

for element in chemId.find_all('Chemical'):
    
    #I thought this part could be useful so record this value
    
    if element.find('DescriptorName') == None:
        chemID_data.append(None) #There was a problem with None values so I had to make a condition for that
    else:
        chemID_data.append((element.find('DescriptorName')).text)
        
    #Systematic name was another attribute that I found useful for the final result    
        
    if element.find('SystematicName') == None:
        chemID_data.append(None) #Solving the None value problem
    else:
        chemID_data.append((element.find('SystematicName')).text)
        
    #Definetly the CAS # is important and has to be recorded
    
    if element.find('CASRegistryNumber') == None:
        chemID_data.append(None)
    else:
        chemID_data.append((element.find('CASRegistryNumber')).text)
    
    #Thought having the source could be nice
        
    if element.find('SourceList') == None:
        chemID_data.append(None)
    else:
        chemID_data.append((element.find('SourceList')).text)
        
#We need to make it more look like a table since it is just a list of data
#In order to do that we reshape it to 83 rows and 4 columns

#len(chemID_data)

chemID_data = np.reshape(chemID_data, (83, 4))

#Convert it to dataframe because I am trying to have all the data set in this format which is
#very straightforward to work with

chemID_data = pd.DataFrame(chemID_data)

#Header for each columns

chemID_data.columns = ['DescriptorName', 'SystematicName', 'CASRegistryNumber', 'SourceList']

#There was a case that CAS # had PubMed,... next to it and I tried to correct that data

chemID_data['CASRegistryNumber'] = chemID_data['CASRegistryNumber'].str.split('PubMed').str[0]
chemID_data['SystematicName'].replace('INDEX NAME NOT YET ASSIGNEDNLM', np.nan, inplace = True)
chemID_data.dropna(subset=['SystematicName'], inplace = True)
chemID_data.reset_index(drop = True, inplace = True)

#Adding the source column

chemID_data['Source_ChemID'] = 'ChemID'

#Final result of ChemId data set

chemID_data.to_excel('ChemID_clean.xls', index = False)


# The 4th data set that I will be reading into here is Mesh
# This one is in XML format as well so I will try to do the same thing that I did for ChemId data set for this one
# I will be looking for the data that could be useful for the final result


#Opening the MeSHSupplemental.xml and saving it in Mesh using BeautifulSoup

with open("input/MeSHSupplemental.xml") as Mesh:
    Mesh = BeautifulSoup(Mesh, 'xml')
    
#Creating an empty list fot recording the values that I will be looking for

Mesh_data = []

#Looping through the Mesh
#After looking into the data I found that each chemical records are called SupplementaRecord (dtd file was not really helpful in here)
#that is why I found that one

for element in Mesh.find_all('SupplementalRecord'):
    
    #Concept name was including the name so I recorded them
    
    if (element.find('ConceptName')).text == None: #Considering the None case
        Mesh_data.append(None)
    else:
        Mesh_data.append((element.find('ConceptName')).text)
    
    #CAS name is another name that might be helpful
    
    if (element.find('CASN1Name')) == None:#Considering None case
        Mesh_data.append(None)
    else:
        Mesh_data.append((element.find('CASN1Name')).text)
        
    #Recording the CAS # for each row    
    if (element.find('RegistryNumber')) == None:
        Mesh_data.append(None)
    else:
        Mesh_data.append((element.find('RegistryNumber')).text)
    
        
    #Having the source coule be nice as well
    if (element.find('Source')) == None:
        Mesh_data.append(None)
    else:
        Mesh_data.append((element.find('Source')).text)
        
    
#len(Mesh_data)

#We need to reshape the list in order to have something closer to a table

Mesh_data = np.reshape(Mesh_data, (79, 4))

#Converting to dataframe for future uses

Mesh_data = pd.DataFrame(Mesh_data)

#Setting the column names

Mesh_data.columns = ['ConceptName', 'CASN1Name', 'RegistryNumber', 'Source']

#Getting rid of the \n characters in the names

Mesh_data['ConceptName'] = Mesh_data['ConceptName'].str.split('\n').str[1]

#Replacing 0 with NaN for easier dropping

Mesh_data['RegistryNumber'].replace('0', np.nan, inplace = True)
Mesh_data = Mesh_data[Mesh_data['RegistryNumber'].str.contains("A|C|E|F|O|Y|\|/") == False]
Mesh_data.dropna(subset=['RegistryNumber'], inplace = True)

#We have to reset the index when we drop values from dataframe

Mesh_data.reset_index(drop = True, inplace = True)

#Adding the source column

Mesh_data['Source_MeSH'] = 'MeSH'

#Final result of the Mesh dataset

Mesh_data.to_excel('Mesh_clean.xls', index = False)


# Now that we have our datasets, we could start working on generating files that only contain the columns that we are
# looking for and get rid of the duplicates.
# In order to do that I will be generating several tables.
#      1. containg different names for each chemical
#      2. containg the CAS # for each chemical
#      3. containing sources and CAS # for each chemical


#For name table we need to have common name and systematic names for each chemical
#We do not want any duplicates
#We join the tables on CAS numbers and it is an outer join since we want to have everything
#The only data set that does not have to be an outer join is the IARC
#We only want the chemical compounds that are already in the data, so we get a left join

names_final = chemID_data.join(ppis.set_index(['systematic_name', 'CAS_NR', 'Common_name']), 
                         how ='outer', on = ['SystematicName', 'CASRegistryNumber', 
                        'DescriptorName']).join(Mesh_data.set_index(['CASN1Name', 'RegistryNumber', 'ConceptName']), 
                         how = 'outer', on = ['SystematicName', 'CASRegistryNumber','DescriptorName']).join(classification_list.set_index(['Agent']),
                         how = 'left', on = ['DescriptorName'])[['DescriptorName', 'SystematicName', 'CASRegistryNumber']]

#Getting rid of the duplicates

names_final.drop_duplicates(subset=['DescriptorName'], inplace=True)
names_final.drop_duplicates(subset=['SystematicName'], inplace=True)

#names_final = names_final[names_final['CASRegistryNumber'].str.contains("A|C|E|F|O|Y|\|/") == False]


#Reseting the index since we droped couple of rows

names_final.reset_index(drop = True, inplace=True)

#Getting the CAS # their own file

CAS_final = names_final['CASRegistryNumber']
CAS_final.to_excel('CAS_final.xls', index = False)

#Final result for names 
names_final.to_excel('names_final.xls', index = False, encoding='utf-8')



#For source table
#We could have a table of CAS # and find in which tables they apear

source_final = ppis.join(chemID_data.set_index('CASRegistryNumber'),
                      how = 'outer', on = 'CAS_NR').join(Mesh_data.set_index('RegistryNumber'),
                      how = 'outer', on = 'CAS_NR').join(classification_list.set_index('CAS No.'), 
                      how = 'left', on = 'CAS_NR')[['Source_PPIS', 'Source_ChemID', 'Source_MeSH', 'Source_IARC', 'CAS_NR']]

#Replacing NaN values with empty space

source_final['Source_PPIS'].replace(np.nan, '', inplace = True) 
source_final['Source_ChemID'].replace(np.nan, '', inplace = True)
source_final['Source_IARC'].replace(np.nan, '', inplace = True) 
source_final['Source_MeSH'].replace(np.nan, '', inplace = True)

#Adding the values in columns so we could have all the sources that the chemicals apeared

source_final['Source'] = source_final['Source_PPIS'] + ' ' + source_final['Source_ChemID'] + ' ' + source_final['Source_MeSH'] + ' ' + source_final['Source_IARC']

#Droping the columns that we are done with

source_final.drop(labels=['Source_ChemID', 'Source_IARC', 'Source_MeSH', 'Source_PPIS'], axis = 1, inplace=True)
source_final.drop_duplicates(subset=['CAS_NR'], inplace=True)

#Only having the values for chemicals that are in CAS_final file

source_final = source_final[source_final['CAS_NR'].isin(CAS_final)]

#Taking a look at the final result
source_final.to_excel('source_final.xls', index = False)


# # Database development
# Now it is time to make the database itself.
# In order to do that, I will use SQLite3 library from Python since I am working on this on my laptop
# and it does not require an actual server.
# I will be using the 3 data set that I generated in the privous steps:
# the CAS_final, names_final and source_final.
# I want to generate 3 tables in this database. 
# 
# 1. Contains the main chemID as pk that I will be giving to each chemical structure and its CAS number. 
# 2. Contains the nameID as pk and chemID as fk and common and systematic name of each chemical.
# 3. Contains the sourceID as pk, nameID and chemID as fk and source of each chemical.
# 
# The dataset that I am looking to gain from this database has to contain chemID, names and sources.


import sqlite3

#Reading the CAS_final file in here

data = pd.read_excel('CAS_final.xls', header = None)

#Generating a database called chemicals
#and connecting to it

database = sqlite3.connect('output/chemicals.db')

#Generatin a cursor

c = database.cursor()

#Defining a function that create the table if it does not exist
#I include the not exist part so it won't generate an error if the table already exists

def create_table():
    
    #I want to have 3 columns, chemID as pk, and CAS_NUMBER
    
    c.execute('CREATE TABLE IF NOT EXISTS chemicalsID(chemID INT PRIMARY KEY, CAS_NUMBER VARCHAR(30))')
    
#Defining a function for inserting the data into our first table
    
def insert_data():
    
    #I am giving each chemical an ID of integer that is incrementing as I go forward
    #Then I just add CAS number from the CAS_final file that is in the ith position
    
    for i in range(len(data)):
        value =  'INSERT INTO chemicalsID VALUES('+ str(i)+",\'"+ data[0][i]+ "\')" #I found an easier way that I used for next table
        value = str(value)
        c.execute(value)
    
    #Commiting the execution
    
    database.commit()
    
    #Closing the cursor
    
    c.close()
    
    #Closing the connection 
    
    database.close()
    
#Calling the functions that we generated above

create_table()
insert_data()



#For second table in our database I will use the names_final file
#Reading the file in here

names_data = pd.read_excel('names_final.xls')

#Connecting to the chemicals database that we generated in the previous step

database = sqlite3.connect('output/chemicals.db')

#Generating a cursor

c = database.cursor()

#Defining a function for creating the second table
#In here I want to have 4 columns
#nameID as pk, chemID as fk and common and systematic name for each chemical

def create_table():
    c.execute('CREATE TABLE IF NOT EXISTS chemicalsName(nameID INT PRIMARY KEY, chemID INT, common_name VARCHAR(100), systematic_name VARCHAR(100), FOREIGN KEY (chemID) REFERENCES chemicalsID(chemID))')
    
#Defining a function for inserting the data into this table

def insert_data():
    
    for i in range(len(names_data)):
        
        #Getting the CAS number from the names_data file
        
        cas_num = names_data['CASRegistryNumber'][i]
        
        #Finding the chemID of this CAS # from our chemicalsID table
        
        c.execute("SELECT chemID FROM chemicalsID WHERE CAS_NUMBER = \'"+ (cas_num)+"\'")
        chemID = c.fetchone()[0]
        
        #Getting the names from our names_data file
        
        common_name = names_data['DescriptorName'][i]
        systematic_name = names_data['SystematicName'][i]
        
        #Inserting the values into the table
        #I found this way easier than the one I used for first table but I kept the other version too
        
        c.execute("INSERT INTO chemicalsName VALUES(?, ?, ?, ?)", (i, chemID, common_name, systematic_name))
    
    #comming the execution    
    
    database.commit()
    
    #Closing the cursor
    
    c.close()
    
    #Closing the connection to database
    
    database.close()
    

#Calling the generated functions

create_table()
insert_data()



#For the third table in our database
#The source_final file is going to be used

#Reading the file in here

source_data = pd.read_excel('source_final.xls')

#Connecting to the chemicals database

database = sqlite3.connect('output/chemicals.db')

#Generating the cursor

c = database.cursor()

#Defining a function for creating the third table
#In here I want to have 4 columns
#source_ID as pk, nameID and chemID as fk and source for each chemical

def create_table():
    c.execute('CREATE TABLE IF NOT EXISTS chemicalSource(source_ID INT PRIMARY KEY, chemID INT, nameID INT, source VARCHAR(100), FOREIGN KEY (chemID) REFERENCES chemicalsID(chemID), FOREIGN KEY (nameID) REFERENCES chemicalsName(nameID))')
    
#Defining a function for inserting the data into this table

def insert_data():
    for i in range(len(source_data)):
        
        #Fining the ith CAS # in source_data file
        
        cas_num = source_data['CAS_NR'][i]
        
        #Finding the chemID of that CAS # in the chemicalsID table
        
        c.execute("SELECT chemID FROM chemicalsID WHERE CAS_NUMBER = \'"+ (cas_num)+"\'")
        chemID = c.fetchone()[0]
        
        #Finding the nameID of that chemID that we found above in chemicalsName table
        
        c.execute("SELECT nameID FROM chemicalsName WHERE chemID = ?", (chemID,))
        nameID = c.fetchone()[0]
        
        #Finding the source of ith value in source_data file
        
        source = source_data['Source'][i]
        
        #Insering the data into the table
        
        c.execute("INSERT INTO chemicalSource VALUES(?, ?, ?, ?)", (i, chemID, nameID, source))
    
    #Commiting the execution
    
    database.commit()
    
    #Closing the cursor
    
    c.close()
    
    #Closing the connection
    
    database.close()
    
#Calling the functions

create_table()
insert_data()


# Now that we have our database we could get the main result that we were looking for.
# We want to execute a query that could get the columns that we were looking for.
# The CAS #, names and sources of each chemical in a way that they only apear once (I took care of duplicates in the cleaning 
# part but I could have uniqueness as a constraint in generating the tables as well)
# I order to do that, I will select the columns from joined tables on chemID.


#Connecting to the database

database = sqlite3.connect('output/chemicals.db')

#Generating a cursor

c = database.cursor()

#Select statement that has to target CAS_NUMBER, common_name, systematic_name and source
#We will join the 3 tables on chemID which is in all the tables

c.execute('SELECT CAS_NUMBER, common_name, systematic_name, source FROM chemicalsID join chemicalsName on chemicalsID.chemID = chemicalsName.nameID join chemicalSource on chemicalsID.chemID = chemicalSource.chemID')

#Getting all the values and putting them in the final dataset

final_dataset = c.fetchall()

#closing the cursor

c.close()

#Closing the connection

database.close()

#Taking a look at the final result

#final_dataset



#Converting the file to a DataFrame for a cleaner look

final_dataset = pd.DataFrame(final_dataset)

final_dataset.columns = ['CAS_NUM', 'Common_name', 'Systematic_name', 'Sources']

#Taking a look at the final data set

final_dataset.to_excel('output/final_dataset.xls', index = False)

