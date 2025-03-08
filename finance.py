import os
import json
import sys
import mariadb
from tags import tagsVar

cred = json.loads(os.getenv("mariaDB_finance"))

jsonfile = open("tags.json", "r")
tagEntries = json.loads(jsonfile.read())
jsonfile.close()

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
    try:
        # Fetch rows where tag1 is empty
        cur.execute(f"SELECT * FROM {cred['table']} WHERE `tag1` = '' ORDER BY `Datum` DESC LIMIT 1000")
        rows = cur.fetchall()

        for row in rows:
            for entry_name, entry_data in tagEntries.items():
                lookup = entry_data["lookup"]
                total_checks = len(lookup)  # Number of conditions to meet
                matches = 0  # Counter for successful matches

                for column, value in lookup.items():
                    if value.lower() in row[column].lower():
                        matches += 1  # Increase match count

                # Only update if all conditions are met
                if matches == total_checks:
                    print("Updating with", entry_data['tags'][0], entry_data['tags'][1])
                    cur.execute(
                        f"UPDATE {cred['table']} SET `tag1` = ?, `tag2` = ? WHERE `uniqueID` = ?",
                        (entry_data["tags"][0], entry_data["tags"][1], row["uniqueID"])
                    )
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
cur = conn.cursor(dictionary=True)
#HERE WE RUN THE DB commands


DB_autoTag(cur)





#HERE WE CLOSE THE CONNECTION
cur.close()
conn.close()    