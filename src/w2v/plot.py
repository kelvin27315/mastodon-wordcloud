from sklearn.decomposition import PCA
from pathlib import Path
from gensim import models
import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib

def w2v_pca(vectors):
    pca = PCA(2)
    pca.fit(vectors)
    pca_vec = pca.transform(vectors)
    return(pca_vec)

if __name__ == "__main__":
    model = models.word2vec.Word2Vec.load(str(Path(__file__).parent.resolve()/"word2vec.gensim.model"))
    with open(str(Path(__file__).parent.resolve()/".."/"dic"/"touhou_character_names.csv"),"r") as f:
        characters = f.read()
    characters = [ch.split(",")[0] for ch in characters.splitlines()]
    characters = [ch for ch in characters if ch in model.wv.vocab]
    vectors = [model[character] for character in characters]
    vectors = w2v_pca(vectors)

    plt.figure(dpi=300)
    plt.scatter(vectors[:,0], vectors[:,1], s=7)
    for word,vec in zip(characters,vectors):
        plt.annotate(word,(vec[0],vec[1]),size=4)
    plt.savefig("w2v.png")



