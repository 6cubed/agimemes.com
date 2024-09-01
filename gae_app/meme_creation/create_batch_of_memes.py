from meme_creation import llm_service
from meme_creation import meme_variants_config
import requests
import api_secrets
import json
import random 
import traceback

_NEWS_SOURCES = {
    'newsapi_techcrunch': 'https://newsapi.org/v2/top-headlines?sources=techcrunch&apiKey=%s' % (api_secrets.NEWS_API_KEY),
    'newsapi_switzerland': 'https://newsapi.org/v2/everything?q=switzerland&apiKey=%s' % (api_secrets.NEWS_API_KEY),
    #'newsapi_ai': 'https://newsapi.org/v2/everything?q=ai&apiKey=%s' % (api_secrets.NEWS_API_KEY),
    #'newsapi_tech': 'https://newsapi.org/v2/everything?q=tech&apiKey=%s' % (api_secrets.NEWS_API_KEY),
    #'newsapi_wallstreet': 'https://newsapi.org/v2/everything?q=wallstreet&apiKey=%s' % (api_secrets.NEWS_API_KEY),
    #'newsapi_cnn': 'https://newsapi.org/v2/top-headlines?sources=cnn&apiKey=%s' % (api_secrets.NEWS_API_KEY),
    #'newsapi_biuk': 'https://newsapi.org/v2/top-headlines?sources=business-insider-uk&apiKey=%s' % (api_secrets.NEWS_API_KEY),
    #'newsapi_wsj': 'https://newsapi.org/v2/top-headlines?sources=the-wall-street-journal&apiKey=%s' % (api_secrets.NEWS_API_KEY),
    #'newsapi_ai': 'https://newsapi.org/v2/everything?q=Artificial Intelligence&from=2024-02-18&sortBy=publishedAt&apiKey=%s' % (api_secrets.NEWS_API_KEY),
    #'newsapi_business_us': 'https://newsapi.org/v2/top-headlines?country=us&category=business&apiKey=%s' % (api_secrets.NEWS_API_KEY)
}

def verify_if_meme_is_funny(article_summary, meme_object, meme_captions):
    print(meme_object)
    meme_is_funny_prompt = llm_service.prepare_meme_is_funny_prompt(article_summary, meme_object, meme_captions)
    answer = llm_service.call_openai_llm(meme_is_funny_prompt)
    return answer

def caption_meme(template_id, username, password, text0, text1=None, text2=None, text3=None, text4=None, font=None):
    url = "https://api.imgflip.com/caption_image"
    payload = {
        'template_id': template_id,
        'username': username,
        'password': password,
        'boxes[0][text]': text0,
        'boxes[1][text]': text1,
        'boxes[2][text]': text2,
        'boxes[3][text]': text3,
        'boxes[4][text]': text4,
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
    news_source_recipe = random.choice(recipe.get('news_source') or list(_NEWS_SOURCES))
    news_source_api = _NEWS_SOURCES[news_source_recipe]
    article_response = requests.get(news_source_api)
    article_objects = json.loads(article_response.content)['articles']
    articles = {}
    for article_object in article_objects[:5]:
        title = article_object['title']
        description = article_object['description']
        article_url = article_object['url']
        articles[article_url] = description

    personality = recipe['personality']

    captioned_meme_urls = []
    for article_url, article_summary in articles.items():
        for meme_object in random.sample(meme_variants_config.MEME_VARIANTS, 2):  # 2 memes * 10 articles
            prompt = llm_service.prepare_meme_generation_prompt(article_summary, meme_object, personality)
            llm_model = random.choice(recipe['llm'])
            llm_response = llm_service.call_llm(prompt, llm_model)
            try:
                caption_list_first_meme = eval(llm_response)
                # Double-check if this is funny with an LLM-rater.
                is_meme_funny_comment = verify_if_meme_is_funny(article_summary, meme_object, caption_list_first_meme)

                if len(caption_list_first_meme) != meme_object['box_count']:
                    print('Meme LLM response caption count did not match the intended numnber of captions for this meme.')
                    continue
                captioned_meme_url = caption_meme(
                    meme_object['id'],
                    api_secrets.IMGFLIP_USERNAME, 
                    api_secrets.IMGFLIP_PASSWORD, 
                    *caption_list_first_meme)
                captioned_meme_urls.append(
                    (captioned_meme_url, prompt, llm_model, caption_list_first_meme, article_url, is_meme_funny_comment))
                print('Meme successfully created')
            except Exception:
                print(traceback.format_exc())

    return(captioned_meme_urls)
