from flask import Flask, render_template, request, redirect, url_for
from cryptography.fernet import Fernet
import uuid
import hashlib
import base64

app = Flask(__name__)
app.secret_key = "vhgMP1hy326376G09hjkjk76523FHPOj"  # Set a secret key for session encryption

# In-memory database to store snippets temporarily (replace with a proper database for production)
snippets = {}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        snippet = request.form.get("snippet")
        secret_key = request.form.get("secret_key")

        # Generate a unique identifier for the snippet
        snippet_id = str(uuid.uuid4())

        # Encrypt the content if a secret key is provided
        if secret_key:
            encrypted_snippet = encrypt_snippet(snippet, secret_key)
            snippets[snippet_id] = encrypted_snippet
        else:
            snippets[snippet_id] = snippet

        return redirect(url_for("view_snippet", snippet_id=snippet_id))

    return render_template("index.html")

@app.route("/view/<string:snippet_id>", methods=["GET", "POST"])
def view_snippet(snippet_id):
    snippet = snippets.get(snippet_id)

    if not snippet:
        return "Snippet not found or has expired."

    if request.method == "POST":
        entered_key = request.form.get("secret_key")

        if entered_key:
            decrypted_snippet = decrypt_snippet(snippet, entered_key)
            return render_template("view_snippet.html", snippet=decrypted_snippet, snippet_id=snippet_id, key_entered=True)

    return render_template("view_snippet.html", snippet=snippet, snippet_id=snippet_id, key_entered=False)

SECRET_KEY = b'1234567890'
def encrypt_snippet(snippet, key):
    key = hashlib.pbkdf2_hmac('sha256', key.encode(), SECRET_KEY, 100000)
    fernet = Fernet(base64.urlsafe_b64encode(key))
    encrypted_data = fernet.encrypt(snippet.encode())
    return encrypted_data.decode()

def decrypt_snippet(snippet, key):
    key = hashlib.pbkdf2_hmac('sha256', key.encode(), SECRET_KEY, 100000)
    fernet = Fernet(base64.urlsafe_b64encode(key))
    decrypted_data = fernet.decrypt(snippet.encode())
    return decrypted_data.decode()

if __name__ == "__main__":
    app.run()
