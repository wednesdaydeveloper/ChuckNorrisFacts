import os
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
    """
    エントリポイント

    Parameters
    ----------
    request
            リクエスト
    """

    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        events = parser.parse(body, signature)
        for event in events:
            send_line_text_message(event.reply_token)
            break
    except InvalidSignatureError:
        abort(400)
    return 'OK'

def send_line_text_message(reply_token):
    """
    LINE に 取得したChuck Norris Facts の英語と日本語のメッセージを返す。

    Parameters
    ----------
    reply_token
            reply_token
    """

    print(f'loading chuck norris facts...')
    joke_en = get_joke()
    print(f'translating chuck norris facts...')
    joke_ja = get_japanese_text(joke_en)
    print(f'english: {joke_en}')
    print(f'japanese: {joke_ja}')
    line_bot_api.reply_message(reply_token, [TextSendMessage(text=joke_en), TextSendMessage(text=joke_ja)])

def get_joke():
    """
    Chuck Norris Facts の英語のメッセージを返す。

    Returns
    -------
    english_message : string
        Chuck Norris Facts の英語のメッセージ。
    """

    resp = http.request('GET', URL)
    data = json.loads(resp.data.decode('utf-8'))
    return data['value']

def get_japanese_text(english_text):
    """
    Chuck Norris Facts の英語のメッセージから、日本語のメッセージを作成して返す。

    Parameters
    ----------
    english_text
            Chuck Norris Facts の英語のメッセージ
    Returns
    -------
    japanese_message : string
        Chuck Norris Facts の日本語のメッセージ。
    """

    target="ja"
    result = translate_client.translate(english_text, target_language=target)
    return result["translatedText"]
