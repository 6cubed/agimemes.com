from meme_creation import llm_service
from meme_creation import meme_variants_config
import requests
import api_secrets
import json

NEWS_API_KEY = ''
MEME_CREATOR_API_USERNAME = ''
MEME_CREATOR_API_PASSWORD = ''

def caption_meme(template_id, username, password, text0, text1, text2, font=None):
    url = "https://api.imgflip.com/caption_image"
    payload = {
        'template_id': template_id,
        'username': username,
        'password': password,
        'boxes[0][text]': text0,
        'boxes[1][text]': text1,
        'boxes[2][text]': text2,
    }
    if font:
        payload['font'] = font

    response = requests.post(url, data=payload)
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            return result['data']['url']
        else:
            return "Error: " + result['error_message']
    else:
        return "Failed to connect to the API."

def create_batch_of_memes(recipe):
    article_response = requests.get('https://newsapi.org/v2/top-headlines?sources=techcrunch&apiKey=%s' % (api_secrets.NEWS_API_KEY))
    article_objects = json.loads(article_response.content)['articles']
    articles = {}
    for article_object in article_objects:
        title = article_object['title']
        description = article_object['description']
        articles[title] = description
    
    personality = recipe['personality']

    captioned_meme_urls = []
    for headline, article_summary in articles.items():
        for meme_object in meme_variants_config.MEME_VARIANTS:  # one meme per article, for now
            prompt = llm_service.prepare_prompt(headline, article_summary, meme_object, personality)
            llm_response = llm_service.call_llm(prompt)
            caption_list_first_meme = eval(llm_response['choices'][0]['message']['content'])
            captioned_meme_url = caption_meme(
                meme_object['id'],
                api_secrets.IMGFLIP_USERNAME, 
                api_secrets.IMGFLIP_PASSWORD, 
                *caption_list_first_meme)
            captioned_meme_urls.append(captioned_meme_url)
    return(captioned_meme_urls)
