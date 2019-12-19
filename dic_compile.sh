#辞書コンパイル
#Arch Linux
CURRENT=$(cd $(dirname $0) && pwd)
cd $CURRENT
for dic in `ls dictionary | grep .csv`
do
    echo "/usr/lib/mecab/mecab-dict-index -d /usr/lib/mecab/dic/mecab-ipadic-neologd -u dictionary/compiled/$dic -f utf-8 -t utf-8 dictionary/$dic" | sed -r "s/\.csv/.dic/" | bash
done
echo "userdic = $CURRENT/dictionary/compiled/gensokyo_town_terms.dic, $CURRENT/dictionary/compiled/touhou_character_names.dic, $CURRENT/dictionary/compiled/touhou_music_names.dic, $CURRENT/dictionary/compiled/touhou_spell_card_names.dic, $CURRENT/dictionary/compiled/touhou_terms.dic, $CURRENT/dictionary/compiled/touhou_work_names.dic, $CURRENT/dictionary/compiled/touhou_doujin_terms.dic" | sudo tee -a /usr/lib/mecab/dic/mecab-ipadic-neologd/dicrc