from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from google.cloud import storage
from urllib.parse import quote_plus, urlencode
from flask import render_template
import json
#from test_functions.credentials import AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, AUTH0_DOMAIN, APP_SECRET_KEY, GCLOUD_PROJECT_ID
from flask import request
import datetime
import uuid
import os


app = Flask(__name__)
app.secret_key = os.environ.get('AUTH0_CLIENT_ID')

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=AUTH0_CLIENT_ID,
    client_secret=os.environ.get('AUTH0_CLIENT_SECRET'),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{os.environ.get('AUTH0_DOMAIN')}/.well-known/openid-configuration'
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
    return render_template("dashboard.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

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
    
        storage_client = storage.Client(project=os.environ.get('GCLOUD_PROJECT_ID'))
        bucket = storage_client.bucket("journalvideoanalysis")
        
        
        name = str(uuid.uuid4()) + ".mp4"
        
        blob = bucket.blob(name)
        
        blob.upload_from_file(video)
        blob.metadata = {'user_id': session.get('user')['userinfo']['email'], 'time': datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}
        blob.patch()
        
        
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
