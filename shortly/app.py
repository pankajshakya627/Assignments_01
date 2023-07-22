from flask import Flask, render_template, request, redirect
import random
import string

app = Flask(__name__)

short_to_original = {}


def generate_short_url():
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for _ in range(6))
    return short_url

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/shorten', methods=['POST'])
def shorten_url():
    original_url = request.form['url']
    if not original_url.startswith(('http://', 'https://')):
        original_url = 'http://' + original_url

    short_url = generate_short_url()
    short_to_original[short_url] = original_url

    return render_template('shorten.html', short_url=short_url)

@app.route('/<short_url>')
def redirect_to_original(short_url):
    original_url = short_to_original.get(short_url)
    if original_url:
        return redirect(original_url)
    else:
        return "Short URL not found.", 404
    
if __name__ == '__main__':
    app.run(debug=True)

