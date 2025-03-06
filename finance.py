import os
import json
import sys
import mariadb

cred = json.loads(os.getenv("mariaDB_finance"))

#currently not being used
def readFile():
    inputFilePath = input("please provide the full path to the comma separated CSV file :")
    try:
        inputFile = open(inputFilePath, "r")
        print(inputFile.read())
        inputFile.close()
    except:
        print("An error occured trying to read the file")

#def addToTagList():
# DIT LIJKT NOG NIET TE WERKEN    
def autoTag(cur, row, tag1, tag2, uniqueID):
    tags = [[{"lidl":1},"boodschappen", "LIDL"],
            [{"Albert Heijn":1}, "boodschappen", "AH"],
            [{"Jumbo":1}, "boodschappen", "AH"],
            ]
    for tag in tags:
        for key, value in tag[0].items():
            if key in row[value]:
                print("found an auto key")
                cur.execute(f"UPDATE {cred["table"]} SET `tag1` = ?, `tag2` = ? WHERE `uniqueID` = ?",(tag1, tag2, uniqueID))
            else:
                print("no autokey:(")
                continue

def updateDB():
    try:
        conn = mariadb.connect(user= cred["user"],password= cred["pw"],host= cred["host"],port=3306,database= cred["db"])
        conn.autocommit = True
        print("connected")
    except mariadb.Error as e:
        print(f"error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    cur = conn.cursor()

    #read database
    try:
        cur.execute(f"SELECT * FROM {cred["table"]} ORDER BY `Datum` DESC LIMIT 1000")
        print("so far so good")
        rows = cur.fetchall()
        for row in rows:
            print(row)
            tag1 = row[2]
            tag2 = row[3]
            uniqueID = row[-1]
            autoTag(cur, row, tag1, tag2, uniqueID)
            print("current tags are ",tag1," and ",tag2, "for row ", uniqueID)
            while(True):
                answer = input("is this correct? ")
                match answer:
                    case "y":
                        break
                    case "n":
                        tag1 = input("tag1:")
                        tag2 = input("tag2:")
                        cur.execute(f"UPDATE {cred["table"]} SET `tag1` = ?, `tag2` = ? WHERE `uniqueID` = ?",(tag1, tag2, uniqueID))
                        break
                    case _:
                        print("please respond y or n")

            input("press enter voor volgende entry")
    #    result = "pass"
    except mariadb.Error as e:
       print(f"error executing to MariaDB Platform: {e}")
    cur.close()
    conn.close()    


updateDB()

