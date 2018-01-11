# mastodon-wordcloud
mastodonで1日のtootを取得しWordCloudを作成します。

Mastodonの東方インスタンス [gensokyo.town](https://gensokyo.town) で動いているbot,幻想トレンド( [@genso_trend@gensokyo.town](https://gensokyo.town/@genso_trend) )のプログラムです。

動いてた(インスタンス: [gensokyo.cloud](https://gensokyo.cloud) , アカウント: [@genso_trend@gensokyo.cloud](https://gensokyo.cloud/@genso_trend) )

### 概要

1日の終了時にgensokyo.cloudのローカルタイムラインに流れた1日分のtootからワードクラウドを作成します。また、そのとき使用したtootの数も表示します。<br>
ワードクラウドに表示される単語は品詞が[名詞, 動詞, 形容詞, 副詞]のもののみで、[動詞, 形容詞, 副詞]の場合は単語の原型が表示されます。CWについては、CWが有効(["sensitive"] が True)の場合表示される["spoiler_text"]のみを使用しており、その場合は隠されている["content"]は使用されません。<br>

絵文字についての１日の使用回数のランキングを表示します。<br>
対象の絵文字は:(コロン)で囲われて表示されるタイプの絵文字で、ランキングにはその使用回数も表示されます。これもワードクラウドと同じくCWについては表示されているもののみ使用し、隠されている方については使用されません。

分かち書きには[MeCab](http://taku910.github.io/mecab/)を、追加辞書には[mecab-ipadic-NEologd](https://github.com/neologd/mecab-ipadic-neologd)を使用しています。<br>
ユーザー辞書は主にきゅー(Cue)様の[東方Project辞書 R7-20170509](http://9lab.jp/works/dic/th-dic.html)を参考に作成しています。
