# 설명은 개념/4단계_제너레이터_연결하기.md
def long_words(words, n):
    for i in words:
        if len(i) >= n:
            yield i 

def add_mark(words):
    for i in words:
        a = i + "!"
        yield a


if __name__ == "__main__":
    for word in add_mark(long_words(["별", "바다", "하늘"], 2)):
        print(word)
