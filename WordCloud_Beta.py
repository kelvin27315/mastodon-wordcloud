from wordcloud import WordCloud
from mastodon import Mastodon
from pytz import timezone
from os import path
import datetime as dt
import pandas as pd
import MeCab
import math
import re

PATH = path.dirname(path.abspath(__file__)) + "/"
if __name__ == "__main__":
    mastodon = Mastodon(
            client_id = PATH + "clientcred.secret",
            access_token = PATH + "usercred.secret",
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
    toots = mastodon.timeline(timeline="local", limit=80)
    while True:
        #UTCからJSTに変更
        time = toots[-1]["created_at"].astimezone(timezone("Asia/Tokyo"))
        #取得したget_toots全てのtootが0:00より前の場合終了
        if time < start:
            break
        #追加でtootの取得
        toots = toots + mastodon.timeline(timeline="local", max_id=toots[-1]["id"]-1, limit=80)
    #取得したtootのリストからcontent(CWはspoiler_text)を抜き出す
    text, num = Extract_content(toots)

    with open(PATH + "toots_log/" + str(YESTERDAY) + ".txt", 'w') as f:
        f.write(text)
    return(num)

def Emoji_lanking():
    """
    絵文字の使用回数のランキング
    """
    with open(PATH + "toots_log/" + str(YESTERDAY) + ".txt", "r") as f:
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

def Wkati(text):
    """
    取得したtootのcontent類に分かち書きを行う。
    必要な品詞だけ使用し、品詞よっては単語の原型を使用する。
    """
    #MeCab(NEologd辞書使用)による分かち書き
    m = MeCab.Tagger("-d /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd")
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

def TF_IDF():
    """
    TF-IDFを行い、一日の重要な単語を出す。
    それぞれの単語のTF-IDFの値の数だけ単語の含んだstrを作る。
    """
    #TF値を出す
    with open(PATH + "toots_log/" + str(YESTERDAY) + ".txt", "r") as f:
        text = f.read()
    Td_words = Wkati(text)
    #保存されたtootから出現回数のSeriesができる.
    temp = pd.Series(Td_words.split()).value_counts()
    #各単語の出現回数を全体の単語数で割る。(別にそう単語数で割らなくても良い気がする。)
    tf = pd.Series(0.0, temp.index)
    for word in tf.index:
        tf[word] = temp[word] / len(Td_words)

    #IDF値を出す
    df = pd.Series(0, tf.index)
    #0でも良いけど、その場合毎回出てるといえど、出現回数0の単語が出る。1の場合はTF値がでかいのが十分に小さくならない(もっと小さくなっても良い気がする)
    idf = pd.Series(1.0, tf.index)
    #過去どのくらい遡って比較するか
    days = 21
    #まずDF値を出す。(ある単語が含まれた過去の文書の数)
    for d in range(days):
        #過去のtootの記録を開く(原型とかで変形しているのでその都度分かち書きにかける)
        with open(PATH + "toots_log/" + str(YESTERDAY - dt.timedelta(days=d)) + ".txt", "r") as f:
            old_words = Wkati(f.read())
        #ある日にその単語が含まれてればdfの値を1つ加算
        for word in df.index:
            if word in old_words:
                df[word] += 1
    #IDFを求める
    for (word, Df) in zip(idf.index, df):
        idf[word] += math.log(days / Df)

    #tf-idf値を求める
    tfidf = pd.Series(0.0, tf.index)
    for (Tf, Idf, word) in zip(tf, idf, tfidf.index):
        tfidf[word] = Tf * Idf

    #TF-IDF値の数だけ単語を追加する(大抵1を下回ってるので適当に大きくしてintに変える)
    words = ""
    for (count, word) in zip(tfidf, tfidf.index):
        for i in range(int(count*100000)):
            words += word + " "

    return(words)

def Make_WordCloud(words):
    """
    WordCloudモジュールを使用しワードクラウドの画像を作成する。
    """
    fpath = PATH + "FJS-NewRodinProN-B.otf"
    stop_words = ["てる", "さん", "こと", "する", "ある", "いる", "それ", "れる", "られ", "なっ", "そう", "なる", "よう",
        "もう", "あれ", "ない", "いい", "思っ", "もの", "みたい", "感じ", "やっ", "どう", "あり", "ちゃん", "あっ", "あと",
        "とりあえず", "すぎる", "まあ", "ちょっと", "みんな", "これ", "よく", "思う", "やる", "見る", "くる", "好き", "良い",
        "いう", "言う", "出る", "ここ", "行く", "出来る", "できる", "られる", "わかる", "いく"]
    wordcloud = WordCloud(
        font_path = fpath, width = 800, height = 600, stopwords = set(stop_words),
        max_font_size = 180, collocations = False).generate(words)
    wordcloud.to_file(filename = PATH + "wordcloud.png")

def Toot(num):
    """
    Mastodonに画像をアップロードし、文字と画像を投稿する
    """
    #画像のURLが返ってくる
    media = [mastodon.media_post(PATH + "wordcloud.png")]
    post = str(YESTERDAY.month) + "月" + str(YESTERDAY.day) + "日のトレンドです。（取得toot数: " + str(num) + "） " + media[0]["text_url"]
    mastodon.status_post(post, media_ids = media)

if __name__ == "__main__":
    num = Get_toots()
    Emoji_lanking()
    words = TF_IDF()
    Make_WordCloud(words)
    Toot(num)
