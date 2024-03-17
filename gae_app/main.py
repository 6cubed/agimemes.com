from flask import Flask, render_template, jsonify
import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from meme_creation import create_batch_of_memes
from meme_creation import creation_recipe_configs

cred = credentials.Certificate('./serviceaccount.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)
app.debug = True

_MEMES = []  # ttlcache one hour here...

placeholder_image_url = "https://example.com/no-meme.jpg"

def get_recent_memes():
  if _MEMES:
    return _MEMES
  memes_ref = db.collection('memes')
  docs = memes_ref.get()
  memes_data = []
  for doc in docs:
      memes_data.append(doc.to_dict())
  return memes_data


@app.route('/tasks/meme_creation')
def meme_creation():
    meme_batch = create_batch_of_memes.create_batch_of_memes(creation_recipe_configs.MINSTRAL_WITTY_RECIPE)
    memes_ref = db.collection('memes')

    for meme in meme_batch:
      meme_doc = {
        'imageUrl': meme,
      }
      memes_ref.add(meme_doc)
    return 'creating memes'

@app.route('/')
def index():
  memes = get_recent_memes()
  return render_template(
    'index.html', 
    memes=memes)

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
