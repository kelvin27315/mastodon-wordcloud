import multiprocessing as mp
import re
import time
from pathlib import Path

import gensim
import MeCab


def get_file_path():
    """
    固有名詞のdfのpathのリスト
    """
    p = Path(__file__).parent.resolve() / ".." / "toots_log"
    file_paths = sorted([f for f in p.iterdir() if f.is_file()])
    return(file_paths)

def read_files(file_paths):
    text = ""
    for file_path in file_paths:
        with open(file_path,"r") as f:
            text += f.read()
            text += "\n"
    text = re.sub(r":[a-zA-Z0-9_-]+:", "", text)
    text = re.sub(" ", "\n", text)
    return(text)

def wakachi(text):
    #corpus = [[word,word,word],[word,word,word,word],,,]
    m = MeCab.Tagger("-d /usr/lib/mecab/dic/mecab-ipadic-neologd")
    corpus = [[word.split("\t")[0] for word in m.parse(sentence).splitlines() if word != "EOS"] for sentence in text.splitlines()]
    return(corpus)

if __name__ == "__main__":
    file_paths = get_file_path()
    print(len(file_paths))
    text = read_files(file_paths)
    print("corpus作成")
    corpus = wakachi(text)
    print(len(corpus))
    print("学習始め")
    model = gensim.models.word2vec.Word2Vec(
        corpus,
        size=60,
        window=8,
        min_count=5,
        workers=mp.cpu_count(),
        sg=1,
        iter=6
    )
    print("学習終了, 保存")
    print("vocab: {}語".format(len(model.wv.vocab)))
    model.save(str(Path(__file__).parent.resolve() /"word2vec.gensim.model"))
    print("---保存完了---")
