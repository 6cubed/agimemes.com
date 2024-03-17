from flask import Flask, render_template, jsonify
import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from meme_creation import create_batch_of_memes
from meme_creation import creation_recipe_configs
import time
from cachetools import cached
from cachetools import TTLCache
import datetime

cred = credentials.Certificate('./serviceaccount.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)
app.debug = True

@cached(cache=TTLCache(maxsize=1024, ttl=3500)) # < 1 hour
def get_recent_memes():
  memes_ref = db.collection('memes')
  query = memes_ref.order_by('creation_time').limit(100)
  docs = query.get()
  memes_data = []
  for doc in docs:
      memes_data.append(doc.to_dict())
  return memes_data


@app.route('/tasks/meme_creation')
def meme_creation():
    meme_batch = create_batch_of_memes.create_batch_of_memes(creation_recipe_configs.MINSTRAL_WITTY_RECIPE)
    memes_ref = db.collection('memes')

    for meme, prompt, llm_model in meme_batch:
      meme_doc = {
        'imageUrl': meme,
        'prompt': prompt,
        'creation_time': datetime.datetime.utcnow(),
        'llmModel': llm_model,
      }
      memes_ref.add(meme_doc)
    return 'creating memes'

@app.route('/')
def index():
  memes = get_recent_memes()
  return render_template(
    'index.html', 
    memes=memes)


if __name__ == '__main__':
    app.run(debug=True)
