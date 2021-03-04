import os
import requests
from flask import abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import urllib3
import json
from google.cloud import translate_v2 as translate

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

# チャック ノリス のジョークのAPIのURI
URL = 'https://api.chucknorris.io/jokes/random'

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(YOUR_CHANNEL_SECRET)
# HTTP通信用
http = urllib3.PoolManager()
# 翻訳
translate_client = translate.Client()

def chuckNorrisFacts(request):
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)
    # for logging request contents
    print(events)
    for event in events:
        send_line_text_message(event.reply_token, event.message.text)
        break
    return 'OK'

def send_line_text_message(reply_token, text_message):
    joke_en = get_joke()
    joke_ja = translate_text(joke_en)
    line_bot_api.reply_message(reply_token, [TextSendMessage(text=joke_en), TextSendMessage(text=joke_ja)])

def get_joke():
    resp = http.request('GET', URL)
    data = json.loads(resp.data.decode('utf-8'))
    return data['value']

def translate_text(english_text):
    target="ja"
    result = translate_client.translate(english_text, target_language=target)
    return result["translatedText"]
