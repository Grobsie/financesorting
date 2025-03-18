from flask import Flask, render_template
import mariadb
import sys
import json
import os

app = Flask(__name__)
cred = json.loads(os.getenv("mariaDB_finance"))

def getData(string):
    try:
        conn = mariadb.connect(user= cred["user"],password= cred["pw"],host= cred["host"],port=3306,database= cred["db"])
        conn.autocommit = True
        print("connected")
        cur = conn.cursor(dictionary=False)
        cur.execute(string)
        result = cur.fetchall()
    except mariadb.Error as e:
        print(f"error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close() 
    return result

@app.route("/")
def home():
    tableData = getData("""
        SELECT * FROM `2025` 
        WHERE MONTH(`Datum`) = 1 
        AND `tag1` NOT IN ('sparen', 'opname')
        """)
    graphData = getData("""
        SELECT MONTH(`Datum`) AS month,`tag1`,SUM(`Bedrag (EUR)`) AS total_spent FROM `2025` 
        WHERE `tag1` NOT IN ('sparen', 'opname') 
        GROUP BY MONTH(`Datum`), `tag1` 
        ORDER BY month, `tag1`
        """)
    return render_template("main.html", tableData=tableData, graphData=graphData)

if __name__ == '__main__':
    app.run(debug=True) 
