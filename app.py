from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from google.cloud import storage
from urllib.parse import quote_plus, urlencode
from flask import render_template
import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi
#from test_functions.credentials import AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, AUTH0_DOMAIN, APP_SECRET_KEY, GCLOUD_PROJECT_ID, uri
from flask import request
import datetime
import uuid
import os


client = MongoClient(os.environ.get('uri'), server_api=ServerApi('1'))

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


def get_documents(userid):
    db = client['UncommonHack']
    collection = db['user_reports']

    user_records = collection.find({'_id': userid})

    records_dict = {
        'UserID': userid,
        'Records': []
    }

    for record in user_records:
        emotion_counter = dict()
        chrono_emotions = []
        for item in record['records']:
            curr_emotion = item['dominant_emotion']
            chrono_emotions.append(curr_emotion)
            try:
               emotion_counter[curr_emotion] += 1
            except:
               emotion_counter[curr_emotion] = 1
            
        records_dict['Records'].append({"emotion_count": emotion_counter}) 
             
    return records_dict, chrono_emotions

def add_information(userid, info1, info2, info3, info4):
    client = MongoClient(uri, server_api=ServerApi('1'))
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


def get_documents(userid):
    client = MongoClient(os.environ.get('uri'), server_api=ServerApi('1'))
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

app = Flask(__name__)
app.secret_key = os.environ.get('AUTH0_CLIENT_ID')

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=os.environ.get('AUTH0_CLIENT_ID'),
    client_secret=os.environ.get('AUTH0_CLIENT_SECRET'),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{os.environ.get('AUTH0_DOMAIN')}/.well-known/openid-configuration"
)

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + os.environ.get('AUTH0_DOMAIN')
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": os.environ.get('AUTH0_CLIENT_ID'),
            },
            quote_via=quote_plus,
        )
    )


@app.route("/")
def index():
    return render_template("index.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

# FOR TESTING PURPOSES
@app.route("/home")
def home():
    return render_template("home.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

@app.route("/dashboard")
def dashboard():
    if not session:
        return redirect("/login")
    
    usr_id = session.get('user')['userinfo']['email']
    print(usr_id)
    mood_count,chrono = get_documents(usr_id)

    try:
        mood_count = mood_count['Records'][0]['emotion_count']
    except:
        mood_count = {'happy': 5, 'sad': 2, 'angry': 1}
        chrono = ['happy', 'happy', 'happy', 'happy', 'happy', 'sad', 'sad', 'angry']

    db = client['UncommonHack']
    collection = db['summary']

    summary_document = collection.find_one({'_id': usr_id})['summary']
    
    
    return render_template("dashboard.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4), mood_count=mood_count, data=chrono, summary=summary_document)


@app.route("/video_upload", methods=["GET", "POST"])
def video_upload():
    if request.method == "POST":
        if not session:
            return redirect("/login")
        
        if 'file' not in request.files:
            return render_template("401.html")
    
        video = request.files['file']
        
        if video.filename == '':
            return render_template("401.html")
    
        storage_client = storage.Client(project=os.environ.get(GCLOUD_PROJECT_ID))
        bucket = storage_client.bucket("journalvideoanalysis")
        
        
        name = str(uuid.uuid4()) + ".mp4"
        
        blob = bucket.blob(name)
        
        blob.upload_from_file(video)
        blob.metadata = {'user_id': session.get('user')['userinfo']['email'], 'time': datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}
        blob.patch()
        
    return render_template("dashboard.html", mood_count = {}, data = [], summary = {})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
