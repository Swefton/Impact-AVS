from google.cloud import storage
from pymongo import MongoClient


client = MongoClient("mongodb+srv://mongodbadder:7JeXvgVz54ATft9G@uncommonhack.3k93vt8.mongodb.net/?retryWrites=true&w=majority&appName=UncommonHack")


db = client["UncommonHack"]
collection = db["User_Reports"]

storage_client = storage.Client()


@functions_framework.cloud_event
def hello_gcs(cloud_event):
    data = cloud_event.data
    
    bucket_name = data["bucket"]
    file_name = data["name"]

    
    metadata = storage_client.get_blob(bucket_name, file_name).metadata
    if metadata["user_id"] == "virajshah@gmail.com":
        collection.insert_one({"video": file_name})

    
    

    print(f"Inserted document with user_id: {metadata["user_id"] }")
    print("DONE")


if __name__ == "__main__":
    hello_gcs(None)
