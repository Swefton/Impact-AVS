from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from urllib.parse import quote_plus, urlencode
from flask import render_template
import json

app = Flask(__name__)
app.secret_key = 'Ddq96xPALr'


AUTH0_CLIENT_ID='jfEtd4vdk4GyHPJUcJck1Wl6lzzrA5ZM'
AUTH0_CLIENT_SECRET='IjK_KNGD7FY1hVtHtGnWD73WCReIyop9vVF95W37KtkZXjjgh9pdzPVYQ7s7HFiy'
AUTH0_DOMAIN='dev-oye6y425565bfb2p.us.auth0.com'
APP_SECRET_KEY='Ddq96xPALr'

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)