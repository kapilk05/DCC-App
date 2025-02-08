import sqlite3
import time
import functools
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# 10-second delay decorator 
def delayed_response(func):
    @functools.wraps(func)  
    def wrapper(*args, **kwargs):
        time.sleep(10)  
        return func(*args, **kwargs)
    return wrapper

# Initialize the database
def init_db():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        quantity INTEGER NOT NULL)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS transformations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        object_name TEXT NOT NULL,
                        transformation_data TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    conn.commit()
    conn.close()

init_db()  # Call this function when the server starts

# Storing Transformations (POST)
@app.route('/store-transformation', methods=['POST'])
@delayed_response
def store_transformation():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Invalid request format, expected JSON"}), 400

        object_name = data.get("object_name")
        transformation_data = data.get("transformation_data")

        if not object_name or not transformation_data:
            return jsonify({"error": "Missing 'object_name' or 'transformation_data'"}), 400

        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO transformations (object_name, transformation_data) VALUES (?, ?)", 
                       (object_name, str(transformation_data)))  
        conn.commit()
        conn.close()

        return jsonify({"message": "Transformation stored successfully!"}), 201
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# Retrieving stored transformations (GET)
@app.route('/get-transformations', methods=['GET'])
def get_transformations():
    try:
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT object_name, transformation_data, timestamp FROM transformations ORDER BY timestamp DESC")
        results = cursor.fetchall()
        conn.close()

        if not results:
            return jsonify({"message": "No transformations found"}), 200

        transformations = [{"object_name": row[0], "transformation_data": eval(row[1]), "timestamp": row[2]} for row in results]
        return jsonify(transformations), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# Adding an item to inventory (POST)
@app.route('/add-item', methods=['POST'])
def add_item():
    data = request.json
    name = data.get("name")
    quantity = data.get("quantity")

    if not name or not isinstance(quantity, int):
        return jsonify({"error": "Invalid data"}), 400

    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO inventory (name, quantity) VALUES (?, ?)", (name, quantity))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Item already exists"}), 400
    finally:
        conn.close()

    return jsonify({"message": f"Added {quantity}x {name}"}), 201

# Removing an item from inventory (POST)
@app.route('/remove-item', methods=['POST'])
def remove_item():
    data = request.json
    name = data.get("name")

    if not name:
        return jsonify({"error": "Invalid data"}), 400

    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE name = ?", (name,))
    conn.commit()
    conn.close()

    return jsonify({"message": f"Removed {name} from inventory"}), 200

# Updating item quantity (POST)
@app.route('/update-quantity', methods=['POST'])
def update_quantity():
    data = request.json
    name = data.get("name")
    quantity = data.get("quantity")

    if not name or not isinstance(quantity, int):
        return jsonify({"error": "Invalid data"}), 400

    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE inventory SET quantity = ? WHERE name = ?", (quantity, name))
    conn.commit()
    conn.close()

    return jsonify({"message": f"Updated {name} quantity to {quantity}"}), 200

# Home Page (GET)
@app.route('/')
def home():
    return "Flask Server is Running!"

# Transform (POST)
@app.route('/transform', methods=['POST'])
def transform():
    data = request.json
    print("Received Transform Data:", data)
    return jsonify({"message": "Transform received", "data": data}), 200

# Translation (POST)
@app.route('/translation', methods=['POST'])
def translation():
    data = request.json
    return jsonify({"message": "Translation received", "data": data}), 200

# Rotation (POST)
@app.route('/rotation', methods=['POST'])
def rotation():
    data = request.json
    return jsonify({"message": "Rotation received", "data": data}), 200

# Scaling (POST)
@app.route('/scaling', methods=['POST'])
def scaling():
    data = request.json
    return jsonify({"message": "Scaling received", "data": data}), 200

# Fetch inventory details (GET)
@app.route('/get-inventory', methods=['GET'])
def get_inventory():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, quantity FROM inventory")
    items = [{"name": row[0], "quantity": row[1]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(items), 200

# Get file path (GET)
@app.route('/file-path', methods=['GET'])
def file_path():
    project_path = request.args.get('projectpath')
    
    if project_path == "true":
        return jsonify({"project_path": os.getcwd()}), 200  
    else:
        dcc_file_path = os.path.join(os.getcwd(), "assignment.blend")  
        return jsonify({"dcc_file_path": dcc_file_path}), 200

# Clear Inventory (POST)
@app.route("/clear-inventory", methods=["POST"])
def clear_inventory():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory")
    conn.commit()
    conn.close()

    return jsonify({"message": "Inventory cleared!"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)

