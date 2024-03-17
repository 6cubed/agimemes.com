import requests
import json
possible_memes = json.loads(requests.get('https://api.imgflip.com/get_memes').content)
meme_configs = []
for p in possible_memes['data']['memes']:
  box_count = p['box_count']
  title = p['name']
  meme_configs.append(
      {
          'id': p['id'],
          'title': title,
          'explanation': '',
          'formatting': '%s text captions overlaying the "%s" meme.' % (box_count, title)
      })
