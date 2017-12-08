from wordcloud import WordCloud
from mastodon import Mastodon
from pytz import timezone
import datetime as dt
import MeCab
import re

if __name__ == "__main__":
    mastodon = Mastodon(
            client_id="clientcred.secret",
            access_token="usercred.secret",
            api_base_url = "https://gensokyo.cloud")

def Get_toots():
    #Mastodonから一日のtootsを取得する

    #JSTで昨日の0:00を指定
    temp = dt.date.today() - dt.timedelta(days=1)
    today = timezone("Asia/Tokyo").localize(dt.datetime(temp.year, temp.month, temp.day, 0, 0, 0, 0))
    #tootの取得
    toots = mastodon.timeline(timeline = "local", limit = 40)
    while True:
        #UTCからJSTに変更
        time = toots[-1]["created_at"].astimezone(timezone("Asia/Tokyo"))
        #取得したget_toots全てのtootが0:00より前の場合終了
        if time < today:
            break
        #追加でtootの取得
        toots = toots + mastodon.timeline(timeline = "local", max_id = toots[-1]["id"] -1, limit = 40)

    f = open("toots_content.txt", 'w')
    f.write("")
    f.close()
    f = open("toots_content.txt", 'a')
    #hiduke wo
    for toot in toots:
        #HTMLタグ, URL, LSEP,RSEPを取り除く
        text = re.sub(r"<[^>]*?>", '', toot["content"])
        text = re.sub(r"(https?|ftp)(:\/\/[-_\.!~*\'()a-zA-Z0-9;\/?:\@&=\+\$,%#]+)",'', text)
        text = re.sub(r"[  ]", '', text)
        f.write(text)
    f.close()

def Wkati():
    #取得されたtootsから分かち書きを行う
    #MeCab(NEologd辞書使用)による分かち書き
    m = MeCab.Tagger("-d mecab/dic/mecab-ipadic-neologd")
    f = open("toots_content.txt")
    text = f.read()
    f.close()

    words = ""
    #分かち書きを行い単語の品詞が形容詞、動詞、名詞、副詞のみを取得する
    for word in m.parse(text).splitlines():
        if word != 'EOS':
            wtype = word.split('\t')[1].split(',')[0]
            if wtype == '形容詞' or wtype == '動詞' or wtype == '名詞' or wtype == '副詞':
                words = words + " " + word.split('\t')[0]
    return(words)

def Make_WordCloud(words):
    #Word Cloudを作成し、画像を保存する
    fpath = "NotoSansCJK-Regular"
    stop_words = ["てる", "さん", "こと", "する", "ある", "いる", "それ", "れる", "られ", "なっ", "そう", "なる", "よう",
        "もう", "あれ", "ない", "いい", "思っ", "もの", "みたい", "感じ", "やっ", "どう", "あり", "ちゃん", "あっ", "あと",
        "とりあえず", "すぎる", "まあ", "ちょっと", "みんな", "これ", "よく"]
    wordcloud = WordCloud(font_path = fpath, width = 800, height = 600, stopwords=set(stop_words),max_font_size=180).generate(words)
    wordcloud.to_file(filename = "wordcloud.png")

def Toot():
    #日付と画像を投稿する
    #画像のURLが返ってくる
    media = [mastodon.media_post("wordcloud.png")]
    today = dt.date.today() - dt.timedelta(days=1)
    post = str(today.month) + '月' + str(today.day) + "日のトレンドです。 " + media[0]["text_url"]
    mastodon.status_post(post, media_ids = media)

if __name__ == "__main__":
    Get_toots()
    words = Wkati()
    Make_WordCloud(words)
    Toot()
