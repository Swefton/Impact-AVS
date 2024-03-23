from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from google.cloud import storage
from urllib.parse import quote_plus, urlencode
from flask import render_template
import json
from test_functions.credentials import AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, AUTH0_DOMAIN, APP_SECRET_KEY, MONGOUSERNAME, MONGOPASSWORD, GCLOUD_PROJECT_ID
from flask import request

app = Flask(__name__)
app.secret_key = APP_SECRET_KEY

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{AUTH0_DOMAIN}/.well-known/openid-configuration'
)

connection_string = f"mongodb+srv://{MONGOUSERNAME}:{MONGOPASSWORD}@uncommonhack.3k93vt8.mongodb.net/?retryWrites=true&w=majority&appName=UncommonHack"

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
        "https://" + AUTH0_DOMAIN
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        )
    )


@app.route("/")
def home():
    return render_template("home.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))


@app.route("/video_upload", methods=["GET", "POST"])
def video_upload():
    if request.method == "POST":
        if 'video' not in request.files:
            return "No file part"
        
        video = request.files['video']
        
        if video.filename == '':
            return "No selected file"
        
    
        storage_client = storage.Client(project=GCLOUD_PROJECT_ID)
        bucket = storage_client.bucket("journalvideoanalysis")
        blob = bucket.blob("video.mp4")
              
        print(blob.metadata)
        
        blob.upload_from_file(video)
        blob.metadata = {'user_id': '123', 'title': 'My Video'}
        blob.patch()
        
        print(blob.metadata)
        print(
            f"File {'video.mp4'} uploaded to {'journalvideoanalysis'}."
        )
    
    return render_template("video_upload.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
