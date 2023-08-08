"""
絵文字ランキングを投稿しているアカウントから
1年分のランキングを取得し、現在までの絵文字の使用回数の総和とそのランキングを出す
"""

import datetime as dt
import re
import time

import pandas as pd
from dateutil.relativedelta import relativedelta
from mastodon import Mastodon
from pytz import timezone
from tqdm import tqdm


class Gensokyo:
    def __init__(self):
        self.token = Mastodon(
                client_id = "clientcred.secret",
                access_token = "usercred.secret",
                api_base_url = "https://gensokyo.town")

    def get_account_toot(self):
        """
        アカウントの過去のtootを全て取得し、絵文字と使用回数のリストを作る
        """
        toots = []
        extend_toots = toots.extend
        temp_toots = self.token.account_statuses(id=113,limit=40)
        last_year = timezone("Asia/Tokyo").localize(dt.datetime((dt.date.today()-relativedelta(years=1)).year,1,2,0,0,0,0))
        while temp_toots[0]["created_at"].astimezone(timezone("Asia/Tokyo")) > last_year:
            for toot in temp_toots:
                if "トレンド" not in toot["content"] and toot["created_at"].astimezone(timezone("Asia/Tokyo")) > last_year:
                    #toot = {content: "<p>内容</p>"}
                    print(toot["content"][3:10])
                    extend_toots(toot["content"].split("<br />"))
            time.sleep(3)
            temp_toots = self.token.account_statuses(id=113,max_id=temp_toots[-1]["id"]-1,limit=40)
        return(toots)

    def post_rank(self, emoji_rank):
        temp_rank = 0
        temp_num = 0
        toot = "{}年に使用された絵文字の使用回数ランキングです。\n".format(dt.date.today().year)
        #ランキング作る
        for i, emoji in emoji_rank.iterrows():
            if emoji["num"] == temp_num:
                temp = "{}位: {} ({}回)\n".format(temp_rank,emoji["emoji"],emoji["num"])
            else:
                temp = "{}位: {} ({}回)\n".format(i+1,emoji["emoji"],emoji["num"])
                temp_num = emoji["num"]
                temp_rank = i+1
            if len(toot) + len(temp) >= 500:
                self.token.status_post(status = toot, visibility = "unlisted")
                toot = ""
                time.sleep(1)
            toot += temp
        self.token.status_post(status = toot, visibility = "unlisted")

def relist(toots):
    """
    不要物を除く
    """
    rank = [toot for toot in toots if toot[-3:] != "です。"]
    rank = [emoji if emoji[-4:] != "</p>" else emoji[0:-4] for emoji in rank]
    return(rank)

def emoji_counter(rank):
    """
    集計
    """
    emoji_rank = pd.DataFrame({"emoji": list(set([re.search(":[a-zA-Z0-9_-]+:", emoji)[0] for emoji in rank])), "num": 0})
    for emoji in tqdm(rank):
        emoji_rank.iat[emoji_rank[emoji_rank["emoji"]==re.search(":[a-zA-Z0-9_-]+:",emoji)[0]].index[0],1] += int(re.search("[0-9]+回", emoji)[0][:-1])
    emoji_rank = emoji_rank.sort_values("num",ascending=False)
    emoji_rank = emoji_rank.reset_index(drop=True)
    return(emoji_rank)

if __name__ == "__main__":
    gensokyo = Gensokyo()
    toots = gensokyo.get_account_toot()
    rank = relist(toots)
    emoji_rank = emoji_counter(rank)
    emoji_rank.to_pickle("emoji_ranking.pkl")
    gensokyo.post_rank(emoji_rank)
