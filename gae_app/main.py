from flask import Flask, render_template, jsonify, request
import os
import random
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
  query = memes_ref.order_by('creationTime', direction=firestore.Query.DESCENDING).limit(100)
  docs = query.get()
  memes_data = []
  for doc in docs:
      meme_id = doc.id
      meme_doc = doc.to_dict()
      meme_doc['id'] = meme_id
      memes_data.append(meme_doc)
  return memes_data


@app.route('/tasks/meme_creation')
def meme_creation():
    meme_recipe = random.choice(creation_recipe_configs.MEME_RECIPES)
    meme_batch = create_batch_of_memes.create_batch_of_memes(meme_recipe)
    memes_ref = db.collection('memes')

    for meme, prompt, llm_model in meme_batch:
      meme_doc = {
        'imageUrl': meme,
        'prompt': prompt,
        'creationTime': datetime.datetime.utcnow(),
        'llmModel': llm_model,
      }
      memes_ref.add(meme_doc)
    return 'creating memes'

@app.route('/vote/<meme_id>', methods=['POST'])
def vote(meme_id):
    is_funny = request.form.get('vote')  # Access 'vote' value from form

    if is_funny == 'yes':
        is_funny = True
    elif is_funny == 'no':
        is_funny = False
    else:
        return jsonify({'error': 'Invalid vote'}), 400  # Handle invalid vote

    # Update the meme document with the user's vote
    db.collection('memes').document(meme_id).update({'isFunny': is_funny})

    return jsonify({'success': True})


@app.route('/')
def index():
  memes = get_recent_memes()
  return render_template(
    'index.html', 
    memes=memes)


if __name__ == '__main__':
    app.run(debug=True)
