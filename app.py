import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "key_jak_chuj"

POSTMARK_SERVER_TOKEN = os.getenv("POSTMARK_SERVER_TOKEN")
POSTMARK_FROM_EMAIL = os.getenv("POSTMARK_FROM_EMAIL")
CONTACT_TO_EMAIL = os.getenv("CONTACT_TO_EMAIL")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/kontakt", methods=["POST"])
def contact():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not email or not message:
        flash("Vyplň meno, e-mail a správu.", "error")
        return redirect(url_for("home"))

    subject = f"Nová správa z webu od {name}"

    text_body = f"""
Nová správa z kontaktného formulára:

Meno: {name}
Email: {email}
Telefón: {phone}

Správa:
{message}
"""

    payload = {
        "From": POSTMARK_FROM_EMAIL,
        "To": CONTACT_TO_EMAIL,
        "ReplyTo": email,
        "Subject": subject,
        "TextBody": text_body,
        "MessageStream": "outbound"
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Postmark-Server-Token": POSTMARK_SERVER_TOKEN
    }

    try:
        response = requests.post(
            "https://api.postmarkapp.com/email",
            json=payload,
            headers=headers,
            timeout=10
        )
        print("Postmark response:", response.status_code, response.text)
        if response.status_code == 200:
            flash("Správa bola odoslaná. Ozvem sa čo najskôr.", "success")
        else:
            print(response.status_code, response.text)
            flash("Správu sa nepodarilo odoslať. Skús to znova.", "error")

    except requests.RequestException as e:
        print("Postmark error:", e)
        flash("Nastala chyba pri odosielaní.", "error")

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)