from gae_app import api_secrets
client = OpenAI(api_key=api_secrets.OPEN_AI_KEY)

import requests
import json
from openai import OpenAI


possible_memes = json.loads(requests.get('https://api.imgflip.com/get_memes').content)
meme_configs = []
for p in possible_memes['data']['memes']:
  box_count = p['box_count']
  title = p['name']
  response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system", "content": "You are a helpful assistant with deep knowledge about internet memes."},
      {"role": "user", "content": "What is funny about the Distracted Boyfriend meme?"},
      {"role": "assistant", "content": "It is a funny way of showing when something could be better than it currently is. The boyfriend looking at the better looking girl can be a metaphor for whatever the meme is about."},
      {"role": "user", "content": "What is funny about the %s meme?" % title}
    ]
  )
  explanation = response.choices[0].message.content
  meme_configs.append(
      {
          'id': p['id'],
          'title': title,
          'box_count': box_count,
          'explanation': explanation,
          'formatting': '%s text captions overlaying the "%s" meme.' % (box_count, title)
      })