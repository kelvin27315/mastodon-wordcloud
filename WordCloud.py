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

def Extract_content(toots):
    #取得したtootのリストからcontent(CWはspoiler_text)を抜き出す
    #1日の終わりの時刻(JST)
    temp = dt.date.today()
    end = timezone("Asia/Tokyo").localize(dt.datetime(temp.year, temp.month, temp.day, 0, 0, 0, 0))
    #1日の始まりの時刻(JST)
    temp = temp - dt.timedelta(days=1)
    start = timezone("Asia/Tokyo").localize(dt.datetime(temp.year, temp.month, temp.day, 0, 0, 0, 0))
    text = ''
    num = 0
    for toot in toots:
        #時間内のtootのみcontentを追加する
        time = toot["created_at"].astimezone(timezone("Asia/Tokyo"))
        if start <= time and time < end:
            #CWの呟きの場合隠されている方を追加せず表示されている方を追加する
            num += 1
            if toot["sensitive"] == True:
                text = text + ' ' + toot["spoiler_text"]
            else:
                text = text + ' ' + toot["content"]
    #HTMLタグ, URL, LSEP,RSEPを取り除く
    text = re.sub(r"<[^>]*?>", '', text)
    text = re.sub(r"(https?|ftp)(:\/\/[-_\.!~*\'()a-zA-Z0-9;\/?:\@&=\+\$,%#]+)",'', text)
    text = re.sub(r"[  ]", '', text)
    return(text, num)

def Get_toots():
    #Mastodonから一日のtootsを取得する

    #1日の始まりの時刻(JST)
    temp = dt.date.today() - dt.timedelta(days=1)
    start = timezone("Asia/Tokyo").localize(dt.datetime(temp.year, temp.month, temp.day, 0, 0, 0, 0))
    #tootの取得
    toots = mastodon.timeline(timeline = "local", limit = 40)
    while True:
        #UTCからJSTに変更
        time = toots[-1]["created_at"].astimezone(timezone("Asia/Tokyo"))
        #取得したget_toots全てのtootが0:00より前の場合終了
        if time < start:
            break
        #追加でtootの取得
        toots = toots + mastodon.timeline(timeline = "local", max_id = toots[-1]["id"] -1, limit = 40)
    #取得したtootのリストからcontent(CWはspoiler_text)を抜き出す
    text, num = Extract_content(toots)

    f = open("toots_content.txt", 'w')
    f.write(text)
    f.close()
    return(num)

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
            #名詞は取得したものそのまま
            #形容詞、動詞、副詞は原型を使用する
            if wtype == '名詞':
                wtype2 = word.split('\t')[1].split(',')[1]
                if wtype2 == "サ変接続":
                    words = words + " " + word.split('\t')[0]
                elif wtype2 == "ナイ形容詞語幹":
                    words = words + " " + word.split('\t')[0]
                elif wtype2 == "一般":
                    words = words + " " + word.split('\t')[0]
                elif wtype2 == "引用文字列":
                    words = words + " " + word.split('\t')[0]
                elif wtype2 == "形容動詞語幹":
                    words = words + " " + word.split('\t')[0]
                elif wtype2 == "固有名詞":
                    words = words + " " + word.split('\t')[0]
                elif wtype2 == "接続詞的":
                    words = words + " " + word.split('\t')[0]
                elif wtype2 == "接尾":
                    words = words + " " + word.split('\t')[0]
                elif wtype2 == "動詞非自立的":
                    words = words + " " + word.split('\t')[0]
                elif wtype2 == "特殊":
                    words = words + " " + word.split('\t')[0]
                elif wtype2 == "副詞可能":
                    words = words + " " + word.split('\t')[0]
            elif wtype == '形容詞':
                wtype2 = word.split('\t')[1].split(',')[1]
                if wtype2 == "自立" or wtype2 == "非自立":
                    words = words + " " + word.split('\t')[1].split(',')[6]
            elif wtype == '動詞':
                wtype2 = word.split('\t')[1].split(',')[1]
                if wtype2 == "自立":
                    words = words + " " + word.split('\t')[1].split(',')[6]
            elif wtype == '副詞':
                words = words + " " + word.split('\t')[1].split(',')[6]
    return(words)

def Make_WordCloud(words):
    #Word Cloudを作成し、画像を保存する
    fpath = "NotoSansCJK-Regular"
    stop_words = ["てる", "さん", "こと", "する", "ある", "いる", "それ", "れる", "られ", "なっ", "そう", "なる", "よう",
        "もう", "あれ", "ない", "いい", "思っ", "もの", "みたい", "感じ", "やっ", "どう", "あり", "ちゃん", "あっ", "あと",
        "とりあえず", "すぎる", "まあ", "ちょっと", "みんな", "これ", "よく", "思う", "やる", "見る", "くる", "好き", "良い",
        "いう", "言う", "出る", "ここ", "行く", "出来る", "できる", "られる", "わかる", "いく"]
    wordcloud = WordCloud(font_path = fpath, width = 800, height = 600, stopwords=set(stop_words),max_font_size=180,collocations=False).generate(words)
    wordcloud.to_file(filename = "wordcloud.png")

def Toot(num):
    #日付と画像を投稿する
    #画像のURLが返ってくる
    media = [mastodon.media_post("wordcloud.png")]
    today = dt.date.today() - dt.timedelta(days=1)
    post = str(today.month) + '月' + str(today.day) + "日のトレンドです。（取得toot数: " + str(num) + "） " + media[0]["text_url"]
    mastodon.status_post(post, media_ids = media)

if __name__ == "__main__":
    num = Get_toots()
    words = Wkati()
    Make_WordCloud(words)
    Toot(num)
