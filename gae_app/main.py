from flask import Flask, render_template, jsonify, request
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
import json

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

    for meme_url, prompt, llm_model, captions in meme_batch:
      meme_doc = {
        'imageUrl': meme_url,
        'creationTime': datetime.datetime.utcnow(),
        'llmModel': llm_model,
        # Later we will use these prompt, caption values along with the isFunny target to fine-tune a model.
        'prompt': prompt, 
        'captions': captions,
      }
      memes_ref.add(meme_doc)
    return 'creating memes'


@app.route('/vote/<meme_id>', methods=['POST'])
def vote(meme_id):
    # Access vote data from JSON request body
    try:
        data = request.get_json()
        vote_value = data.get('vote')
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON data'}), 400

    if vote_value not in ('yes', 'no'):
        return jsonify({'error': 'Invalid vote'}), 400

    is_funny = vote_value == 'yes'  # Convert 'yes' to True, 'no' to False

    # Update the meme document with the user's vote
    try:
        db.collection('memes').document(meme_id).update({'isFunny': is_funny})
    except Exception as e:  # Catch broader exceptions for database errors
        return jsonify({'error': 'Database error'}), 500

    return jsonify({'success': True})


@app.route('/')
def index():
  memes = get_recent_memes()
  return render_template(
    'index.html', 
    memes=memes)


if __name__ == '__main__':
    app.run(debug=True)
