import csv
import sqlite3
from functools import wraps
from flask import Flask, request, abort, jsonify, Response

app = Flask(__name__)

users_dict = {
    "admin": "admin"
}

def load_users_from_file():
    users = {}
    try:
        with open("users.txt", "r") as file:
            for line in file:
                username, password = line.strip().split(",")
                users[username] = password
    except FileNotFoundError:
        pass
    return users

users_dict.update(load_users_from_file())
db_name = "catalog.db"

def init_db():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS catalog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL
    )''')
    conn.commit()
    conn.close()

init_db()
catalog_dict = {}


def read_catalog_dict():
    return catalog_dict
def save_data_dict(post_data):
    new_id = len(catalog_dict) + 1
    catalog_dict[new_id] = {'id': new_id, 'name': post_data['name'], 'price': post_data['price']}
    return True
def delete_item_dict(item_id):
    if item_id in catalog_dict:
        del catalog_dict[item_id]
        return True
    return False


def read_catalog_file():
    response_list = []
    with open("catalog.txt") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for item in reader:
            response_dict = {}
            response_dict['id'] = int(item[0])
            response_dict['name'] = item[1]
            response_dict['price'] = float(item[2])
            response_list.append(response_dict)
    return response_list
def save_data_file(post_data):
    with open("catalog.txt", 'a') as file:
        data_to_write = f"{get_new_id_file()}, {post_data['name']}, {post_data['price']}\n"
        file.write(data_to_write)
    return True
def get_new_id_file():
    items = read_catalog_file()
    if items:
        return max(item['id'] for item in items) + 1
    return 1
def delete_item_file(item_id):
    items = read_catalog_file()
    with open("catalog.txt", 'w') as file:
        deleted = False
        for item in items:
            if item['id'] != item_id:
                file.write(f"{item['id']}, {item['name']}, {item['price']}\n")
            else:
                deleted = True
        return deleted


def read_catalog_db():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM catalog")
    rows = cursor.fetchall()
    conn.close()
    response_list = [{'id': row[0], 'name': row[1], 'price': row[2]} for row in rows]
    return response_list
def save_data_db(post_data):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO catalog (name, price) VALUES (?, ?)", (post_data['name'], post_data['price']))
    conn.commit()
    conn.close()
    return True
def delete_item_db(item_id):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM catalog WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    return True


def check_auth(username, password):
    return users_dict.get(username) == password
def authenticate():
    return Response(
        'Unauthorized access. Please provide credentials.', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route('/items', methods=['GET'])
@requires_auth
def get_handler():
    response_data = read_catalog_db()
    return jsonify({"items": response_data})

@app.route('/items/<int:item_id>', methods=['GET'])
@requires_auth
def get_item_by_id(item_id):
    item_data = get_item_by_id_from_db(item_id)
    if not item_data:
        abort(404, description="Item not found")

    return jsonify({"item": item_data})
def get_item_by_id_from_db(item_id):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM catalog WHERE id=?", (item_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {'id': row[0], 'name': row[1], 'price': row[2]}
    return None


@app.route('/items', methods=['POST'])
@requires_auth
def post_handler():
    if request.headers['Content-Type'] != "application/json":
        abort(400)

    save_data_dict(request.json)
    save_data_file(request.json)
    if save_data_db(request.json):
        return "Catalog entry was recorded", 201
    return "ok", 200

@app.route('/add_user', methods=['POST'])
@requires_auth
def add_user():
    auth = request.authorization
    if auth.username != "admin":
        return "Unauthorized", 403
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if username and password:
        users_dict[username] = password
        with open("users.txt", "a") as file:
            file.write(f"{username},{password}\n")
        return jsonify({"message": "User added successfully"}), 201
    return "Invalid data", 400


@app.route('/items/<int:item_id>', methods=['DELETE'])
@requires_auth
def delete_item(item_id):
    deleted_from_dict = delete_item_dict(item_id)
    deleted_from_file = delete_item_file(item_id)
    deleted_from_db = delete_item_db(item_id)

    if deleted_from_dict or deleted_from_file or deleted_from_db:
        return jsonify({"message": f"Item {item_id} deleted successfully."}), 200
    else:
        return jsonify({"message": f"Item {item_id} not found."}), 404


if __name__ == '__main__':
    app.run(debug=True)
