from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from credentials import uri

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
        emotion_counter = dict()
        for item in record['records']:
            curr_emotion = item['dominant_emotion']
            try:
               emotion_counter[curr_emotion] += 1
            except:
               emotion_counter[curr_emotion] = 1
            
        records_dict['Records'].append({"emotion_count": emotion_counter}) 
             
    return records_dict


if __name__ == "__main__":
    """    
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    
    result = get_user_records('Luffy')
    print(result['Records'][0])
    """
    
    
    db = client["UncommonHack"]
    collection = db["User_reports"]
    collection.insert_one({"video": "test"})
