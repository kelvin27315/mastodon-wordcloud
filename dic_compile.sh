#辞書コンパイル
#Arch Linux
CURRENT=$(cd $(dirname $0) && pwd)
cd $CURRENT
for dic in `ls dic | grep .csv`
do
    echo "/usr/lib/mecab/mecab-dict-index -d /usr/lib/mecab/dic/mecab-ipadic-neologd -u dic/compiled/$dic -f utf-8 -t utf-8 dic/$dic" | sed -r "s/\.csv/.dic/" | bash
done
echo "userdic = $CURRENT/dic/compiled/gensokyo_town_terms.dic, $CURRENT/dic/compiled/touhou_character_names.dic, $CURRENT/dic/compiled/touhou_music_names.dic, $CURRENT/dic/compiled/touhou_spell_card_names.dic, $CURRENT/dic/compiled/touhou_terms.dic, $CURRENT/dic/compiled/touhou_work_names.dic, $CURRENT/dic/compiled/touhou_doujin_terms.dic" | sudo tee -a /usr/lib/mecab/dic/mecab-ipadic-neologd/dicrc