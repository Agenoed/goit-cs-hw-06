import socket
import json
from datetime import datetime
import pymongo

HOST = "0.0.0.0" 
SOCKET_PORT = 5000
MONGO_HOST = "mongodb" 
MONGO_PORT = 27017

def save_data_to_mongodb(data):
    client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
    db = client["mydatabase"] 
    collection = db["messages"] 
    
    data_with_date = {
        "date": datetime.now().isoformat(),
        "username": data.get("username", ""),
        "message": data.get("message", "")
    }
    collection.insert_one(data_with_date)
    print(f"Data saved to MongoDB: {data_with_date}")


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