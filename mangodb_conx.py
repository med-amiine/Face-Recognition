import pymongo
from PIL import Image
import io

client = pymongo.MongoClient("mongodb://m001-student:Password@cluster0-shard-00-00.nvnbz.mongodb.net:27017/Positive?ssl=true&replicaSet=atlas-qi9ptr-shard-0&authSource=admin&retryWrites=true&w=majority")  # open connection to mongo db to save face to database
face_database = client["face_detection"]  # select database
faces_collection = face_database["faces"]  # select collection

print(faces_collection)


faceDict = { "time": "ipsita Nanda", "faceCount":"midmoussi" }
faces_collection.insert_one(faceDict) # insert faces to database collection


im = Image.open("../images/amine/1.png")
image_bytes = io.BytesIO()
im.save(image_bytes, format='PNG')
image = {
    'data': image_bytes.getvalue()
}

faces_collection.insert_one(image).inserted_id

print(faces_collection)
