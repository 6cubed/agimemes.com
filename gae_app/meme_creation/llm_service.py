import requests
import api_secrets

_NEETS_API_URL = "https://api.neets.ai/v1/chat/completions"
_MODELS = {
    'mistral': 'mistralai/Mixtral-8X7B-Instruct-v0.1'
}
def prepare_prompt(headline, article_url_content, meme_object, personality):
    prompt = 'You are a meme-generating AI assistant'
    if personality:
        prompt += ' with the personality of a %s' % personality
    prompt += '. You are given the following news story: "%s" and the following article content: "%s".' % (headline, article_url_content)
    prompt += ' React with a funny and creative caption for the "%s" meme.' % meme_object['title']
    prompt += ' The format should be a single python list format representing %s' % meme_object['formatting']
    return prompt

def call_llm(prompt):
  payload = {
      "messages": [
          {
              "role": "user",
              "content": prompt
          }
      ],
      "model": _MODELS['mistral']
  }

  headers = {
      "accept": "application/json",
      "content-type": "application/json",
      "X-API-Key": api_secrets.NEETS_API_KEY
  }

  try:
    response = requests.post(_NEETS_API_URL, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    return(data)
  except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")