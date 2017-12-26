# mastodon-wordcloud
mastodonで1日のtootを取得しWordCloudを作成します。

Mastodonの東方インスタンス[gensokyo.cloud](https://gensokyo.cloud),  [gensokyo.town](https://gensokyo.town)で動いているbot,幻想トレンド([@genso_trend@gensokyo.cloud](https://gensokyo.cloud/@genso_trend), [@genso_trend@gensokyo.town](https://gensokyo.town/@genso_trend))のプログラムです。

### 概要

1日の終了時にgensokyo.cloudのローカルタイムラインに流れた1日分のtootからワードクラウドを作成します。また、そのとき使用したtootの数も表示します。<br>
ワードクラウドに表示される単語は品詞が[名詞, 動詞, 形容詞, 副詞]のもののみで、[動詞, 形容詞, 副詞]の場合は単語の原型が表示されます。<br>
分かち書きには[MeCab](http://taku910.github.io/mecab/)を、追加辞書には[mecab-ipadic-NEologd](https://github.com/neologd/mecab-ipadic-neologd)を使用しています。<br>
ユーザー辞書は主にきゅー(Cue)様の[東方Project辞書 R7-20170509](http://9lab.jp/works/dic/th-dic.html)を参考に作成しています。
