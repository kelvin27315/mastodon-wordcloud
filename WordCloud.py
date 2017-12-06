from wordcloud import WordCloud
from mastodon import Mastodon
from dateutil.tz import tzutc
import datetime as dt
import pandas as pd
import MeCab
import re

if __name__ == "__main__":
    mastodon = Mastodon(
            client_id="clientcred.secret",
            access_token="usercred.secret",
            api_base_url = "https://gensokyo.cloud")

def Get_toots():
    #Mastodonから一日のtootsを取得する
    temp = dt.date.today()
    today = dt.datetime(temp.year, temp.month, temp.day - 2, 15, 0, 0, 0, tzinfo = tzutc())#1->2

    toots = mastodon.timeline(timeline = "local", limit = 40)
    while True:
        time = toots[-1]["created_at"]
        #取得したget_toots全てのtootが0:00より前の場合終了
        if time < today:
            break
        toots = toots + mastodon.timeline(timeline = "local", max_id = toots[-1]["id"] -1, limit = 40)

    f = open("toots_content.txt", 'w')
    f.write("")
    f.close()
    f = open("toots_content.txt", 'a')
    #hiduke wo
    for toot in toots:
        text = re.sub(r"<[^>]*?>", '', toot["content"])
        text = re.sub(r"(https?|ftp)(:\/\/[-_\.!~*\'()a-zA-Z0-9;\/?:\@&=\+\$,%#]+)",'', text)
        f.write(text)
    f.close()

def Wkati():
    #取得されたtootsから分かち書きを行う
    #MeCab(NEologd辞書使用)による分かち書き
    m = MeCab.Tagger("-Owakati")
    f = open("toots_content.txt")
    text = f.read()
    f.close()
    words = m.parse(text)
    return(words)

def Make_WordCloud(words):
    #Word Cloudを作成し、画像を保存する
    fpath = "NotoSansCJK-Regular"
    wordcloud = WordCloud(font_path = fpath, width = 800, height = 600).generate(words)
    wordcloud.to_file(filename = "wordcloud.png")

def Toot():
    #日付と画像を投稿する
    media = [mastodon.media_post("wordcloud.png")]
    today = dt.date.today()
    post = str(today.month) + '月' + str(today.day - 1) + "日のトレンドです。 " + media[0]["text_url"]
    mastodon.status_post(post, media_ids = media)

if __name__ == "__main__":
    Get_toots()
    words = Wkati()
    Make_WordCloud(words)
    Toot()
