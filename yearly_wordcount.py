from pathlib import Path
from tqdm import tqdm
import matplotlib.pyplot as plt
import pandas as pd
import japanize_matplotlib
import collections
import MeCab
import re

def get_word(word):
    norns = ["サ変接続", "ナイ形容詞語幹", "一般", "引用文字列", "形容動詞語幹", "固有名詞", "接続詞的", "接尾", "動詞非自立的", "特殊", "副詞可能"]
    if word != "":
        wtype = word.split('\t')[1].split(',')[0]   #品詞
        wtype2 = word.split('\t')[1].split(',')[1]  #品詞細分類1
        #名詞はそのまま,形容詞、動詞、副詞は原型を使用する
        if wtype == "名詞" and wtype2 in norns:
            return(word.split('\t')[0])
        elif wtype == "形容詞" and wtype2 in ["自立", "非自立"]:
            return(word.split('\t')[1].split(',')[6])
        elif wtype == "動詞" and wtype2 == "自立":
            return(word.split('\t')[1].split(',')[6])
        elif wtype == "副詞":
            return(word.split('\t')[1].split(',')[6])

if __name__ == "__main__":
    p = Path(__file__).parent.resolve() / "toots_log"
    file_paths = [f for f in p.iterdir()]
    m = MeCab.Tagger("-d /usr/lib/mecab/dic/mecab-ipadic-neologd")
    words = []
    #使用する品詞細分類1のリスト

    for file_path in tqdm(file_paths):
        with open(file_path, "r") as f:
            text = f.read()
        #カスタム絵文字を取り除く
        text = re.sub(r":[a-zA-Z0-9_-]+:", "", text)
        #分かち書きを行い単語の品詞が形容詞、動詞、名詞、副詞のみを取得する
        words.extend([get_word(word) for word in m.parse(text).splitlines()[:-1]])
    words = collections.Counter(words)
    words = pd.DataFrame(words,index=["num"])
    words = words.T
    words = words[words["num"]>199]
    d_list = ["てる", "さん", "こと", "する", "ある", "いる", "それ", "れる", "られ", "なっ", "そう", "なる", "よう",
        "もう", "あれ", "ない", "いい", "思っ", "もの", "みたい", "感じ", "やっ", "どう", "あり", "ちゃん", "あっ", "あと",
        "とりあえず", "すぎる", "まあ", "ちょっと", "みんな", "これ", "よく", "思う", "やる", "見る", "くる", "好き", "良い",
        "いう", "言う", "出る", "ここ", "行く", "出来る", "できる", "られる", "わかる", "いく"]
    temp = list(words.index)
    d_list = [d_word for d_word in d_list if d_word in temp]
    words = words.drop(d_list)
    words = words.sort_values("num",ascending=False)
    words = words.drop(index = [words.index[0]])
    length = len(words)

    for i in range(4):
        temp = words[int(length*i/4):int(length*(i+1)/4)]

        plt.figure(figsize=(20,3),dpi=400)
        plt.bar(x=range(len(temp)), height=temp["num"],tick_label=temp.index)
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig(("{}.png".format(i)))
