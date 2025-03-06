import os
import json
import sys
import mariadb

cred = json.loads(os.getenv("mariaDB_finance"))

#pending
def DB_uploadData(cur):
    inputFilePath = input("please provide the full path to the comma separated CSV file :")
    try:
        inputFile = open(inputFilePath, "r")
        print(inputFile.read())
        #write data to mariaDB 
        inputFile.close()
    except:
        print("An error occured trying to read the file")

def DB_autoTag(cur):
    tags = [[{"lidl":1},"boodschappen", "Lidl"],
            [{"Albert Heijn":1}, "boodschappen", "Albert Heijn"],
            [{"Jumbo":1}, "boodschappen", "Jumbo"],
            [{"BEN NEDERLAND":1}, "vaste lasten", "telefoon"],
            [{"YELLOWBRICK BY BUCKAROO":1}, "auto", "parkeren"],
            [{"VITENS NV":1}, "vaste lasten", "water"],
            [{"HNVB LANCYR":1}, "vaste lasten", "auto"],
            [{"Naar Oranje spaarrekening":9}, "sparen", ""],
            [{"Vattenfall Customers":1}, "auto", "laden"],
            [{"Zilveren Kruis Zorgverzekeringen":1}, "vaste lasten", "zorgverzekering"],
            ]
    
    try:
        cur.execute(f"SELECT * FROM {cred["table"]} WHERE `tag1` = '' ORDER BY `Datum` DESC LIMIT 1000")
        rows = cur.fetchall()
        for row in rows:
            for tag in tags:
                for key, value in tag[0].items():
                    if key.lower() in row[value].lower():
                        print("found an auto key")
                        print("tag[1] = ", tag[1], "and key = ", tag[2])
                        cur.execute(f"UPDATE {cred["table"]} SET `tag1` = ?, `tag2` = ? WHERE `uniqueID` = ?",(tag[1], tag[2], row[-1]))
                    else:
                        continue
    except mariadb.Error as e:
       print(f"error executing to MariaDB Platform: {e}")

def DB_manualTag(cur):
    try:
        cur.execute(f"SELECT * FROM {cred["table"]} ORDER BY `Datum` DESC LIMIT 1000")
        print("so far so good")
        rows = cur.fetchall()
        for row in rows:
            print(row)
            tag1 = row[2]
            tag2 = row[3]
            uniqueID = row[-1]
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

            #input("press enter voor volgende entry")
    except mariadb.Error as e:
       print(f"error executing to MariaDB Platform: {e}")

#START PROGRAM HERE
try:
    conn = mariadb.connect(user= cred["user"],password= cred["pw"],host= cred["host"],port=3306,database= cred["db"])
    conn.autocommit = True
except mariadb.Error as e:
    print(f"error connecting to MariaDB Platform: {e}")
    sys.exit(1)
cur = conn.cursor()
#HERE WE RUN THE DB commands


DB_autoTag(cur)



#HERE WE CLOSE THE CONNECTION
cur.close()
conn.close()    