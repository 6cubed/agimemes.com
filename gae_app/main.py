from flask import Flask, render_template, jsonify
import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
# Initialize Firestore connection (replace with your credentials)
cred = credentials.Certificate('./serviceaccount.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)
app.debug = True

_MEMES = []  # ttlcache one hour here...

memes = [
        { 'id': 1, 'imageUrl': "https://i.imgflip.com/8ja5so.jpg" },
        { 'id': 2, 'imageUrl': "https://i.imgflip.com/8j8msk.gif" },
        { 'id': 3, 'imageUrl': "https://i.imgflip.com/8j9aq5.jpg" },
        { 'id': 4, 'imageUrl': "https://i.imgflip.com/8j4j8l.gif" },
        { 'id': 5, 'imageUrl': "https://i.imgflip.com/8jcel0.jpg" },
        { 'id': 6, 'imageUrl': "https://i.imgflip.com/8jbbtn.jpg" },
        { 'id': 7, 'imageUrl': "https://i.imgflip.com/8jhb8a.jpg" },
        { 'id': 8, 'imageUrl': "https://i.imgflip.com/8jhba2.jpg" },
        { 'id': 9, 'imageUrl': "https://i.imgflip.com/8jhbbw.jpg" },
        { 'id': 10, 'imageUrl': "https://i.imgflip.com/8jhbfw.jpg" },
]

placeholder_image_url = "https://example.com/no-meme.jpg"

def get_recent_memes():
  agimemes_ref = db.collection('memes')
  docs = agimemes_ref.get()
  agimemes_data = []
  for doc in docs:
      agimemes_data.append(doc.to_dict())
  return agimemes_data


@app.route('/tasks/meme_creation')
def meme_creation():
    return 'creating memes'

@app.route('/')
def index():
  memes = get_recent_memes()
  return render_template(
    'index.html', 
    memes=memes, 
    placeholder_image_url=placeholder_image_url)

@app.route('/config.json')
def config():
    return jsonify(
      {
        "news_api_key": os.getenv("NEWS_API_KEY"),
        "imgflip_username": os.getenv("IMG_FLIP_USERNAME"),
        "imgflip_pasword": os.getenv("IMG_FLIP_PASSWORD"),
      })

if __name__ == '__main__':
    app.run(debug=True)
