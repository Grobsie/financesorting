from flask import Flask, jsonify, render_template, request
import mariadb
import sys
import json
import os
from contextlib import contextmanager

app = Flask(__name__)

# Load environment variables securely using os.getenv
cred = json.loads(os.getenv("mariaDB_finance"))
TAGS_FILE = os.path.join("static", "tags.json")

# Database connection management using a context manager for safe opening and closing of connections
@contextmanager
def get_db_connection():
    """ Context manager for MariaDB database connection """
    conn = None
    try:
        conn = mariadb.connect(
            user=cred["user"],
            password=cred["pw"],
            host=cred["host"],
            port=3306,
            database=cred["db"]
        )
        conn.autocommit = True
        yield conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

def DB_autoTag(cur):
    try:
        print("Start reading JSON file")
        
        if not os.path.exists(TAGS_FILE):
            print(f"Error: {TAGS_FILE} does not exist!")
            return  # Exit function if file is missing
        
        with open(TAGS_FILE, "r", encoding="utf-8") as f:
            file_content = f.read().strip()  # Read and remove whitespace/newlines
            
            if not file_content:
                print("Error: JSON file is empty!")
                return  # Exit function if file has no content
            
            tagEntries = json.loads(file_content)  # Load JSON after checking it's not empty

        print("Successfully loaded tags:", tagEntries)

        # Fetch records that need tagging
        cur.execute("SELECT * FROM `2025` WHERE `tag1` = '' ORDER BY `Datum` DESC LIMIT 1000")
        rows = cur.fetchall()  # Fetch as dictionary
        print(f"Fetched {len(rows)} rows")

        # Process each row and check for tag matches
        for row in rows:
            for entry_name, entry_data in tagEntries.items():
                lookup = entry_data["lookup"]
                total_checks = len(lookup)
                matches = 0

                for column, value in lookup.items():
                    if column in row and value.lower() in row[column].lower():
                        matches += 1

                if matches == total_checks:
                    print(f"Updating row {row['uniqueID']} with {entry_data['tags']}")
                    cur.execute("""
                        UPDATE `2025` SET `tag1` = ?, `tag2` = ? WHERE `uniqueID` = ?
                    """, (entry_data["tags"][0], entry_data["tags"][1], row["uniqueID"]))

    except mariadb.Error as e:
        print(f"Error executing to MariaDB Platform: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON file: {e}")

# Helper function to execute SQL queries and fetch results
def get_data(query):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(dictionary=True)  # Ensure dictionary mode
            cur.execute(query)
            return cur.fetchall()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

@app.route("/")
def home():
    # Fetch table data, graph data, and tag data for the main page
    tableData = get_data("""
        SELECT `Datum`, `Naam / Omschrijving`, `Bedrag (EUR)`, `Mededelingen`, `tag1`, `tag2`, `uniqueID`
        FROM `2025`
        WHERE `tag1` = ''
    """)
    graphData = get_data("""
        SELECT MONTH(`Datum`) AS month, `tag1`, SUM(`Bedrag (EUR)`) AS total_spent
        FROM `2025`
        WHERE `tag1` NOT IN ('sparen', 'opname')
        GROUP BY MONTH(`Datum`), `tag1`
        ORDER BY month, `tag1`
    """)
    tagDataOne = [row['tag1'] for row in get_data("""
        SELECT DISTINCT `tag1` FROM `2025` WHERE `tag1` <> ''
    """)]
    tagDataTwo = [row['tag2'] for row in get_data("""
        SELECT DISTINCT `tag2` FROM `2025` WHERE `tag2` <> ''
    """)]

    return render_template("main.html", tableData=tableData, graphData=graphData, tagDataOne=tagDataOne, tagDataTwo=tagDataTwo)

#manually add tags 
@app.route("/update_tags", methods=["POST"])
def update_tags():
    try:
        data = request.json.get('data', [])
        if not data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400

        # Connect to the DB and process updates
        with get_db_connection() as conn:
            cur = conn.cursor()

            for entry in data:
                tag1 = entry['tag1']
                tag2 = entry.get('tag2', '')  # Handle missing tag2
                tag3 = entry.get('tag3', '')
                uniqueID = entry['uniqueID']

                cur.execute("""
                    UPDATE `2025`
                    SET `tag1` = ?, `tag2` = ?, `tag3` = ?
                    WHERE `uniqueID` = ?
                """, (tag1, tag2, tag3, uniqueID))

            conn.commit()

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        print(f"Error updating database: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/add-tag', methods=['POST'])
def add_tag():
    new_data = request.json

    if not new_data:
        return jsonify({"status": "error", "message": "Invalid data"})

    try:
        if os.path.exists(TAGS_FILE):
            with open(TAGS_FILE, "r", encoding="utf-8") as f:
                tags = json.load(f)
        else:
            tags = {}

        tags.update(new_data)

        with open(TAGS_FILE, "w", encoding="utf-8") as f:
            json.dump(tags, f, indent=4, ensure_ascii=False)

        # Now update the database **after** closing the file
        try:
            with get_db_connection() as conn:
                cur = conn.cursor(dictionary=True)
                print("Starting auto-tagging")
                DB_autoTag(cur)
            return jsonify({"status": "success", "message": "Tags updated successfully!"})
        except Exception as e:
            print(f"Error updating tags: {e}")
            return jsonify({"status": "error", "message": str(e)})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/run-auto-tag", methods=["GET"])
def run_auto_tag():
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(dictionary=True)
            DB_autoTag(cur)
        return jsonify({"status": "success", "message": "Auto-tagging completed!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
