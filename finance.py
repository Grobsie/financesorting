import os
import json
import sys
import mariadb
import csv
from decimal import Decimal

cred = json.loads(os.getenv("mariaDB_finance"))

def DB_uploadData(cur):
    inputFilePath = input("please provide the full path to the comma separated CSV file :")
    try:
        inputFile = open(inputFilePath, "r")
        read = csv.reader(inputFile)
        for row in reversed(list(read)[1:]): #convert the file to a list, remove the first line and then reverse it
            cols = ".".join(row).replace('"','').split(";") #rows are being split on the , so these have to be combined again but now we use . to fix values
            amount = Decimal(cols[6].strip('""'))
            if cols[5] == "Af":
                amount = -abs(amount)
            cur.execute('INSERT INTO `2025` (`Datum`,`Naam / Omschrijving`,`Tegenrekening`,`Code`, `Af Bij`, `Bedrag (EUR)`,`Mutatiesoort`,`Mededelingen`) VALUES (?,?,?,?,?,?,?,?)', (cols[0], cols[1], cols[3], cols[4], cols[5], amount, cols[7], cols[8]))
        inputFile.close()
        print("finished adding the rows")
    except  Exception as e:
        print("An error occured", e)

def DB_autoTag(cur):
    try:
        jsonfile = open("static/tags.json", "r")
        tagEntries = json.loads(jsonfile.read())
        jsonfile.close()

        cur.execute("SELECT * FROM `2025` WHERE `tag1` = '' ORDER BY `Datum` DESC LIMIT 1000")
        rows = cur.fetchall()

        for row in rows:
            for entry_name, entry_data in tagEntries.items():
                lookup = entry_data["lookup"]
                total_checks = len(lookup)
                matches = 0

                for column, value in lookup.items():
                    if value.lower() in row[column].lower():
                        matches += 1
                #if all matched, update 
                if matches == total_checks:
                    print("Updating with", entry_data['tags'][0], entry_data['tags'][1])
                    cur.execute(
                        f"UPDATE `2025` SET `tag1` = ?, `tag2` = ? WHERE `uniqueID` = ?",
                        (entry_data["tags"][0], entry_data["tags"][1], row["uniqueID"])
                    )
    except mariadb.Error as e:
       print(f"error executing to MariaDB Platform: {e}")

#pending
def DB_AddToAutoTag(cur, tag1, tag2):
    while(True):
        answer = input("Would you like to add this to the auto tagger list? y or n ")
        match answer.lower():
            case "n":
                break
            case "y":
                entryName = input("name:")
                tag1 = input("tag1:")
                tag2 = input("tag2:")
                #another input question to ask which columns to check for
                #cur.execute(f"UPDATE {cred["table"]} SET `tag1` = ?, `tag2` = ? WHERE `uniqueID` = ?",(tag1, tag2, uniqueID))
                
                break
            case _:
                print("please respond y or n")

#pending
def DB_addsplashscreen():
    lookupDict = {}
    tagDict = ["", ""]
    nameOfEntry = input("please give a name for the new entry: ")
    tagDict[0] = input("please input the first tag: ")
    tagDict[1] = input("please input the second tag: ")

    print("-------column to select:")
    print("1: Naam_Omschrijving")
    print("2: Af_Bij")
    print("3: Mutatiesoort")
    print("4: Mededelingen")
    while(True):
        selectedEntry = input("please select a number or type done: ")
        match selectedEntry:
            case "1":
                response = input("give a string to look for: ")
                lookupDict.update({"Naam_Omschrijving": response})
            case "2":
                response = input("give a string to look for: ")
                lookupDict.update({"Af_Bij": response})
            case "3":
                response = input("give a string to look for: ")
                lookupDict.update({"Mutatiesoort": response})
            case "4":
                response = input("give a string to look for: ")
                lookupDict.update({"Mededelingen": response})
            case "done":
                print("adding the following tags:", tagDict)
                print("adding", lookupDict, "to the lookuplist")
                break
            case _:
                print("please give a valid response")

def DB_manualTag(cur):
    try:
        cur.execute(f"SELECT * FROM {cred['table']} WHERE `tag1` IS NULL ORDER BY `Datum` DESC LIMIT 1000")
        print("so far so good")
        rows = cur.fetchall()
        for row in rows:
            print(row)
            tag1 = row["tag1"]
            tag2 = row["tag2"]
            uniqueID = row["uniqueID"]
            print("current tags are ",tag1," and ",tag2, "for row ", uniqueID)
            while(True):
                answer = input("is this correct? ")
                match answer.lower():
                    case "y":
                        break
                    case "n":
                        tag1 = input("tag1:")
                        tag2 = input("tag2:")
                        cur.execute(f"UPDATE {cred['table']} SET `tag1` = ?, `tag2` = ? WHERE `uniqueID` = ?",(tag1, tag2, uniqueID))
                        
                        break
                    case _:
                        print("please respond y or n")

            #input("press enter voor volgende entry")
    except mariadb.Error as e:
       print(f"error executing to MariaDB Platform: {e}")

def getTable(cur):
    cur.execute("SELECT * FROM `2025` WHERE MONT(`Datum`)=1")
    result = cur.fetchall()
    return result

#START PROGRAM HERE
try:
    conn = mariadb.connect(user= cred["user"],password= cred["pw"],host= cred["host"],port=3306,database= cred["db"])
    conn.autocommit = True
    print("connected")
except mariadb.Error as e:
    print(f"error connecting to MariaDB Platform: {e}")
    sys.exit(1)
cur = conn.cursor(dictionary=True)

#HERE WE RUN THE DB commands

#DB_uploadData(cur)
#DB_manualTag(cur)
DB_autoTag(cur)
#DB_addsplashscreen()



#HERE WE CLOSE THE CONNECTION
cur.close()
conn.close()    

#C:\Users\jelmer\Downloads\NL71INGB0008685092_01-02-2025_28-02-2025.csv
#C:\Users\jelmer\Downloads\NL71INGB0008685092_01-01-2025_31-01-2025.csv