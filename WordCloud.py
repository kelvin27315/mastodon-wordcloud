from wordcloud import WordCloud
from mastodon import Mastodon
from pytz import timezone
from os import path
import datetime as dt
import pandas as pd
import MeCab
import re

PATH = path.dirname(path.abspath(__file__))
if __name__ == "__main__":
    mastodon = Mastodon(
            client_id = PATH + "/clientcred.secret",
            access_token = PATH + "/usercred.secret",
            api_base_url = "https://gensokyo.town")
TODAY = dt.date.today()
YESTERDAY = TODAY - dt.timedelta(days=1)

def Extract_content(toots):
    """
    tootのリストから使用する日付のものからcontentを集める。
    CWが使用されている場合はspoiler_textを集める。
    また、使用するtootの数も数える。
    """
    #1日の終わりの時刻(JST)
    end = timezone("Asia/Tokyo").localize(dt.datetime(TODAY.year, TODAY.month, TODAY.day, 0, 0, 0, 0))
    #1日の始まりの時刻(JST)
    start = timezone("Asia/Tokyo").localize(dt.datetime(YESTERDAY.year, YESTERDAY.month, YESTERDAY.day, 0, 0, 0, 0))
    text = ""
    num = 0
    for toot in toots:
        #時間内のtootのみcontentを追加する
        time = toot["created_at"].astimezone(timezone("Asia/Tokyo"))
        if start <= time and time < end:
            #CWの呟きの場合隠されている方を追加せず表示されている方を追加する
            num += 1
            if toot["sensitive"] == True:
                text = text + " " + toot["spoiler_text"]
            else:
                text = text + " " + toot["content"]
    #HTMLタグ, URL, LSEP,RSEP, 絵文字, HTML特殊文字を取り除く
    text = re.sub(r"<[^>]*?>", "", text)
    text = re.sub(r"(https?|ftp)(:\/\/[-_\.!~*\'()a-zA-Z0-9;\/?:\@&=\+\$,%#]+)", "", text)
    text = re.sub(r"[  ]", "", text)
    text = re.sub(r"&[a-zA-Z0-9]+;", "", text)
    return(text, num)

def Get_toots():
    """
    Mastodonから前日1日分のtootを取得し、呟き内容を保存する。
    また、前日1日分の取得したtootの数も返す
    """
    #1日の始まりの時刻(JST)
    start = timezone("Asia/Tokyo").localize(dt.datetime(YESTERDAY.year, YESTERDAY.month, YESTERDAY.day, 0, 0, 0, 0))
    #tootの取得
    toots = mastodon.timeline(timeline="local", limit=40)
    while True:
        #UTCからJSTに変更
        time = toots[-1]["created_at"].astimezone(timezone("Asia/Tokyo"))
        #取得したget_toots全てのtootが0:00より前の場合終了
        if time < start:
            break
        #追加でtootの取得
        toots = toots + mastodon.timeline(timeline = "local", max_id = toots[-1]["id"] - 1, limit = 40)
    #取得したtootのリストからcontent(CWはspoiler_text)を抜き出す
    text, num = Extract_content(toots)

    with open(PATH + "/toots_log/" + str(YESTERDAY) + ".txt", 'w') as f:
        f.write(text)
    return(num)

def Emoji_lanking():
    """
    絵文字の使用回数のランキング
    """
    with open(PATH + "/toots_log/" + str(YESTERDAY) + ".txt", "r") as f:
        text = f.read()

    #保存されたtootから絵文字だけ取り出してそれの出現回数のSeriesができる
    emoji = pd.Series(re.findall(r":[a-zA-Z0-9_-]+:", text)).value_counts()
    toot = str(YESTERDAY.month) + "月" + str(YESTERDAY.day) + "日に使用された絵文字の使用回数ランキングです。\n"
    #ランキング作る
    for (i,(count, em)) in enumerate(zip(emoji, emoji.index)):
        temp = str(i+1) + "位: " + em + " (" + str(count) + "回)\n"
        #500文字超えたら一度投稿して再度文を作り始める。
        if len(toot) + len(temp) >= 500:
            mastodon.status_post(status = toot, visibility = "unlisted")
            toot = ""
        toot += temp
    mastodon.status_post(status = toot, visibility = "unlisted")

def Wkati():
    """
    取得したtootのcontent類に分かち書きを行う。
    必要な品詞だけ使用し、品詞よっては単語の原型を使用する。
    """
    #MeCab(NEologd辞書使用)による分かち書き
    #m = MeCab.Tagger("-d /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd")
    m = MeCab.Tagger()
    with open(PATH + "/toots_log/" + str(YESTERDAY) + ".txt", "r") as f:
        text = f.read()
    #カスタム絵文字を取り除く
    text = re.sub(r":[a-zA-Z0-9_-]+:", "", text)

    words = ""
    #使用する品詞細分類1のリスト
    norns = ["サ変接続", "ナイ形容詞語幹", "一般", "引用文字列", "形容動詞語幹", "固有名詞", "接続詞的", "接尾", "動詞非自立的", "特殊", "副詞可能"]
    adjectives = ["自立", "非自立"]
    #分かち書きを行い単語の品詞が形容詞、動詞、名詞、副詞のみを取得する
    for word in m.parse(text).splitlines():
        if word != "EOS":
            wtype = word.split('\t')[1].split(',')[0]   #品詞
            wtype2 = word.split('\t')[1].split(',')[1]  #品詞細分類1
            #名詞はそのまま,形容詞、動詞、副詞は原型を使用する
            if wtype == "名詞" and wtype2 in norns:
                words = words + " " + word.split('\t')[0]
            elif wtype == "形容詞" and wtype2 in adjectives:
                words = words + " " + word.split('\t')[1].split(',')[6]
            elif wtype == "動詞" and wtype2 == "自立":
                words = words + " " + word.split('\t')[1].split(',')[6]
            elif wtype == "副詞":
                words = words + " " + word.split('\t')[1].split(',')[6]
    return(words)

def Make_WordCloud(words):
    """
    WordCloudモジュールを使用しワードクラウドの画像を作成する。
    """
    fpath = PATH + "/FJS-NewRodinProN-B.otf"
    stop_words = ["てる", "さん", "こと", "する", "ある", "いる", "それ", "れる", "られ", "なっ", "そう", "なる", "よう",
        "もう", "あれ", "ない", "いい", "思っ", "もの", "みたい", "感じ", "やっ", "どう", "あり", "ちゃん", "あっ", "あと",
        "とりあえず", "すぎる", "まあ", "ちょっと", "みんな", "これ", "よく", "思う", "やる", "見る", "くる", "好き", "良い",
        "いう", "言う", "出る", "ここ", "行く", "出来る", "できる", "られる", "わかる", "いく"]
    wordcloud = WordCloud(
        font_path = fpath, width = 800, height = 600, stopwords = set(stop_words),
        max_font_size = 180, collocations = False).generate(words)
    wordcloud.to_file(filename = PATH + "/wordcloud.png")

def Toot(num):
    """
    Mastodonに画像をアップロードし、文字と画像を投稿する
    """
    #画像のURLが返ってくる
    media = [mastodon.media_post(PATH + "/wordcloud.png")]
    post = str(YESTERDAY.month) + "月" + str(YESTERDAY.day) + "日のトレンドです。（取得toot数: " + str(num) + "）"
    mastodon.status_post(post, media_ids = media)

if __name__ == "__main__":
    num = Get_toots()
    Emoji_lanking()
    words = Wkati()
    Make_WordCloud(words)
    Toot(num)
