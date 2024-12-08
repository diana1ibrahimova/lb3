import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://127.0.0.1:5000/items"

USERNAME = 'Diana'
PASSWORD = '1111'

def get_all_items():
    response = requests.get(BASE_URL, auth=HTTPBasicAuth(USERNAME, PASSWORD))
    if response.status_code == 200:
        print("Available items")
        items = response.json().get("items", [])
        print(f"{'ID':<5} {'Name':<30} {'Price':<10}")
        print("-" * 50)
        for item in items:
            print(f"{item['id']:<5} {item['name']:<30} {item['price']:<10} UAH")
        print()
    else:
        print(f"Error. Status code: {response.status_code}")

def add_new_item(name, price):
    new_item = {
        "name": name,
        "price": price
    }
    response = requests.post(BASE_URL, json=new_item, auth=HTTPBasicAuth(USERNAME, PASSWORD))
    if response.status_code == 201:
        print(f"Item '{name}' is added")
    else:
        print(f"Error. Status code: {response.status_code}")
    print()

def delete_item(item_id):
    response = requests.delete(f"{BASE_URL}/{item_id}", auth=HTTPBasicAuth(USERNAME, PASSWORD))
    if response.status_code == 200:
        print(f"Item {item_id} is deleted")
    else:
        print(f"Error. Status code: {response.status_code}")
    print()

if __name__ == "__main__":
    get_all_items()
    add_new_item("Turkish coffee", 80)
    delete_item(15)
    print("Updated catalog")
    get_all_items()
