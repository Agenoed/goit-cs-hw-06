import socket
import json
from datetime import datetime
from pymongo import MongoClient
import os

HOST = "0.0.0.0"
SOCKET_PORT = 5000
MONGO_HOST = os.environ.get("MONGO_HOST", "mongodb")  # Default value changed to mongodb
MONGO_DB = os.environ.get("MONGO_DB", "myFirstDatabase")
MONGO_URI = f"mongodb://{MONGO_HOST}:27017/"  # Змінений URI

# Створюємо директорію для логів, якщо її немає
LOG_DIR = "/app/data"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db["messages"]

def save_data_to_mongodb(data):
    data_with_date = {
        "date": datetime.now().isoformat(),
        "username": data.get("username", ""),
        "message": data.get("message", "")
    }
    result = collection.insert_one(data_with_date)
    log_message(f"Data saved to MongoDB: {data_with_date}, inserted ID: {result.inserted_id}")

def log_message(message):
    with open(os.path.join(LOG_DIR, "socket_server.log"), "a") as log_file:
        log_file.write(f"{datetime.now().isoformat()} - {message}\n")

def run_socket_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, SOCKET_PORT))
        s.listen()
        print(f"Socket server started on port {SOCKET_PORT}")
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    try:
                        decoded_data = json.loads(data.decode())
                        save_data_to_mongodb(decoded_data)
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON: {data.decode()}")

if __name__ == "__main__":
    run_socket_server()