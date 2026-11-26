# 설명은 개념/1단계_yield와_next.md
def countdown(n):
    for i in range(n, 0, -1):
        yield i

if __name__ == "__main__":
    for number in countdown(5):
        print(number)
