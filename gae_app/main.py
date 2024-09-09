from flask import Flask, render_template, jsonify, request
import random
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from meme_creation import create_batch_of_memes
from meme_creation import creation_recipe_configs
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

    for meme_url, prompt, llm_model, captions, url, is_funny_comment in meme_batch:
      meme_doc = {
        'imageUrl': meme_url,
        'creationTime': datetime.datetime.utcnow(),
        'contextUrl': url,
        'llmModel': llm_model,
        # Later we will use these prompt, caption values along with the isFunny target to fine-tune a model.
        'prompt': prompt, 
        'captions': captions,
        'isFunnyComment': is_funny_comment,
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

    if vote_value not in ('up', 'down'):
        return jsonify({'error': 'Invalid vote'}), 400

    is_funny = vote_value == 'up'  # Convert 'up' to True, 'down' to False - do something fancier later

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

@app.route('/admin')
def admin():
  memes = get_recent_memes()
  return render_template(
    'admin_index.html', 
    memes=memes)

@app.route('/memes/<meme_id>')
def meme_detail(meme_id):
  # Fetch meme from Firestore by ID
  doc = db.collection('memes').document(meme_id).get()

  if doc.exists:
    meme = doc.to_dict()
    meme_id = doc.id
    meme['id'] = meme_id
    # Return the meme data and render the detail template (adjust as needed)
    return render_template('meme_detail.html', meme=meme)
  else:
    # Handle meme not found case (e.g., return a 404 error)
    return 'Meme not found', 404
    

@app.route("/override_caption/<meme_id>", methods=["POST"])
def override_caption(meme_id):
    # Implement logic to handle the received caption data (e.g., save it, update database)
    data = request.get_json()
    custom_caption = data.get("caption")

    # Example logic (replace with your actual processing)
    try:
        db.collection('memes').document(meme_id).update({'overrideCaption': custom_caption})
    except Exception as e:  # Catch broader exceptions for database errors
        return jsonify({'error': 'Database error'}), 500
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True)
