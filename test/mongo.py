from pymongo import MongoClient

# Konfigurasi koneksi
username = 'root'
password = 'example'
host = 'mongo'
port = 27017

# URL koneksi MongoDB dengan authSource
connection_string = f"mongodb://{username}:{password}@{host}:{port}/"

# Membuat koneksi ke MongoDB
client = MongoClient(connection_string)

# Memilih database (atau membuatnya jika belum ada)
db = client["mydatabase"]

# Memilih koleksi (atau membuatnya jika belum ada)
collection = db["mycollection"]

# Menambahkan dokumen ke koleksi
sample_data = {"name": "John Doe", "age": 30}
collection.insert_one(sample_data)

# Mengambil dokumen dari koleksi
result = collection.find_one({"name": "John Doe"})
print(result)
