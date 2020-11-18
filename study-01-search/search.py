### 検索ツールサンプル
### これをベースに課題の内容を追記してください

import csv

# 検索ソース
source=["ねずこ","たんじろう","きょうじゅろう","ぎゆう","げんや","かなお","ぜんいつ"]

### 検索ツール
def search():
    word =input("鬼滅の登場人物の名前を入力してください >>> ")
    
    ### ここに検索ロジックを書く
    if word in source:
        print("{}が見つかりした".format(word))

    else:
        print("{}が見つかりませんでした".format(word))
        source.append(word)

    with open('character_list.csv', 'w') as f:
        writer = csv.writer(f)

        for i, character in enumerate(source):
            writer.writerow([i, character])

if __name__ == "__main__":
    search()