"""
絵文字ランキングを投稿しているアカウントから
過去のランキングを取得し、現在までの絵文字の使用回数の総和とそのランキングを出す
"""

from mastodon import Mastodon
from tqdm import tqdm
import pandas as pd
import time
import re

if __name__ == "__main__":
    mastodon = Mastodon(
                client_id = "clientcred.secret",
                access_token = "usercred.secret",
                api_base_url = "https://gensokyo.town")

def get_account_toot():
    """
    アカウントの過去のtootを全て取得し、絵文字と使用回数のリストを作る
    """
    toots = []
    extend_toots = toots.extend
    temp_toots = mastodon.account_statuses(id=113,limit=40)
    #whileに書き直す
    while True:
        if len(temp_toots) == 0:
            break
        for toot in temp_toots:
            if "トレンド" not in toot["content"]:
                print(toot["content"][3:10])
                extend_toots(toot["content"].split("<br />"))
        time.sleep(3)
        temp_toots = mastodon.account_statuses(id=113,max_id=temp_toots[-1]["id"]-1,limit=40)
    return(toots)

def relist(toots):
    """
    不要物を除く
    """
    rank = [toot for toot in toots if toot[0:3] != "<p>"]
    for i, toot in enumerate(tqdm(rank)):
        if toot[-4:] == "</p>":
            rank[i] = toot[0:-4]
    return(rank)

def emoji_counter(rank):
    """
    集計
    """
    emoji_rank = pd.DataFrame({"emoji":re.search(":[a-zA-Z0-9_-]+:", rank[0])[0],
                               "num":[int(re.search("[0-9]+回", rank[0])[0][:-1])]})

    for emoji in tqdm(rank[1:]):
        if (emoji_rank["emoji"] == re.search(":[a-zA-Z0-9_-]+:", emoji)[0]).sum() == 0:
            emoji_rank = emoji_rank.append(pd.DataFrame({"emoji":re.search(":[a-zA-Z0-9_-]+:", emoji)[0],
                                            "num":[int(re.search("[0-9]+回", emoji)[0][:-1])]})).reset_index(drop=True)
        else:
            emoji_rank.iat[list(emoji_rank.query("emoji ==\'"+re.search(":[a-zA-Z0-9_-]+:",emoji)[0]+"\'").index)[0],1] += int(re.search("[0-9]+回", emoji)[0][:-1])
    return(emoji_rank)

if __name__ == "__main__":
    toots = get_account_toot()
    rank = relist(toots)
    emoji_rank = emoji_counter(rank)
    emoji_rank = emoji_rank.sort_values("num",ascending=False)
    emoji_rank.to_pickle("emoji_ranking.pkl")
    print(emoji_rank)
