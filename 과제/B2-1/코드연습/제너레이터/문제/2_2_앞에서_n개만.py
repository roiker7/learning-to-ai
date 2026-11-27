# 설명은 개념/2단계_필요한_만큼만_꺼내기.md
def take(items, n):
    a = 0
    for i in items:
        if a >= n:
           return
        a+=1
        yield i


if __name__ == "__main__":
    for item in take(["가", "나", "다"], 2):
        print(item)
