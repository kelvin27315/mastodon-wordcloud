"""
保存してあるログから一年間のトレンドを作る。
なければ取得
"""

import datetime as dt
import re
import time
from os import path

import MeCab
import pandas as pd
from dateutil.relativedelta import relativedelta
from mastodon import Mastodon
from pytz import timezone
from tqdm import tqdm


def Extract_content(toots, today, yesterday):
    """
    tootのリストから使用する日付のものからcontentを集める。
    CWが使用されている場合はspoiler_textを集める。
    また、使用するtootの数も数える。
    """
    text = ""
    for i, toot in enumerate(toots):
        # 時間内のtootのみcontentを追加する
        time = toot["created_at"].astimezone(timezone("Asia/Tokyo"))
        if yesterday <= time and time < today:
            # CWの呟きの場合隠されている方を追加せず表示されている方を追加する
            if toot["sensitive"] == True:
                text += " " + toot["spoiler_text"]
            else:
                text += " " + toot["content"]
        if time < yesterday:
            toots = toots[i:]
            break
    # HTMLタグ, URL, LSEP,RSEP, 絵文字, HTML特殊文字を取り除く
    text = re.sub(r"<[^>]*?>", "", text)
    text = re.sub(r"(https?|ftp)(:\/\/[-_\.!~*\'()a-zA-Z0-9;\/?:\@&=\+\$,%#]+)", "", text)
    text = re.sub(r"[  ]", "", text)
    text = re.sub(r"&[a-zA-Z0-9]+;", "", text)
    return (text, toots)


class Gensokyo:
    def __init__(self):
        self.token = Mastodon(
            client_id="clientcred.secret", access_token="usercred.secret", api_base_url="https://gensokyo.town"
        )

    def get_toots(self):
        """
        Mastodonから前日1日分のtootを取得し、呟き内容を保存する。
        また、前日1日分の取得したtootの数も返す
        """
        # 1日の始まりの時刻(JST)
        last_year = timezone("Asia/Tokyo").localize(
            dt.datetime((TODAY - relativedelta(years=1)).year, 1, 1, 0, 0, 0, 0)
        )
        today = timezone("Asia/Tokyo").localize(dt.datetime(TODAY.year, TODAY.month, TODAY.day, 0, 0, 0, 0))
        yesterday = timezone("Asia/Tokyo").localize(
            dt.datetime(YESTERDAY.year, YESTERDAY.month, YESTERDAY.day, 0, 0, 0, 0)
        )
        yesterday_day = YESTERDAY
        toots = self.token.timeline(timeline="local", max_id=101341909845622273, limit=40)
        p = PATH / "toots_log"
        file_lists = [str(f) for f in p.iterdir()]
        while yesterday >= last_year:
            print(today)
            file_path = str(PATH / "toots_log" / ("{}.txt".format(yesterday_day)))
            if file_path not in file_lists:
                while toots[-1]["created_at"].astimezone(timezone("Asia/Tokyo")) >= yesterday:
                    # 追加でtootの取得
                    print("get: {}".format(toots[-1]["created_at"].astimezone(timezone("Asia/Tokyo"))))
                    time.sleep(1)
                    toots += self.token.timeline(timeline="local", max_id=toots[-1]["id"] - 1, limit=40)
                # 取得したtootのリストからcontent(CWはspoiler_text)を抜き出す
                text, toots = Extract_content(toots, today, yesterday)
                with open(file_path, "w") as f:
                    f.write(text)
            today = yesterday
            yesterday -= dt.timedelta(days=1)
            yesterday_day -= dt.timedelta(days=1)

    def toot(self):
        """
        Mastodonに画像をアップロードし、文字と画像を投稿する
        """
        # 画像のURLが返ってくる
        media = [self.token.media_post(str(PATH / "wordcloud.png"))]
        post = "{}年のトレンドです。".format(YESTERDAY.year)
        self.token.status_post(post, media_ids=media)


def wkati():
    """
    取得したtootのcontent類に分かち書きを行う。
    必要な品詞だけ使用し、品詞よっては単語の原型を使用する。
    """
    # MeCab(NEologd辞書使用)による分かち書き
    m = MeCab.Tagger("-d /usr/lib/mecab/dic/mecab-ipadic-neologd")
    words = ""
    # 使用する品詞細分類1のリスト
    norns = ["サ変接続", "ナイ形容詞語幹", "一般", "引用文字列", "形容動詞語幹", "固有名詞", "接続詞的", "接尾", "動詞非自立的", "特殊", "副詞可能"]
    adjectives = ["自立", "非自立"]

    text = ""
    p = PATH / "toots_log"
    file_lists = [f for f in p.iterdir()]
    for file_path in file_lists:
        with open(file_path, "r") as f:
            text = f.read()
        # カスタム絵文字を取り除く
        text = re.sub(r":[a-zA-Z0-9_-]+:", "", text)

        # 分かち書きを行い単語の品詞が形容詞、動詞、名詞、副詞のみを取得する
        for word in tqdm(m.parse(text).splitlines()[:-1]):
            if word != "":
                wtype = word.split("\t")[1].split(",")[0]  # 品詞
                wtype2 = word.split("\t")[1].split(",")[1]  # 品詞細分類1
                # 名詞はそのまま,形容詞、動詞、副詞は原型を使用する
                if wtype == "名詞" and wtype2 in norns:
                    words += " " + word.split("\t")[0]
                elif wtype == "形容詞" and wtype2 in adjectives:
                    words += " " + word.split("\t")[1].split(",")[6]
                elif wtype == "動詞" and wtype2 == "自立":
                    words += " " + word.split("\t")[1].split(",")[6]
                elif wtype == "副詞":
                    words += " " + word.split("\t")[1].split(",")[6]
    return words


def make_wordcloud(words):
    """
    WordCloudモジュールを使用しワードクラウドの画像を作成する。
    """
    fpath = str(PATH / "FJS-NewRodinProN-B.otf")
    stop_words = [
        "てる",
        "さん",
        "こと",
        "する",
        "ある",
        "いる",
        "それ",
        "れる",
        "られ",
        "なっ",
        "そう",
        "なる",
        "よう",
        "もう",
        "あれ",
        "ない",
        "いい",
        "思っ",
        "もの",
        "みたい",
        "感じ",
        "やっ",
        "どう",
        "あり",
        "ちゃん",
        "あっ",
        "あと",
        "とりあえず",
        "すぎる",
        "まあ",
        "ちょっと",
        "みんな",
        "これ",
        "よく",
        "思う",
        "やる",
        "見る",
        "くる",
        "好き",
        "良い",
        "いう",
        "言う",
        "出る",
        "ここ",
        "行く",
        "出来る",
        "できる",
        "られる",
        "わかる",
        "いく",
    ]
    wordcloud = WordCloud(
        font_path=fpath, width=800, height=600, stopwords=set(stop_words), max_font_size=180, collocations=False
    ).generate(words)
    wordcloud.to_file(filename=str(PATH / "wordcloud.png"))


if __name__ == "__main__":
    PATH = Path(__file__).parent.resolve()
    TODAY = dt.date.today()
    YESTERDAY = TODAY - dt.timedelta(days=1)
    gensokyo = Gensokyo()
    gensokyo.get_toots()
    words = wkati()
    make_wordcloud(words)
    gensokyo.toot()
