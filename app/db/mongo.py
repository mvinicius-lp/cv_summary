from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")  
MONGO_DB = os.getenv("MONGO_DB", "resume_ai")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "summaries")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

# Função para salvar o resumo no banco
def save_summary_record(data: dict):
    result = collection.insert_one(data)
    return str(result.inserted_id)  # Garante retorno serializável
