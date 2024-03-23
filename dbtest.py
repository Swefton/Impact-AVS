from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime

from credetials import MONGOUSERNAME, MONGOPASSWORD

uri = f"mongodb+srv://{MONGOUSERNAME}:{MONGOPASSWORD}@uncommonhack.3k93vt8.mongodb.net/?retryWrites=true&w=majority&appName=UncommonHack"

client = MongoClient(uri, server_api=ServerApi('1'))


def add_information(userid, info1, info2, info3, info4):
    db = client['UncommonHack']
    collection = db['user_reports']

    current_datetime = datetime.now()

    data = {
        '_id': userid,
        'records': [
            {
                'id_datetime': current_datetime,
                'info1': info1,
                'info2': info2,
                'info3': info3,
                'info4': info4
            }
        ]
    }
    
    if collection.count_documents({'_id': userid}) > 0:
        collection.update_one({'_id': userid}, {'$push': {'records': {'$each': data['records']}}})
        return True
    else:
        insert_result = collection.insert_one(data)
        return insert_result.acknowledged


def get_user_records(userid):
    db = client['UncommonHack']
    collection = db['user_reports']

    user_records = collection.find({'_id': userid})

    records_dict = {
        'UserID': userid,
        'Records': []
    }

    for record in user_records:
        for item in record['records']:
            record_info = {
                'ID Datetime': item['id_datetime'],
                'Info1': item['info1'],
                'Info2': item['info2'],
                'Info3': item['info3'],
                'Info4': item['info4']
            }
            records_dict['Records'].append(record_info)
    
    return records_dict


if __name__ == "__main__":
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    print(get_user_records('1235')['Records'])
