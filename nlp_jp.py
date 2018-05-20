#!/usr/bin/env python3
from konlpy.tag import Kkma, Hannanum, Mecab, Twitter
from collections import Counter, OrderedDict

IGNORE_WORDS = ['네', '저', '요', '제', '전', '분', '더', '좀', '너무']

def main():
    # kkma = Kkma()
    # hannanum = Hannanum()
    # mecab = Mecab()
    twitter = Twitter()
    sentences = []
    words = []
    with open('result') as f:
        for line in f:
            sentences.append(line)

    for s in sentences:
        words.extend(twitter.nouns(s))
        # words.extend(mecab.nouns(s))
        # words.extend(kkma.nouns(s))
        # words.extend(hannanum.nouns(s))

    od = OrderedDict(Counter(words).most_common(30))
    for k, v in od.items():
        if k in IGNORE_WORDS:
            continue
        print(k, '\t', v)


if __name__ == '__main__':
    main()
