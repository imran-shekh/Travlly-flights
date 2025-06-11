from pymongo import MongoClient

try:
    client = MongoClient("mongodb+srv://imran:BICnDyOGCG5t9sFI@cluster0.yydgnvm.mongodb.net/?retryWrites=true&w=majority", serverSelectionTimeoutMS=5000)
    print(client.server_info())  # Forces a connection test
except Exception as e:
    print("Connection failed:", e)
db = client["travlly_flights"]
flights_collection = db["flights"]